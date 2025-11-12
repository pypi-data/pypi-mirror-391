# coding: UTF-8
import sys
bstack11111l_opy_ = sys.version_info [0] == 2
bstack1111ll1_opy_ = 2048
bstack1l1llll_opy_ = 7
def bstack11l111_opy_ (bstack1111ll_opy_):
    global bstack111ll1l_opy_
    bstack11lll_opy_ = ord (bstack1111ll_opy_ [-1])
    bstack11lll1_opy_ = bstack1111ll_opy_ [:-1]
    bstack1111l11_opy_ = bstack11lll_opy_ % len (bstack11lll1_opy_)
    bstack1l11111_opy_ = bstack11lll1_opy_ [:bstack1111l11_opy_] + bstack11lll1_opy_ [bstack1111l11_opy_:]
    if bstack11111l_opy_:
        bstack111l1_opy_ = unicode () .join ([unichr (ord (char) - bstack1111ll1_opy_ - (bstack11ll111_opy_ + bstack11lll_opy_) % bstack1l1llll_opy_) for bstack11ll111_opy_, char in enumerate (bstack1l11111_opy_)])
    else:
        bstack111l1_opy_ = str () .join ([chr (ord (char) - bstack1111ll1_opy_ - (bstack11ll111_opy_ + bstack11lll_opy_) % bstack1l1llll_opy_) for bstack11ll111_opy_, char in enumerate (bstack1l11111_opy_)])
    return eval (bstack111l1_opy_)
import threading
import queue
from typing import Callable, Union
class bstack1llllll111l_opy_:
    timeout: int
    bstack1llllll11l1_opy_: Union[None, Callable]
    bstack1lllll1llll_opy_: Union[None, Callable]
    def __init__(self, timeout=1, bstack1llllll11ll_opy_=1, bstack1llllll11l1_opy_=None, bstack1lllll1llll_opy_=None):
        self.timeout = timeout
        self.bstack1llllll11ll_opy_ = bstack1llllll11ll_opy_
        self.bstack1llllll11l1_opy_ = bstack1llllll11l1_opy_
        self.bstack1lllll1llll_opy_ = bstack1lllll1llll_opy_
        self.queue = queue.Queue()
        self.bstack1llllll1111_opy_ = threading.Event()
        self.threads = []
    def enqueue(self, job: Callable):
        if not callable(job):
            raise ValueError(bstack11l111_opy_ (u"ࠨࡩ࡯ࡸࡤࡰ࡮ࡪࠠ࡫ࡱࡥ࠾ࠥࠨპ") + type(job))
        self.queue.put(job)
    def start(self):
        if self.threads:
            return
        self.threads = [threading.Thread(target=self.worker, daemon=True) for _ in range(self.bstack1llllll11ll_opy_)]
        for thread in self.threads:
            thread.start()
    def stop(self):
        if not self.threads:
            return
        if not self.queue.empty():
            self.queue.join()
        self.bstack1llllll1111_opy_.set()
        for _ in self.threads:
            self.queue.put(None)
        for thread in self.threads:
            thread.join()
        self.threads.clear()
    def worker(self):
        while not self.bstack1llllll1111_opy_.is_set():
            try:
                job = self.queue.get(block=True, timeout=self.timeout)
                if job is None:
                    break
                try:
                    job()
                except Exception as e:
                    if callable(self.bstack1llllll11l1_opy_):
                        self.bstack1llllll11l1_opy_(e, job)
                finally:
                    self.queue.task_done()
            except queue.Empty:
                pass
            except Exception as e:
                if callable(self.bstack1lllll1llll_opy_):
                    self.bstack1lllll1llll_opy_(e)