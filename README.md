# WSL-Port-Forward

Windows Subsystem Linux (WSL) is a very useful Windows feature for developers, security researchers and technical people in general. 
But one thing that trips a lot of people up when doing ethical hacking, is **creating listeners**. When creating a listener with `nc` for example, 
in WSL, you might expect it to be accessable straight away from anyone in your LAN trying to connect to your computer with the port. But actually, 
Windows does **not** automatically send connections to a specific port through to WSL. 

This is where this tool comes in. `pfw` (Port ForWard) can use the Windows `netsh` commands to tell windows to send connections to a specific port through to WSL. This will allow you to create listeners in WSL, and forward the port from Windows, to make a connection to your computers IP go straight to the listener on WSL. 

Because `netsh` requires administrator privilages, it uses [wsl-sudo](https://github.com/Chronial/wsl-sudo) by [Chronial](https://github.com/Chronial) to give an administrator prompt. It makes it as simple as just clicking "Yes".

## Install

```shell
git clone https://github.com/JorianWoltjer/WSL-Port-Forward.git
cd WSL-Port-Forward
pip install -r requirements.txt
alias pfw="python3 /path/to/pfw.py"  # Also put in ~/.bashrc
pfw -h
```

## Usage

A common use case for this tool is listeners. If you have a `nc -lp 1234` listener for example in one terminal, you can use another to run `pfw add 1234`. That will create the listener. 

One small issue is the fact that Windows randomizes the WSL IP address that needs to be provided with `netsh` every time that WSL restarts. This would mean that every time you restart WSL, you would need to `clear` the ports, and `add` them all back. To automate this there is also an **`update`** command, that will update all forwarded ports to use the current address. 

```
usage: pfw [-h] {add,remove,list,clear,update} ...

positional arguments:
  {add,remove,list,clear,update}
    add                 Add ports to forward
    remove              Remove forwarded ports
    list                List all forwarded ports
    clear               Clear all forwarded ports
    update              Update all forwarded ports to use current WSL address (changes after boot)

optional arguments:
  -h, --help            show this help message and exit
```

## Examples

* Add port 80 and 443:

```Shell
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

* Remove port 443:

```Shell
$ pfw remove 443
[~] Removing port 443...
[~] Starting administrator prompt...

Listen on ipv4:             Connect to ipv4:

Address         Port        Address         Port
--------------- ----------  --------------- ----------
*               80          172.28.118.26   80
```

* List all ports:

```shell
$ pfw list
Listen on ipv4:             Connect to ipv4:

Address         Port        Address         Port
--------------- ----------  --------------- ----------
*               80          172.28.118.26   80
```

* Clear all ports:

```Shell
$ pfw clear
[~] Starting administrator prompt...

[+] Cleared all ports!
```
