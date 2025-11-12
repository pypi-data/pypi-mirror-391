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
class bstack1l111111_opy_:
    def __init__(self, handler):
        self._1llll1lll11l_opy_ = None
        self.handler = handler
        self._1llll1lll1ll_opy_ = self.bstack1llll1lll1l1_opy_()
        self.patch()
    def patch(self):
        self._1llll1lll11l_opy_ = self._1llll1lll1ll_opy_.execute
        self._1llll1lll1ll_opy_.execute = self.bstack1llll1llll11_opy_()
    def bstack1llll1llll11_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            self.handler(bstack11l111_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࠣ₄"), driver_command, None, this, args)
            response = self._1llll1lll11l_opy_(this, driver_command, *args, **kwargs)
            self.handler(bstack11l111_opy_ (u"ࠤࡤࡪࡹ࡫ࡲࠣ₅"), driver_command, response)
            return response
        return execute
    def reset(self):
        self._1llll1lll1ll_opy_.execute = self._1llll1lll11l_opy_
    @staticmethod
    def bstack1llll1lll1l1_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver