from .. import *
from os import *

import subprocess as _subprocess

from .. import sys as _sys

TEMP_DIR = 'C:\\Temp' if _sys.is_this_windows() else \
           '/tmp'

def getuserenv(name  :str,
               expand:bool=False):
    
    return (popen(f'powershell -NoProfile -Command "(Get-Item -Path HKCU:\\Environment).GetValue(\'{name}\')"')                                         if expand else \
            popen(f'powershell -NoProfile -Command "(Get-Item -Path HKCU:\\Environment).GetValue(\'{name}\', $null, \'DoNotExpandEnvironmentNames\')"')).read()

@warn_deprecated_redirect(getuserenv)
def get_user_env(name  :str,
                 expand:bool=False):
     
    return getuserenv(name, expand)


def pout(cmd:str|list[str]):
    if isinstance(cmd,str):
        cmd = [cmd,]
    completed = _subprocess.run(
        cmd,
        stdout=_subprocess.PIPE,
        stderr=_subprocess.STDOUT,
        shell=True,
        universal_newlines=True)
    return completed.stdout
