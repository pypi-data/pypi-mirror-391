from .function import function


class Cmd:
    clear= function.clear
    title= function.title

class System:
    iswin32= function.iswin32
    islinux= function.islinux
    isdarwin= function.isdarwin
    isadmin= function.isadmin
    runasadmin= function.runasadmin