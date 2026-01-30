---
title: "部署AI模型的记录"
description: "临时笔记，未成功部署"
author: Pancake
date: 2026-01-30
categories: Coffee
tags: AI StableDiffusion
---

本文是我首次尝试部署一个AI模型到本地服务器时记录下来的。

当前是还**没**成功部署的，临时记录当前遇到的问题。

总结来说还是环境不干净

    我实际是在用docker再做开发环境，

    自己构建的镜像也不是为了AI做的，所以很多AI的依赖缺失或者版本不对，

    另外主机系统上的开发环境很简陋，本来想用cog打包，也会因为环境问题而失败。

所以下次捡起来搞，还是要从头全部依赖一点点搭建好，尽可能“一劳永逸”

## 一、理解开源AI模型的项目结构

开源AI项目通常遵循标准化的结构设计，了解这些组件是成功部署的基础：

### 核心项目组件

不一定能完全找到对应文件，但是大致是这些概念：

- **模型定义代码** (`modeling_*.py`, `unet.py`): 神经网络架构的具体实现
- **推理管道** (`pipeline.py`): 将预处理、推理、后处理封装为统一接口
- **配置文件** (`config.json`, `*.yaml`): 存储超参数和模型配置
- **依赖管理** (`requirements.txt`, `pyproject.toml`): Python包依赖清单
- **模型权重文件**: 通常托管在云存储（如Hugging Face Hub），不包含在代码仓库中
- **启动脚本** (`cli.py`, `webui.sh`, `launch.py`): 提供命令行或图形界面入口

### 重要原则：代码与数据分离

开源项目通常只包含“食谱”（模型架构和训练代码），

训练好的“菜品”（模型权重）体积比较大，通常需要单独下载。

部署时需确保权重文件放置在正确路径，并通过配置文件正确引用。

## 二、Stable Diffusion生态定位澄清

为避免混淆，必须明确相关概念的区别：

| 概念                            | 实际定位                             | 类比               |
| ------------------------------- | ------------------------------------ | ------------------ |
| **Stable Diffusion架构**        | 扩散模型的**设计蓝图**               | 建筑图纸           |
| **具体SD模型** (如SD 1.5, SDXL) | 基于架构训练得到的**可执行模型文件** | 按图纸建成的房子   |
| **Hugging Face Diffusers库**    | 加载/运行扩散模型的**标准化工具集**  | 建筑工具和施工规范 |
| **Stable Diffusion WebUI**      | 基于模型和库构建的**图形界面应用**   | 精装修的住宅小区   |

当你部署一个“基于Stable Diffusion”的项目时，你实际上是在使用Diffusers库操作一个具体的模型文件。

## 三、本地环境部署

TODO 遇到了很多问题，还没有成功部署，日后再补充

1：AI模型一般都对python/curd/torch等有明确的版本要求，而且是一致的版本，而不只是大于某个版本即可

2：不管是linux还是windows，都需要安装好Nvidia显卡驱动，如果是容器运行，还需要显式参数来允许容器访问GPU

3：在windows上尝试的时候，又遇到了某个py脚本需要调用rust编译某个子模块的情况，安装rust又需要安装vs来安装vc的依赖

以上这些似乎都很合理，似乎只是运行某个install命令即可，但实际上我出现了很多问题，各种报错。

## 四、Docker化部署的完整流程

TODO 尝试了直接使用 `pytorch`的镜像，但也不是开箱即用，和【三】中一样，遇到了很多脚本报错

不过依然有一些值得记录下来的：Docker Compose GPU配置

```yaml
services:
  ai-model:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=all
```

## 五、Cog：专业模型部署工具

Cog是一个专门为这些AI模型打包成docker镜像的工具，模型的介绍中也提供了命令

```bash
download_weights.py
cog predict -i image="link-to-image"
```

先要下载模型权重，这个脚本又因为 `torch`版本问题失败了.......
