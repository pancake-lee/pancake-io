---
title: '分享一下Pull Request成功的小喜悦'
description: # 留空则文章卡片上展示文章最前面的部分内容
author: Pancake
date: 2018-05-10
categories: Coffee
tags: Cpp Github
---

# 我的Pull Request经历
很多人知道Git，开始使用了，也许也没有体会到Git平台的意义，这里分享一下，一定程度上了解一下  
* 首先是本人需要使用OpenSsl从事PKI相关工作，由于需要开发国密SM2/SM3/SM4/SM9等，所以转而使用[GmSSL](http://gmssl.org/)
* 参考源码测试示例代码，在开发SM2加解密功能时，遇到解密失败，从调用代码检查清楚无发现错误后，怀疑是否某些参数设置错误，转而研究其源码，最后发现返回值在返回前被释放，经过测试，确定这就是罪魁祸首：

```cpp
    SM2CiphertextValue *ret = NULL;
    SM2CiphertextValue *cv = NULL;
    /*.......*/
    ret = cv;
end:
    SM2CiphertextValue_free(cv);
    return ret;
```
* 解决办法只需要在ret = cv;后加上cv = NULL;紧接着的free语句是支持NULL而不做任何工作的
* 那么问题来了，虽然发现了bug，也能解决，但是如果你只修改本地代码，那么官方更新了什么功能，下载新源码后又需要修改该bug，麻烦。
## pull request
* 首先你需要登陆你的GitHub账号，fork对方代码到自己仓库，clone是不行的，只有fork才能pull到对方仓库。
* 然后clone你自己的仓库到本地，修改代码，提交，推送到自己的仓库
* 这时候你自己的仓库则多了一次提交，然后前往对方的仓库，点击new pull request
* 这里根据下图操作，对比你仓库的版本和对方仓库的版本，正确处理冲突后，则可以create pull request了，剩下的则是对方的处理了，对方将选择是否接受你的提交  

### 第一次被采纳还是很开心的，虽然解决的也是很简单bug，一行代码而已
https://github.com/guanzhi/GmSSL/pull/492