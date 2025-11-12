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
import logging
logger = logging.getLogger(__name__)
bstack1lllll111lll_opy_ = 1000
bstack1lllll11lll1_opy_ = 2
class bstack1lllll11llll_opy_:
    def __init__(self, handler, bstack1lllll11l111_opy_=bstack1lllll111lll_opy_, bstack1lllll11ll11_opy_=bstack1lllll11lll1_opy_):
        self.queue = []
        self.handler = handler
        self.bstack1lllll11l111_opy_ = bstack1lllll11l111_opy_
        self.bstack1lllll11ll11_opy_ = bstack1lllll11ll11_opy_
        self.lock = threading.Lock()
        self.timer = None
        self.bstack1llllll1111_opy_ = None
    def start(self):
        if not (self.timer and self.timer.is_alive()):
            self.bstack1lllll11l11l_opy_()
    def bstack1lllll11l11l_opy_(self):
        self.bstack1llllll1111_opy_ = threading.Event()
        def bstack1lllll11l1l1_opy_():
            self.bstack1llllll1111_opy_.wait(self.bstack1lllll11ll11_opy_)
            if not self.bstack1llllll1111_opy_.is_set():
                self.bstack1lllll11l1ll_opy_()
        self.timer = threading.Thread(target=bstack1lllll11l1l1_opy_, daemon=True)
        self.timer.start()
    def bstack1lllll1l111l_opy_(self):
        try:
            if self.bstack1llllll1111_opy_ and not self.bstack1llllll1111_opy_.is_set():
                self.bstack1llllll1111_opy_.set()
            if self.timer and self.timer.is_alive() and self.timer != threading.current_thread():
                self.timer.join()
        except Exception as e:
            logger.debug(bstack11l111_opy_ (u"ࠬࡡࡳࡵࡱࡳࡣࡹ࡯࡭ࡦࡴࡠࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴ࠺ࠡࠩ‴") + (str(e) or bstack11l111_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡦࡳࡺࡲࡤࠡࡰࡲࡸࠥࡨࡥࠡࡥࡲࡲࡻ࡫ࡲࡵࡧࡧࠤࡹࡵࠠࡴࡶࡵ࡭ࡳ࡭ࠢ‵")))
        finally:
            self.timer = None
    def bstack1lllll11ll1l_opy_(self):
        if self.timer:
            self.bstack1lllll1l111l_opy_()
        self.bstack1lllll11l11l_opy_()
    def add(self, event):
        with self.lock:
            self.queue.append(event)
            if len(self.queue) >= self.bstack1lllll11l111_opy_:
                threading.Thread(target=self.bstack1lllll11l1ll_opy_).start()
    def bstack1lllll11l1ll_opy_(self, source = bstack11l111_opy_ (u"ࠧࠨ‶")):
        with self.lock:
            if not self.queue:
                self.bstack1lllll11ll1l_opy_()
                return
            data = self.queue[:self.bstack1lllll11l111_opy_]
            del self.queue[:self.bstack1lllll11l111_opy_]
        self.handler(data)
        if source != bstack11l111_opy_ (u"ࠨࡵ࡫ࡹࡹࡪ࡯ࡸࡰࠪ‷"):
            self.bstack1lllll11ll1l_opy_()
    def shutdown(self):
        self.bstack1lllll1l111l_opy_()
        while self.queue:
            self.bstack1lllll11l1ll_opy_(source=bstack11l111_opy_ (u"ࠩࡶ࡬ࡺࡺࡤࡰࡹࡱࠫ‸"))