#!/usr/bin/python3
import argparse
import re
import subprocess
from importlib import import_module
wsl_sudo = import_module("wsl-sudo")  # Cannot normally import name with a dash (-)


class PortsParser(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not re.fullmatch(r'\d+(,\d+)*', values):
            parser.error(f"Invalid port range: {values}")
        
        values = values.split(",")
        setattr(namespace, self.dest, values)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="action", required=True)

parser_add = subparsers.add_parser("add")
parser_remove = subparsers.add_parser("remove")
for p in [parser_add, parser_remove]:  # Add options to both
    p.add_argument("-ip", "--ip", help="IP address to forward to")
    p.add_argument("port", help="Port to forward (multiple seperated by comma)", action=PortsParser)

subparsers.add_parser("list")
subparsers.add_parser("clear")

ARGS = parser.parse_args()


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


if __name__ == "__main__":
    if ARGS.action == "add":
        add_ports(ARGS.port)
    elif ARGS.action == "remove":
        remove_ports(ARGS.port)
    elif ARGS.action == "list":
        list_ports()
    elif ARGS.action == "clear":
        clear_ports()
