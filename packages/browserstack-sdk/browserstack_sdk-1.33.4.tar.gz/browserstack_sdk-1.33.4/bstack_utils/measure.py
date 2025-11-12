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
import logging
from functools import wraps
from typing import Optional
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.bstack11l111111l_opy_ import get_logger
from bstack_utils.bstack1llllll1l_opy_ import bstack1ll1l11ll1l_opy_
bstack1llllll1l_opy_ = bstack1ll1l11ll1l_opy_()
logger = get_logger(__name__)
def measure(event_name: EVENTS, stage: STAGE, hook_type: Optional[str] = None, bstack1ll111l111_opy_: Optional[str] = None):
    bstack11l111_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࡉ࡫ࡣࡰࡴࡤࡸࡴࡸࠠࡵࡱࠣࡰࡴ࡭ࠠࡵࡪࡨࠤࡸࡺࡡࡳࡶࠣࡸ࡮ࡳࡥࠡࡱࡩࠤࡦࠦࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠡࡧࡻࡩࡨࡻࡴࡪࡱࡱࠎࠥࠦࠠࠡࡣ࡯ࡳࡳ࡭ࠠࡸ࡫ࡷ࡬ࠥ࡫ࡶࡦࡰࡷࠤࡳࡧ࡭ࡦࠢࡤࡲࡩࠦࡳࡵࡣࡪࡩ࠳ࠐࠠࠡࠢࠣࠦࠧࠨṗ")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            label: str = event_name.value
            bstack1l1llll11ll_opy_: str = bstack1llllll1l_opy_.bstack11ll111ll1l_opy_(label)
            start_mark: str = label + bstack11l111_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧṘ")
            end_mark: str = label + bstack11l111_opy_ (u"ࠨ࠺ࡦࡰࡧࠦṙ")
            result = None
            try:
                if stage.value == STAGE.bstack1llll1l1l1_opy_.value:
                    bstack1llllll1l_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                elif stage.value == STAGE.END.value:
                    result = func(*args, **kwargs)
                    bstack1llllll1l_opy_.end(label, start_mark, end_mark, status=True, failure=None,hook_type=hook_type,test_name=bstack1ll111l111_opy_)
                elif stage.value == STAGE.bstack1l1l111l1_opy_.value:
                    start_mark: str = bstack1l1llll11ll_opy_ + bstack11l111_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢṚ")
                    end_mark: str = bstack1l1llll11ll_opy_ + bstack11l111_opy_ (u"ࠣ࠼ࡨࡲࡩࠨṛ")
                    bstack1llllll1l_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                    bstack1llllll1l_opy_.end(label, start_mark, end_mark, status=True, failure=None, hook_type=hook_type,test_name=bstack1ll111l111_opy_)
            except Exception as e:
                bstack1llllll1l_opy_.end(label, start_mark, end_mark, status=False, failure=str(e), hook_type=hook_type,
                                       test_name=bstack1ll111l111_opy_)
            return result
        return wrapper
    return decorator