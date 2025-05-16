---
title: "gcc/g++链接选项"
description: "链接顺序/符号冲突/显示指定动态还是静态链接"
author: Pancake
date: 2019-06-06
categories: Coding
tags: build Cpp
---
# 珍惜生命，远离链接顺序导致的问题

* 链接问题一般不会给你带来什么收益，但是出现问题，查错有时候是困难的，所以要了解一下。
* 无需深入研究，遇到问题再来看一下解决办法即可。
* 知道有这回事，当你设计一个库的时候，尽可能保证库的垂直关系，不要循环依赖。
* 尽量避免同名，C++的namespace，以及C中按模块添加前缀XXX_func()，都是为了避免同名而存在的。

# 链接顺序--依赖

在ld -v大于2.2时，ld自带了-as-needed参数，于其对应的参数是--no-as-needed

* -Wl,-as-needed，**该参数表示ld将会检查每个指定动态库，当需要才链接，并认为仅依赖后面（右边）的库，不依赖前面的（左边）**
* -Wl,--no-as-needed，**链接所有列举出来的库，并且没有顺序依赖关系的判断**

---

### 测试代码

b.cpp

```c++
#include <iostream>
#include "b.h"
int say_hi(void)
{
	std::cout << "hi!" << std::endl;
}
void same_func()
{
	std::cout << "i am b!" << std::endl;
}
```

b.h

```c++
#pragma once
int say_hi(void);
void same_func();
```

a.cpp

```c++
#include <iostream>
#include "a.h"
#include "b.h"
int say_hello(void)
{
	std::cout << "hello world!" << std::endl;
	say_hi();//来自libb.so，
}
void same_func()
{
	std::cout << "i am b!" << std::endl;
}
```

a.h

```c++
#pragma once
int say_hello(void);
void same_func();
```

test2.cpp

```c++
#include <iostream>
#include "a.h"
int main(void)
{
	say_hello();//来自liba.so，函数内又调用了libb.so的内容
	same_func();
}
```

以上代码接口按顺序编译，先是libb.so，然后liba.so，最后编译test2.cpp

---

### 第一种情况

**先忽略same_func相关的内容**

1. libb.so没有疑问
   g++ -shared -fPIC b.cpp -o libb.so
2. liba.so，没有真实链接到b
   这里编译器默认开启了-as-need选项，所以认为a.cpp不需要libb.so，使用ldd命令查看，并没有libb.so

```
$ g++ -shared -fPIC -L. -lb a.cpp -o liba.so
$ ldd liba.so
linux-vdso.so.1 (0x00007fffca820000)
libstdc++.so.6 => /usr/lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007ff3a03b0000)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007ff39ffb0000)
libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007ff39fc10000)
/lib64/ld-linux-x86-64.so.2 (0x00007ff3a0a00000)
libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007ff39f9f0000)
```

PS：动态库的编译方式导致了这里可以通过编译，如果编译可执行文件，将遇到-lb a.cpp的顺序问题。

3. test2.cpp

* 3.1 失败原因：在第二步的时候，-lb写在a.cpp左边，导致liba.so实际上没有链接libb.so

```
$ g++ -o test test2.cpp -L. -la
./liba.so: undefined reference to `say_hi()'
collect2: error: ld returned 1 exit status
```

* 3.2 这两种方法都没有问题，但涉及符号冲突时，以下两行命令导致不同的结果，下文会说到

```
g++ -o test -Wl,--no-as-need -L. -lb -la test2.cpp
g++ -o test test2.cpp -L. -la -lb
```

---

### 第二种情况

**先忽略same_func相关的内容**

1. libb.so没有疑问
   g++ -shared -fPIC b.cpp -o libb.so
2. liba.so，真正链接libb.so，注意对比第一种情况的第2步命令

```
$ g++ -shared -fPIC a.cpp -L. -lb -o liba.so
$ ldd liba.so 
	linux-vdso.so.1 (0x00007fffdfa42000)
	libb.so => ./libb.so (0x00007f686bfb0000)
	libstdc++.so.6 => /usr/lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007f686bc20000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f686b820000)
	libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007f686b480000)
	/lib64/ld-linux-x86-64.so.2 (0x00007f686c400000)
	libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007f686b260000)
