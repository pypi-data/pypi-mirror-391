import functools as _functools
import os.path as _os_path
import time as _time
import typing as _typing

def warn_deprecated_redirect(funcnew:_typing.Callable|None=None):

    def decorator(funcdepr:_typing.Callable):

        @_functools.wraps(funcdepr)
        def wrapper(*aa, **kaa):

            print(f'[WARNING] {funcdepr.__module__}.{funcdepr.__qualname__} is deprecated{f', use {funcnew.__module__}.{funcnew.__qualname__} instead' if funcnew else ''}')
            return funcdepr(*aa, **kaa)
        
        return wrapper
    
    return decorator

def warn_deprecated(funcdepr:_typing.Callable):

    return warn_deprecated_redirect(None)(funcdepr)

def is_module(path:str):

    if _os_path.isfile(path) and path.endswith('.py'): return True

    if not _os_path.isdir(path): return False
    
    init_path = _os_path.join(path, '__init__.py')
    return _os_path.exists(init_path) and \
           _os_path.isfile(init_path)

class Enumerator[T]:

    def __init__(self):

        self._managed:list[T] = list()
    
    def __call__(self, x):

        self._managed.append(x)
        return x

    @warn_deprecated_redirect(__call__)
    def E(self, x):

        return self(x)
    
    def __iter__(self):

        return self._managed.__iter__()

class _CallablesRef:

    def __init__(self, *ff:_typing.Callable):

        self._ff = ff

class _JoinedCallables(_CallablesRef):

    def __call__(self, *aa, **kaa):

        for f in self._ff: 
            
            f(*aa, **kaa)

def joincallables(*ff:_typing.Callable): return _JoinedCallables(*ff).__call__

class _JoinedFunctions(_CallablesRef):

    def __call__(self, *aa, **kaa): 
        
        for f in self._ff: 
            
            yield f(*aa, **kaa)

def joinfunctions(*ff:_typing.Callable): return _JoinedFunctions(*ff).__call__

class _Raiser:

    def __init__(self, ex:Exception):       self._ex = ex
    def __call__(self)              : raise self._ex

def raiser(ex:Exception): return _Raiser(ex).__call__

def selfie[T](v:T): return v # instead of "self" since the latter is widely used for the instance reference in methods

class _Constant[T]:

    def __init__(self, v:T): self._v = v
    def __call__(self, *aa, **kaa): return self._v

def constant[T](v:T): return _Constant(v).__call__

def waitkbi(poll_time_s:float=60):

    while True:
        try: _time.sleep(poll_time_s)
        except KeyboardInterrupt: break
