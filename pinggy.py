import argparse
from multiprocessing import Process
import os
import socket
import subprocess
import sys
import time
import psutil

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def run_app(env, command, port):
    print(command)
    subprocess.run(f'{command} & ssh -o StrictHostKeyChecking=no -p 80 -R0:localhost:{port} a.pinggy.io > log.txt', shell=True, env=env)
    
def print_url():
    print("waiting for output")
    time.sleep(2)
    sys.stdout.flush()
    
    found = False
    with open('log.txt', 'r') as file:
        end_word = '.pinggy.link'
        for line in file:
            start_index = line.find("http:")
            if start_index != -1:
                end_index = line.find(end_word, start_index)
                if end_index != -1:
                    print("😁 😁 😁")
                    print("URL: " + line[start_index:end_index + len(end_word)])
                    print("😁 😁 😁")
                    found = True
    if not found:
        print_url()
    else:
        with open('log.txt', 'r') as file:
            for line in file:
                print(line)
    
def find_and_terminate_process(port):
    for process in psutil.process_iter(['pid', 'name', 'connections']):
        for conn in process.info.get('connections', []):
            if conn.laddr.port == port:
                print(f"Port {port} is in use by process {process.info['name']} (PID {process.info['pid']})")
                try:
                    process.terminate()
                    print(f"Terminated process with PID {process.info['pid']}")
                except psutil.NoSuchProcess:
                    print(f"Process with PID {process.info['pid']} not found")

def main():
    parser = argparse.ArgumentParser(description='Start pinggy with shell command and port')
    parser.add_argument('--command', help='Specify the command to run with pinggy')
    parser.add_argument('--port', help='Specify the port')
    args = parser.parse_args()
    
    print(args.port)
    print(args.command)
    env = os.environ.copy()
    target_port = args.port
    command = args.command
    if is_port_in_use(int(target_port)):
        find_and_terminate_process(int(target_port))
    else:
        print(f"Port {target_port} is free.")
    
    open('log.txt', 'w').close()
    p_app = Process(target=run_app, args=(env, command, target_port,))
    p_url = Process(target=print_url)
    p_app.start()
    p_url.start()
    p_app.join()
    p_url.join()
    
if __name__ == '__main__':
    main()
