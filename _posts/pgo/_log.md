## 日志模块

首先，如果搭建了完善的日志平台，比如 ELK
那么，本文就是废话，因为这些平台已经提供足够方便的功能查询日志
查询某个关键字，查询某个请求，查询某个用户的日志，都能得到很好的支持
只需要输出日志时，提供一份 key-value，录入足够多的索引即可

---

下面我们只讨论直接查阅日志文件的情况

业务上，我们需要怎么样的日志 api 呢？
我们先看 zap 库最简单的使用输出的结果，
然后对比地提出我期望的日志格式，
最后我们看业务代码希望如何调用日志库。

### zaplog

```go
func TestZapLogger(t *testing.T) {
    logger, _ := zap.NewDevelopment()
    defer logger.Sync()
    logger.Debug("test zap Debug, 中文测试，1234567890")
    logger.Info("test zap Info, 中文测试，1234567890")
    logger.Warn("test zap Warn, 中文测试，1234567890")
    logger.Error("test zap Error, 中文测试，1234567890")

    log := logger.Sugar()
    log.Debug("test zap SugaredLogger Debug, 中文测试，1234567890")
    log.Debugf("test zap SugaredLogger Debug, 中文测试，%d", 1234567890)
    log.Debugln("test zap SugaredLogger Debugln, 中文测试，1234567890")
    log.Debugw("test zap SugaredLogger Debugw, 中文测试，1234567890",
        "key1", "value1", "key2", "value2")
}
```

```log
2025-06-06T16:52:07.160+0800	DEBUG	logger/unit_test.go:13	test zap Debug, 中文测试，1234567890
2025-06-06T16:52:07.165+0800	INFO	logger/unit_test.go:14	test zap Info, 中文测试，1234567890
2025-06-06T16:52:07.166+0800	WARN	logger/unit_test.go:15	test zap Warn, 中文测试，1234567890
pgo/pkg/logger.TestZapLogger
	g:/workspace/pgo/pkg/logger/unit_test.go:15
testing.tRunner
	C:/Program Files/Go/src/testing/testing.go:1792
2025-06-06T16:52:07.166+0800	ERROR	logger/unit_test.go:16	test zap Error, 中文测试，1234567890
pgo/pkg/logger.TestZapLogger
	g:/workspace/pgo/pkg/logger/unit_test.go:16
testing.tRunner
	C:/Program Files/Go/src/testing/testing.go:1792
2025-06-06T16:52:07.166+0800	DEBUG	logger/unit_test.go:19	test zap SugaredLogger Debug, 中文测试，1234567890
2025-06-06T16:52:07.166+0800	DEBUG	logger/unit_test.go:20	test zap SugaredLogger Debug, 中文测试，1234567890
2025-06-06T16:52:07.166+0800	DEBUG	logger/unit_test.go:21	test zap SugaredLogger Debugln, 中文测试，1234567890
2025-06-06T16:52:07.166+0800	DEBUG	logger/unit_test.go:22	test zap SugaredLogger Debugw, 中文测试，1234567890	{"key1": "value1", "key2": "value2"}
```

### 期望

#### 日志格式

期望：定长前缀 + Message + 变长后缀
进阶：基础框架的定长前缀 + 业务框架的定长前缀 + Message + + 业务框架的变长后缀 + 基础框架的变长后缀

```log
250606T16:52:07.160 DEBUG test zap Debug, 中文测试，1234567890 aaa.go:13
250606T16:52:07.160 DEBUG test2 zap Debug, 中文测试2，1234567890 bbb.go:13

250606T16:52:07.160 DEBUG [RequestId] test zap Debug, 中文测试，1234567890 [有什么变长内容想要拼接呢] aaa.go:13
250606T16:52:07.160 DEBUG [RequestId] test2 zap Debug, 中文测试2，1234567890 [还没想好] bbb.go:13
```

#### 文件命名

期望：进程名 + 日期
test_20250606.log
进阶 1：进程名 + PID + 日期
你可能希望每次重启都生成一个新的日志文件，但这种方式会导致 zap 的日志轮转失效
进阶 2：进程名 + 实例编号 + 日期
可能是以多进程的方式运行多个实例

另外：需要有软连接指向当前使用的日志文件

#### 调用

首先，基础框架应该提供固定的日志初始化，业务代码只需要调用具体的输出方法
然后，业务框架应该封装一层，拼接上业务固定信息，比如所有日志都拼接上 RequestId，这样容易追踪同一个请求的所有日志

这里视乎有没有所谓的“业务框架”，
比如一个带有账号管理的系统，那么每个请求都应该带着 token 或者 session，
那么也许你会希望每条日志都输出当前的用户是谁，可以固定拼接用户名或者用户 ID

### logger 封装

```go
func InitLogger(isLogConsole bool, lv zapcore.Level, path string)
```

TODO
