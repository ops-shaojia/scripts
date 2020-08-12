# -*- coding:utf-8 -*-
import subprocess, sys, re, time, argparse, os.path

def get_thread_id(pid):
    command = "top -H -p %s -n 1 |grep java | head -10 | awk '{print $2,$10}'" % (pid)
    stdin, stdout = subprocess.getstatusoutput(command)
    stdout = stdout.replace("\x1b(B\x1b[m", '')
    pid_list = stdout.split("\n")
    result = []
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    for i in pid_list:
        pattern = re.compile("\d+")
        m = pattern.findall(i)
        if m:
            pass
        else:
            continue
        data = i.split(" ")
        thread_pid = data[0]
        m = pattern.findall(data[1])
        if m:
            pass
        else:
            continue
        thread_used_cpu = float(data[1])
        if thread_used_cpu > cpu:
            pass
        else:
            continue
        get_nid_command = 'printf "%x\n" {}'.format(thread_pid)
        stdin, stdout = subprocess.getstatusoutput(get_nid_command)
        if stdin == 0:
            result.append({"cpu": thread_used_cpu, "nid": stdout, "time": t, "pid": thread_pid})
    return result

def get_jstack_data(pid):
    command = "{} -l {}".format(command_path, pid)
    stdin, stdout = subprocess.getstatusoutput(command)
    if stdin == 0:
        return stdout
    else:
        print(stdout)
        return False

def write_thread_jstack(msg):
    with open("thread.log", 'a+') as f:
        f.write(msg + "\n")

def Parser():
    parser = argparse.ArgumentParser(prog="Get thread stack", add_help=True)
    parser.add_argument("-c", "--cpu", dest="cpu", action="store", type=int, help="Thread cpu. Default gt 10 percentage", metavar="cpu", default=10)
    parser.add_argument("-d", "--command", dest="command", action="store", type=str, help="Jstack command path. Default $PATH", metavar="command")
    parser.add_argument("-t", "--time", dest="trace_time", action="store", type=int, help="Trace time. Default 3min", metavar="trace_time", default=3)
    parser.add_argument("-p", "--pid", dest="pid", action="store", type=int, help="process pid", metavar="pid")
    return parser

def main():
    jstack_data = get_jstack_data(pid)
    if jstack_data == False:
        return
    result = get_thread_id(pid)
    jstack_data = jstack_data.split("\n")
    for i in result:
        nid = i["nid"]
        pattern = re.compile(" nid=0x{} ".format(nid))
        x = 1
        for data in jstack_data:
            if x == 1:
                m = pattern.findall(data)
                if m:
                    content = "time: {}\npid: {}\nthread cpu: {}%\nthread nid: {}\n{}".format(i["time"], i["pid"], i["cpu"], nid, data)
                    write_thread_jstack("----------------------------------------------------------------------------------------")
                    write_thread_jstack(content)
                    x += 1
                    continue
                else:
                    continue
            sec_pattern = re.compile('^".*')
            m = sec_pattern.findall(data)
            if m:
                break
            else:
                write_thread_jstack(data)
            x += 1

if __name__ == '__main__':
    parser = Parser()
    option = parser.parse_args()
    t = int(option.trace_time) * 60
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
    for i  in range(t):
        main()
        time.sleep(1)
