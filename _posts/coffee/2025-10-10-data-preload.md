---
title: "从“逐一处理”到“批量处理”的优化方案"
description:
author: Pancake
date: 2025-10-10
categories: Coffee
tags: coding
---

## 场景

我们经常会遇到：有 N 个数据需要处理，而每个数据都需要查询一些数据，计算后写入一些数据。
简单总结是：逐一处理代码清晰，但是性能稍差。批量处理整体性能好，但是事务时间长带来风险。
当然有些项目一开始就明确了需要处理的数据量，我们根据实际情况可以在初期确定处理的策略，
但是有些项目一开始是没有那么清晰的，项目在发展，业务在变化，
代码既要考虑前期的快，也要考虑后期的稳，有没有方式可以更好适配项目的发展。

## 常见代码

### 逐一处理

```go
for _, item := range items {
    err := processSingleItem(item)
    if err != nil {
        return err
    }
}

func processSingleItem(item Item) error {
    // 查询相关表数据
    data, err := tx.Query("SELECT ... WHERE ...", item.ID)
    // 业务逻辑判断
    if !shouldProcess(data) {
        return nil
    }
    // 插入数据
    return tx.Exec("INSERT ...", item.Data)
}
```

这样的代码很清晰，非常贴合这个功能逻辑的口头描述。
但是很快发现数据量稍微大一点时，运行起来性能不佳，因为在 for 循环里面做了数据库操作。

我们可以再分析一下优缺点：

- 优点
  - 代码简单清晰，易于理解和维护
  - 事务粒度小，锁持有时间短
  - 内存占用稳定，不会因数据量大而 OOM
  - 部分失败不影响其他记录处理
- 缺点
  - 网络往返次数多（N+1 查询问题）
  - 总体执行时间长
  - 数据库连接利用率低

### 批量处理

于是很快就有了第二版代码，把数据库的操作变成批量的，
其优缺点基本和逐一处理相反，比如事务长，内存占用大，但是总体耗时短等等。

```go
func processBatch(items []Item) error {
    // 批量查询所有需要的数据
    allData, err := batchQueryData(tx, items)
    if err != nil {
        return err
    }

    // 批量计算和判断
    var toInsert []InsertData
    for i, item := range items {
        if shouldProcess(allData[i]) {
            toInsert = append(toInsert, buildInsertData(item, allData[i]))
        }
    }

    // 批量插入
    if len(toInsert) > 0 {
        err = batchInsert(tx, toInsert)
        if err != nil {
            return err
        }
    }

    return nil
}
```

### 分批处理

分批处理，结合两者优点

```go
func processInBatches(items []Item, batchSize int) error {
    for i := 0; i < len(items); i += batchSize {
        end := i + batchSize
        if end > len(items) {
            end = len(items)
        }

        batch := items[i:end]
        err := processBatch(batch)
        if err != nil {
            return fmt.Errorf("batch %d failed: %w", i/batchSize, err)
        }
    }
    return nil
}
```

### 考虑因素

- 数据一致性要求
  - 单个数据处理失败，需要整批数据回滚吗？
  - 顺便考虑部分数据失败，如何返回错误信息？
- 数据量大小
  - 小数据量（几十到几百条）：逐一处理足够
  - 中等数据量（几百到几千条）：需要考虑批量处理
  - 大数据量（上万条）：需要更复杂的分批处理
- 逻辑复杂程度
  - 数据计算复杂度远大于数据操作量时，为了保持代码的可读性，而性能上可以妥协，应该考虑逐一处理，让代码清晰表达单条数据的处理过程。
  - 反之，如果逻辑简单，或者封装后代码清晰，那么数据的批量操作不至于导致可读性差，则可以选择批量处理。

## 遇到的困难

整个代码的演变过程很大可能是逐步优化，从“逐一处理”到“批量处理”再到“分批处理”。

先简单讨论从“批量处理”到“分批处理”，
这个过程是相对简单的，很大可能是找到分批的切入点，
可能是入参直接分批处理，
也可能是给某个 select 语句加上 offset 和 limit。

**再来讨论从“逐一处理”到“批量处理”，我认为这个优化有时候是困难的。**
尤其是我们会对处理逻辑进行封装和复用。考虑以下代码（从上面逐一处理稍微修改而来）

```go
for _, item := range items {
    err := processSingleItem(item)
    if err != nil {
        return err
    }
}

func processSingleItem(item Item) error {
    // 业务逻辑判断
    if !shouldProcess(item) {
        return nil
    }
    // 插入数据
    return tx.Exec("INSERT ...", item.Data)
}

func shouldProcess(item Item) bool {
    // 查询相关表数据
    data, err := tx.Query("SELECT ... WHERE ...", item.ID)
    return err != nil || data.Status != 0 // 有对应的数据并且状态不为零，表示待处理
}

```

shouldProcess 方法可能被其他代码复用了，考虑这是一个更早存在的代码，并且有一定的复杂度，也有不少引用。
那么把它改成“批量处理”的模式，难度将暴增。

