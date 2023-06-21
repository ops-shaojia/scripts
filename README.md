# get_thread_stack
通过process pid获取java程序占用CPU较高的线程栈, 命令执行完成后会在当前目录生成`source.log`和`java_thread_stack.log`

建议下载使用二进制程序, 这样即使系统中没有python环境也可以执行

工具依赖top, echo, grep, awk, jstack, printf命令, jstack命令默认使用$PATH

```
使用方法: 
./get_java_thread_stack --help
usage: Get thread stack [-h] [-d command] [-p pid]

optional arguments:
  -h, --help            show this help message and exit
  -d command, --command command
                        Jstack command path. Default $PATH
  -p pid, --pid pid     process pid
```
