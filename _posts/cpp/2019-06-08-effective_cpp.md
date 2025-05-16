---
title: "Effective C++ 读书笔记"
description: "各章节主要内容个人理解总结"
date: 2019-06-08
author: Pancake
categories: Coding
tags: Cpp
---

# 第一章

#### 2：尽量以const,enum,inline替换#define

* #define PI 3.14预处理直接替换了该宏，如果编译报错时，你只能看到3.14，也许你难以意识到是这个define而来的3.14带来的错误，而使用其他方法，编译器能定位到const变量或者inline函数
* #define NAME "Pancake"会导致代码有多份字符串字面值，每一份都占用内存，而定义成const变量则只有一份
* 定义数组大小可以使用enum作为大小

```c++
class A{
private:
    enum { NumTurns = 5 };
    int scores[NumTurns];//enum定义的值可以用来定义数组（行为上类似define)，而普通变量不行
}
```

* 用inline函数代替，使用define来定义一些函数体。define经常需要很谨慎地使用，需要注意各种标点，作用域等问题

#### 3：尽可能使用const

* 首先要学习指针的const

```c++
const char* p;          //non-const pointer, const data
char const * p;         //等价于上一条
char* const p;          //const pointer, non-const data
const char* const p;    //const pointer, const data

const std::vector<int>::iterator it;    //T* const, const pointer, non-const data
*it = 10;                               //true, non-const data
++it;                                   //err, const pointer

std::vector<int>::const_iterator it;    //const T*, non-const pointer, const data
*it = 10;                               //err, const data
++it;                                   //true, non-const pointer
```

* 尽可能使用const声明函数，来约束使用者，尽可能避免意料之外的情况，习惯使用const，可以更好地利用编译器来找出自己的低级错误

```c++
bool is_ten(const int a){
    return a = 10;
    //编译器会给你报错“给const变量赋值”
    //但是int a可以通过编译，直到你检查数据一路追踪到这一行代码，才发现应该用“==”
}
```

* * 返回const常量值
* * const引用作为参数是一个高效率的参数传递方式
* * const成员函数，表示不改变任何成员变量

#### 4：确定对象被使用前已先被初始化

* 永远都手动初始化内置类型
* 类类型使用（并所有成员变量都要）初始化列表，而不是构造函数赋值。
* * 次序：初始化列表保证根据定义中的先后次序初始化成员变量
* * 效率：无论是否使用初始化列表，构造函数都给成员变量设初始值，然后再在函数体做赋值，显然完全是重复工作。尤其是类类型的成员函数，先默认构造函数，再做一次赋值，而初始化列表直接调用该类的拷贝构造函数
* 对于重载多个构造函数时，为了代码不重复，使用一个init()来统一处理“赋值表现像初始化一样好”的初始化工作，却是更好的方案。其实基本也就是指内置类型。
* 对于静态（全局）变量，需要考虑编译先后，也许使用的时候，根本还没有编译到静态变量的代码。所以，对于调用跨度很大的变量，应该：（其实就是单例Singleton的用法）

```c++
class A{
};
A& getA(){
    static A a;
    return a;
}
```

---

# 第二章

#### 5/6：构造、析构、赋值运算

* 多关心编译器默认为你声明的函数：构造，析构，拷贝，赋值。他们会做什么？如：尤其是拷贝构造和赋值操作符，当成员函数为引用或者const的时候，编译器会拒绝编译那一行赋值动作，所以需要关心其行为，决定是否需要自行定义自己的版本
* 如果声明了构造函数，系统不会再为你声明无参的默认构造函数
* 禁止使用某些函数，常用于拷贝构造和赋值操作
* = defult可以显式声明编译器默认版本的函数，只能用于编译器本来就会默认声明的函数，当你需要定义带参数的构造函数，但是不想放弃默认构造函数时有用。

```c++
class A{
public:
    A() = default;          //c++11,该函数比用户自己定义的默认构造函数获得更高的代码效率
    A(const A&) = delete;  //c++11,禁止使用该函数
    A& operator=(const A&) = delete;
  
    A(long);
    A(int) = delete;        //禁止使用int利用自动转换来构造，必须使用long
private:
    A(const A&);           //声明为private并且不实现其定义也能达到=delete的效果
    A& operator=(const A&);
}

//以下例子，B想要直接调用A的一些函数，但其实严格来说不是"is-a"关系，仅仅利用继承降低代码重复
//这里要考虑多重继承的危害，考虑B是否被继承，考虑A的继承情况
//还要考虑因为B的拷贝构造和赋值操作符，会尝试调用父类A的拷贝构造和赋值操作符
//而因为是private，所以最后会编译出错
class B : private A{
  
}
```

