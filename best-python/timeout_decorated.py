#!/usr/bin/env python
# -*- coding: utf-8


import signal
import functools


class TimeoutError(Exception):
    pass  # 定义一个Exception，后面超时抛出


def timeout(seconds, error_message='Function call timed out'):
    def decorated(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return functools.wraps(func)(wrapper)
    return decorated


# 示例

@timeout(5)  # 限定下面的slowfunc函数如果在5s内不返回就强制抛TimeoutError Exception结束
def slowfunc(sleep_time):
    import time
    time.sleep(sleep_time)  # 这个函数就是休眠sleep_time秒

slowfunc(3)  # sleep 3秒，正常返回 没有异常

slowfunc(10)  # 被终止

"""
## 输出 
---------------------------------------------------------------------------
TimeoutError                              Traceback (most recent call last)
"""
