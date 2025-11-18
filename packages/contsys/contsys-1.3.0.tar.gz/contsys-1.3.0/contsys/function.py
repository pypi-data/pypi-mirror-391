import subprocess
import socket
import os
import sys
import ctypes
from datetime import date, datetime

class function:
    #Cmd
    @staticmethod
    def clear():
        if sys.platform=='win32':
            subprocess.run('cls', shell=True)
        elif sys.platform=='linux':
            subprocess.run('clear', shell=True)

    @staticmethod
    def title(title, ssh_indicator: bool = True):
        if ssh_indicator and 'SSH_CONNECTION' in os.environ:
            title = f"{title} - SSH Connection - {socket.gethostname()}"
        if sys.platform=="win32":
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        elif sys.platform=="linux":
            sys.stdout.write("\033]0;{title}\007")
            sys.stdout.flush()

    
    #System
    @staticmethod
    def iswin32():
        if sys.platform == 'win32':
            return True
        else:
            return False
    
    @staticmethod
    def islinux():
        if sys.platform == 'linux':
            return True
        else:
            return False
    
    @staticmethod
    def isdarwin():
        if sys.platform == 'darwin':
            return True
        else:
            return False
    
    @staticmethod
    def isadmin():
        if sys.platform == 'win32':
            if ctypes.windll.shell32.IsUserAnAdmin():
                return True
            else:
                return False
        elif sys.platform == 'linux' or sys.platform == 'darwin':
            if os.geteuid() == 0:
                return True
            else:
                return False
        else:
            raise  OSError(f'{sys.platform} is not supported.')
    
    @staticmethod
    def runasadmin(target, *args):
        import subprocess
        import sys
        if sys.platform == 'win32':
            args_str = " ".join(f'"{arg}"' for arg in args)
            cmd = [
                "powershell",
                "-Command",
                f'Start-Process -FilePath "{sys.executable}" -ArgumentList "{target} {args_str}" -Verb runAs'
            ]
            subprocess.run(cmd)
        elif sys.platform in ('linux', 'darwin'):
            cmd = ['sudo', sys.executable, target] + list(args)
            subprocess.run(cmd)
        else:
            raise OSError(f'{sys.platform} is not supported.')
