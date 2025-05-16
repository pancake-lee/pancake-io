---
title: '利用boost::property_tree读取INI文件'
description: '通过读取INI文件的实例学习boost::property_tree类的用法'
author: Pancake
date: 2018-05-10
categories: Coding
tags: boost Cpp
---

* 本文主要通过读取INI配置文件的简单实例，初步使用boost::property_tree类
* 该类的使用方法也非常简单，如下几行代码即可
* 如xml/json等更多的使用方法请跳转：  
[boost::property_tree的官方描述](https://www.boost.org/doc/libs/1_61_0/doc/html/property_tree.html)  
[boost::property_tree的方法](https://www.boost.org/doc/libs/1_61_0/doc/html/property_tree/reference.html#header.boost.property_tree.ini_parser_hpp)

## Example:
Test.ini
```cpp
[SERVER]
IpAddr=127.0.0.1
```
Test.cpp
```cpp
#include <boost/property_tree/ptree.hpp>    
#include <boost/property_tree/ini_parser.hpp> 
void func(){
    boost::property_tree::ptree pt;        
    boost::property_tree::ini_parser::read_ini("./Test.ini", pt);
    //在windows上vs编译后出现ipStr为乱码，原因未知，改用string即可正常处理
    //char *ipStr = pt.get<std::string>("SERVER.IpAddr").c_str();
    std::string ip = pt.get<std::string>("SERVER.IpAddr");
}
```