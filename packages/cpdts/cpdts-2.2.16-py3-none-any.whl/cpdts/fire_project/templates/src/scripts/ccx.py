
from .build import build
from .clean import clean
from .public import public 



def ccx():
    """依次执行 clean、build 和 public 操作"""
    clean()
    build()
    public()
