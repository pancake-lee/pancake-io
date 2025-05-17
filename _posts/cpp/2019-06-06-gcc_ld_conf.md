---
title: "gcc/g++链接选项"
description: "链接顺序/符号冲突/显示指定动态还是静态链接"
author: Pancake
date: 2019-06-06
categories: Coding
tags: build Cpp
---

## 珍惜生命，远离链接顺序导致的问题

- 链接问题一般不会给你带来什么收益，但是出现问题，查错有时候是困难的，所以要了解一下。
- 无需深入研究，遇到问题再来看一下解决办法即可。
- 知道有这回事，当你设计一个库的时候，尽可能保证库的垂直关系，不要循环依赖。
- 尽量避免同名，C++的 namespace，以及 C 中按模块添加前缀 XXX_func()，都是为了避免同名而存在的。

---

## 测试代码

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

以上代码接口按顺序编译，先是 libb.so，然后 liba.so，最后编译 test2.cpp

---

## 链接顺序--依赖

在 ld -v 大于 2.2 时，ld 自带了-as-needed 参数，于其对应的参数是--no-as-needed

- -Wl,-as-needed，**该参数表示 ld 将会检查每个指定动态库，当需要才链接，并认为仅依赖后面（右边）的库，不依赖前面的（左边）**
- -Wl,--no-as-needed，**链接所有列举出来的库，并且没有顺序依赖关系的判断**

### 第一种情况

先忽略 same_func 相关的内容

#### libb.so 没有疑问

`g++ -shared -fPIC b.cpp -o libb.so`

#### liba.so 没有真实链接到 b

这里编译器默认开启了-as-need 选项，所以认为 a.cpp 不需要 libb.so，使用 ldd 命令查看，并没有 libb.so

```sh
$ g++ -shared -fPIC -L. -lb a.cpp -o liba.so
$ ldd liba.so
linux-vdso.so.1 (0x00007fffca820000)
libstdc++.so.6 => /usr/lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007ff3a03b0000)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007ff39ffb0000)
libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007ff39fc10000)
/lib64/ld-linux-x86-64.so.2 (0x00007ff3a0a00000)
libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007ff39f9f0000)
```

PS：动态库的编译方式导致了这里可以通过编译，如果编译可执行文件，将遇到-lb a.cpp 的顺序问题。

#### test2.cpp 编译失败

失败原因：在第二步的时候，-lb 写在 a.cpp 左边，导致 liba.so 实际上没有链接 libb.so

```sh
$ g++ -o test test2.cpp -L. -la
./liba.so: undefined reference to `say_hi()'
collect2: error: ld returned 1 exit status
```

- 这两种方法都没有问题，但涉及符号冲突时，以下两行命令导致不同的结果，下文会说到

```sh
g++ -o test -Wl,--no-as-need -L. -lb -la test2.cpp
g++ -o test test2.cpp -L. -la -lb
```

---

### 第二种情况

先忽略 same_func 相关的内容

#### libb.so

`g++ -shared -fPIC b.cpp -o libb.so`

#### liba.so，真正链接 libb.so，注意对比第一种情况的第 2 步命令

```sh
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

#### test2.cpp

由于 liba.so 已经指明了依赖于 libb.so，所以这里只需要链接 liba.so
`g++ -o test test2.cpp -L. -la`

---

### 额外细节

按照《第二种情况》的方法编译，最后加上 libpthread.so 的库
-Wl,--no-as-need 会链接上代码完全没有使用到的 pthread 库

```sh
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

-Wl,-as-need（默认选项）则不会

```sh
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

## 链接顺序--同一符号

**请注意 same_func 相关的内容**
按照《第一种情况》的方法编译到步骤 3.2，整体的输出是：

```sh
$ g++ -shared -fPIC b.cpp -o libb.so
$ g++ -shared -fPIC -L. -lb a.cpp -o liba.so
```

liba.so 在前（左），输出了**liba.so**的 same_func

```sh
$ g++ -o test test2.cpp -L. -la -lb
$ ./test
hello world!
hi!
i am a!
```

libb.so 在前（左），输出了**libb.so**的 same_func

```sh
$ g++ -o test -Wl,--no-as-need -L. -lb -la test2.cpp
$ ./test
hello world!
hi!
i am b!
```

也就是说，假设 libA.so 和 libB.so 都包含 func()函数（符号），编译时，顺序是左到右按顺序的，后加载的重名符号会被忽略掉，第一次找到的符号有效
如，-lA -lB，则将忽略 B 中的 func 版本，因此遇到问题的话：

- 方案一：利用-Wl,--no-as-need，把库的顺序写对，一般满足大多数需求，设计时也应该避免重名
- 方案二：利用 dlopen 等一系列 dl 函数动态加载库。可能你需要用 A 版本的 func1，又需要用 B 版本的 func2，而他们都是重名的，比如以下情景：（PKI 行业）程序需要集成两个厂商提供的 PKCS11 标准接口的驱动库，用于一台服务器兼容两种产品，而这两个库依赖的 openssl 版本不同，于是底下 openssl 就有一堆重名函数，但是实现未必一致。这种情况下，不仅厂商库需要链接指定版本 openssl，本身工程代码也需要用到 openssl，总不能链接 3 个不同的 openssl 库吧。
  - 要么，找到一个准确的顺序，刚好每个库都得到了他需要的函数
  - 否则，考虑使用动态加载（推荐）：一个链接使用，一个动态加载使用；或者两个都动态加载，写个类封装一下接口，还可以使用工厂模式和单例模式。

---

## 显式指定动态链接或静态链接

-Wl,-Bstatic -la  -Wl,-Bdynamic -lb

- 这样，a 将会被静态链接，而 b 将会被动态链接。前提是路径中有 liba.a 以及 libb.so。
- 显式指定一般用于：在路径中既有 a 的动态库 liba.so 也有静态库 liba.a，而你希望链接静态库。
