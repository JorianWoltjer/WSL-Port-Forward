#!/usr/bin/python3
import argparse
import re
import subprocess
from importlib import import_module
import sys
wsl_sudo = import_module("wsl-sudo")  # Cannot normally import name with a dash (-)


class PortsParser(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None, return_value=False):
        if not re.fullmatch(r'\d+(,\d+)*', values):
            if return_value:
                return None
            parser.error(f"Invalid port range: {values}")
        
        values = values.split(",")
        
        if return_value:
            return values
        setattr(namespace, self.dest, values)
        

if sys.version_info >= (3, 9):
    parser = argparse.ArgumentParser(exit_on_error=False)
else:
    parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest="action", required=True)

parser_add = subparsers.add_parser("add", help="Add ports to forward")
parser_remove = subparsers.add_parser("remove", help="Remove forwarded ports")
for p in [parser_add, parser_remove]:  # Add options to both
    p.add_argument("-ip", "--ip", help="IP address to forward to")
    p.add_argument("port", help="Port to forward (multiple seperated by comma)", action=PortsParser)

parser_update = subparsers.add_parser("update", help="Update all forwarded ports to use current WSL address (changes after boot)")
parser_update.add_argument("-ip", "--ip", help="IP address to forward to")

subparsers.add_parser("list", help="List all forwarded ports")
subparsers.add_parser("clear", help="Clear all forwarded ports")

try:
    ARGS = parser.parse_args()
except argparse.ArgumentError as e:
    # Default to `add` if a port is given instead of an action
    if e.argument_name == "action" and e.message.startswith("invalid choice:"):
        match = re.findall(r"invalid choice: '(.*?)'", e.message)
        if match:
            # Try parsing as a port
            portsparser = PortsParser(None, None, None)
            if portsparser(None, None, match[0], return_value=True):  # If it is a port, use `add` action
                ARGS = parser.parse_args(["add", match[0]])
            else:
                print(e.message)
                exit(1)
        else:
            print(e.message)
            exit(1)


def get_ip():  # Get WSL IP from interface
    import netifaces as ni
    return ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']

def run_as_admin(command):  # Run command as administrator using wsl-sudo
    print("[~] Starting administrator prompt...")
    wsl_sudo.UnprivilegedClient().main(["powershell.exe", "-Command", command], 0)

def run_as_user(command):  # Run command normally
    return subprocess.check_output(["powershell.exe", "-Command", command]).decode("utf-8").strip()


def add_ports(ports):  # Add a port
    ip = ARGS.ip or get_ip()
    commands = []
    
    for port in ports:
        print(f"[~] Forwarding port {port} to {ip}...")
        commands.append(f"netsh interface portproxy set v4tov4 {port} {ip}")
        
    run_as_admin("; ".join(commands))  # Run all commands at once
    list_ports()

def remove_ports(ports):  # Remove a port
    commands = []
    
    for port in ports:
        print(f"[~] Removing port {port}...")
        commands.append(f"netsh interface portproxy delete v4tov4 {port}")

    run_as_admin("; ".join(commands))  # Run all commands at once
    list_ports()

def list_ports():   # List all ports
    output = run_as_user("netsh interface portproxy show v4tov4")
    print(output or "[-] No ports forwarded.")

def clear_ports():  # Clear all ports
    run_as_admin("netsh interface portproxy reset")
    print("[+] Cleared all ports!")

def update_ports():  # Update all ports to use current address
    print("[~] Finding forwarded ports...")
    ip = ARGS.ip or get_ip()
    
    list_output = run_as_user("netsh interface portproxy show v4tov4")
    print(list_output)
    matches = re.findall(r'^\S+\s+(\d+)', list_output, re.MULTILINE)
    
    if not matches:
        print("[-] No ports forwarded.")
        return
    
    commands = []
    for port in matches:
        print(f"[~] Updating port {port} to {ip}...")
        commands.append(f"netsh interface portproxy set v4tov4 listenport={port} connectaddress={ip}")
    
    run_as_admin("; ".join(commands))  # Run all commands at once
    print("[+] Updated all ports!")
    list_ports()


if __name__ == "__main__":
    if ARGS.action == "add":
        add_ports(ARGS.port)
    elif ARGS.action == "remove":
        remove_ports(ARGS.port)
    elif ARGS.action == "list":
        list_ports()
    elif ARGS.action == "clear":
        clear_ports()
    elif ARGS.action == "update":
        update_ports()