```

3. test2.cpp，由于liba.so已经指明了依赖于libb.so，所以这里只需要链接liba.so
   g++ -o test test2.cpp -L. -la

---

### 额外细节

按照《第二种情况》的方法编译，最后加上libpthread.so的库

* -Wl,--no-as-need 会链接上代码完全没有使用到的pthread库

```
$ g++ -o test  -Wl,--no-as-need  test2.cpp -L. -la -lpthread
$ ldd test
	linux-vdso.so.1 (0x00007fffe3316000)
	liba.so => ./liba.so (0x00007fb3ca2b0000)
	libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007fb3ca090000)
	libstdc++.so.6 => /usr/lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007fb3c9d00000)
	libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007fb3c9960000)
	libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007fb3c9740000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fb3c9340000)
	libb.so => ./libb.so (0x00007fb3c9120000)
	/lib64/ld-linux-x86-64.so.2 (0x00007fb3ca800000)
```

* -Wl,-as-need（默认选项）则不会

```
$ g++ -o test test2.cpp -L. -la -lpthread
$ ldd test
	linux-vdso.so.1 (0x00007fffc0ccd000)
	liba.so => ./liba.so (0x00007fb805100000)
	libstdc++.so.6 => /usr/lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007fb804d70000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fb804970000)
	libb.so => ./libb.so (0x00007fb804760000)
	libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007fb8043c0000)
	/lib64/ld-linux-x86-64.so.2 (0x00007fb805600000)
	libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007fb8041a0000)
```

---

# 链接顺序--同一符号

**请注意same_func相关的内容**
按照《第一种情况》的方法编译到步骤3.2，整体的输出是：

```
$ g++ -shared -fPIC b.cpp -o libb.so
$ g++ -shared -fPIC -L. -lb a.cpp -o liba.so
```

* liba.so在前（左），输出了**liba.so**的same_func

```
$ g++ -o test test2.cpp -L. -la -lb
$ ./test
hello world!
hi!
i am a!
```

* libb.so在前（左），输出了**libb.so**的same_func

```
$ g++ -o test -Wl,--no-as-need -L. -lb -la test2.cpp
$ ./test
hello world!
hi!
i am b!
```

也就是说，假设libA.so和libB.so都包含func()函数（符号），编译时，顺序是左到右按顺序的，后加载的重名符号会被忽略掉，第一次找到的符号有效
如，-lA -lB，则将忽略B中的func版本，因此遇到问题的话：

* 方案一：利用-Wl,--no-as-need，把库的顺序写对，一般满足大多数需求，设计时也应该避免重名
* 方案二：利用dlopen等一系列dl函数动态加载库。可能你需要用A版本的func1，又需要用B版本的func2，而他们都是重名的，比如以下情景：（PKI行业）程序需要集成两个厂商提供的PKCS11标准接口的驱动库，用于一台服务器兼容两种产品，而这两个库依赖的openssl版本不同，于是底下openssl就有一堆重名函数，但是实现未必一致。这种情况下，不仅厂商库需要链接指定版本openssl，本身工程代码也需要用到openssl，总不能链接3个不同的openssl库吧。
  * 要么，找到一个准确的顺序，刚好每个库都得到了他需要的函数
  * 否则，考虑使用动态加载（推荐）：一个链接使用，一个动态加载使用；或者两个都动态加载，写个类封装一下接口，还可以使用工厂模式和单例模式。

---

# 显式指定动态链接或静态链接

-Wl,-Bstatic -la  -Wl,-Bdynamic -lb

* 这样，a将会被静态链接，而b将会被动态链接。前提是路径中有liba.a以及libb.so。
* 显式指定一般用于：在路径中既有a的动态库liba.so也有静态库liba.a，而你希望链接静态库。
