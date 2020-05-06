# get_thread_stack
通过process pid获取java程序占用CPU较高的线程栈


使用方法: 

usage: Get thread stack [-h] [-c cpu] [-d command] [-t trace_time] [-p pid]

optional arguments:
  -h, --help            show this help message and exit
  -c cpu, --cpu cpu     Thread cpu. Default gt 10 percentage
  -d command, --command command
                        Jstack command path. Default $PATH
  -t trace_time, --time trace_time
                        Trace time. Default 3min
  -p pid, --pid pid     process pid
