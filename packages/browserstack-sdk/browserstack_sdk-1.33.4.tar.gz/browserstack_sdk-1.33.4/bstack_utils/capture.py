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
import builtins
import logging
class bstack111ll1llll_opy_:
    def __init__(self, handler):
        self._11l1ll1ll11_opy_ = builtins.print
        self.handler = handler
        self._started = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._11l1ll1l1ll_opy_ = {
            level: getattr(self.logger, level)
            for level in [bstack11l111_opy_ (u"ࠩ࡬ࡲ࡫ࡵࠧ១"), bstack11l111_opy_ (u"ࠪࡨࡪࡨࡵࡨࠩ២"), bstack11l111_opy_ (u"ࠫࡼࡧࡲ࡯࡫ࡱ࡫ࠬ៣"), bstack11l111_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ៤")]
        }
    def start(self):
        if self._started:
            return
        self._started = True
        builtins.print = self._11l1ll1lll1_opy_
        self._11l1lll1111_opy_()
    def _11l1ll1lll1_opy_(self, *args, **kwargs):
        self._11l1ll1ll11_opy_(*args, **kwargs)
        message = bstack11l111_opy_ (u"࠭ࠠࠨ៥").join(map(str, args)) + bstack11l111_opy_ (u"ࠧ࡝ࡰࠪ៦")
        self._log_message(bstack11l111_opy_ (u"ࠨࡋࡑࡊࡔ࠭៧"), message)
    def _log_message(self, level, msg, *args, **kwargs):
        if self.handler:
            self.handler({bstack11l111_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ៨"): level, bstack11l111_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ៩"): msg})
    def _11l1lll1111_opy_(self):
        for level, bstack11l1ll1llll_opy_ in self._11l1ll1l1ll_opy_.items():
            setattr(logging, level, self._11l1ll1ll1l_opy_(level, bstack11l1ll1llll_opy_))
    def _11l1ll1ll1l_opy_(self, level, bstack11l1ll1llll_opy_):
        def wrapper(msg, *args, **kwargs):
            bstack11l1ll1llll_opy_(msg, *args, **kwargs)
            self._log_message(level.upper(), msg)
        return wrapper
    def reset(self):
        if not self._started:
            return
        self._started = False
        builtins.print = self._11l1ll1ll11_opy_
        for level, bstack11l1ll1llll_opy_ in self._11l1ll1l1ll_opy_.items():
            setattr(logging, level, bstack11l1ll1llll_opy_)