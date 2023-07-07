# -*- coding:utf-8 -*-
import re
import time
import argparse
import subprocess
import sys

def analysis_stack(data):
    stack_dict = {}
    nid = ""
    content = ""
    lastnid = ""
    for i in data.split("\n"):
        pattern1 = re.compile('^".*"')
        pattern2 = re.compile(" os_prio=[0-9a-zA-Z]{1,} ")
        pattern3 = re.compile(" tid=[0-9a-zA-Z]{1,} ")
        pattern4 = re.compile(" nid=[0-9a-zA-Z]{1,} ")
        result1 = pattern1.findall(i)
        if result1:
            if lastnid != "":
                stack_dict[lastnid]["content"] = content
            nid = pattern4.findall(i)[0].strip()
            stack_dict[nid] = {
                "thread_name": result1[0].strip(),
                "os_prio": pattern2.findall(i)[0].strip(),
                "tid": pattern3.findall(i)[0].strip(),
                "nid": nid
            }
            content = i
            lastnid = nid
            continue
        pattern5 = re.compile("java.lang.Thread.State: ([a-zA-Z0-9]{1,})")
        result5 = pattern5.findall(i)
        if result5:
            stack_dict[nid]["thread_state"] = result5[0]
        pattern6 = re.compile("JNI global references: ([0-9]{1,})")
        jni_global_references = pattern6.findall(i)
        if jni_global_references:
            stack_dict["JNI_global_references"] = jni_global_references[0]
        else:
            content += f"\n{i}"
    stack_dict[lastnid]["content"] = content
    return stack_dict

def get_process_threads(pid):
    command = "top -H -p %s -n 1 -b" % (pid)
    thread_data = execute_command(command)
    stack_command = "{} -l {}".format(command_path, pid)
    stack_stdout = execute_command(stack_command)
    return thread_data, stack_stdout

def execute_command(command):
    stdin, stdout = subprocess.getstatusoutput(command)
    if stdin != 0:
        raise Exception(f"command: {command}执行异常, 状态码'{stdin}' 错误输出: {stdout}")
    return stdout

def write(msg):
    with open("java_thread_stack.log", 'a+') as f:
        f.write(msg + "\n")

def Parser():
    parser = argparse.ArgumentParser(prog="Get thread stack", add_help=True)
    parser.add_argument("-d", "--command", dest="command", action="store", default="jstack", type=str, help="Jstack command path. Default $PATH", metavar="command")
    parser.add_argument("-p", "--pid", dest="pid", action="store", type=int, help="process pid", metavar="pid")
    return parser

if __name__ == '__main__':
    parser = Parser()
    option = parser.parse_args()
    command_path = option.command
    pid = option.pid
    if pid == "" or pid is None:
        parser.print_help()
        sys.exit(1)
    data = {}
    # 连续获取3次线程堆栈, 间隔3秒
    for i in range(3):
        top_dash, stack_data = get_process_threads(pid)
        with open("source.log", "a+") as f:
            f.write(f"{stack_data}\n\n\n{top_dash}\n\n\n")
        data[f"{i}"] = {
            "top_dash": top_dash,
            "stack": stack_data
        }
        time.sleep(3)
    # 分析java栈的cpu使用情况
    for i in range(3):
        thread_stacks = analysis_stack(data[f"{i}"]["stack"])
        process_ids = []
        result = execute_command("echo '%s' | grep java | awk '{print $1,$2,$9,$10,$11}'" % data[f"{i}"]["top_dash"])
        # 解析top命令的输出内容
        for d in result.split("\n"):
            t = d.split(" ")
            cmd = 'printf "%x\n" {}'.format(t[0])
            stdout = execute_command(cmd)
            cpu = float(t[2])
            process_ids.append({
                "user": t[1],
                "pid": t[0],
                "cpu": cpu,
                "memory": t[3],
                "run_time": t[4],
                "nid": f"0x{stdout.strip()}"
            })
        write(f"第{i + 1}次java线程堆栈分析结果: ")
        threads = len(thread_stacks.keys()) - 1
        write(f"线程数量: {threads}")
        write(f"引用对象: {thread_stacks['JNI_global_references']}个")
        thread_states = {}
        unknown_thread = 0
        for nid in thread_stacks.keys():
            if nid == "JNI_global_references":
                continue
            if "thread_state" in thread_stacks[nid]:
                if thread_stacks[nid]["thread_state"] not in thread_states:
                    thread_states[thread_stacks[nid]["thread_state"]] = 1
                else:
                    thread_states[thread_stacks[nid]["thread_state"]] += 1
            else:
                unknown_thread += 1
        for x in thread_states.keys():
            write(f"{x}线程: {thread_states[x]}个")
        write(f"其他线程: {unknown_thread}个\n\n")
        for process_id in process_ids:
            for nid in thread_stacks.keys():
                if f"nid={process_id['nid']}" == nid:
                    print(".", end="", flush=True)
                    log = f"运行用户: {process_id['user']}\n线程PID: {process_id['pid']}\n内存使用率: {process_id['memory']}%\n线程运行时间: {process_id['run_time']}\nCPU使用率: {process_id['cpu']}%\nNative nid: {process_id['nid']}\n\n\n{thread_stacks[nid]['content']}\n"
                    write(log)
                    write("=====================================================================================================================================")
