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
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Any, Tuple
from browserstack_sdk.sdk_cli.bstack1llll11ll11_opy_ import bstack1lllll1l1l1_opy_
from browserstack_sdk.sdk_cli.utils.bstack1l111l11_opy_ import bstack1l11111l1l1_opy_
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1lll111l1l1_opy_,
    bstack1lll11l11ll_opy_,
    bstack1ll1l11l11l_opy_,
    bstack11lll1ll1l1_opy_,
    bstack1lll11l1lll_opy_,
)
import traceback
from bstack_utils.helper import bstack1l1ll111lll_opy_
from bstack_utils.bstack1llllll1l_opy_ import bstack1ll1l11ll1l_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.utils.bstack1lll11l1111_opy_ import bstack1ll1l1lll1l_opy_
from browserstack_sdk.sdk_cli.bstack1llllll1l11_opy_ import bstack1llllll111l_opy_
bstack1l1ll11l1l1_opy_ = bstack1l1ll111lll_opy_()
bstack1l1ll1111l1_opy_ = bstack11l111_opy_ (u"ࠤࡘࡴࡱࡵࡡࡥࡧࡧࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳ࠮ࠤᒋ")
bstack11llll1ll1l_opy_ = bstack11l111_opy_ (u"ࠥࡌࡴࡵ࡫ࡍࡧࡹࡩࡱࠨᒌ")
bstack11llll1l1ll_opy_ = bstack11l111_opy_ (u"ࠦࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠥᒍ")
bstack11llll11l11_opy_ = 1.0
_1l1l1lll1l1_opy_ = set()
class PytestBDDFramework(TestFramework):
    bstack11lllll1lll_opy_ = bstack11l111_opy_ (u"ࠧࡺࡥࡴࡶࡢࡪ࡮ࡾࡴࡶࡴࡨࡷࠧᒎ")
    bstack1l111111l11_opy_ = bstack11l111_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡵࡢࡷࡹࡧࡲࡵࡧࡧࠦᒏ")
    bstack1l1111ll1ll_opy_ = bstack11l111_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࡣ࡫࡯࡮ࡪࡵ࡫ࡩࡩࠨᒐ")
    bstack1l111l111ll_opy_ = bstack11l111_opy_ (u"ࠣࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡱࡧࡳࡵࡡࡶࡸࡦࡸࡴࡦࡦࠥᒑ")
    bstack11llllll11l_opy_ = bstack11l111_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡲࡡࡴࡶࡢࡪ࡮ࡴࡩࡴࡪࡨࡨࠧᒒ")
    bstack11llll1111l_opy_: bool
    bstack1llllll1l11_opy_: bstack1llllll111l_opy_  = None
    bstack1l111111ll1_opy_ = [
        bstack1lll111l1l1_opy_.BEFORE_ALL,
        bstack1lll111l1l1_opy_.AFTER_ALL,
        bstack1lll111l1l1_opy_.BEFORE_EACH,
        bstack1lll111l1l1_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack1l111l1l11l_opy_: Dict[str, str],
        bstack1ll11111l11_opy_: List[str]=[bstack11l111_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠢᒓ")],
        bstack1llllll1l11_opy_: bstack1llllll111l_opy_ = None,
        bstack1lll111llll_opy_=None
    ):
        super().__init__(bstack1ll11111l11_opy_, bstack1l111l1l11l_opy_, bstack1llllll1l11_opy_)
        self.bstack11llll1111l_opy_ = any(bstack11l111_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠣᒔ") in item.lower() for item in bstack1ll11111l11_opy_)
        self.bstack1lll111llll_opy_ = bstack1lll111llll_opy_
    def track_event(
        self,
        context: bstack11lll1ll1l1_opy_,
        test_framework_state: bstack1lll111l1l1_opy_,
        test_hook_state: bstack1ll1l11l11l_opy_,
        *args,
        **kwargs,
    ):
        super().track_event(self, context, test_framework_state, test_hook_state, *args, **kwargs)
        if test_framework_state == bstack1lll111l1l1_opy_.TEST or test_framework_state in PytestBDDFramework.bstack1l111111ll1_opy_:
            bstack1l11111l1l1_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1lll111l1l1_opy_.NONE:
            self.logger.warning(bstack11l111_opy_ (u"ࠧ࡯ࡧ࡯ࡱࡵࡩࡩࠦࡣࡢ࡮࡯ࡦࡦࡩ࡫ࠡࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿࠣࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࡂࠨᒕ") + str(test_hook_state) + bstack11l111_opy_ (u"ࠨࠢᒖ"))
            return
        if not self.bstack11llll1111l_opy_:
            self.logger.warning(bstack11l111_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡥࡷࡧࡱࡸ࠿ࠦࡵ࡯ࡵࡸࡴࡵࡵࡲࡵࡧࡧࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࠽ࠣᒗ") + str(str(self.bstack1ll11111l11_opy_)) + bstack11l111_opy_ (u"ࠣࠤᒘ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack11l111_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡷࡱࡩࡽࡶࡥࡤࡶࡨࡨࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᒙ") + str(kwargs) + bstack11l111_opy_ (u"ࠥࠦᒚ"))
            return
        instance = self.__11lll1lllll_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack11l111_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࡼࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࢀࠤࡦࡸࡧࡴ࠿ࠥᒛ") + str(args) + bstack11l111_opy_ (u"ࠧࠨᒜ"))
            return
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1l111111ll1_opy_ and test_hook_state == bstack1ll1l11l11l_opy_.PRE:
                bstack1l1llll11ll_opy_ = bstack1ll1l11ll1l_opy_.bstack1l1lllllll1_opy_(EVENTS.bstack11l1ll1ll1_opy_.value)
                name = str(EVENTS.bstack11l1ll1ll1_opy_.name)+bstack11l111_opy_ (u"ࠨ࠺ࠣᒝ")+str(test_framework_state.name)
                TestFramework.bstack11lll1llll1_opy_(instance, name, bstack1l1llll11ll_opy_)
        except Exception as e:
            self.logger.debug(bstack11l111_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡨࡰࡱ࡮ࠤࡪࡸࡲࡰࡴࠣࡴࡷ࡫࠺ࠡࡽࢀࠦᒞ").format(e))
        try:
            if test_framework_state == bstack1lll111l1l1_opy_.TEST:
                if not TestFramework.bstack1lllll1l111_opy_(instance, TestFramework.bstack1l1111l1lll_opy_) and test_hook_state == bstack1ll1l11l11l_opy_.PRE:
                    if not (len(args) >= 3):
                        return
                    test = PytestBDDFramework.__11llllll1ll_opy_(args)
                    if test:
                        instance.data.update(test)
                        self.logger.debug(bstack11l111_opy_ (u"ࠣ࡮ࡲࡥࡩ࡫ࡤࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿ࡮ࡴࡳࡵࡣࡱࡧࡪ࠴ࡲࡦࡨࠫ࠭ࢂࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࠣᒟ") + str(test_hook_state) + bstack11l111_opy_ (u"ࠤࠥᒠ"))
                if test_hook_state == bstack1ll1l11l11l_opy_.PRE and not TestFramework.bstack1lllll1l111_opy_(instance, TestFramework.bstack1l1l11l11l1_opy_):
                    TestFramework.bstack1llll1l1111_opy_(instance, TestFramework.bstack1l1l11l11l1_opy_, datetime.now(tz=timezone.utc))
                    PytestBDDFramework.__11lllllll11_opy_(instance, args)
                    self.logger.debug(bstack11l111_opy_ (u"ࠥࡷࡪࡺࠠࡵࡧࡶࡸ࠲ࡹࡴࡢࡴࡷࠤ࡫ࡵࡲࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿ࡮ࡴࡳࡵࡣࡱࡧࡪ࠴ࡲࡦࡨࠫ࠭ࢂࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࠣᒡ") + str(test_hook_state) + bstack11l111_opy_ (u"ࠦࠧᒢ"))
                elif test_hook_state == bstack1ll1l11l11l_opy_.POST and not TestFramework.bstack1lllll1l111_opy_(instance, TestFramework.bstack1l1l1ll1111_opy_):
                    TestFramework.bstack1llll1l1111_opy_(instance, TestFramework.bstack1l1l1ll1111_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack11l111_opy_ (u"ࠧࡹࡥࡵࠢࡷࡩࡸࡺ࠭ࡦࡰࡧࠤ࡫ࡵࡲࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿ࡮ࡴࡳࡵࡣࡱࡧࡪ࠴ࡲࡦࡨࠫ࠭ࢂࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࠣᒣ") + str(test_hook_state) + bstack11l111_opy_ (u"ࠨࠢᒤ"))
            elif test_framework_state == bstack1lll111l1l1_opy_.STEP:
                if test_hook_state == bstack1ll1l11l11l_opy_.PRE:
                    PytestBDDFramework.__1l111l1l1l1_opy_(instance, args)
                elif test_hook_state == bstack1ll1l11l11l_opy_.POST:
                    PytestBDDFramework.__1l111l11111_opy_(instance, args)
            elif test_framework_state == bstack1lll111l1l1_opy_.LOG and test_hook_state == bstack1ll1l11l11l_opy_.POST:
                PytestBDDFramework.__1l11111l1ll_opy_(instance, *args)
            elif test_framework_state == bstack1lll111l1l1_opy_.LOG_REPORT and test_hook_state == bstack1ll1l11l11l_opy_.POST:
                self.__1l11111l11l_opy_(instance, *args)
                self.__1l1111l11ll_opy_(instance)
            elif test_framework_state in PytestBDDFramework.bstack1l111111ll1_opy_:
                self.__1l1111l1l1l_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack11l111_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡥࡷࡧࡱࡸ࠿ࠦࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣᒥ") + str(instance.ref()) + bstack11l111_opy_ (u"ࠣࠤᒦ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack11llll11lll_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1l111111ll1_opy_ and test_hook_state == bstack1ll1l11l11l_opy_.POST:
                name = str(EVENTS.bstack11l1ll1ll1_opy_.name)+bstack11l111_opy_ (u"ࠤ࠽ࠦᒧ")+str(test_framework_state.name)
                bstack1l1llll11ll_opy_ = TestFramework.bstack1l1111lllll_opy_(instance, name)
                bstack1ll1l11ll1l_opy_.end(EVENTS.bstack11l1ll1ll1_opy_.value, bstack1l1llll11ll_opy_+bstack11l111_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥᒨ"), bstack1l1llll11ll_opy_+bstack11l111_opy_ (u"ࠦ࠿࡫࡮ࡥࠤᒩ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack11l111_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡭ࡵ࡯࡬ࠢࡨࡶࡷࡵࡲ࠻ࠢࡾࢁࠧᒪ").format(e))
    def bstack1l1ll1l111l_opy_(self):
        return self.bstack11llll1111l_opy_
    def __11lllllllll_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack11l111_opy_ (u"ࠨࡧࡦࡶࡢࡶࡪࡹࡵ࡭ࡶࠥᒫ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1l1l11l1l1l_opy_(rep, [bstack11l111_opy_ (u"ࠢࡸࡪࡨࡲࠧᒬ"), bstack11l111_opy_ (u"ࠣࡱࡸࡸࡨࡵ࡭ࡦࠤᒭ"), bstack11l111_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤᒮ"), bstack11l111_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥᒯ"), bstack11l111_opy_ (u"ࠦࡸࡱࡩࡱࡲࡨࡨࠧᒰ"), bstack11l111_opy_ (u"ࠧࡲ࡯࡯ࡩࡵࡩࡵࡸࡴࡦࡺࡷࠦᒱ")])
        return None
    def __1l11111l11l_opy_(self, instance: bstack1lll11l11ll_opy_, *args):
        result = self.__11lllllllll_opy_(*args)
        if not result:
            return
        failure = None
        bstack1llllll1lll_opy_ = None
        if result.get(bstack11l111_opy_ (u"ࠨ࡯ࡶࡶࡦࡳࡲ࡫ࠢᒲ"), None) == bstack11l111_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢᒳ") and len(args) > 1 and getattr(args[1], bstack11l111_opy_ (u"ࠣࡧࡻࡧ࡮ࡴࡦࡰࠤᒴ"), None) is not None:
            failure = [{bstack11l111_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬᒵ"): [args[1].excinfo.exconly(), result.get(bstack11l111_opy_ (u"ࠥࡰࡴࡴࡧࡳࡧࡳࡶࡹ࡫ࡸࡵࠤᒶ"), None)]}]
            bstack1llllll1lll_opy_ = bstack11l111_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࡅࡳࡴࡲࡶࠧᒷ") if bstack11l111_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࠣᒸ") in getattr(args[1].excinfo, bstack11l111_opy_ (u"ࠨࡴࡺࡲࡨࡲࡦࡳࡥࠣᒹ"), bstack11l111_opy_ (u"ࠢࠣᒺ")) else bstack11l111_opy_ (u"ࠣࡗࡱ࡬ࡦࡴࡤ࡭ࡧࡧࡉࡷࡸ࡯ࡳࠤᒻ")
        bstack1l11111lll1_opy_ = result.get(bstack11l111_opy_ (u"ࠤࡲࡹࡹࡩ࡯࡮ࡧࠥᒼ"), TestFramework.bstack11lll1lll1l_opy_)
        if bstack1l11111lll1_opy_ != TestFramework.bstack11lll1lll1l_opy_:
            TestFramework.bstack1llll1l1111_opy_(instance, TestFramework.bstack1l1ll111111_opy_, datetime.now(tz=timezone.utc))
        TestFramework.bstack1l111111lll_opy_(instance, {
            TestFramework.bstack1l11ll11l1l_opy_: failure,
            TestFramework.bstack1l111l1111l_opy_: bstack1llllll1lll_opy_,
            TestFramework.bstack1l11ll11l11_opy_: bstack1l11111lll1_opy_,
        })
    def __11lll1lllll_opy_(
        self,
        context: bstack11lll1ll1l1_opy_,
        test_framework_state: bstack1lll111l1l1_opy_,
        test_hook_state: bstack1ll1l11l11l_opy_,
        *args,
        **kwargs,
    ):
        instance = None
        if test_framework_state == bstack1lll111l1l1_opy_.SETUP_FIXTURE:
            instance = self.__11llll111l1_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        else:
            target = None # bstack1l111111l1l_opy_ bstack11llllll1l1_opy_ this to be bstack11l111_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥᒽ")
            if test_framework_state == bstack1lll111l1l1_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__1l111l11l11_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1lll111l1l1_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack11l111_opy_ (u"ࠦࡳࡵࡤࡦࠤᒾ"), None), bstack11l111_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᒿ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack11l111_opy_ (u"ࠨ࡮ࡰࡦࡨࠦᓀ"), None):
                target = args[0].node.nodeid
            elif getattr(args[0], bstack11l111_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢᓁ"), None):
                target = args[0].nodeid
            instance = TestFramework.bstack1llll11l1ll_opy_(target) if target else None
        return instance
    def __1l1111l1l1l_opy_(
        self,
        instance: bstack1lll11l11ll_opy_,
        test_framework_state: bstack1lll111l1l1_opy_,
        test_hook_state: bstack1ll1l11l11l_opy_,
        *args,
    ):
        key = test_framework_state.name
        bstack1l11111llll_opy_ = TestFramework.bstack1llll1ll11l_opy_(instance, PytestBDDFramework.bstack1l111111l11_opy_, {})
        if not key in bstack1l11111llll_opy_:
            bstack1l11111llll_opy_[key] = []
        bstack1l111l1l1ll_opy_ = TestFramework.bstack1llll1ll11l_opy_(instance, PytestBDDFramework.bstack1l1111ll1ll_opy_, {})
        if not key in bstack1l111l1l1ll_opy_:
            bstack1l111l1l1ll_opy_[key] = []
        bstack11lllll111l_opy_ = {
            PytestBDDFramework.bstack1l111111l11_opy_: bstack1l11111llll_opy_,
            PytestBDDFramework.bstack1l1111ll1ll_opy_: bstack1l111l1l1ll_opy_,
        }
        if test_hook_state == bstack1ll1l11l11l_opy_.PRE:
            hook_name = args[1] if len(args) > 1 else None
            hook = {
                bstack11l111_opy_ (u"ࠣ࡭ࡨࡽࠧᓂ"): key,
                TestFramework.bstack1l11111l111_opy_: uuid4().__str__(),
                TestFramework.bstack11lllll1ll1_opy_: TestFramework.bstack11lllll1l11_opy_,
                TestFramework.bstack1l1111ll111_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack11lll1ll1ll_opy_: [],
                TestFramework.bstack1l11111ll1l_opy_: hook_name,
                TestFramework.bstack11llll11111_opy_: bstack1ll1l1lll1l_opy_.bstack11lll1lll11_opy_()
            }
            bstack1l11111llll_opy_[key].append(hook)
            bstack11lllll111l_opy_[PytestBDDFramework.bstack1l111l111ll_opy_] = key
        elif test_hook_state == bstack1ll1l11l11l_opy_.POST:
            bstack1l1111l1ll1_opy_ = bstack1l11111llll_opy_.get(key, [])
            hook = bstack1l1111l1ll1_opy_.pop() if bstack1l1111l1ll1_opy_ else None
            if hook:
                result = self.__11lllllllll_opy_(*args)
                if result:
                    bstack1l1111l11l1_opy_ = result.get(bstack11l111_opy_ (u"ࠤࡲࡹࡹࡩ࡯࡮ࡧࠥᓃ"), TestFramework.bstack11lllll1l11_opy_)
                    if bstack1l1111l11l1_opy_ != TestFramework.bstack11lllll1l11_opy_:
                        hook[TestFramework.bstack11lllll1ll1_opy_] = bstack1l1111l11l1_opy_
                hook[TestFramework.bstack1l1111lll11_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack11llll11111_opy_] = bstack1ll1l1lll1l_opy_.bstack11lll1lll11_opy_()
                self.bstack11llll1ll11_opy_(hook)
                logs = hook.get(TestFramework.bstack1l11111111l_opy_, [])
                self.bstack1l1l11lll1l_opy_(instance, logs)
                bstack1l111l1l1ll_opy_[key].append(hook)
                bstack11lllll111l_opy_[PytestBDDFramework.bstack11llllll11l_opy_] = key
        TestFramework.bstack1l111111lll_opy_(instance, bstack11lllll111l_opy_)
        self.logger.debug(bstack11l111_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡ࡫ࡳࡴࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦ࠿ࡾ࡯ࡪࡿࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥ࡮࡯ࡰ࡭ࡶࡣࡸࡺࡡࡳࡶࡨࡨࡂࢁࡨࡰࡱ࡮ࡷࡤࡹࡴࡢࡴࡷࡩࡩࢃࠠࡩࡱࡲ࡯ࡸࡥࡦࡪࡰ࡬ࡷ࡭࡫ࡤ࠾ࠤᓄ") + str(bstack1l111l1l1ll_opy_) + bstack11l111_opy_ (u"ࠦࠧᓅ"))
    def __11llll111l1_opy_(
        self,
        context: bstack11lll1ll1l1_opy_,
        test_framework_state: bstack1lll111l1l1_opy_,
        test_hook_state: bstack1ll1l11l11l_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1l1l11l1l1l_opy_(args[0], [bstack11l111_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᓆ"), bstack11l111_opy_ (u"ࠨࡡࡳࡩࡱࡥࡲ࡫ࠢᓇ"), bstack11l111_opy_ (u"ࠢࡱࡣࡵࡥࡲࡹࠢᓈ"), bstack11l111_opy_ (u"ࠣ࡫ࡧࡷࠧᓉ"), bstack11l111_opy_ (u"ࠤࡸࡲ࡮ࡺࡴࡦࡵࡷࠦᓊ"), bstack11l111_opy_ (u"ࠥࡦࡦࡹࡥࡪࡦࠥᓋ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scenario = args[2] if len(args) == 3 else None
        scope = request.scope if hasattr(request, bstack11l111_opy_ (u"ࠦࡸࡩ࡯ࡱࡧࠥᓌ")) else fixturedef.get(bstack11l111_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᓍ"), None)
        fixturename = request.fixturename if hasattr(request, bstack11l111_opy_ (u"ࠨࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࠦᓎ")) else None
        node = request.node if hasattr(request, bstack11l111_opy_ (u"ࠢ࡯ࡱࡧࡩࠧᓏ")) else None
        target = request.node.nodeid if hasattr(node, bstack11l111_opy_ (u"ࠣࡰࡲࡨࡪ࡯ࡤࠣᓐ")) else None
        baseid = fixturedef.get(bstack11l111_opy_ (u"ࠤࡥࡥࡸ࡫ࡩࡥࠤᓑ"), None) or bstack11l111_opy_ (u"ࠥࠦᓒ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack11l111_opy_ (u"ࠦࡤࡶࡹࡧࡷࡱࡧ࡮ࡺࡥ࡮ࠤᓓ")):
            target = PytestBDDFramework.__11llllllll1_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack11l111_opy_ (u"ࠧࡲ࡯ࡤࡣࡷ࡭ࡴࡴࠢᓔ")) else None
            if target and not TestFramework.bstack1llll11l1ll_opy_(target):
                self.__1l111l11l11_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack11l111_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡬ࡩࡹࡶࡸࡶࡪࡥࡥࡷࡧࡱࡸ࠿ࠦࡦࡢ࡮࡯ࡦࡦࡩ࡫ࠡࡶࡤࡶ࡬࡫ࡴ࠾ࡽࡷࡥࡷ࡭ࡥࡵࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥ࠾ࡽࡩ࡭ࡽࡺࡵࡳࡧࡱࡥࡲ࡫ࡽࠡࡰࡲࡨࡪࡃࡻ࡯ࡱࡧࡩࢂࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࠣᓕ") + str(test_hook_state) + bstack11l111_opy_ (u"ࠢࠣᓖ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack11l111_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠࡧࡹࡩࡳࡺ࠺ࠡࡷࡱ࡬ࡦࡴࡤ࡭ࡧࡧࠤࡪࡼࡥ࡯ࡶࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁ࠳ࢁࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥࡾࠢࡩ࡭ࡽࡺࡵࡳࡧࡧࡩ࡫ࡃࡻࡧ࡫ࡻࡸࡺࡸࡥࡥࡧࡩࢁࠥࡹࡣࡰࡲࡨࡁࢀࡹࡣࡰࡲࡨࢁࠥࡺࡡࡳࡩࡨࡸࡂࠨᓗ") + str(target) + bstack11l111_opy_ (u"ࠤࠥᓘ"))
            return None
        instance = TestFramework.bstack1llll11l1ll_opy_(target)
        if not instance:
            self.logger.warning(bstack11l111_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡩ࡭ࡽࡺࡵࡳࡧࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࡼࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡶࡧࡴࡶࡥ࠾ࡽࡶࡧࡴࡶࡥࡾࠢࡥࡥࡸ࡫ࡩࡥ࠿ࡾࡦࡦࡹࡥࡪࡦࢀࠤࡹࡧࡲࡨࡧࡷࡁࠧᓙ") + str(target) + bstack11l111_opy_ (u"ࠦࠧᓚ"))
            return None
        bstack11llll11l1l_opy_ = TestFramework.bstack1llll1ll11l_opy_(instance, PytestBDDFramework.bstack11lllll1lll_opy_, {})
        if os.getenv(bstack11l111_opy_ (u"࡙ࠧࡄࡌࡡࡆࡐࡎࡥࡆࡍࡃࡊࡣࡋࡏࡘࡕࡗࡕࡉࡘࠨᓛ"), bstack11l111_opy_ (u"ࠨ࠱ࠣᓜ")) == bstack11l111_opy_ (u"ࠢ࠲ࠤᓝ"):
            bstack11llllll111_opy_ = bstack11l111_opy_ (u"ࠣ࠼ࠥᓞ").join((scope, fixturename))
            bstack1l111l1l111_opy_ = datetime.now(tz=timezone.utc)
            bstack1l1111l111l_opy_ = {
                bstack11l111_opy_ (u"ࠤ࡮ࡩࡾࠨᓟ"): bstack11llllll111_opy_,
                bstack11l111_opy_ (u"ࠥࡸࡦ࡭ࡳࠣᓠ"): PytestBDDFramework.__11lllll11l1_opy_(request.node, scenario),
                bstack11l111_opy_ (u"ࠦ࡫࡯ࡸࡵࡷࡵࡩࠧᓡ"): fixturedef,
                bstack11l111_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᓢ"): scope,
                bstack11l111_opy_ (u"ࠨࡴࡺࡲࡨࠦᓣ"): None,
            }
            try:
                if test_hook_state == bstack1ll1l11l11l_opy_.POST and callable(getattr(args[-1], bstack11l111_opy_ (u"ࠢࡨࡧࡷࡣࡷ࡫ࡳࡶ࡮ࡷࠦᓤ"), None)):
                    bstack1l1111l111l_opy_[bstack11l111_opy_ (u"ࠣࡶࡼࡴࡪࠨᓥ")] = TestFramework.bstack1l1l11l11ll_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1ll1l11l11l_opy_.PRE:
                bstack1l1111l111l_opy_[bstack11l111_opy_ (u"ࠤࡸࡹ࡮ࡪࠢᓦ")] = uuid4().__str__()
                bstack1l1111l111l_opy_[PytestBDDFramework.bstack1l1111ll111_opy_] = bstack1l111l1l111_opy_
            elif test_hook_state == bstack1ll1l11l11l_opy_.POST:
                bstack1l1111l111l_opy_[PytestBDDFramework.bstack1l1111lll11_opy_] = bstack1l111l1l111_opy_
            if bstack11llllll111_opy_ in bstack11llll11l1l_opy_:
                bstack11llll11l1l_opy_[bstack11llllll111_opy_].update(bstack1l1111l111l_opy_)
                self.logger.debug(bstack11l111_opy_ (u"ࠥࡹࡵࡪࡡࡵࡧࡧࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡶࡧࡴࡶࡥ࠾ࡽࡶࡧࡴࡶࡥࡾࠢࡩ࡭ࡽࡺࡵࡳࡧࡀࠦᓧ") + str(bstack11llll11l1l_opy_[bstack11llllll111_opy_]) + bstack11l111_opy_ (u"ࠦࠧᓨ"))
            else:
                bstack11llll11l1l_opy_[bstack11llllll111_opy_] = bstack1l1111l111l_opy_
                self.logger.debug(bstack11l111_opy_ (u"ࠧࡹࡡࡷࡧࡧࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡶࡧࡴࡶࡥ࠾ࡽࡶࡧࡴࡶࡥࡾࠢࡩ࡭ࡽࡺࡵࡳࡧࡀࡿࡹ࡫ࡳࡵࡡࡩ࡭ࡽࡺࡵࡳࡧࢀࠤࡹࡸࡡࡤ࡭ࡨࡨࡤ࡬ࡩࡹࡶࡸࡶࡪࡹ࠽ࠣᓩ") + str(len(bstack11llll11l1l_opy_)) + bstack11l111_opy_ (u"ࠨࠢᓪ"))
        TestFramework.bstack1llll1l1111_opy_(instance, PytestBDDFramework.bstack11lllll1lll_opy_, bstack11llll11l1l_opy_)
        self.logger.debug(bstack11l111_opy_ (u"ࠢࡴࡣࡹࡩࡩࠦࡦࡪࡺࡷࡹࡷ࡫ࡳ࠾ࡽ࡯ࡩࡳ࠮ࡴࡳࡣࡦ࡯ࡪࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴࠫࢀࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡃࠢᓫ") + str(instance.ref()) + bstack11l111_opy_ (u"ࠣࠤᓬ"))
        return instance
    def __1l111l11l11_opy_(
        self,
        context: bstack11lll1ll1l1_opy_,
        test_framework_state: bstack1lll111l1l1_opy_,
        target: Any,
        *args,
    ):
        ctx = bstack1lllll1l1l1_opy_.create_context(target)
        ob = bstack1lll11l11ll_opy_(ctx, self.bstack1ll11111l11_opy_, self.bstack1l111l1l11l_opy_, test_framework_state)
        TestFramework.bstack1l111111lll_opy_(ob, {
            TestFramework.bstack1l1lllll1l1_opy_: context.test_framework_name,
            TestFramework.bstack1l1l11ll1ll_opy_: context.test_framework_version,
            TestFramework.bstack1l1111lll1l_opy_: [],
            PytestBDDFramework.bstack11lllll1lll_opy_: {},
            PytestBDDFramework.bstack1l1111ll1ll_opy_: {},
            PytestBDDFramework.bstack1l111111l11_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1llll1l1111_opy_(ob, TestFramework.bstack1l11111ll11_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1llll1l1111_opy_(ob, TestFramework.bstack1ll111l1l1l_opy_, context.platform_index)
        TestFramework.bstack1lllll1ll1l_opy_[ctx.id] = ob
        self.logger.debug(bstack11l111_opy_ (u"ࠤࡶࡥࡻ࡫ࡤࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࠣࡧࡹࡾ࠮ࡪࡦࡀࡿࡨࡺࡸ࠯࡫ࡧࢁࠥࡺࡡࡳࡩࡨࡸࡂࢁࡴࡢࡴࡪࡩࡹࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫ࡳ࠾ࠤᓭ") + str(TestFramework.bstack1lllll1ll1l_opy_.keys()) + bstack11l111_opy_ (u"ࠥࠦᓮ"))
        return ob
    @staticmethod
    def __11lllllll11_opy_(instance, args):
        request, feature, scenario = args
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack11l111_opy_ (u"ࠫ࡮ࡪࠧᓯ"): id(step),
                bstack11l111_opy_ (u"ࠬࡺࡥࡹࡶࠪᓰ"): step.name,
                bstack11l111_opy_ (u"࠭࡫ࡦࡻࡺࡳࡷࡪࠧᓱ"): step.keyword,
            })
        meta = {
            bstack11l111_opy_ (u"ࠧࡧࡧࡤࡸࡺࡸࡥࠨᓲ"): {
                bstack11l111_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᓳ"): feature.name,
                bstack11l111_opy_ (u"ࠩࡳࡥࡹ࡮ࠧᓴ"): feature.filename,
                bstack11l111_opy_ (u"ࠪࡨࡪࡹࡣࡳ࡫ࡳࡸ࡮ࡵ࡮ࠨᓵ"): feature.description
            },
            bstack11l111_opy_ (u"ࠫࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭ᓶ"): {
                bstack11l111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᓷ"): scenario.name
            },
            bstack11l111_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬᓸ"): steps,
            bstack11l111_opy_ (u"ࠧࡦࡺࡤࡱࡵࡲࡥࡴࠩᓹ"): PytestBDDFramework.__11lllll11ll_opy_(request.node)
        }
        instance.data.update(
            {
                TestFramework.bstack1l1111l1l11_opy_: meta
            }
        )
    def bstack11llll1ll11_opy_(self, hook: Dict[str, Any]) -> None:
        bstack11l111_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡖࡲࡰࡥࡨࡷࡸ࡫ࡳࠡࡶ࡫ࡩࠥࡎ࡯ࡰ࡭ࡏࡩࡻ࡫࡬ࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦࡳࡪ࡯࡬ࡰࡦࡸࠠࡵࡱࠣࡸ࡭࡫ࠠࡋࡣࡹࡥࠥ࡯࡭ࡱ࡮ࡨࡱࡪࡴࡴࡢࡶ࡬ࡳࡳ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡖ࡫࡭ࡸࠦ࡭ࡦࡶ࡫ࡳࡩࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡉࡨࡦࡥ࡮ࡷࠥࡺࡨࡦࠢࡋࡳࡴࡱࡌࡦࡸࡨࡰࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹࠡ࡫ࡱࡷ࡮ࡪࡥࠡࢀ࠲࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠲࡙ࡵࡲ࡯ࡢࡦࡨࡨࡆࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡈࡲࡶࠥ࡫ࡡࡤࡪࠣࡪ࡮ࡲࡥࠡ࡫ࡱࠤ࡭ࡵ࡯࡬ࡡ࡯ࡩࡻ࡫࡬ࡠࡨ࡬ࡰࡪࡹࠬࠡࡴࡨࡴࡱࡧࡣࡦࡵ࡙ࠣࠦ࡫ࡳࡵࡎࡨࡺࡪࡲࠢࠡࡹ࡬ࡸ࡭ࠦࠢࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮ࠥࠤ࡮ࡴࠠࡪࡶࡶࠤࡵࡧࡴࡩ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡋࡩࠤࡦࠦࡦࡪ࡮ࡨࠤ࡮ࡴࠠࡵࡪࡨࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿࠠ࡮ࡣࡷࡧ࡭࡫ࡳࠡࡣࠣࡱࡴࡪࡩࡧ࡫ࡨࡨࠥ࡮࡯ࡰ࡭࠰ࡰࡪࡼࡥ࡭ࠢࡩ࡭ࡱ࡫ࠬࠡ࡫ࡷࠤࡨࡸࡥࡢࡶࡨࡷࠥࡧࠠࡍࡱࡪࡉࡳࡺࡲࡺࠢࡲࡦ࡯࡫ࡣࡵࠢࡺ࡭ࡹ࡮ࠠࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠤࡩ࡫ࡴࡢ࡫࡯ࡷ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡘ࡯࡭ࡪ࡮ࡤࡶࡱࡿࠬࠡ࡫ࡷࠤࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠠࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢ࡯ࡳࡨࡧࡴࡦࡦࠣ࡭ࡳࠦࡈࡰࡱ࡮ࡐࡪࡼࡥ࡭࠱ࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࡎ࡯ࡰ࡭ࡈࡺࡪࡴࡴࠡࡤࡼࠤࡷ࡫ࡰ࡭ࡣࡦ࡭ࡳ࡭ࠠࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠧࠦࡷࡪࡶ࡫ࠤࠧࡎ࡯ࡰ࡭ࡏࡩࡻ࡫࡬࠰ࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࡍࡵ࡯࡬ࡇࡹࡩࡳࡺࠢ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡕࡪࡨࠤࡨࡸࡥࡢࡶࡨࡨࠥࡒ࡯ࡨࡇࡱࡸࡷࡿࠠࡰࡤ࡭ࡩࡨࡺࡳࠡࡣࡵࡩࠥࡧࡤࡥࡧࡧࠤࡹࡵࠠࡵࡪࡨࠤ࡭ࡵ࡯࡬ࠩࡶࠤࠧࡲ࡯ࡨࡵࠥࠤࡱ࡯ࡳࡵ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡆࡸࡧࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡪࡲࡳࡰࡀࠠࡕࡪࡨࠤࡪࡼࡥ࡯ࡶࠣࡨ࡮ࡩࡴࡪࡱࡱࡥࡷࡿࠠࡤࡱࡱࡸࡦ࡯࡮ࡪࡰࡪࠤࡪࡾࡩࡴࡶ࡬ࡲ࡬ࠦ࡬ࡰࡩࡶࠤࡦࡴࡤࠡࡪࡲࡳࡰࠦࡩ࡯ࡨࡲࡶࡲࡧࡴࡪࡱࡱ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࡬ࡴࡵ࡫ࡠ࡮ࡨࡺࡪࡲ࡟ࡧ࡫࡯ࡩࡸࡀࠠࡍ࡫ࡶࡸࠥࡵࡦࠡࡒࡤࡸ࡭ࠦ࡯ࡣ࡬ࡨࡧࡹࡹࠠࡧࡴࡲࡱࠥࡺࡨࡦࠢࡗࡩࡸࡺࡌࡦࡸࡨࡰࠥࡳ࡯࡯࡫ࡷࡳࡷ࡯࡮ࡨ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡤࡸ࡭ࡱࡪ࡟࡭ࡧࡹࡩࡱࡥࡦࡪ࡮ࡨࡷ࠿ࠦࡌࡪࡵࡷࠤࡴ࡬ࠠࡑࡣࡷ࡬ࠥࡵࡢ࡫ࡧࡦࡸࡸࠦࡦࡳࡱࡰࠤࡹ࡮ࡥࠡࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠥࡳ࡯࡯࡫ࡷࡳࡷ࡯࡮ࡨ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢᓺ")
        global _1l1l1lll1l1_opy_
        platform_index = os.environ[bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩᓻ")]
        bstack1l1l1ll1ll1_opy_ = os.path.join(bstack1l1ll11l1l1_opy_, (bstack1l1ll1111l1_opy_ + str(platform_index)), bstack11llll1ll1l_opy_)
        if not os.path.exists(bstack1l1l1ll1ll1_opy_) or not os.path.isdir(bstack1l1l1ll1ll1_opy_):
            return
        logs = hook.get(bstack11l111_opy_ (u"ࠥࡰࡴ࡭ࡳࠣᓼ"), [])
        with os.scandir(bstack1l1l1ll1ll1_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1l1l1lll1l1_opy_:
                    self.logger.info(bstack11l111_opy_ (u"ࠦࡕࡧࡴࡩࠢࡤࡰࡷ࡫ࡡࡥࡻࠣࡴࡷࡵࡣࡦࡵࡶࡩࡩࠦࡻࡾࠤᓽ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack11l111_opy_ (u"ࠧࠨᓾ")
                    log_entry = bstack1lll11l1lll_opy_(
                        kind=bstack11l111_opy_ (u"ࠨࡔࡆࡕࡗࡣࡆ࡚ࡔࡂࡅࡋࡑࡊࡔࡔࠣᓿ"),
                        message=bstack11l111_opy_ (u"ࠢࠣᔀ"),
                        level=bstack11l111_opy_ (u"ࠣࠤᔁ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1l1l1l111ll_opy_=entry.stat().st_size,
                        bstack1l1l1lll1ll_opy_=bstack11l111_opy_ (u"ࠤࡐࡅࡓ࡛ࡁࡍࡡࡘࡔࡑࡕࡁࡅࠤᔂ"),
                        bstack111111l_opy_=os.path.abspath(entry.path),
                        bstack1l1111ll11l_opy_=hook.get(TestFramework.bstack1l11111l111_opy_)
                    )
                    logs.append(log_entry)
                    _1l1l1lll1l1_opy_.add(abs_path)
        platform_index = os.environ[bstack11l111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪᔃ")]
        bstack11llll1l1l1_opy_ = os.path.join(bstack1l1ll11l1l1_opy_, (bstack1l1ll1111l1_opy_ + str(platform_index)), bstack11llll1ll1l_opy_, bstack11llll1l1ll_opy_)
        if not os.path.exists(bstack11llll1l1l1_opy_) or not os.path.isdir(bstack11llll1l1l1_opy_):
            self.logger.info(bstack11l111_opy_ (u"ࠦࡓࡵࠠࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࡌࡴࡵ࡫ࡆࡸࡨࡲࡹࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿࠠࡧࡱࡸࡲࡩࠦࡡࡵ࠼ࠣࡿࢂࠨᔄ").format(bstack11llll1l1l1_opy_))
        else:
            self.logger.info(bstack11l111_opy_ (u"ࠧࡖࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࡎ࡯ࡰ࡭ࡈࡺࡪࡴࡴࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦࡦࡳࡱࡰࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿ࠺ࠡࡽࢀࠦᔅ").format(bstack11llll1l1l1_opy_))
            with os.scandir(bstack11llll1l1l1_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1l1l1lll1l1_opy_:
                        self.logger.info(bstack11l111_opy_ (u"ࠨࡐࡢࡶ࡫ࠤࡦࡲࡲࡦࡣࡧࡽࠥࡶࡲࡰࡥࡨࡷࡸ࡫ࡤࠡࡽࢀࠦᔆ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack11l111_opy_ (u"ࠢࠣᔇ")
                        log_entry = bstack1lll11l1lll_opy_(
                            kind=bstack11l111_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡁࡕࡖࡄࡇࡍࡓࡅࡏࡖࠥᔈ"),
                            message=bstack11l111_opy_ (u"ࠤࠥᔉ"),
                            level=bstack11l111_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢᔊ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1l1l1l111ll_opy_=entry.stat().st_size,
                            bstack1l1l1lll1ll_opy_=bstack11l111_opy_ (u"ࠦࡒࡇࡎࡖࡃࡏࡣ࡚ࡖࡌࡐࡃࡇࠦᔋ"),
                            bstack111111l_opy_=os.path.abspath(entry.path),
                            bstack1l1l1ll11l1_opy_=hook.get(TestFramework.bstack1l11111l111_opy_)
                        )
                        logs.append(log_entry)
                        _1l1l1lll1l1_opy_.add(abs_path)
        hook[bstack11l111_opy_ (u"ࠧࡲ࡯ࡨࡵࠥᔌ")] = logs
    def bstack1l1l11lll1l_opy_(
        self,
        bstack1l1l1lllll1_opy_: bstack1lll11l11ll_opy_,
        entries: List[bstack1lll11l1lll_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack11l111_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡉࡌࡊࡡࡅࡍࡓࡥࡓࡆࡕࡖࡍࡔࡔ࡟ࡊࡆࠥᔍ"))
        req.platform_index = TestFramework.bstack1llll1ll11l_opy_(bstack1l1l1lllll1_opy_, TestFramework.bstack1ll111l1l1l_opy_)
        req.execution_context.hash = str(bstack1l1l1lllll1_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1l1lllll1_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1l1lllll1_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll1ll11l_opy_(bstack1l1l1lllll1_opy_, TestFramework.bstack1l1lllll1l1_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll1ll11l_opy_(bstack1l1l1lllll1_opy_, TestFramework.bstack1l1l11ll1ll_opy_)
            log_entry.uuid = entry.bstack1l1111ll11l_opy_ if entry.bstack1l1111ll11l_opy_ else TestFramework.bstack1llll1ll11l_opy_(bstack1l1l1lllll1_opy_, TestFramework.bstack1ll1111l1ll_opy_)
            log_entry.test_framework_state = bstack1l1l1lllll1_opy_.state.name
            log_entry.message = entry.message.encode(bstack11l111_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨᔎ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack11l111_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡁࡕࡖࡄࡇࡍࡓࡅࡏࡖࠥᔏ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1l1l111ll_opy_
                log_entry.file_path = entry.bstack111111l_opy_
        def bstack1l1ll11ll1l_opy_():
            bstack11l1l11l1l_opy_ = datetime.now()
            try:
                self.bstack1lll111llll_opy_.LogCreatedEvent(req)
                bstack1l1l1lllll1_opy_.bstack1l11lllll_opy_(bstack11l111_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡧࡱࡨࡤࡲ࡯ࡨࡡࡦࡶࡪࡧࡴࡦࡦࡢࡩࡻ࡫࡮ࡵࡡࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠨᔐ"), datetime.now() - bstack11l1l11l1l_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack11l111_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࡴࡧࡱࡨࡤࡲ࡯ࡨࡡࡦࡶࡪࡧࡴࡦࡦࡢࡩࡻ࡫࡮ࡵࡡࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠦࡻࡾࠤᔑ").format(str(e)))
                traceback.print_exc()
        self.bstack1llllll1l11_opy_.enqueue(bstack1l1ll11ll1l_opy_)
    def __1l1111l11ll_opy_(self, instance) -> None:
        bstack11l111_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡎࡲࡥࡩࡹࠠࡤࡷࡶࡸࡴࡳࠠࡵࡣࡪࡷࠥ࡬࡯ࡳࠢࡷ࡬ࡪࠦࡧࡪࡸࡨࡲࠥࡺࡥࡴࡶࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡇࡷ࡫ࡡࡵࡧࡶࠤࡦࠦࡤࡪࡥࡷࠤࡨࡵ࡮ࡵࡣ࡬ࡲ࡮ࡴࡧࠡࡶࡨࡷࡹࠦ࡬ࡦࡸࡨࡰࠥࡩࡵࡴࡶࡲࡱࠥࡳࡥࡵࡣࡧࡥࡹࡧࠠࡳࡧࡷࡶ࡮࡫ࡶࡦࡦࠣࡪࡷࡵ࡭ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡆࡹࡸࡺ࡯࡮ࡖࡤ࡫ࡒࡧ࡮ࡢࡩࡨࡶࠥࡧ࡮ࡥࠢࡸࡴࡩࡧࡴࡦࡵࠣࡸ࡭࡫ࠠࡪࡰࡶࡸࡦࡴࡣࡦࠢࡶࡸࡦࡺࡥࠡࡷࡶ࡭ࡳ࡭ࠠࡴࡧࡷࡣࡸࡺࡡࡵࡧࡢࡩࡳࡺࡲࡪࡧࡶ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤᔒ")
        bstack11lllll111l_opy_ = {bstack11l111_opy_ (u"ࠧࡩࡵࡴࡶࡲࡱࡤࡳࡥࡵࡣࡧࡥࡹࡧࠢᔓ"): bstack1ll1l1lll1l_opy_.bstack11lll1lll11_opy_()}
        TestFramework.bstack1l111111lll_opy_(instance, bstack11lllll111l_opy_)
    @staticmethod
    def __1l111l1l1l1_opy_(instance, args):
        request, bstack11lllll1l1l_opy_ = args
        bstack11lllllll1l_opy_ = id(bstack11lllll1l1l_opy_)
        bstack1l111111111_opy_ = instance.data[TestFramework.bstack1l1111l1l11_opy_]
        step = next(filter(lambda st: st[bstack11l111_opy_ (u"࠭ࡩࡥࠩᔔ")] == bstack11lllllll1l_opy_, bstack1l111111111_opy_[bstack11l111_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᔕ")]), None)
        step.update({
            bstack11l111_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬᔖ"): datetime.now(tz=timezone.utc)
        })
        index = next((i for i, st in enumerate(bstack1l111111111_opy_[bstack11l111_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᔗ")]) if st[bstack11l111_opy_ (u"ࠪ࡭ࡩ࠭ᔘ")] == step[bstack11l111_opy_ (u"ࠫ࡮ࡪࠧᔙ")]), None)
        if index is not None:
            bstack1l111111111_opy_[bstack11l111_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫᔚ")][index] = step
        instance.data[TestFramework.bstack1l1111l1l11_opy_] = bstack1l111111111_opy_
    @staticmethod
    def __1l111l11111_opy_(instance, args):
        bstack11l111_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡻ࡭࡫࡮ࠡ࡮ࡨࡲࠥࡧࡲࡨࡵࠣ࡭ࡸࠦ࠲࠭ࠢ࡬ࡸࠥࡹࡩࡨࡰ࡬ࡪ࡮࡫ࡳࠡࡶ࡫ࡩࡷ࡫ࠠࡪࡵࠣࡲࡴࠦࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡢࡴࡪࡷࠥࡧࡲࡦࠢ࠰ࠤࡠࡸࡥࡲࡷࡨࡷࡹ࠲ࠠࡴࡶࡨࡴࡢࠐࠠࠡࠢࠣࠤࠥࠦࠠࡪࡨࠣࡥࡷ࡭ࡳࠡࡣࡵࡩࠥ࠹ࠠࡵࡪࡨࡲࠥࡺࡨࡦࠢ࡯ࡥࡸࡺࠠࡷࡣ࡯ࡹࡪࠦࡩࡴࠢࡨࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤᔛ")
        bstack11llll1l111_opy_ = datetime.now(tz=timezone.utc)
        request = args[0]
        bstack11lllll1l1l_opy_ = args[1]
        bstack11lllllll1l_opy_ = id(bstack11lllll1l1l_opy_)
        bstack1l111111111_opy_ = instance.data[TestFramework.bstack1l1111l1l11_opy_]
        step = None
        if bstack11lllllll1l_opy_ is not None and bstack1l111111111_opy_.get(bstack11l111_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᔜ")):
            step = next(filter(lambda st: st[bstack11l111_opy_ (u"ࠨ࡫ࡧࠫᔝ")] == bstack11lllllll1l_opy_, bstack1l111111111_opy_[bstack11l111_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᔞ")]), None)
            step.update({
                bstack11l111_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨᔟ"): bstack11llll1l111_opy_,
            })
        if len(args) > 2:
            exception = args[2]
            step.update({
                bstack11l111_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫᔠ"): bstack11l111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬᔡ"),
                bstack11l111_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫ࠧᔢ"): str(exception)
            })
        else:
            if step is not None:
                step.update({
                    bstack11l111_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧᔣ"): bstack11l111_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨᔤ"),
                })
        index = next((i for i, st in enumerate(bstack1l111111111_opy_[bstack11l111_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᔥ")]) if st[bstack11l111_opy_ (u"ࠪ࡭ࡩ࠭ᔦ")] == step[bstack11l111_opy_ (u"ࠫ࡮ࡪࠧᔧ")]), None)
        if index is not None:
            bstack1l111111111_opy_[bstack11l111_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫᔨ")][index] = step
        instance.data[TestFramework.bstack1l1111l1l11_opy_] = bstack1l111111111_opy_
    @staticmethod
    def __11lllll11ll_opy_(node):
        try:
            examples = []
            if hasattr(node, bstack11l111_opy_ (u"࠭ࡣࡢ࡮࡯ࡷࡵ࡫ࡣࠨᔩ")):
                examples = list(node.callspec.params[bstack11l111_opy_ (u"ࠧࡠࡲࡼࡸࡪࡹࡴࡠࡤࡧࡨࡤ࡫ࡸࡢ࡯ࡳࡰࡪ࠭ᔪ")].values())
            return examples
        except:
            return []
    def bstack1l1l1l1l1l1_opy_(self, instance: bstack1lll11l11ll_opy_, bstack1llll11llll_opy_: Tuple[bstack1lll111l1l1_opy_, bstack1ll1l11l11l_opy_]):
        bstack11llll11ll1_opy_ = (
            PytestBDDFramework.bstack1l111l111ll_opy_
            if bstack1llll11llll_opy_[1] == bstack1ll1l11l11l_opy_.PRE
            else PytestBDDFramework.bstack11llllll11l_opy_
        )
        hook = PytestBDDFramework.bstack1l1111111ll_opy_(instance, bstack11llll11ll1_opy_)
        entries = hook.get(TestFramework.bstack11lll1ll1ll_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1llll1ll11l_opy_(instance, TestFramework.bstack1l1111lll1l_opy_, []))
        return entries
    def bstack1l1l1l1lll1_opy_(self, instance: bstack1lll11l11ll_opy_, bstack1llll11llll_opy_: Tuple[bstack1lll111l1l1_opy_, bstack1ll1l11l11l_opy_]):
        bstack11llll11ll1_opy_ = (
            PytestBDDFramework.bstack1l111l111ll_opy_
            if bstack1llll11llll_opy_[1] == bstack1ll1l11l11l_opy_.PRE
            else PytestBDDFramework.bstack11llllll11l_opy_
        )
        PytestBDDFramework.bstack1l1111llll1_opy_(instance, bstack11llll11ll1_opy_)
        TestFramework.bstack1llll1ll11l_opy_(instance, TestFramework.bstack1l1111lll1l_opy_, []).clear()
    @staticmethod
    def bstack1l1111111ll_opy_(instance: bstack1lll11l11ll_opy_, bstack11llll11ll1_opy_: str):
        bstack1l111l11l1l_opy_ = (
            PytestBDDFramework.bstack1l1111ll1ll_opy_
            if bstack11llll11ll1_opy_ == PytestBDDFramework.bstack11llllll11l_opy_
            else PytestBDDFramework.bstack1l111111l11_opy_
        )
        bstack1l111l111l1_opy_ = TestFramework.bstack1llll1ll11l_opy_(instance, bstack11llll11ll1_opy_, None)
        bstack1l1111l1111_opy_ = TestFramework.bstack1llll1ll11l_opy_(instance, bstack1l111l11l1l_opy_, None) if bstack1l111l111l1_opy_ else None
        return (
            bstack1l1111l1111_opy_[bstack1l111l111l1_opy_][-1]
            if isinstance(bstack1l1111l1111_opy_, dict) and len(bstack1l1111l1111_opy_.get(bstack1l111l111l1_opy_, [])) > 0
            else None
        )
    @staticmethod
    def bstack1l1111llll1_opy_(instance: bstack1lll11l11ll_opy_, bstack11llll11ll1_opy_: str):
        hook = PytestBDDFramework.bstack1l1111111ll_opy_(instance, bstack11llll11ll1_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack11lll1ll1ll_opy_, []).clear()
    @staticmethod
    def __1l11111l1ll_opy_(instance: bstack1lll11l11ll_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack11l111_opy_ (u"ࠣࡩࡨࡸࡤࡸࡥࡤࡱࡵࡨࡸࠨᔫ"), None)):
            return
        if os.getenv(bstack11l111_opy_ (u"ࠤࡖࡈࡐࡥࡃࡍࡋࡢࡊࡑࡇࡇࡠࡎࡒࡋࡘࠨᔬ"), bstack11l111_opy_ (u"ࠥ࠵ࠧᔭ")) != bstack11l111_opy_ (u"ࠦ࠶ࠨᔮ"):
            PytestBDDFramework.logger.warning(bstack11l111_opy_ (u"ࠧ࡯ࡧ࡯ࡱࡵ࡭ࡳ࡭ࠠࡤࡣࡳࡰࡴ࡭ࠢᔯ"))
            return
        bstack1l111l11lll_opy_ = {
            bstack11l111_opy_ (u"ࠨࡳࡦࡶࡸࡴࠧᔰ"): (PytestBDDFramework.bstack1l111l111ll_opy_, PytestBDDFramework.bstack1l111111l11_opy_),
            bstack11l111_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࠤᔱ"): (PytestBDDFramework.bstack11llllll11l_opy_, PytestBDDFramework.bstack1l1111ll1ll_opy_),
        }
        for when in (bstack11l111_opy_ (u"ࠣࡵࡨࡸࡺࡶࠢᔲ"), bstack11l111_opy_ (u"ࠤࡦࡥࡱࡲࠢᔳ"), bstack11l111_opy_ (u"ࠥࡸࡪࡧࡲࡥࡱࡺࡲࠧᔴ")):
            bstack11llll1l11l_opy_ = args[1].get_records(when)
            if not bstack11llll1l11l_opy_:
                continue
            records = [
                bstack1lll11l1lll_opy_(
                    kind=TestFramework.bstack1l1l1lll111_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack11l111_opy_ (u"ࠦࡱ࡫ࡶࡦ࡮ࡱࡥࡲ࡫ࠢᔵ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack11l111_opy_ (u"ࠧࡩࡲࡦࡣࡷࡩࡩࠨᔶ")) and r.created
                        else None
                    ),
                )
                for r in bstack11llll1l11l_opy_
                if isinstance(getattr(r, bstack11l111_opy_ (u"ࠨ࡭ࡦࡵࡶࡥ࡬࡫ࠢᔷ"), None), str) and r.message.strip()
            ]
            if not records:
                continue
            bstack11llll1llll_opy_, bstack1l111l11l1l_opy_ = bstack1l111l11lll_opy_.get(when, (None, None))
            bstack11llll111ll_opy_ = TestFramework.bstack1llll1ll11l_opy_(instance, bstack11llll1llll_opy_, None) if bstack11llll1llll_opy_ else None
            bstack1l1111l1111_opy_ = TestFramework.bstack1llll1ll11l_opy_(instance, bstack1l111l11l1l_opy_, None) if bstack11llll111ll_opy_ else None
            if isinstance(bstack1l1111l1111_opy_, dict) and len(bstack1l1111l1111_opy_.get(bstack11llll111ll_opy_, [])) > 0:
                hook = bstack1l1111l1111_opy_[bstack11llll111ll_opy_][-1]
                if isinstance(hook, dict) and TestFramework.bstack11lll1ll1ll_opy_ in hook:
                    hook[TestFramework.bstack11lll1ll1ll_opy_].extend(records)
                    continue
            logs = TestFramework.bstack1llll1ll11l_opy_(instance, TestFramework.bstack1l1111lll1l_opy_, [])
            logs.extend(records)
    @staticmethod
    def __11llllll1ll_opy_(args) -> Dict[str, Any]:
        request, feature, scenario = args
        bstack1l11l1l11l_opy_ = request.node.nodeid
        test_name = PytestBDDFramework.__1l1111ll1l1_opy_(request.node, scenario)
        bstack11llll1lll1_opy_ = feature.filename
        if not bstack1l11l1l11l_opy_ or not test_name or not bstack11llll1lll1_opy_:
            return None
        code = None
        return {
            TestFramework.bstack1ll1111l1ll_opy_: uuid4().__str__(),
            TestFramework.bstack1l1111l1lll_opy_: bstack1l11l1l11l_opy_,
            TestFramework.bstack1ll11l1111l_opy_: test_name,
            TestFramework.bstack1l1l1111l1l_opy_: bstack1l11l1l11l_opy_,
            TestFramework.bstack11lllll1111_opy_: bstack11llll1lll1_opy_,
            TestFramework.bstack1l1111111l1_opy_: PytestBDDFramework.__11lllll11l1_opy_(feature, scenario),
            TestFramework.bstack1l111l11ll1_opy_: code,
            TestFramework.bstack1l11ll11l11_opy_: TestFramework.bstack11lll1lll1l_opy_,
            TestFramework.bstack1l111llll11_opy_: test_name
        }
    @staticmethod
    def __1l1111ll1l1_opy_(node, scenario):
        if hasattr(node, bstack11l111_opy_ (u"ࠧࡤࡣ࡯ࡰࡸࡶࡥࡤࠩᔸ")):
            parts = node.nodeid.rsplit(bstack11l111_opy_ (u"ࠣ࡝ࠥᔹ"))
            params = parts[-1]
            return bstack11l111_opy_ (u"ࠤࡾࢁࠥࡡࡻࡾࠤᔺ").format(scenario.name, params)
        return scenario.name
    @staticmethod
    def __11lllll11l1_opy_(feature, scenario) -> List[str]:
        return (list(feature.tags) if hasattr(feature, bstack11l111_opy_ (u"ࠪࡸࡦ࡭ࡳࠨᔻ")) else []) + (list(scenario.tags) if hasattr(scenario, bstack11l111_opy_ (u"ࠫࡹࡧࡧࡴࠩᔼ")) else [])
    @staticmethod
    def __11llllllll1_opy_(location):
        return bstack11l111_opy_ (u"ࠧࡀ࠺ࠣᔽ").join(filter(lambda x: isinstance(x, str), location))