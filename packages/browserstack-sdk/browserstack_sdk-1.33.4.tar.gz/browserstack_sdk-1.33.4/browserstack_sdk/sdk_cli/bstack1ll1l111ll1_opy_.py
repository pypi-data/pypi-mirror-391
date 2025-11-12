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
import traceback
from typing import Dict, Tuple, Callable, Type, List, Any
from urllib.parse import urlparse
from browserstack_sdk.sdk_cli.bstack1lllll11lll_opy_ import (
    bstack1llll1ll111_opy_,
    bstack1lllll1lll1_opy_,
    bstack1llll11111l_opy_,
    bstack1llll1l11l1_opy_,
)
import copy
from datetime import datetime, timezone, timedelta
class bstack1ll1l11111l_opy_(bstack1llll1ll111_opy_):
    bstack1l111l1ll1l_opy_ = bstack11l111_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠦᑱ")
    bstack1l11llll111_opy_ = bstack11l111_opy_ (u"ࠧ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠧᑲ")
    bstack1l11lllll11_opy_ = bstack11l111_opy_ (u"ࠨࡨࡶࡤࡢࡹࡷࡲࠢᑳ")
    bstack1l11lllllll_opy_ = bstack11l111_opy_ (u"ࠢࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᑴ")
    bstack1l111l1ll11_opy_ = bstack11l111_opy_ (u"ࠣࡹ࠶ࡧࡪࡾࡥࡤࡷࡷࡩࡸࡩࡲࡪࡲࡷࠦᑵ")
    bstack1l111ll1l11_opy_ = bstack11l111_opy_ (u"ࠤࡺ࠷ࡨ࡫ࡸࡦࡥࡸࡸࡪࡹࡣࡳ࡫ࡳࡸࡦࡹࡹ࡯ࡥࠥᑶ")
    NAME = bstack11l111_opy_ (u"ࠥࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠢᑷ")
    bstack1l111l1lll1_opy_: Dict[str, List[Callable]] = dict()
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1ll1llll111_opy_: Any
    bstack1l111ll11ll_opy_: Dict
    def __init__(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        methods=[bstack11l111_opy_ (u"ࠦࡱࡧࡵ࡯ࡥ࡫ࠦᑸ"), bstack11l111_opy_ (u"ࠧࡩ࡯࡯ࡰࡨࡧࡹࠨᑹ"), bstack11l111_opy_ (u"ࠨ࡮ࡦࡹࡢࡴࡦ࡭ࡥࠣᑺ"), bstack11l111_opy_ (u"ࠢࡤ࡮ࡲࡷࡪࠨᑻ"), bstack11l111_opy_ (u"ࠣࡦ࡬ࡷࡵࡧࡴࡤࡪࠥᑼ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.platform_index = platform_index
        self.bstack1llll11l111_opy_(methods)
    def bstack1lllll11ll1_opy_(self, instance: bstack1lllll1lll1_opy_, method_name: str, bstack1lllll1l11l_opy_: timedelta, *args, **kwargs):
        pass
    def bstack1lllll11111_opy_(
        self,
        target: object,
        exec: Tuple[bstack1lllll1lll1_opy_, str],
        bstack1llll11llll_opy_: Tuple[bstack1llll11111l_opy_, bstack1llll1l11l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable[..., Any]:
        instance, method_name = exec
        bstack1llll1l1l1l_opy_, bstack1l111ll11l1_opy_ = bstack1llll11llll_opy_
        bstack1l111ll1l1l_opy_ = bstack1ll1l11111l_opy_.bstack1l111l1llll_opy_(bstack1llll11llll_opy_)
        if bstack1l111ll1l1l_opy_ in bstack1ll1l11111l_opy_.bstack1l111l1lll1_opy_:
            bstack1l111ll111l_opy_ = None
            for callback in bstack1ll1l11111l_opy_.bstack1l111l1lll1_opy_[bstack1l111ll1l1l_opy_]:
                try:
                    bstack1l111ll1111_opy_ = callback(self, target, exec, bstack1llll11llll_opy_, result, *args, **kwargs)
                    if bstack1l111ll111l_opy_ == None:
                        bstack1l111ll111l_opy_ = bstack1l111ll1111_opy_
                except Exception as e:
                    self.logger.error(bstack11l111_opy_ (u"ࠤࡨࡶࡷࡵࡲࠡ࡫ࡱࡺࡴࡱࡩ࡯ࡩࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯࠿ࠦࠢᑽ") + str(e) + bstack11l111_opy_ (u"ࠥࠦᑾ"))
                    traceback.print_exc()
            if bstack1l111ll11l1_opy_ == bstack1llll1l11l1_opy_.PRE and callable(bstack1l111ll111l_opy_):
                return bstack1l111ll111l_opy_
            elif bstack1l111ll11l1_opy_ == bstack1llll1l11l1_opy_.POST and bstack1l111ll111l_opy_:
                return bstack1l111ll111l_opy_
    def bstack1llll11l1l1_opy_(
        self, method_name, previous_state: bstack1llll11111l_opy_, *args, **kwargs
    ) -> bstack1llll11111l_opy_:
        if method_name == bstack11l111_opy_ (u"ࠫࡱࡧࡵ࡯ࡥ࡫ࠫᑿ") or method_name == bstack11l111_opy_ (u"ࠬࡩ࡯࡯ࡰࡨࡧࡹ࠭ᒀ") or method_name == bstack11l111_opy_ (u"࠭࡮ࡦࡹࡢࡴࡦ࡭ࡥࠨᒁ"):
            return bstack1llll11111l_opy_.bstack1llll111l1l_opy_
        if method_name == bstack11l111_opy_ (u"ࠧࡥ࡫ࡶࡴࡦࡺࡣࡩࠩᒂ"):
            return bstack1llll11111l_opy_.bstack1llll1llll1_opy_
        if method_name == bstack11l111_opy_ (u"ࠨࡥ࡯ࡳࡸ࡫ࠧᒃ"):
            return bstack1llll11111l_opy_.QUIT
        return bstack1llll11111l_opy_.NONE
    @staticmethod
    def bstack1l111l1llll_opy_(bstack1llll11llll_opy_: Tuple[bstack1llll11111l_opy_, bstack1llll1l11l1_opy_]):
        return bstack11l111_opy_ (u"ࠤ࠽ࠦᒄ").join((bstack1llll11111l_opy_(bstack1llll11llll_opy_[0]).name, bstack1llll1l11l1_opy_(bstack1llll11llll_opy_[1]).name))
    @staticmethod
    def bstack1ll111111ll_opy_(bstack1llll11llll_opy_: Tuple[bstack1llll11111l_opy_, bstack1llll1l11l1_opy_], callback: Callable):
        bstack1l111ll1l1l_opy_ = bstack1ll1l11111l_opy_.bstack1l111l1llll_opy_(bstack1llll11llll_opy_)
        if not bstack1l111ll1l1l_opy_ in bstack1ll1l11111l_opy_.bstack1l111l1lll1_opy_:
            bstack1ll1l11111l_opy_.bstack1l111l1lll1_opy_[bstack1l111ll1l1l_opy_] = []
        bstack1ll1l11111l_opy_.bstack1l111l1lll1_opy_[bstack1l111ll1l1l_opy_].append(callback)
    @staticmethod
    def bstack1ll1111llll_opy_(method_name: str):
        return True
    @staticmethod
    def bstack1l1llllll11_opy_(method_name: str, *args) -> bool:
        return True
    @staticmethod
    def bstack1ll11l1l11l_opy_(instance: bstack1lllll1lll1_opy_, default_value=None):
        return bstack1llll1ll111_opy_.bstack1llll1ll11l_opy_(instance, bstack1ll1l11111l_opy_.bstack1l11lllllll_opy_, default_value)
    @staticmethod
    def bstack1l1ll1llll1_opy_(instance: bstack1lllll1lll1_opy_) -> bool:
        return True
    @staticmethod
    def bstack1ll11ll11l1_opy_(instance: bstack1lllll1lll1_opy_, default_value=None):
        return bstack1llll1ll111_opy_.bstack1llll1ll11l_opy_(instance, bstack1ll1l11111l_opy_.bstack1l11lllll11_opy_, default_value)
    @staticmethod
    def bstack1l1lllll11l_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1l1llllll1l_opy_(method_name: str, *args):
        if not bstack1ll1l11111l_opy_.bstack1ll1111llll_opy_(method_name):
            return False
        if not bstack1ll1l11111l_opy_.bstack1l111l1ll11_opy_ in bstack1ll1l11111l_opy_.bstack1l11l1lll1l_opy_(*args):
            return False
        bstack1l1lll1l1l1_opy_ = bstack1ll1l11111l_opy_.bstack1l1lll1l11l_opy_(*args)
        return bstack1l1lll1l1l1_opy_ and bstack11l111_opy_ (u"ࠥࡷࡨࡸࡩࡱࡶࠥᒅ") in bstack1l1lll1l1l1_opy_ and bstack11l111_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᒆ") in bstack1l1lll1l1l1_opy_[bstack11l111_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧᒇ")]
    @staticmethod
    def bstack1ll11ll1l1l_opy_(method_name: str, *args):
        if not bstack1ll1l11111l_opy_.bstack1ll1111llll_opy_(method_name):
            return False
        if not bstack1ll1l11111l_opy_.bstack1l111l1ll11_opy_ in bstack1ll1l11111l_opy_.bstack1l11l1lll1l_opy_(*args):
            return False
        bstack1l1lll1l1l1_opy_ = bstack1ll1l11111l_opy_.bstack1l1lll1l11l_opy_(*args)
        return (
            bstack1l1lll1l1l1_opy_
            and bstack11l111_opy_ (u"ࠨࡳࡤࡴ࡬ࡴࡹࠨᒈ") in bstack1l1lll1l1l1_opy_
            and bstack11l111_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡨࡸࡩࡱࡶࠥᒉ") in bstack1l1lll1l1l1_opy_[bstack11l111_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࠣᒊ")]
        )
    @staticmethod
    def bstack1l11l1lll1l_opy_(*args):
        return str(bstack1ll1l11111l_opy_.bstack1l1lllll11l_opy_(*args)).lower()