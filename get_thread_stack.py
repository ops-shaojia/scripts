# -*- coding:utf-8 -*-
import sys
import re
import time
import argparse
import subprocess
import os.path


def get_process_threads(pid):
    command = "ps aux -L %s |grep java|grep ' %s ' | awk '{print $1,$2,$3,$4,$6,$12}'" % (pid, pid)
    stdin, stdout = subprocess.getstatusoutput(command)
    if stdin != 0:
        return []
    result = stdout.split("\n")
    threads = []
    ps_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    for thread in result:
        t = thread.split(" ")
        cmd = 'printf "%x\n" {}'.format(t[2])
        stdin, stdout = subprocess.getstatusoutput(cmd)
        if stdin == 0 and float(t[3]) > 50:
            threads.append({
                "time": ps_time,
                "user": t[0],
                "pid": t[1],
                "LWP": t[2],
                "cpu": t[3],
                "memory": t[4],
                "run_time": t[5],
                "nid": f"0x{stdout}"
            })
    return threads

def get_jstack_data(pid):
    command = "{} -l {}".format(command_path, pid)
    stdin, stdout = subprocess.getstatusoutput(command)
    if stdin == 0:
        return stdout
    else:
        print(stdout)
        return False

def write_thread_jstack(msg):
    with open("java_thread_stack.log", 'a+') as f:
        f.write(msg + "\n")

def Parser():
    parser = argparse.ArgumentParser(prog="Get thread stack", add_help=True)
    parser.add_argument("-c", "--cpu", dest="cpu", action="store", type=int, help="Thread cpu. Default gt 10 percentage", metavar="cpu", default=10)
    parser.add_argument("-d", "--command", dest="command", action="store", type=str, help="Jstack command path. Default $PATH", metavar="command")
    parser.add_argument("-t", "--time", dest="trace_time", action="store", type=int, help="Trace time. Default 30second", metavar="trace_time", default=30)
    parser.add_argument("-p", "--pid", dest="pid", action="store", type=int, help="process pid", metavar="pid")
    return parser

def main():
    jstack_data = get_jstack_data(pid)
    if not jstack_data:
        return
    threads = get_process_threads(pid)
    jstack_data = jstack_data.split("\n")
    for thread in threads:
        nid = thread["nid"]
        i = 1
        for data in jstack_data:
            if i == 1:
                pattern = re.compile(" nid={} ".format(nid))
                m = pattern.findall(data)
                if m:
                    print(".", end="")
                    content = f"Time: {thread['time']}\nProcess running user: {thread['user']}\nProcess pid: {thread['pid']}\nProcess mem: {thread['memory']}%\nThread running time: {thread['run_time']}\nThread LWP: {thread['LWP']}\nThread cpu: {thread['cpu']}%\nThread nid: {thread['nid']}\n{data}"
                    write_thread_jstack("=====================================================================================================================================")
                    write_thread_jstack(content)
                    i += 1
                    continue
                else:
                    continue
            sec_pattern = re.compile('^".*')
            m = sec_pattern.findall(data)
            if m:
                break
            else:
                write_thread_jstack(data)
            i += 1

if __name__ == '__main__':
    parser = Parser()
    option = parser.parse_args()
    t = int(option.trace_time)
    cpu = int(option.cpu)
    if option.command:
        if os.path.isfile(option.command):
            command_path = option.command
        else:
            print("jstack command not found.")
            sys.exit(1)
    else:
        command_path = "jstack"
    pid = option.pid
    for i in range(t):
        main()
        time.sleep(1)
