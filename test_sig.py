from functools import wraps
import inspect
from os import setsid
from util.setsig import funcsig, metsig

def func(a: str, b: int, c: int) -> None:
    pass

@funcsig(func)
def func2(*args, **kwargs) -> None:
    print("eae")
    func(*args, **kwargs)
    pass

class Test:
    @metsig(func)
    def method(self, *args, **kwargs) -> None:
        print(f"Test::method called with {self=}, {args=} and {kwargs=}")
        pass


def test_func():
    func2("a", 1, 2)
    t = Test()
    t.method()