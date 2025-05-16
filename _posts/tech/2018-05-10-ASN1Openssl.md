---
title: 'ASN.1编码的OpenSsl实现'
description: 'ASN.1规则利用OpenSsl提供的实现进行编码与解码'
author: Pancake
date: 2018-05-10
categories: Tech
tags: PKI OpenSsl Cpp
---

# OpenSsl提供的用于处理ASN1的宏
* ASN1_SEQUENCE 定义一个最外层是SEQUENCE类型的ASN1数据类型
* DECLARE_ASN1_FUNCTIONS 声明指定ASN1数据类型对应的函数
* IMPLEMENT_ASN1_FUNCTIONS 定义指定ASN1数据类型对应的函数
* 以上宏主要实现i2d和d2i的OpenSsl类型到数据的转换，另外需要自己实现构造/析构/GET/SET等函数

Example：  
OpenSslAsn1.h:
```cpp
#pragma once
#include <openssl/bn.h>
#include <openssl/asn1.h>
#include <openssl/asn1t.h>
#include <openssl/objects.h>
struct Sm2Signature_Hander
{
	BIGNUM* x;
	BIGNUM* y;
	Sm2Signature_Hander();
	Sm2Signature_Hander(Sm2Signature_Hander *s1);
	virtual ~Sm2Signature_Hander();
	void setX(const unsigned char* data, int len);
	void setY(const unsigned char* data, int len);
	int getX(unsigned char* data);
	int getY(unsigned char* data);
};

DECLARE_ASN1_FUNCTIONS(Sm2Signature_Hander);
/* 
DECLARE_ASN1_FUNCTIONS展开如下
Sm2Signature_Hander *Sm2Signature_Hander_new(void);//新构造这么一个类
void Sm2Signature_Hander_free(Sm2Signature_Hander *a); //释放
Sm2Signature_Hander *d2i_Sm2Signature_Hander(Sm2Signature_Hander **a, 
    const unsigned char **in, long len);//把in里的数据转换成该类
int i2d_Sm2Signature_Hander(Sm2Signature_Hander *a, 
    unsigned char **out);//把该类转换成数据
const ASN1_ITEM * Sm2Signature_Hander_it(void);//iterator 迭代器
*/
```
OpenSslAsn1.c
```cpp
#include "OpenSslAsn1.h"
//
Sm2Signature_Hander::Sm2Signature_Hander(){
    x = BN_new();
    y = BN_new();
}
Sm2Signature_Hander::~Sm2Signature_Hander(){
    if (x) BN_free(x);
    if (y) BN_free(y);
}
void Sm2Signature_Hander::setX(const unsigned char* data, int len)
{ BN_bin2bn(data, len, x); }
void Sm2Signature_Hander::setY(const unsigned char* data, int len)
{ BN_bin2bn(data, len, y); }
int Sm2Signature_Hander::getX(unsigned char* data)
{ return BN_bn2bin(x, data); }
int Sm2Signature_Hander::getY(unsigned char* data)
{ return BN_bn2bin(y, data); }
ASN1_SEQUENCE(Sm2Signature_Hander) ={
	ASN1_SIMPLE(Sm2Signature_Hander, x, BIGNUM),
	ASN1_SIMPLE(Sm2Signature_Hander, y, BIGNUM),
} ASN1_SEQUENCE_END(Sm2Signature_Hander)
IMPLEMENT_ASN1_FUNCTIONS(Sm2Signature_Hander);
```

以上代码则定义了一套函数用于编码以及解析“国密SM2算法进行数字签名时的输出格式”的ASN.1数据  
可以如下使用：
```cpp
//把x，y的数据按照Sm2Signature_Hander数据结构定义的ASN.1格式编码到缓冲区out中。
unsigned char x[32];
unsigned char y[32];
Sm2Signature_Hander * sm2Sign = Sm2Signature_Hander_new();
sm2Sign->setX(x, 32);
sm2Sign->setY(y, 32);
unsigned char out[128] = {0};
unsigned char *p = out;
int outLen = i2d_Sm2Signature_Hander(sm2Sign, &p);
Sm2Signature_Hander_free(sm2Sign);

//从ASN.1数据中解码出原始数据
unsigned char *p1 = out;
Sm2Signature_Hander *sm2Sign1 = 
    d2i_Sm2Signature_Hander(NULL, (const unsigned char **)&p1, outLen);
int xLen = sm2Sign->getX(x);
int yLen = sm2Sign->getY(y);
```
