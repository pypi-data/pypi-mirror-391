"""
简便的多进程调用工具
基于 concurrent.futures.ProcessPoolExecutor 的封装
"""

from .process_pool import ProcessPool, parallel_map, batch_execute

__version__ = "1.0.0"
__all__ = ["ProcessPool", "parallel_map", "batch_execute"]