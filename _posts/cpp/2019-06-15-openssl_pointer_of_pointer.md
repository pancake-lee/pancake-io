---
title: "OPENSSL中二级指针作为参数的坑"
description: " "
date: 2019-06-15
author: Pancake
categories: Coding
tags: OpenSsl Cpp
---

## 现象

```c
unsigned char *pPub, *pPub1;
pubLen = i2d_X509_PUBKEY(x509Puk, NULL);
pPub1 = pPub = (unsigned char*)malloc(pubLen);
pubLen = i2d_X509_PUBKEY(x509Puk, &pPub1);
```

以上代码关注最后一行第二个参数，传入一个二级指针`pPub1`，但是这个参数在函数内部会被修改，所以在传入前要先记录指针原来指向`pPub`，后续代码应该使用`pPub`，而不应信任`pPub2`。

## 原理猜测

没有详细研究源码，个人猜测内部操作大概如下：

```c
    func(char* buf){
        for(int i=0;i!=100;i++){
            *(buf++) = i;
        }
    }
```

直接改变指针指向操作了 buf，导致实参指向改变了，这里是 openssl 常见的。