#### 7：为多态基类声明vitrual析构函数

* 仅仅当一个类被作为，带多态性质的bass class时，才需要考虑该问题
* 总结为：作为多态性质的base class时，就应该声明一个virtual析构函数，否则不要声明virtual析构函数

##### 析构要声明为vitrual

* 因为c++明白指出，当derived class（子类）对象经由一个base class（父类）指针被删除，而该base class带着一个non-virtual析构函数，其结果未有定义，[例子](https://www.cnblogs.com/x1957/archive/2012/10/23/2734918.html)
* 上诉情况，实际执行时（静态绑定），通常是derived成分没有被销毁，则仅仅调用了base class的析构函数
* 以上情况经常出现在工厂模式，返回一个基类指针，然后进行delete时
* （动态绑定）解决问题只需要把base class的析构函数定义为virtual即可，这样根据动态绑定，将调用这个指针原本的动态类型derived class的版本的析构函数
* 所以**只要该类带有vitrual函数，至少析构函数要定义为vitrual**
* 更进一步可以为base class定义纯虚函数virtual void func() = 0;来阻止使用者实例化base class

##### 析构不能声明为vitrual

* 当需要跨语言（如C语言）等情况时，定义vitrual，会带入vtbl虚函数表，导致意想不到的结果

##### 不应该继承任何没有vitrual函数的类

* 如std::string,(vector,set,list)等等，都带有non-virtual析构函数，如果继承，当出现利用指针转换了类型，然后delete时，也会出现上述问题
* 以上列举的例子，本来就并不是被设计来利用多态性的

#### 8：析构函数绝对不能抛出异常

* 假设有一个vector`<A>`，而A析构时抛出异常，那么在析构vector内多个A时，抛出不止一个异常，对于C++，则要么结束执行，要么导致不明确行为
* 析构函数有可能抛出异常，在析构函数内捕捉并吞掉（忽略）或者结束程序
* 有可能抛异常的操作，应该安排在普通函数

```c++
class DBConn{
public:
    void close()//提供给使用者，使用者可以主动close并捕捉错误
    {
        db.close;       //假设db.close可能抛出异常
        closed = true;
    }
    ~DBConn()
    {
        if(!closed){//也兼顾使用者（确信不会有错误而）不主动close（或者忘了）的情况
            try{
                db.close();
            }
            catch(){
                //记录错误信息
                //std::abort();//不处理，或者结束程序
            }
        }
    }
private:
    DBConnection db;
    bool closed;
}
```

#### 9：绝不在构造和析构中调用virtual函数

* 构造函数（析构函数）会先（后）调用基类自己的构造（析构），一下代码则在构造AA时调用func，但是首先会调用A的构造，调用到func函数，在该例子中，func为A的版本，但A的版本是纯虚函数，于是很可能出现不确定行为。即使A的func有实现（非纯虚），那么调用A版本的func又并非设计初衷（不同的类具体的操作不一样）

```c++
class A{
    A(){func();}//设计时认为，这种类都需要执行某个处理，只是不同的类，具体操作不一样
    virtual void func() = 0;
}
class AA{
    virtual void func();//实现自己版本的func
}
//当有如下代码
AA a;
```

* 析构同理由于次序问题导致一些奇怪的情况
* 小心多个调用层次而忽略的虚函数调用，这样甚至躲过了一些编译器的警告提示

```c++
class A{
    A(){init();}
    virtual void func() = 0;
    void init(){func();}
}
```

* （父类称为上级，子类称为下级）无法使用vitual从base class向下调用，但是可以把必要的构造信息向上传递，如下：构造AA时，向上传递name参数，给到A::func来执行相应处理

```c++
class A{
    A(int i){//根据i执行不同的处理
        func(int i);
    }
    void func(int i);
}
class AA{
    AA(std::string name):A(name_2_type(name))
    {}
    static int name_2_type(std::string name);
}
```

####10/11： operator= （与下一条比，主要是内存管理问题）

* 返回一个reference to *this，包括+=, -=, *=等等，因为可能很习惯地写出这样的代码

```c++
a = b = c = 10;
a = (b = (c = 10));
```

* 证同测试，处理自我赋值，因为:
* * 很多隐含的自我赋值的情况
* * 有可能赋值时把左操作数delete了，然后用右操作数拷贝构造，左右操作数是同一对象时，则崩溃了

```c++
A& A::operator=(const A& rhs){
    if(this == &rhs) return *this;//证同测试
}

//很可能忽略这种情况
std::vector<A> vec;
int i = j = 5;//模拟两个for循环嵌套
vec[i] = vec[j];//隐藏的自我赋值

A a1;
A *p_a2 = &a1;
*p_a2 = a1;//隐藏的自我赋值
```

* 异常问题，主要是new操作可能会抛出异常，如内存不足。
  版本234都可以处理好自我赋值和处理异常，并且可以考虑加证同测试，在自我赋值情况发生比较多的时候，效率更高，发生概率低时，因为要if判断所以反而低效

```c++
//版本1，不该用版本
A& A::operator=(const A& rhs){
    //不管有没有证同测试，以下new抛出异常，都会造成，pb指向无效内存
    delete pb;//pb是一个指针类型的成员变量，赋值需要拷贝这对象
    pb = new B(*rhs.pb);//而有可能它没有定义=号，而使用拷贝构造
    return *this;
}
//版本2
A& A::operator=(const A& rhs){
    B* pb_old = pb;//先记下旧的
    pb = new B(*rhs.pb);//如果这里抛出错误，pb仍然指向旧的内存
    delete pb_old;//抛出错误不会执行delete，旧的内存仍然有效
    return *this;
}
//版本3
A& A::operator=(const A& rhs){
    A tmp(rhs);//制作一个临时副本
    swap(tmp);//this和副本交换数据
    return *this;
}
//版本4
A& A::operator=(A tmp){
    //制作临时副本的动作可以利用参数传值产生副本，这样编译器的代码更高效，当然阅读性较低
    swap(tmp);//this和副本交换数据
    return *this;
}
```

#### 12：拷贝构造和赋值运算时记得每一个变量（与上一条比，主要是能不能达到设计预期的问题）

* 对于指针，是拷贝指针，还是拷贝数据，如果拷贝指针，那么内存管理的问题要怎么设计
* 对于父类，需要调用父类的赋值构造和赋值运算操作

```c++
class A : public B {}

A::A(const A& a):B(a) {}//使用a（自动转换后的父类部分）来构造新对象中父类B部分

A::operator=(const A& rhs){
    B::operator=(rhs);//使用rhs（自动转换后的父类部分）来给左值中的父类部分数据赋值
}
```

* 可见，如果加一个成员变量，相关的所有coping函数（所有重载版本的复制拷贝和赋值操作）都需要加上其复制的操作代码，当然构造函数的初始化也要加上。

---

# 第三章

资源管理，包括动态分配的内存，文件描述符，互斥锁等等
涉及:
std::auto_ptr
std::tr1::shared_ptr
以及一系列相关细节问题的讨论，由于目前大多数情况不会遇到所以
目前仅保证new的内存在每一条路径上都会被delete即可

---

# 第四章

#### 18：让接口容易被正确使用，不易被误用

* * 观念：任何接口如果要求客户必须记得做某些事情，就是有着“不正确使用”的倾向
* * 多用const就是一种方法，“以const修饰operator * 的返回类型”就可以避免if(a * b = c)这样的代码（本来是要==）
* * 观念：尽量令你的自定义类型行为与内置类型（或已有常用类型）一致。（上一行中的例子，也支持了本观念，不能对int * int的返回值赋值）（又如：stl所有容器都有一个size接口，可别取名为length来实现size一样意义的接口）
* * 如果你希望客户那么做，你尽量限制他只能这么做，或者帮他完成

```c++
//例子一
class Month{
public:
    Month(int m);//普通版本
}

class Month{
public:
    static Month Jan() { return Month(1); }//使用static函数替换直接声明static对象，理由见条款4
    ...
    ////既然月份是有限的，也不希望客户创建额外的值，那么直接列举，就可以避免错误
private:
    explicit Month(int m);//不允许这样创建
}

//例子二
//factory函数返回基类指针
A* createObj(int type);

//你一定希望客户记得delete这个指针，并且不要delete两次
//那么你可能希望客户使用std::tr1::shared_ptr来管理指针，请直接限制客户只能使用它
std::tr1::shared_ptr<A> createObj(int type);

//你可能希望客户使用这个类时，不只是简单的delete，而是再额外调用一些操作delA()
//那么shared_ptr是支持指定删除器的，于是你应该为客户使用，而不是只告知客户
void delA(){}
std::tr1::shared_ptr<A> createObj(int type){
    AA *aa = new AA;//继承了A的类，先生成对象，条款27
    std::tr1::shared_ptr<A> retVal(aa, delA);
    return retVal;
}
//指定删除器的方案同时还解决了“cross-DLL problem”（在一个dll被new，在另一个dll中delete带来的问题）
//因为对应的删除器是来自于new所在的dll中
```

* * 第三章和这里都在举例使用std::tr1::shared_ptr，因为它可以较轻易地解决这些问题，但是它也带来体积和效率等问题，要衡量“降低客户错误”和“执行成本”之间的优先级。

#### 19：设计class犹如设计type

直接翻书

#### 20：尽量以pass-by-reference-to-const替换pass-by-value

* 一下两种声明，在func函数体内，使用a的语句几乎都一致，却节省了A的构造和析构（包括其 成员变量以及父类的构造和析构）

```c++
void func(A a);
void func(const A &a);
```

* slicing problem切割问题：当一个derived class以pass-by-value的方式传递给base class对象时，将使用base class的构造函数，于是形参仅仅是一个base class，丢弃了一切实参derived class特异部分。除非你是故意这么做，否者用pass-by-reference-to-const就可以轻易解决问题

```c++
class A : public B {}

void func1(B b) { b.f(); }//调用的是B的版本
void func2(const B &b) { b.f(); }//调用的是A的版本
```

* 当传递内置类型，以及STL的迭代器和函数对象（以及一些较小的自定义类型）使用pass-by-value反而效率高一些，看起来也简洁

#### 21：必须返回对象时，别妄想返回其reference

* 举了一百个反例证明“必须返回一个新对象时，只能返回一个pass-by-value”
* 这个问题，在localtime在多线程下的bug，也有一定体现

#### 22：将成员变量生命为private

* 一致性，一个类所有使用都是成员函数，不需要考虑是方法还是变量，是否需要加()
* 更精确的控制：读写权限，值的范围等
* 封装性：封装的意义在于，在对外输出逻辑一致的前提下，可以修改内部逻辑。比如有很多“利用空间换速度”的方案，具体使用哪种方案，上一层的代码不应该关系，不应该受到影响

#### 23：宁以non-member、non-friend替换member函数

* 涉及namespace，目前很少用所以直接再看一遍书吧
* class保持精简，把一些便利性质的函数做成，在同一namespace下的non-member、non-friend函数，如一个函数仅仅为了一次过（便利地）调用某class的3个成员函数
* 这些non-member、non-friend函数应该按照功能，分别定义在几个头文件中，避免“我仅仅需要一个简单的函数，却要把这个namespace下所有内容都include进来”的问题
* 这样做，连客户都可以使用这个namespace编写属于他们自己的“便利函数”

#### 24：若所有参数皆需类型转换，请采用non-member函数

* 先记住：只有在参数列表中的变量，才会被隐式转换
* 所谓参数列表外的参数，一般指的是成员函数的this参数
* 主要例子是operator*

```c++
class Rational{//有理数
public:
    A(int a = 0, b = 1):numerator(a),denominator(b) {}
    //利用这个构造，可以由int隐式转换成Rational
  
    //member版本
    const Rational operator*(const Rational &rhs) const;
  
private:
    int numerator;//分子
    int denominator;//分母
}

//根据member版本，可以由以下代码
Rational a(1, 2);
Rational result = a * 2;//正确，等价于a.operater*(2);这样2被转换成Rational
Rational result = 2 * a;//错误，展开为2.operater*(a);2不在形参内，不会被转换

//non-member版本，可以正确运行上述代码
const Rational operator*(const Rational &lhs, const Rational &rhs)
{
    return Rational(lhs.getn() * rhs.getn(),
                    lhs.getd() * rhs.getd());
}
```

* 这个条款，当从Object-Oriented C++ 跨进 Template C++ 时（条款1），并不一定适用（条款46）

#### 25：考虑写出一个不抛异常的swap函数

* 当一个类里包含指针时，std提供的默认的swap函数将使用拷贝数据来交换两个指针的内容，但其实我们只需要把两个指针的值交换即可
* 于是有时候我们需要实现特例版本的swap函数，这一条款是讨论实现这个swap时需要注意什么

---

# 第五章

#### 26：尽可能延后变量定义式的出现时间

* “非得使用这个变量再定义它”：当你需要使用某变量了，再去定义这个变量
* “甚至直到能够给它初值为止”：当你定义一个变量，最好可以直接对其赋值，就无需先调用默认构造，再调用赋值操作
* 这样做，避免定义了一个不使用的变量，比如定义后，在使用前执行了return，或者抛出异常
* 当遇到循环，并该变量仅在循环内用到时（如下），除非你知道两者的效率差距很大，并且你对效率有很高的需求时，才使用版本一，否则使用版本二（作用域更小，代码更清晰）

```c++
//版本一：一次构造，一次析构，n次赋值
A a;
for(int i = 0; i != n; ++i){
    a = i * i;//示意给a设置某个值
    send(a);//发送a的数据到网络
}
//版本二：n次构造，n次析构
for(int i = 0; i != n; ++i){
    A a(i * i);//示意给a设置某个值
    send(a);//发送a的数据到网络
}
```

#### 27：尽量少做转型动作

* 关于
  const_cast,
  dynamic_cast,
  reinterpret_cast,
  static_cast
  4个类型转换，以及一些细节问题（如下），但目前未必需要牢记

```c++
class B {};
class A : public B {};
A a;
B *p_b = &a;
//这里p_a的值是A*隐式转换成B*的，所以p_a的值（指针值）未必等于&a
//因为A的内存首地址处也许是vtbl，而不是其B的部分，具体要看编译器
```

#### 28：避免返回handles指向对象内部成分

* handles是指各种成员函数等可以调用一个类的操作
* 如果返回了对象的内部成分，也许客户就可以操作本来不能修改的内部变量
* 还可能返回的内部变量被保存，而整个类已经被析构后，还使用了这个（以为还存在的）变量

#### 29：为“异常安全”而努力是值得的

* 保证如果异常被抛出，程序状态不改变，回到调用函数之前的状态
* 一般包括：不泄露任何资源，不允许数据败坏
* 例子，可以使用条款13和14来改正

```c++
void A::setB(){
    lock(&mutex);//用条款14来保证lock一定会unlock
    delete m_p_b;//用条款13来改正
    m_p_b = new B;//当new抛出异常，unlock没有调用，m_p_b指向无效内存
    unlock(&mutex);
}
```

* 此外为了保证异常安全，还有很深的讨论，直接看书

#### 30：彻底了解inlining的里里外外

* 并非你生命了inline，编译器就一定给你做inlining，具体要看使用场景以及编译器
* 过多使用inline会是的代码体积增加，这很容易理解
* inline函数无法跟随程序库的升级而升级，因为是以函数本体写到代码中的，所以使用到inline的部分，都因为inline升级，而必须重新编译才能生效。
* inline函数极难调试，因为这根本不在你的源代码中，是编译器帮你粘贴过去的
* 比较好的策略是，编写时不要声明inline，直到你需要优化代码效率，再去寻找代码中值得inline的地方

#### 31：将文件间的编译依存关系降至最低

* N：在不是特别大的工程（重新make也是分分钟的时）中花太多时间在这个问题上不是特别值得

```c++
class A{
public:
    void func();
private:
    std::string str;
    B b;
}
```

* 问题：当你修改private的成员变量，比如增加一个变量，那么所有使用A的源码都需要重新编译，哪怕那些代码其实仅仅用到了A::func()，那要提倡实现和接口分离，客户调用func()接口，当修改起相关实现时，能否不需要重新编译（如何实现与我无关，我为什么要重新编译），这样在修改代码时，重新编译的内容也更小，编译也就更迅速了
* 利用handle classes和interface classes
* * handle则设计一个类持有实现类的references或者pointers
* * interface则设计一个纯虚基类来描述派生类都有什么接口，客户仅能看到接口
* * 以上两个方案都把头文件分开，客户仅include其handle或者interface的头文件
* 未必每次使用都需要调用A的成员函数，比如只是生命一个函数的参数和返回值，则仅仅需要声明式 `class A;`不需要定义式

---

# 第六章

#### 32：确定你的public继承塑模出is-a关系

* 仅仅只public部分，也正是给用户看到的部分
* 主要是概念和思维，文字描述：
* * 正确：学生是一个（is-a继承）人，人可以做的所有事情，学生都可以做
* * 错误：企鹅是一只（is-a继承）鸟，鸟（定义了一个方法）可以飞，那么企鹅也可以飞
* * 改正：鸟不一定会飞，企鹅继承鸟，会飞的鸟继承鸟
* 总结：基类里有那么几个性质，如果这些性质与子类有差异，那么他们不该是public继承关系，又或者要加一层继承来区分这个差异
* * 又如：正方形是一种矩形是书本的说法，在这里不能成立
* * 矩形：我可以保证在不增加高度的条件下，增加宽度可以增加面积
* * 正方形：只要我的宽度增加，我的高度一定增加，我无法保证上一行所说
* * 如果客户使用一个正方形时，利用其矩形（基类）的特性来做某事（我只想改变长度），那客户的高和宽应该遵循什么规则（咦？我的宽为什么被改变了）？
* * 所以：正方形不能由矩形public继承而来，他们不是is-a关系，甚至他们的定义都不相像，矩形应该有宽和高两个成员变量并分别赋值没有依赖关系，但是正方形只有一个边长值

#### 33：避免遮掩继承而来的名称

* 继承时，编译器查找名字的顺序：
* * 假设：子类成员函数func()调用了一个叫f()的函数
* * 先查找func内部有无定义名称f，然后是子类，然后是父类，然后是namespace，然后是global
* 当找到了名字（不会去匹配类型），则使用，不会继续查找，这个问题不管类型，不管是否virtual等属性，都遵循

```c++
class Base{
public:
    virtual void mf1() = 0;
    virtual void mf1(int);
}
class Derived: public Base{
public:
    virtual void mf1();//我实现这个虚函数的具体行为，但是这覆盖了父类所有mf1的名字
}

Derived d;
d.mf1();    //正确，这就是Derived::mf1
d.mf1(2);   //错误，由于查找名字的顺序，在Derived中找到了mf1，不会再找父类

```

* 不应该利用以上的规则来故意覆盖名字（故意让Derived没有mf(int)函数），或者描述为“不想继承base classes的所有函数”，因为这样就违反条款32，不做累述
* 如何在重载/继承时不额外覆盖？
* * 使用using

```c++
class Base{
public:
    virtual void mf1() = 0;
    virtual void mf1(int);
}
class Derived: public Base{
public:
    //让Base class内名为mf1的所有东西在Derived作用域内都可见，并且是public
    using Base::mf1;
    virtual void mf1();
    //意味着，首先继承Base的mf1（名为mf1的所有）同时重载mf1无参数版本
}
```

* private继承：由于别的因素（条款39）使用了private继承base class，并且希望继承mf1无参数版本（这个函数在base是public，仅因为用private继承，导致在Derived中为private），那么如果使用using，则把所有名为mf1的都提供（public）了，所以需要别的办法，如下一行
* 转交函数，在某些不能使用using的编译环境下，也只能用这个办法实现上一方案

```c++
class Derived: private Base{
public:
    virtual void mf1() { Base::mf1(); }
    //这个声明实质其实只是名称的覆盖，并非一个继承
    //而定义中调用mf1()则仿照了继承
    //同时这里是隐式inline，所以与平时的继承几乎一模一样
}
```

#### 34：区分接口继承和实现继承

* 一般，继承时，一个public函数有一下选择：
* * derived class只继承成员函数的接口（声明）
* * derived class继承接口和实现，并能够覆写所继承过来的实现
* * derived class继承接口和实现，但不准覆写所继承过来的实现

```c++
class Shape {//一个可以显示在屏幕上的几何性质
public:
    virtual void draw() const = 0;
    virtual void error(const std::string& msg);
    int objectID() const;
}
```

* 下面分别分析

##### pure virtual（纯虚函数）：derived class只继承成员函数的接口（声明）

声明为pure virtual表示：“你必须提供一个draw函数，但是我不干涉你怎么实现它”
一般pure virtual都没有定义，目前所知唯一作用是，他的定义可以实现一种机制，后面impure virtual中提到

##### non virtual：derived class继承接口和实现，但不准覆写所继承过来的实现

声明为non virtual表示：“每个Shape对象（包括其子类）都有一个用来生成ID的函数，并且总是使用相同的计算方法，这个方法在基类Shape已经定义了”

##### impure virtual：derived class继承接口和实现，并能够覆写所继承过来的实现

声明为impure virtual表示：“当遇上错误，你可以调用error来处理，你可以为derived实现一份特殊的实现，你也可以按照通常的处理方法（base class的缺省定义）”

* * 但是如果不注意的话，这里是有可能出现漏洞的，并没有完美的解决办法，应该自己注意：
    基类是飞机，继承出A型和B型飞机，他们使用相同飞行模块，于是飞行模块在设计之初被定义在基类（飞机）中，现在扩展设计C型飞机，有更好的飞行模块，但是由于忘了重新编写这个impure virtual函数(如果是pure则编译器会报错)，导致C型飞机按照基类定义那样飞行，甚至有可能这样飞不了。
    所以设计者必须记得这么一个问题。当然也可以用下面的方法来避免（提醒自己在干嘛）
* * 第一种：把“virtual函数接口”和“缺省实现”分离开来

```c++
class Airplane{
public:
    virtual void fly() = 0;//不定义其实现
protected://提供给继承类内部使用，但是继承类使用者不可见
    void defaultFly();//谁都不应该修改一个飞机普通的飞行模块
}
class ModeA: public Airplane{
public:
    virtual void fly(){ defaultFly(); }
    //设计者明确知道自己必须定义“这个飞机怎么飞”
    //并且，明确知道这个飞机具体“怎么”飞
    //当设计ModeC时，他也一定记得是调用缺省还是自己重新实现
}
```

* * 第二种：上面提到对pure virtual有一种作用

```c++
class Airplane{
public:
    virtual void fly() = 0;
}
void Airplane::fly() {} //定义其实现

class ModeA: public Airplane{
public:
    virtual void fly(){ Airplane::fly(); }  //纯虚函数，即使有定义，也一定要实现
    //思路和上一种一样，写法不一样
    //但是这样，fly的缺省实现代码从第一种中的protect提升到了public，客户可以调用到
}
```

#### 35：考虑virtual函数以外的其他选择

* 书中讨论引用的例子很多，篇幅比较长
* 值得一提的是，其引用的例子最后用Strategy设计模式的普遍方案比较值得参考
* * 例子：设计一个游戏人物，人物的血量需要一个计算方法，最初步的方案是virtual函数，每一个子类都实现自己的计算方法，也可以继承使用父类的缺省方法
* * 而你很快就遇到一个人物的计算方法并非一成不变的，会有BUFF和DEBUFF，问题就编程了典型的策略模式所要解决的问题了
* * strategy（策略模式）描述起来就是：人物血量的计算方法并不是自己的一个函数，而是另一个类的接口，则有一个“血量计算员”的类，其派生出各种不一样的子类来实现多种计算方法，每个人物持有一个“血量计算员”的基类指针，利用多态性调用其实际派生类实现的计算方法

#### 36：绝不重新定义继承而来的non-virtual函数

* 因为这样做违反几条其他条款，不管用其他条款或者面向对象的思路来说明，最终都能证明不应该这么做
* 以下为这样做最直观的效果

```c++
class B{
public:
    void func1();
    virtual void func2();
}

class D:public B{
public:
    void func1();
    virtual void func2();
}

B b;
D d;
B* pb = &b;
D* pd = &d;
pb->func1();    //B::func1
pb->func2();    //B::func2
pd->func1();    //D::func1
pd->func2();    //D::func2

pb = &d;        //使用基类指针持有子类对象，ok
pb->func1();    //B::fun1，non-virtual静态绑定
pb->func2();    //D::fun2，virtual动态绑定
//不管基于什么理由，你都不应该这样设计，违反一般的开发设计习惯
//比如：违反条款32的is-a原则
//完全可以把fun1声明为virtual，书中也没提供更多解决方案，只是证明不该这么干
```

#### 37：绝不重新定义继承而来的缺省参数值

```c++
class B{
    virtual void func(int i = 0);
}

class D: public B{
    virtual void func(int i = 1);
}
B b;
b.func();   //i为0
D d;
d.func();   //i为1
B *pb = &d;
pb->func(); //调用了D::func但是i为0

```

* 因为默认参数是静态绑定的，而virtual函数是动态绑定的
* 静态绑定表示：编译器在编译时判断func是来自于B类（指针）的调用而使用了B的默认参数int i = 0
* 动态绑定表示：当运行时，根据pb持有的对象实际是什么，在vtbl中查找对应版本的函数版本D::func
* 如果想定义成D::func(int i= 0)默认参数就一样了，也是错的，因为这样代码重复，修改B也要记得修改D
* 解决的设计思路翻书比较好，其实是条款35列举的NVI（non-virtual interface）手法，大概是(当然默认值永远都是0)

```c++
class B{
public:
    void func(int i = 0) { return doFunc(i); }
private:
    virtual void doFunc(int i);
  
}

class D: public B{
private:
    virtual void doFunc(int i);
}
```

#### 38：通过复合塑模出has-a或“根据某物实现出”

* 分清楚has-a和is-a的关系，来区分应该继承一个类，还是，作为成员变量

#### 39：明智而审慎地使用private继承

* private表示：根据某物实现出，具备父类的某些特性，拥有父类某种技术的实现
* “根据某物实现出”这个概念在“38：复合”中也有，如何取舍？
* 应该尽可能使用复合，当涉及到protected或者virtual函数牵扯进来的时候，才使用private继承
* 例子：
* * 两个版本只是表明方法不只有一个，具体怎么设计比较好根据具体情况而定
* * 而更多的情况，可能是版本二更有参考价值，原因如下
* * 版本二，你可以把onTick保护起来，因为版本一的onTick是可以被Widget的子类继承重写的
* * 版本二，你可以把WidgetTimer定义在Widget外，并使用指针来保存Timer，这样可以实现条款31的编译依存性的最小化

```c++
//timer可以设置一个onTick函数当定时器到时间了就调用
class Timer{
public:
    virtual void onTick() const;  
}
//版本一
//我们有一个widget类，带有一个功能是定时备份一次数据到本地
class Widget: private Timer{
private:
    virtual void onTick() const;
    //这并不是一个需要提供给Widget用户的接口，而是Widget需要的一个技术的实现
    //继承并实现onTick后，Widget内部代码使用该函数
}
//版本二
//可以结合38：复合，来实现
class Widget{
private:
    class WidgetTimer: public Timer{//多封装一层来继承onTick并避免private继承
    public:
        virtual void onTick() const;
    }
    WidgetTimer timer;
}
```

* 另外private会涉及到EBO（空白基类最优化）的实现，这种空白基类没有成员变量，但是可能拥有typedefs,enums,static,non-virtual函数，使用private继承而不是复合，可以优化对象大小

#### 40：明智而审慎地使用多重继承

##### 问题1：

* 相同名字：C继承了A和B两个类，而A和B中分别有功能不同的但同名的func
* 于是仅有 `c.A::func()`来指明是哪个func才能通过编译
* 这个问题即使控制func的访问权限，编译器也无法正确判断应该用哪个，它仅仅判断名字。

##### 问题2：

* 砖石（菱形）型多重继承：D1和D2都是继承B的，而现在有A同时继承D1和D2
* 那么现在A的对象，内部持有一个D1对象和D2对象，而他们都持有一个B对象，也就是说A持有两个B对象，当你使用B对象中一个成员变量时，到底是调用了哪份？这个问题从持有两个B对象时，就已经不符合逻辑了。
* 这里可以引入virtual继承来处理持有两份B对象的问题，但是virtual在大小，速度，初始化复杂度都会增加成本。
* 所以砖石型多重继承是需要尽可能避免的

##### 实用情况举例：（只是表明多重继承还是有意义的）

* 我们有一个接口类I（interface），通过该类提供接口同时封装实现。
* 然后我们又有一个类B中的代码对于实现接口很有帮助，希望复用这些代码。
* 这时，我们public继承I，然后private继承B，实现I接口时，使用B的实现

---

# 第七章：模板和泛型编程

其主要涉及模板编程的问题讨论，将来接触到了再看书详细思考

---

# 第八章：定制new和delete

其主要涉及new和delete的异常处理，以及重载，以及placement new的应用，暂时用不上，将来再看书补充

# 第九章：杂项讨论

# 53：不要轻忽编译器的警告

* 严肃对待编译器的每条警告，争取在最高警告等级也无任何警告
* 举例说明严重性：D根本不是继承了B::f而是直接名字覆盖了f，其危害看条款33，这会导致也许你写代码真的出现了问题时，而调试多天后发现，是一个编译器一开始就给你警告的问题。

```c++
class B{
public:
    virtual void f() const;
}
class D: public B{
public:
    virtual void f();
}
```

#### 54：让自己熟悉包括TR1在内的标准程序库

#### 55：让自己熟悉Boost

这两条可以翻书查阅大概包括哪些技术，提供了哪些功能，更多的需要看其他文献，这里不展开