- 是否应该复用该方法
  - 复用，则考虑是否提取对应的数据操作代码到外部
    - 提取，则需要修改现存的引用代码，引入新 BUG 的风险也很大。
    - **不提取，不修改这份代码，只能通过其他方式（下面继续讨论这个思路）**
  - 不复用，重新写一份功能一致，但是符合批量处理模式的代码
    - 开发成本和维护成本都增加
      - 开发成本：要先深入理解现有代码逻辑
      - 维护成本：后续增减功能点都需要维护这两份代码，需要逐步废弃一份
    - 这个方案的执行大概是：
      - 新写一个批量处理的代码，然后把旧代码，则逐一处理的标记为废弃
      - 新代码经过足够的测试，甚至生产验证，再替换掉旧代码的引用，或者逐一处理的内部调用批量处理代码，只是入参列表只有一个元素而已。
      - 最后彻底删掉旧代码

## 利用缓存

利用缓存可以保持复用又能批量处理，这里说的缓存并不只是指 redis 这样的特定技术，我们有很多可以做缓存的切面。

核心思路：

- 对于读操作，可以先批量读取并缓存，后续读取直接从缓存读取，
- 对于写操作，可以先缓存起来，最后批量做一次批量写操作。

示例代码，只对读操作做了缓存：

```go
var idList []int
for _, item := range items {
    idList = append(idList, item.ID)
}

// 根据业务逻辑，先把所有需要用到的数据，都加载到缓存中
_,err := selectByIdList(idList)

for _, item := range items {
    err := processSingleItem(item)
    if err != nil {
        return err
    }
}

func processSingleItem(item Item) error {
    // 业务逻辑判断
    if !shouldProcess(item) {
        return nil
    }
    // 插入数据
    return tx.Exec("INSERT ...", item.Data)
}

func shouldProcess(item Item) bool {
    // 查询相关表数据
    data, err := selectById(item.ID) // 复用代码里，先读取缓存，减少数据读写操作次数
    return err != nil || data.Status != 0 // 有对应的数据并且状态不为零，表示待处理
}

// 一般是DAO层代码，可以直接在这里做缓存，需要一定的管理逻辑，也可以考虑配合redis等做更加完善的缓存方案
var cacheMap = make(map[id]Data)
func selectByIdList(idList []int)([]Data, error){
    results, err := tx.Query("SELECT ... WHERE id in ...", id)
    for _, res := range results{
        cacheMap[res.ID] = res // 批量查询时写入缓存
    }
    return results, err
}

func selectById(id int)(Data, error){
    cacheData, ok := cacheMap[id]
    if ok {// 单个查询时先找缓存，如果有则直接用
        return cacheData, nil
    }

    return tx.Query("SELECT ... WHERE ...", id)
}
```

注意：

- 依然需要对旧代码做一次基本审查，确保新增的缓存逻辑不会引发 BUG
  - 比如某个逻辑多次读写同一个表甚至同一行数据的情况，可能会出现 BUG
- 要求代码有一定的封装层次，常见的数据库访问，网络请求等等都会有一层自己的封装

## 让 AI 评价一下这个方案

直接贴 AI 的回答：

这个方案在实践中被称为 "预加载缓存模式" 或 "批量预取模式"。
（这个名字 AI 可能是从“Prefetch 预取”或者“Eager Loading 饿汉模式”或者“Preload”等翻译而来，都是类似的思路，我比较喜欢 Preload）
优点：

- 代码复用性极高
- 渐进式优化，风险可控
  - 现有代码完全不受影响（AI 说没有，其实还是有，如果现有代码又改又查还多次操作，而缓存又没有更新）
  - 可以逐步为高频场景添加批量版本
  - 出现问题时可以快速回退到单条处理
- 保持接口简洁
- 缓存生命周期清晰

缺点：

- 数据访问层的复杂性增加
- 预加载逻辑的准确性要求高
- 内存使用可能较高
- 事务管理的挑战
- 错误处理边界模糊

建议：

- 使用依赖注入明确数据源，则旧代码保持常规 dao 读取，新代码提供带有缓存功能的 dao
- 分层预加载策略，提供更加准确的预加载方式
- 缓存有效性检查，优化缓存的失效机制，避免数据滞后等等问题

适用场景

- 这个方案特别适合：
  - 业务逻辑复杂，难以重构为纯批量处理
  - 需要保持现有接口的稳定性
  - 数据依赖关系相对明确和固定
  - 团队对现有代码熟悉，希望最小化修改
- 不太适合：
  - 数据依赖关系动态变化，难以预测
  - 内存资源非常紧张
  - 需要极致的性能（额外的缓存查找仍有开销）

总结
你提出的这个方案是一个非常实用的折中方案，它：

✅ 保持了代码复用性和一致性
✅ 最小化了对现有代码的侵入
✅ 提供了显著的性能提升
⚠️ 但需要仔细设计缓存策略和数据预加载逻辑

## 其他方案

最后列举一下 AI 到的一些方案：
简单/片面的总结两句，我希望达成的是“避免两份实现”，如果抛开这个限制，那下面的方案都值得考虑。

- 适配器模式：调用一个方法，该方法会判断调用“逐一处理”还是“批量处理”
- 策略模式：思路同上，只是代码封装结构上的区别
- 装饰器模式 + 批量缓冲：以“逐一处理”作为方法，内部缓冲到一定的阈值再“批量处理”
