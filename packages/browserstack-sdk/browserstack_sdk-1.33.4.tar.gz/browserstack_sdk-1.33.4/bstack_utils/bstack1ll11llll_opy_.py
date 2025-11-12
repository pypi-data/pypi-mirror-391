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
from collections import deque
from bstack_utils.constants import *
class bstack111l1l11_opy_:
    def __init__(self):
        self._1llllllll1ll_opy_ = deque()
        self._1lllllll1l1l_opy_ = {}
        self._1lllllll11ll_opy_ = False
        self._lock = threading.RLock()
    def bstack1lllllllll1l_opy_(self, test_name, bstack1lllllll111l_opy_):
        with self._lock:
            bstack1lllllll1ll1_opy_ = self._1lllllll1l1l_opy_.get(test_name, {})
            return bstack1lllllll1ll1_opy_.get(bstack1lllllll111l_opy_, 0)
    def bstack1llllllll11l_opy_(self, test_name, bstack1lllllll111l_opy_):
        with self._lock:
            bstack1lllllll1lll_opy_ = self.bstack1lllllllll1l_opy_(test_name, bstack1lllllll111l_opy_)
            self.bstack1llllllll111_opy_(test_name, bstack1lllllll111l_opy_)
            return bstack1lllllll1lll_opy_
    def bstack1llllllll111_opy_(self, test_name, bstack1lllllll111l_opy_):
        with self._lock:
            if test_name not in self._1lllllll1l1l_opy_:
                self._1lllllll1l1l_opy_[test_name] = {}
            bstack1lllllll1ll1_opy_ = self._1lllllll1l1l_opy_[test_name]
            bstack1lllllll1lll_opy_ = bstack1lllllll1ll1_opy_.get(bstack1lllllll111l_opy_, 0)
            bstack1lllllll1ll1_opy_[bstack1lllllll111l_opy_] = bstack1lllllll1lll_opy_ + 1
    def bstack111l11l1l_opy_(self, bstack1lllllll1l11_opy_, bstack1llllllll1l1_opy_):
        bstack1lllllll11l1_opy_ = self.bstack1llllllll11l_opy_(bstack1lllllll1l11_opy_, bstack1llllllll1l1_opy_)
        event_name = bstack11l1l1l11l1_opy_[bstack1llllllll1l1_opy_]
        bstack1l1l1111l11_opy_ = bstack11l111_opy_ (u"ࠤࡾࢁ࠲ࢁࡽ࠮ࡽࢀࠦ῁").format(bstack1lllllll1l11_opy_, event_name, bstack1lllllll11l1_opy_)
        with self._lock:
            self._1llllllll1ll_opy_.append(bstack1l1l1111l11_opy_)
    def bstack11ll1111l1_opy_(self):
        with self._lock:
            return len(self._1llllllll1ll_opy_) == 0
    def bstack1lll1l11l_opy_(self):
        with self._lock:
            if self._1llllllll1ll_opy_:
                bstack1lllllllll11_opy_ = self._1llllllll1ll_opy_.popleft()
                return bstack1lllllllll11_opy_
            return None
    def capturing(self):
        with self._lock:
            return self._1lllllll11ll_opy_
    def bstack1lll111l11_opy_(self):
        with self._lock:
            self._1lllllll11ll_opy_ = True
    def bstack1l1l11ll1_opy_(self):
        with self._lock:
            self._1lllllll11ll_opy_ = False