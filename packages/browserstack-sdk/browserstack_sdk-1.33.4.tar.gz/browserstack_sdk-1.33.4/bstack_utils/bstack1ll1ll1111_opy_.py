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
from time import sleep
from datetime import datetime
from urllib.parse import urlencode
from bstack_utils.bstack11l1lll111l_opy_ import bstack11l1lll1ll1_opy_
from bstack_utils.constants import *
import json
class bstack111l1l1ll_opy_:
    def __init__(self, bstack11ll1l11_opy_, bstack11l1llll111_opy_):
        self.bstack11ll1l11_opy_ = bstack11ll1l11_opy_
        self.bstack11l1llll111_opy_ = bstack11l1llll111_opy_
        self.bstack11l1lll11ll_opy_ = None
    def __call__(self):
        bstack11l1lll1lll_opy_ = {}
        while True:
            self.bstack11l1lll11ll_opy_ = bstack11l1lll1lll_opy_.get(
                bstack11l111_opy_ (u"ࠫࡳ࡫ࡸࡵࡡࡳࡳࡱࡲ࡟ࡵ࡫ࡰࡩࠬ៎"),
                int(datetime.now().timestamp() * 1000)
            )
            bstack11l1lll1l11_opy_ = self.bstack11l1lll11ll_opy_ - int(datetime.now().timestamp() * 1000)
            if bstack11l1lll1l11_opy_ > 0:
                sleep(bstack11l1lll1l11_opy_ / 1000)
            params = {
                bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ៏"): self.bstack11ll1l11_opy_,
                bstack11l111_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩ័"): int(datetime.now().timestamp() * 1000)
            }
            bstack11l1llll11l_opy_ = bstack11l111_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤ៑") + bstack11l1lll11l1_opy_ + bstack11l111_opy_ (u"ࠣ࠱ࡤࡹࡹࡵ࡭ࡢࡶࡨ࠳ࡦࡶࡩ࠰ࡸ࠴࠳្ࠧ")
            if self.bstack11l1llll111_opy_.lower() == bstack11l111_opy_ (u"ࠤࡵࡩࡸࡻ࡬ࡵࡵࠥ៓"):
                bstack11l1lll1lll_opy_ = bstack11l1lll1ll1_opy_.results(bstack11l1llll11l_opy_, params)
            else:
                bstack11l1lll1lll_opy_ = bstack11l1lll1ll1_opy_.bstack11l1lll1l1l_opy_(bstack11l1llll11l_opy_, params)
            if str(bstack11l1lll1lll_opy_.get(bstack11l111_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ។"), bstack11l111_opy_ (u"ࠫ࠷࠶࠰ࠨ៕"))) != bstack11l111_opy_ (u"ࠬ࠺࠰࠵ࠩ៖"):
                break
        return bstack11l1lll1lll_opy_.get(bstack11l111_opy_ (u"࠭ࡤࡢࡶࡤࠫៗ"), bstack11l1lll1lll_opy_)