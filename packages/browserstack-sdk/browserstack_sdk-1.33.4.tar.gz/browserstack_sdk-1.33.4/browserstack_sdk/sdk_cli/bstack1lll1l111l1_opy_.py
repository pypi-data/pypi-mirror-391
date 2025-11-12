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
from typing import Dict, List, Any, Callable, Tuple, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll1l11ll1_opy_ import bstack1lll1ll1l11_opy_
from browserstack_sdk.sdk_cli.bstack1lllll11lll_opy_ import (
    bstack1llll11111l_opy_,
    bstack1llll1l11l1_opy_,
    bstack1lllll1lll1_opy_,
)
from bstack_utils.helper import  bstack1l11lll1l1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l111ll_opy_ import bstack1ll1l111l11_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll111l1l1_opy_, bstack1lll11l11ll_opy_, bstack1ll1l11l11l_opy_, bstack1lll11l1lll_opy_
from typing import Tuple, Any
import threading
from bstack_utils.bstack1ll11llll_opy_ import bstack111l1l11_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l1111l_opy_ import bstack1ll1lll1l1l_opy_
from bstack_utils.percy import bstack1ll1l111ll_opy_
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.constants import *
import re
class bstack1ll1ll11l11_opy_(bstack1lll1ll1l11_opy_):
    def __init__(self, bstack1l1l1111ll1_opy_: Dict[str, str]):
        super().__init__()
        self.bstack1l1l1111ll1_opy_ = bstack1l1l1111ll1_opy_
        self.percy = bstack1ll1l111ll_opy_()
        self.bstack111111111_opy_ = bstack111l1l11_opy_()
        self.bstack1l1l11l1111_opy_()
        bstack1ll1l111l11_opy_.bstack1ll111111ll_opy_((bstack1llll11111l_opy_.bstack1llll111lll_opy_, bstack1llll1l11l1_opy_.PRE), self.bstack1l1l111ll1l_opy_)
        TestFramework.bstack1ll111111ll_opy_((bstack1lll111l1l1_opy_.TEST, bstack1ll1l11l11l_opy_.POST), self.bstack1l1llllllll_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1l1ll1l1l_opy_(self, instance: bstack1lllll1lll1_opy_, driver: object):
        bstack1l1l1lll11l_opy_ = TestFramework.bstack1lllll1ll11_opy_(instance.context)
        for t in bstack1l1l1lll11l_opy_:
            bstack1l1l1l1l11l_opy_ = TestFramework.bstack1llll1ll11l_opy_(t, bstack1ll1lll1l1l_opy_.bstack1l1l11l1ll1_opy_, [])
            if any(instance is d[1] for d in bstack1l1l1l1l11l_opy_) or instance == driver:
                return t
    def bstack1l1l111ll1l_opy_(
        self,
        f: bstack1ll1l111l11_opy_,
        driver: object,
        exec: Tuple[bstack1lllll1lll1_opy_, str],
        bstack1llll11llll_opy_: Tuple[bstack1llll11111l_opy_, bstack1llll1l11l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if not bstack1ll1l111l11_opy_.bstack1ll1111llll_opy_(method_name):
                return
            platform_index = f.bstack1llll1ll11l_opy_(instance, bstack1ll1l111l11_opy_.bstack1ll111l1l1l_opy_, 0)
            bstack1l1l1lllll1_opy_ = self.bstack1l1l1ll1l1l_opy_(instance, driver)
            bstack1l1l1111l11_opy_ = TestFramework.bstack1llll1ll11l_opy_(bstack1l1l1lllll1_opy_, TestFramework.bstack1l1l1111l1l_opy_, None)
            if not bstack1l1l1111l11_opy_:
                self.logger.debug(bstack11l111_opy_ (u"ࠨ࡯࡯ࡡࡳࡶࡪࡥࡥࡹࡧࡦࡹࡹ࡫࠺ࠡࡴࡨࡸࡺࡸ࡮ࡪࡰࡪࠤࡦࡹࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡ࡫ࡶࠤࡳࡵࡴࠡࡻࡨࡸࠥࡹࡴࡢࡴࡷࡩࡩࠨጸ"))
                return
            driver_command = f.bstack1l1lllll11l_opy_(*args)
            for command in bstack1llllll1ll_opy_:
                if command == driver_command:
                    self.bstack11111ll1l_opy_(driver, platform_index)
            bstack1lll11lll_opy_ = self.percy.bstack1llll1llll_opy_()
            if driver_command in bstack11l11l111l_opy_[bstack1lll11lll_opy_]:
                self.bstack111111111_opy_.bstack111l11l1l_opy_(bstack1l1l1111l11_opy_, driver_command)
        except Exception as e:
            self.logger.error(bstack11l111_opy_ (u"ࠢࡰࡰࡢࡴࡷ࡫࡟ࡦࡺࡨࡧࡺࡺࡥ࠻ࠢࡨࡶࡷࡵࡲࠣጹ"), e)
    def bstack1l1llllllll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11ll_opy_,
        bstack1llll11llll_opy_: Tuple[bstack1lll111l1l1_opy_, bstack1ll1l11l11l_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack1llllll1l_opy_ import bstack1ll1l11ll1l_opy_
        bstack1l1l1l1l11l_opy_ = f.bstack1llll1ll11l_opy_(instance, bstack1ll1lll1l1l_opy_.bstack1l1l11l1ll1_opy_, [])
        if not bstack1l1l1l1l11l_opy_:
            self.logger.debug(bstack11l111_opy_ (u"ࠣࡱࡱࡣࡦ࡬ࡴࡦࡴࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥጺ") + str(kwargs) + bstack11l111_opy_ (u"ࠤࠥጻ"))
            return
        if len(bstack1l1l1l1l11l_opy_) > 1:
            self.logger.debug(bstack11l111_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࢀࡲࡥ࡯ࠪࡧࡶ࡮ࡼࡥࡳࡡ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡷ࠮ࢃࠠࡥࡴ࡬ࡺࡪࡸࡳࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧጼ") + str(kwargs) + bstack11l111_opy_ (u"ࠦࠧጽ"))
        bstack1l1l111lll1_opy_, bstack1l1l1111lll_opy_ = bstack1l1l1l1l11l_opy_[0]
        driver = bstack1l1l111lll1_opy_()
        if not driver:
            self.logger.debug(bstack11l111_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨጾ") + str(kwargs) + bstack11l111_opy_ (u"ࠨࠢጿ"))
            return
        bstack1l1l111l1ll_opy_ = {
            TestFramework.bstack1ll11l1111l_opy_: bstack11l111_opy_ (u"ࠢࡵࡧࡶࡸࠥࡴࡡ࡮ࡧࠥፀ"),
            TestFramework.bstack1ll1111l1ll_opy_: bstack11l111_opy_ (u"ࠣࡶࡨࡷࡹࠦࡵࡶ࡫ࡧࠦፁ"),
            TestFramework.bstack1l1l1111l1l_opy_: bstack11l111_opy_ (u"ࠤࡷࡩࡸࡺࠠࡳࡧࡵࡹࡳࠦ࡮ࡢ࡯ࡨࠦፂ")
        }
        bstack1l1l111llll_opy_ = { key: f.bstack1llll1ll11l_opy_(instance, key) for key in bstack1l1l111l1ll_opy_ }
        bstack1l1l111l1l1_opy_ = [key for key, value in bstack1l1l111llll_opy_.items() if not value]
        if bstack1l1l111l1l1_opy_:
            for key in bstack1l1l111l1l1_opy_:
                self.logger.debug(bstack11l111_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥࠨፃ") + str(key) + bstack11l111_opy_ (u"ࠦࠧፄ"))
            return
        platform_index = f.bstack1llll1ll11l_opy_(instance, bstack1ll1l111l11_opy_.bstack1ll111l1l1l_opy_, 0)
        if self.bstack1l1l1111ll1_opy_.percy_capture_mode == bstack11l111_opy_ (u"ࠧࡺࡥࡴࡶࡦࡥࡸ࡫ࠢፅ"):
            bstack1111111l_opy_ = bstack1l1l111llll_opy_.get(TestFramework.bstack1l1l1111l1l_opy_) + bstack11l111_opy_ (u"ࠨ࠭ࡵࡧࡶࡸࡨࡧࡳࡦࠤፆ")
            bstack1l1llll11ll_opy_ = bstack1ll1l11ll1l_opy_.bstack1l1lllllll1_opy_(EVENTS.bstack1l1l111ll11_opy_.value)
            PercySDK.screenshot(
                driver,
                bstack1111111l_opy_,
                bstack1l1111l111_opy_=bstack1l1l111llll_opy_[TestFramework.bstack1ll11l1111l_opy_],
                bstack111l11ll_opy_=bstack1l1l111llll_opy_[TestFramework.bstack1ll1111l1ll_opy_],
                bstack11llll1l1l_opy_=platform_index
            )
            bstack1ll1l11ll1l_opy_.end(EVENTS.bstack1l1l111ll11_opy_.value, bstack1l1llll11ll_opy_+bstack11l111_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢፇ"), bstack1l1llll11ll_opy_+bstack11l111_opy_ (u"ࠣ࠼ࡨࡲࡩࠨፈ"), True, None, None, None, None, test_name=bstack1111111l_opy_)
    def bstack11111ll1l_opy_(self, driver, platform_index):
        if self.bstack111111111_opy_.bstack11ll1111l1_opy_() is True or self.bstack111111111_opy_.capturing() is True:
            return
        self.bstack111111111_opy_.bstack1lll111l11_opy_()
        while not self.bstack111111111_opy_.bstack11ll1111l1_opy_():
            bstack1l1l1111l11_opy_ = self.bstack111111111_opy_.bstack1lll1l11l_opy_()
            self.bstack1111l11ll_opy_(driver, bstack1l1l1111l11_opy_, platform_index)
        self.bstack111111111_opy_.bstack1l1l11ll1_opy_()
    def bstack1111l11ll_opy_(self, driver, bstack11ll1l1l11_opy_, platform_index, test=None):
        from bstack_utils.bstack1llllll1l_opy_ import bstack1ll1l11ll1l_opy_
        bstack1l1llll11ll_opy_ = bstack1ll1l11ll1l_opy_.bstack1l1lllllll1_opy_(EVENTS.bstack1l1ll1111l_opy_.value)
        if test != None:
            bstack1l1111l111_opy_ = getattr(test, bstack11l111_opy_ (u"ࠩࡱࡥࡲ࡫ࠧፉ"), None)
            bstack111l11ll_opy_ = getattr(test, bstack11l111_opy_ (u"ࠪࡹࡺ࡯ࡤࠨፊ"), None)
            PercySDK.screenshot(driver, bstack11ll1l1l11_opy_, bstack1l1111l111_opy_=bstack1l1111l111_opy_, bstack111l11ll_opy_=bstack111l11ll_opy_, bstack11llll1l1l_opy_=platform_index)
        else:
            PercySDK.screenshot(driver, bstack11ll1l1l11_opy_)
        bstack1ll1l11ll1l_opy_.end(EVENTS.bstack1l1ll1111l_opy_.value, bstack1l1llll11ll_opy_+bstack11l111_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦፋ"), bstack1l1llll11ll_opy_+bstack11l111_opy_ (u"ࠧࡀࡥ࡯ࡦࠥፌ"), True, None, None, None, None, test_name=bstack11ll1l1l11_opy_)
    def bstack1l1l11l1111_opy_(self):
        os.environ[bstack11l111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡅࡓࡅ࡜ࠫፍ")] = str(self.bstack1l1l1111ll1_opy_.success)
        os.environ[bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡆࡔࡆ࡝ࡤࡉࡁࡑࡖࡘࡖࡊࡥࡍࡐࡆࡈࠫፎ")] = str(self.bstack1l1l1111ll1_opy_.percy_capture_mode)
        self.percy.bstack1l1l111l11l_opy_(self.bstack1l1l1111ll1_opy_.is_percy_auto_enabled)
        self.percy.bstack1l1l111l111_opy_(self.bstack1l1l1111ll1_opy_.percy_build_id)