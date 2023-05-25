# get_thread_stack
通过process pid获取java程序占用CPU较高的线程栈

默认执行30秒, 当有线程CPU占用超过指定数值，会在当前目录下生成java_thread_stack.log

建议下载使用二进制程序, 这样即使系统中没有python环境也可以执行

工具依赖top、jstack命令, jstack命令默认使用$PATH

```
使用方法: 
./get_thread --help
usage: Get thread stack [-h] [-c cpu] [-d command] [-t trace_time] [-p pid]

optional arguments:
  -h, --help            show this help message and exit
  -c cpu, --cpu cpu     Thread cpu. Default gt 10 percentage
  -d command, --command command
                        Jstack command path. Default $PATH
  -t trace_time, --time trace_time
                        Trace time. Default 30second
  -p pid, --pid pid     process pid
```
