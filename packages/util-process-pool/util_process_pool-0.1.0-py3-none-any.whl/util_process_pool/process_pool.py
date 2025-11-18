"""
多进程池管理工具
提供简便的多进程调用接口
"""

import os
import time
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Callable, List, Any, Iterator, Union, Optional
from functools import partial


class ProcessPool:
    """
    简便的多进程池管理类
    封装了 ProcessPoolExecutor 的常用功能
    """
    
    def __init__(self, max_workers: Optional[int] = None, 
                 initializer: Optional[Callable] = None,
                 initargs: tuple = (),
                 logger: Optional[logging.Logger] = None):
        """
        初始化进程池
        
        Args:
            max_workers: 最大工作进程数，默认为 CPU 核心数
            initializer: 每个工作进程启动时调用的初始化函数
            initargs: 初始化函数的参数
            logger: 日志记录器
        """
        self.max_workers = max_workers or max(1, os.cpu_count() - 2)
        self.initializer = initializer
        self.initargs = initargs
        self.logger = logger or self._get_default_logger()
        self._executor = None
        self._futures = []
        
    def _get_default_logger(self) -> logging.Logger:
        """获取默认的日志记录器"""
        logger = logging.getLogger("ProcessPool")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
        
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.shutdown()
        
    def set_pool_size(self, max_workers: int):
        """设置进程池大小"""
        self.max_workers = max_workers
        
    def start(self):
        """启动进程池"""
        if self._executor is None:
            self._executor = ProcessPoolExecutor(
                max_workers=self.max_workers,
                initializer=self.initializer,
                initargs=self.initargs
            )
            self.logger.info(f"进程池已启动，工作进程数: {self.max_workers}")
            
    def shutdown(self, wait: bool = True):
        """关闭进程池"""
        if self._executor:
            self._executor.shutdown(wait=wait)
            self._executor = None
            self.logger.info("进程池已关闭")
            
    def submit(self, func: Callable, *args, **kwargs) -> Any:
        """
        提交单个任务到进程池
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            Future 对象
        """
        if self._executor is None:
            self.start()
            
        future = self._executor.submit(func, *args, **kwargs)
        self._futures.append(future)
        return future
        
    def map(self, func: Callable, iterable: List, 
            timeout: Optional[float] = None,
            chunksize: int = 1) -> Iterator[Any]:
        """
        并行执行函数，类似内置的 map 函数
        
        Args:
            func: 要执行的函数
            iterable: 可迭代对象
            timeout: 超时时间
            chunksize: 每个工作进程一次处理的任务数
            
        Returns:
            结果迭代器
        """
        if self._executor is None:
            self.start()
            
        return self._executor.map(func, iterable, timeout=timeout, chunksize=chunksize)
        
    def execute_batch(self, func: Callable, args_list: List[tuple], 
                     timeout: Optional[float] = None,
                     show_progress: bool = False) -> List[Any]:
        """
        批量执行任务
        
        Args:
            func: 要执行的函数
            args_list: 参数列表，每个元素是 (args, kwargs) 或 args
            timeout: 超时时间
            show_progress: 是否显示进度
            
        Returns:
            结果列表
        """
        if self._executor is None:
            self.start()
            
        futures = []
        results = []
        
        # 提交所有任务
        for i, args in enumerate(args_list):
            if (isinstance(args, tuple) or isinstance(args, list)) and len(args) == 2 and isinstance(args[1], dict):
                # (args, kwargs) 格式
                self.logger.info(f'args: {args[0]}, kwargs: {args[1]}')
                future = self.submit(func, *args[0], **args[1])
            elif (isinstance(args, tuple) or isinstance(args, list)) and len(args) == 1:
                # 只有 args 格式
                self.logger.info(f'args: {args}')
                future = self.submit(func, *args)
            else:
                # 未知格式，记录警告
                self.logger.warning(f"任务 {i} 格式未知，跳过执行")
                continue
            futures.append((i, future))
            
        # 收集结果
        completed = 0
        total = len(futures)
        
        for i, future in futures:
            try:
                result = future.result(timeout=timeout)
                results.append((i, result))
                completed += 1
                
                if show_progress:
                    progress = completed / total * 100
                    self.logger.info(f"进度: {completed}/{total} ({progress:.1f}%)")
                    
            except Exception as e:
                self.logger.error(f"任务 {i} 执行失败: {e}")
                results.append((i, e))
                
        # 按原始顺序排序结果
        results.sort(key=lambda x: x[0])
        return [result for _, result in results]
        
    def wait_completion(self, timeout: Optional[float] = None) -> List[Any]:
        """
        等待所有已提交的任务完成
        
        Args:
            timeout: 超时时间
            
        Returns:
            结果列表
        """
        results = []
        for future in as_completed(self._futures, timeout=timeout):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                self.logger.error(f"任务执行失败: {e}")
                results.append(e)
                
        self._futures.clear()
        return results


def parallel_map(func: Callable, iterable: List, 
                max_workers: Optional[int] = None,
                chunksize: int = 1,
                timeout: Optional[float] = None) -> List[Any]:
    """
    简便的并行映射函数
    
    Args:
        func: 要执行的函数
        iterable: 可迭代对象
        max_workers: 最大工作进程数
        chunksize: 每个工作进程一次处理的任务数
        timeout: 超时时间
        
    Returns:
        结果列表
    """
    with ProcessPool(max_workers=max_workers) as pool:
        return list(pool.map(func, iterable, timeout=timeout, chunksize=chunksize))


def batch_execute(func: Callable, args_list: List[tuple],
                 max_workers: Optional[int] = None,
                 timeout: Optional[float] = None,
                 show_progress: bool = False) -> List[Any]:
    """
    批量执行任务的简便函数
    
    Args:
        func: 要执行的函数
        args_list: 参数列表
        max_workers: 最大工作进程数
        timeout: 超时时间
        show_progress: 是否显示进度
        
    Returns:
        结果列表
    """
    with ProcessPool(max_workers=max_workers) as pool:
        return pool.execute_batch(func, args_list, timeout=timeout, show_progress=show_progress)


# 示例函数，用于演示
def _example_worker(x: int) -> int:
    """示例工作函数"""
    import time
    time.sleep(0.1)  # 模拟工作负载
    return x * x


if __name__ == "__main__":
    # 使用示例
    numbers = list(range(10))
    
    # 使用 parallel_map
    print("使用 parallel_map:")
    results = parallel_map(_example_worker, numbers)
    print(f"结果: {results}")
    
    # 使用 ProcessPool 类
    print("\n使用 ProcessPool 类:")
    with ProcessPool(max_workers=4) as pool:
        results = pool.map(_example_worker, numbers)
        print(f"结果: {list(results)}")
    
    # 使用 batch_execute
    print("\n使用 batch_execute:")
    args_list = [(i,) for i in numbers]  # 每个任务一个参数
    results = batch_execute(_example_worker, args_list, show_progress=True)
    print(f"结果: {results}")
    
    # 使用 batch_execute all
    print("\n使用 batch_execute:")
    args_list = [((i,), {}) for i in numbers]  # 每个任务一个参数
    results = batch_execute(_example_worker, args_list, show_progress=True)
    print(f"结果: {results}")