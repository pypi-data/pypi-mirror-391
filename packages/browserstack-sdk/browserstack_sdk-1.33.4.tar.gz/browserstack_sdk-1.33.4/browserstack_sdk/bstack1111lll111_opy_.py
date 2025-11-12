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
import os
class RobotHandler():
    def __init__(self, args, logger, bstack11111l1ll1_opy_, bstack1111111lll_opy_):
        self.args = args
        self.logger = logger
        self.bstack11111l1ll1_opy_ = bstack11111l1ll1_opy_
        self.bstack1111111lll_opy_ = bstack1111111lll_opy_
    @staticmethod
    def version():
        import robot
        return robot.__version__
    @staticmethod
    def bstack1111llll11_opy_(bstack1lllllll111_opy_):
        bstack1llllll1ll1_opy_ = []
        if bstack1lllllll111_opy_:
            tokens = str(os.path.basename(bstack1lllllll111_opy_)).split(bstack11l111_opy_ (u"ࠣࡡࠥკ"))
            camelcase_name = bstack11l111_opy_ (u"ࠤࠣࠦლ").join(t.title() for t in tokens)
            suite_name, bstack1llllll1l1l_opy_ = os.path.splitext(camelcase_name)
            bstack1llllll1ll1_opy_.append(suite_name)
        return bstack1llllll1ll1_opy_
    @staticmethod
    def bstack1llllll1lll_opy_(typename):
        if bstack11l111_opy_ (u"ࠥࡅࡸࡹࡥࡳࡶ࡬ࡳࡳࠨმ") in typename:
            return bstack11l111_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࡅࡳࡴࡲࡶࠧნ")
        return bstack11l111_opy_ (u"࡛ࠧ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷࠨო")