# WSL-Port-Forward
Forward network traffic directed to Windows to your WSL environment.  
Pretty much a user friendly wrapper for the netsh portproxy

## Install

```shell
git clone https://github.com/JorianWoltjer/WSL-Port-Forward.git
alias pfw="python3 $(pwd)/WSL-Port-Forward/pfw.py"  # Also put in ~/.bashrc
pfw -h
```

## Usage

```
usage: pfw.py [-h] {add,remove,delete,list,show,clear,reset} ...

positional arguments:
  {add,remove,delete,list,show,clear,reset}

optional arguments:
  -h, --help            show this help message and exit
```

## Examples

Add port 80 and 443:
```shell
$ pfw add 80,443
[~] Forwarding port 80 to 172.28.118.26...
[~] Forwarding port 443 to 172.28.118.26...
[~] Starting administrator prompt...


Listen on ipv4:             Connect to ipv4:

Address         Port        Address         Port
--------------- ----------  --------------- ----------
*               80          172.28.118.26   80
*               443         172.28.118.26   443
```

Remove port 443:
```shell
$ pfw remove 443
[~] Removing port 443...
[~] Starting administrator prompt...

Listen on ipv4:             Connect to ipv4:

Address         Port        Address         Port
--------------- ----------  --------------- ----------
*               80          172.28.118.26   80
```

List all ports:
```shell
$ pfw list
Listen on ipv4:             Connect to ipv4:

Address         Port        Address         Port
--------------- ----------  --------------- ----------
*               80          172.28.118.26   80
```

Clear all ports:
```shell
$ pfw clear
[~] Starting administrator prompt...

[+] Cleared all ports!
```
