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
import json
import time
import os
import threading
import asyncio
from browserstack_sdk.sdk_cli.bstack1lllll11lll_opy_ import (
    bstack1llll11111l_opy_,
    bstack1llll1l11l1_opy_,
    bstack1lllll1lll1_opy_,
    bstack1llll111ll1_opy_,
)
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1l1l1l1ll_opy_, bstack1lll1ll111_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l111ll_opy_ import bstack1ll1l111l11_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll111l1l1_opy_, bstack1ll1l11l11l_opy_, bstack1lll11l11ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l111ll1_opy_ import bstack1ll1l11111l_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll1ll11l_opy_ import bstack1l1lll11l11_opy_
from typing import Tuple, List, Any
from bstack_utils.bstack111l1lll_opy_ import bstack1l11111l1_opy_, bstack1ll11l1ll1_opy_, bstack11lll111_opy_
from browserstack_sdk import sdk_pb2 as structs
class bstack1ll1ll1l11l_opy_(bstack1l1lll11l11_opy_):
    bstack1l11ll1ll11_opy_ = bstack11l111_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡧࡶ࡮ࡼࡥࡳࡵࠥ፮")
    bstack1l1l11l1ll1_opy_ = bstack11l111_opy_ (u"ࠧࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡶࡩࡸࡹࡩࡰࡰࡶࠦ፯")
    bstack1l11ll111l1_opy_ = bstack11l111_opy_ (u"ࠨ࡮ࡰࡰࡢࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡳࡦࡵࡶ࡭ࡴࡴࡳࠣ፰")
    bstack1l11ll1111l_opy_ = bstack11l111_opy_ (u"ࠢࡵࡧࡶࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡹࠢ፱")
    bstack1l11ll111ll_opy_ = bstack11l111_opy_ (u"ࠣࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤ࡯࡮ࡴࡶࡤࡲࡨ࡫࡟ࡳࡧࡩࡷࠧ፲")
    bstack1l1l11lll11_opy_ = bstack11l111_opy_ (u"ࠤࡦࡦࡹࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡤࡴࡨࡥࡹ࡫ࡤࠣ፳")
    bstack1l11ll1l111_opy_ = bstack11l111_opy_ (u"ࠥࡧࡧࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡰࡤࡱࡪࠨ፴")
    bstack1l11ll11ll1_opy_ = bstack11l111_opy_ (u"ࠦࡨࡨࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡶࡸࡦࡺࡵࡴࠤ፵")
    def __init__(self):
        super().__init__(bstack1l1lll111l1_opy_=self.bstack1l11ll1ll11_opy_, frameworks=[bstack1ll1l111l11_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1ll111111ll_opy_((bstack1lll111l1l1_opy_.BEFORE_EACH, bstack1ll1l11l11l_opy_.POST), self.bstack1l11l1lllll_opy_)
        if bstack1lll1ll111_opy_():
            TestFramework.bstack1ll111111ll_opy_((bstack1lll111l1l1_opy_.TEST, bstack1ll1l11l11l_opy_.POST), self.bstack1l1llll1ll1_opy_)
        else:
            TestFramework.bstack1ll111111ll_opy_((bstack1lll111l1l1_opy_.TEST, bstack1ll1l11l11l_opy_.PRE), self.bstack1l1llll1ll1_opy_)
        TestFramework.bstack1ll111111ll_opy_((bstack1lll111l1l1_opy_.TEST, bstack1ll1l11l11l_opy_.POST), self.bstack1l1llllllll_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11l1lllll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11ll_opy_,
        bstack1llll11llll_opy_: Tuple[bstack1lll111l1l1_opy_, bstack1ll1l11l11l_opy_],
        *args,
        **kwargs,
    ):
        bstack1l11ll1lll1_opy_ = self.bstack1l11ll11lll_opy_(instance.context)
        if not bstack1l11ll1lll1_opy_:
            self.logger.debug(bstack11l111_opy_ (u"ࠧࡹࡥࡵࡡࡤࡧࡹ࡯ࡶࡦࡡࡳࡥ࡬࡫࠺ࠡࡰࡲࠤࡵࡧࡧࡦࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࠥ፶") + str(bstack1llll11llll_opy_) + bstack11l111_opy_ (u"ࠨࠢ፷"))
            return
        f.bstack1llll1l1111_opy_(instance, bstack1ll1ll1l11l_opy_.bstack1l1l11l1ll1_opy_, bstack1l11ll1lll1_opy_)
    def bstack1l11ll11lll_opy_(self, context: bstack1llll111ll1_opy_, bstack1l11ll11111_opy_= True):
        if bstack1l11ll11111_opy_:
            bstack1l11ll1lll1_opy_ = self.bstack1l1ll1ll1ll_opy_(context, reverse=True)
        else:
            bstack1l11ll1lll1_opy_ = self.bstack1l1ll1ll111_opy_(context, reverse=True)
        return [f for f in bstack1l11ll1lll1_opy_ if f[1].state != bstack1llll11111l_opy_.QUIT]
    def bstack1l1llll1ll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11ll_opy_,
        bstack1llll11llll_opy_: Tuple[bstack1lll111l1l1_opy_, bstack1ll1l11l11l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lllll_opy_(f, instance, bstack1llll11llll_opy_, *args, **kwargs)
        if not bstack1l1l1l1l1ll_opy_:
            self.logger.debug(bstack11l111_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࡹࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥ፸") + str(kwargs) + bstack11l111_opy_ (u"ࠣࠤ፹"))
            return
        bstack1l11ll1lll1_opy_ = f.bstack1llll1ll11l_opy_(instance, bstack1ll1ll1l11l_opy_.bstack1l1l11l1ll1_opy_, [])
        if not bstack1l11ll1lll1_opy_:
            self.logger.debug(bstack11l111_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࡳࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧ፺") + str(kwargs) + bstack11l111_opy_ (u"ࠥࠦ፻"))
            return
        if len(bstack1l11ll1lll1_opy_) > 1:
            self.logger.debug(
                bstack1lll111l111_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦࡻ࡭ࡧࡱࠬࡵࡧࡧࡦࡡ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡷ࠮ࢃࠠࡥࡴ࡬ࡺࡪࡸࡳࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࢀࡱࡷࡢࡴࡪࡷࢂࠨ፼"))
        bstack1l11ll1l11l_opy_, bstack1l1l1111lll_opy_ = bstack1l11ll1lll1_opy_[0]
        page = bstack1l11ll1l11l_opy_()
        if not page:
            self.logger.debug(bstack11l111_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࠣࡴࡦ࡭ࡥࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧ፽") + str(kwargs) + bstack11l111_opy_ (u"ࠨࠢ፾"))
            return
        bstack1ll111l111_opy_ = getattr(args[0], bstack11l111_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢ፿"), None)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11l111_opy_ (u"ࠣࡶࡨࡷࡹࡉ࡯࡯ࡶࡨࡼࡹࡕࡰࡵ࡫ࡲࡲࡸࠨᎀ")).get(bstack11l111_opy_ (u"ࠤࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦᎁ")):
            try:
                page.evaluate(bstack11l111_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦᎂ"),
                            bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠨᎃ") + json.dumps(
                                bstack1ll111l111_opy_) + bstack11l111_opy_ (u"ࠧࢃࡽࠣᎄ"))
            except Exception as e:
                self.logger.debug(bstack11l111_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡲࡦࡳࡥࠡࡽࢀࠦᎅ"), e)
    def bstack1l1llllllll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11ll_opy_,
        bstack1llll11llll_opy_: Tuple[bstack1lll111l1l1_opy_, bstack1ll1l11l11l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lllll_opy_(f, instance, bstack1llll11llll_opy_, *args, **kwargs)
        if not bstack1l1l1l1l1ll_opy_:
            self.logger.debug(bstack11l111_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࡹࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᎆ") + str(kwargs) + bstack11l111_opy_ (u"ࠣࠤᎇ"))
            return
        bstack1l11ll1lll1_opy_ = f.bstack1llll1ll11l_opy_(instance, bstack1ll1ll1l11l_opy_.bstack1l1l11l1ll1_opy_, [])
        if not bstack1l11ll1lll1_opy_:
            self.logger.debug(bstack11l111_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࡳࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᎈ") + str(kwargs) + bstack11l111_opy_ (u"ࠥࠦᎉ"))
            return
        if len(bstack1l11ll1lll1_opy_) > 1:
            self.logger.debug(
                bstack1lll111l111_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦࡻ࡭ࡧࡱࠬࡵࡧࡧࡦࡡ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡷ࠮ࢃࠠࡥࡴ࡬ࡺࡪࡸࡳࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࢀࡱࡷࡢࡴࡪࡷࢂࠨᎊ"))
        bstack1l11ll1l11l_opy_, bstack1l1l1111lll_opy_ = bstack1l11ll1lll1_opy_[0]
        page = bstack1l11ll1l11l_opy_()
        if not page:
            self.logger.debug(bstack11l111_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࠣࡴࡦ࡭ࡥࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᎋ") + str(kwargs) + bstack11l111_opy_ (u"ࠨࠢᎌ"))
            return
        status = f.bstack1llll1ll11l_opy_(instance, TestFramework.bstack1l11ll11l11_opy_, None)
        if not status:
            self.logger.debug(bstack11l111_opy_ (u"ࠢ࡯ࡱࠣࡷࡹࡧࡴࡶࡵࠣࡪࡴࡸࠠࡵࡧࡶࡸ࠱ࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࠥᎍ") + str(bstack1llll11llll_opy_) + bstack11l111_opy_ (u"ࠣࠤᎎ"))
            return
        bstack1l11ll1ll1l_opy_ = {bstack11l111_opy_ (u"ࠤࡶࡸࡦࡺࡵࡴࠤᎏ"): status.lower()}
        bstack1l11ll1l1ll_opy_ = f.bstack1llll1ll11l_opy_(instance, TestFramework.bstack1l11ll11l1l_opy_, None)
        if status.lower() == bstack11l111_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪ᎐") and bstack1l11ll1l1ll_opy_ is not None:
            bstack1l11ll1ll1l_opy_[bstack11l111_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫ᎑")] = bstack1l11ll1l1ll_opy_[0][bstack11l111_opy_ (u"ࠬࡨࡡࡤ࡭ࡷࡶࡦࡩࡥࠨ᎒")][0] if isinstance(bstack1l11ll1l1ll_opy_, list) else str(bstack1l11ll1l1ll_opy_)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack11l111_opy_ (u"ࠨࡴࡦࡵࡷࡇࡴࡴࡴࡦࡺࡷࡓࡵࡺࡩࡰࡰࡶࠦ᎓")).get(bstack11l111_opy_ (u"ࠢࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦ᎔")):
            try:
                page.evaluate(
                        bstack11l111_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤ᎕"),
                        bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࠧ᎖")
                        + json.dumps(bstack1l11ll1ll1l_opy_)
                        + bstack11l111_opy_ (u"ࠥࢁࠧ᎗")
                    )
            except Exception as e:
                self.logger.debug(bstack11l111_opy_ (u"ࠦࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡵࡷࡥࡹࡻࡳࠡࡽࢀࠦ᎘"), e)
    def bstack1l1ll11l11l_opy_(
        self,
        instance: bstack1lll11l11ll_opy_,
        f: TestFramework,
        bstack1llll11llll_opy_: Tuple[bstack1lll111l1l1_opy_, bstack1ll1l11l11l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lllll_opy_(f, instance, bstack1llll11llll_opy_, *args, **kwargs)
        if not bstack1l1l1l1l1ll_opy_:
            self.logger.debug(
                bstack1lll111l111_opy_ (u"ࠧࡳࡡࡳ࡭ࡢࡳ࠶࠷ࡹࡠࡵࡼࡲࡨࡀࠠ࡯ࡱࡷࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡷࡪࡹࡳࡪࡱࡱ࠰ࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࢀࡱࡷࡢࡴࡪࡷࢂࠨ᎙"))
            return
        bstack1l11ll1lll1_opy_ = f.bstack1llll1ll11l_opy_(instance, bstack1ll1ll1l11l_opy_.bstack1l1l11l1ll1_opy_, [])
        if not bstack1l11ll1lll1_opy_:
            self.logger.debug(bstack11l111_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤ᎚") + str(kwargs) + bstack11l111_opy_ (u"ࠢࠣ᎛"))
            return
        if len(bstack1l11ll1lll1_opy_) > 1:
            self.logger.debug(
                bstack1lll111l111_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡿࡱ࡫࡮ࠩࡲࡤ࡫ࡪࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࡽ࡮ࡻࡦࡸࡧࡴࡿࠥ᎜"))
        bstack1l11ll1l11l_opy_, bstack1l1l1111lll_opy_ = bstack1l11ll1lll1_opy_[0]
        page = bstack1l11ll1l11l_opy_()
        if not page:
            self.logger.debug(bstack11l111_opy_ (u"ࠤࡰࡥࡷࡱ࡟ࡰ࠳࠴ࡽࡤࡹࡹ࡯ࡥ࠽ࠤࡳࡵࠠࡱࡣࡪࡩࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤ᎝") + str(kwargs) + bstack11l111_opy_ (u"ࠥࠦ᎞"))
            return
        timestamp = int(time.time() * 1000)
        data = bstack11l111_opy_ (u"ࠦࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࡗࡾࡴࡣ࠻ࠤ᎟") + str(timestamp)
        try:
            page.evaluate(
                bstack11l111_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨᎠ"),
                bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫᎡ").format(
                    json.dumps(
                        {
                            bstack11l111_opy_ (u"ࠢࡢࡥࡷ࡭ࡴࡴࠢᎢ"): bstack11l111_opy_ (u"ࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥᎣ"),
                            bstack11l111_opy_ (u"ࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧᎤ"): {
                                bstack11l111_opy_ (u"ࠥࡸࡾࡶࡥࠣᎥ"): bstack11l111_opy_ (u"ࠦࡆࡴ࡮ࡰࡶࡤࡸ࡮ࡵ࡮ࠣᎦ"),
                                bstack11l111_opy_ (u"ࠧࡪࡡࡵࡣࠥᎧ"): data,
                                bstack11l111_opy_ (u"ࠨ࡬ࡦࡸࡨࡰࠧᎨ"): bstack11l111_opy_ (u"ࠢࡥࡧࡥࡹ࡬ࠨᎩ")
                            }
                        }
                    )
                )
            )
        except Exception as e:
            self.logger.debug(bstack11l111_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡴ࠷࠱ࡺࠢࡤࡲࡳࡵࡴࡢࡶ࡬ࡳࡳࠦ࡭ࡢࡴ࡮࡭ࡳ࡭ࠠࡼࡿࠥᎪ"), e)
    def bstack1l1ll11l111_opy_(
        self,
        instance: bstack1lll11l11ll_opy_,
        f: TestFramework,
        bstack1llll11llll_opy_: Tuple[bstack1lll111l1l1_opy_, bstack1ll1l11l11l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lllll_opy_(f, instance, bstack1llll11llll_opy_, *args, **kwargs)
        if f.bstack1llll1ll11l_opy_(instance, bstack1ll1ll1l11l_opy_.bstack1l1l11lll11_opy_, False):
            return
        self.bstack1ll111111l1_opy_()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll1ll11l_opy_(instance, TestFramework.bstack1ll111l1l1l_opy_)
        req.test_framework_name = TestFramework.bstack1llll1ll11l_opy_(instance, TestFramework.bstack1l1lllll1l1_opy_)
        req.test_framework_version = TestFramework.bstack1llll1ll11l_opy_(instance, TestFramework.bstack1l1l11ll1ll_opy_)
        req.test_framework_state = bstack1llll11llll_opy_[0].name
        req.test_hook_state = bstack1llll11llll_opy_[1].name
        req.test_uuid = TestFramework.bstack1llll1ll11l_opy_(instance, TestFramework.bstack1ll1111l1ll_opy_)
        for bstack1l11lll1111_opy_ in bstack1ll1l11111l_opy_.bstack1lllll1ll1l_opy_.values():
            session = req.automation_sessions.add()
            session.provider = (
                bstack11l111_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠣᎫ")
                if bstack1l1l1l1l1ll_opy_
                else bstack11l111_opy_ (u"ࠥࡹࡳࡱ࡮ࡰࡹࡱࡣ࡬ࡸࡩࡥࠤᎬ")
            )
            session.ref = bstack1l11lll1111_opy_.ref()
            session.hub_url = bstack1ll1l11111l_opy_.bstack1llll1ll11l_opy_(bstack1l11lll1111_opy_, bstack1ll1l11111l_opy_.bstack1l11lllll11_opy_, bstack11l111_opy_ (u"ࠦࠧᎭ"))
            session.framework_name = bstack1l11lll1111_opy_.framework_name
            session.framework_version = bstack1l11lll1111_opy_.framework_version
            session.framework_session_id = bstack1ll1l11111l_opy_.bstack1llll1ll11l_opy_(bstack1l11lll1111_opy_, bstack1ll1l11111l_opy_.bstack1l11llll111_opy_, bstack11l111_opy_ (u"ࠧࠨᎮ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll111lll1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11ll_opy_,
        bstack1llll11llll_opy_: Tuple[bstack1lll111l1l1_opy_, bstack1ll1l11l11l_opy_],
        *args,
        **kwargs
    ):
        bstack1l11ll1lll1_opy_ = f.bstack1llll1ll11l_opy_(instance, bstack1ll1ll1l11l_opy_.bstack1l1l11l1ll1_opy_, [])
        if not bstack1l11ll1lll1_opy_:
            self.logger.debug(bstack11l111_opy_ (u"ࠨࡧࡦࡶࡢࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡥࡴ࡬ࡺࡪࡸ࠺ࠡࡰࡲࠤࡵࡧࡧࡦࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᎯ") + str(kwargs) + bstack11l111_opy_ (u"ࠢࠣᎰ"))
            return
        if len(bstack1l11ll1lll1_opy_) > 1:
            self.logger.debug(bstack11l111_opy_ (u"ࠣࡩࡨࡸࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡿࡱ࡫࡮ࠩࡲࡤ࡫ࡪࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᎱ") + str(kwargs) + bstack11l111_opy_ (u"ࠤࠥᎲ"))
        bstack1l11ll1l11l_opy_, bstack1l1l1111lll_opy_ = bstack1l11ll1lll1_opy_[0]
        page = bstack1l11ll1l11l_opy_()
        if not page:
            self.logger.debug(bstack11l111_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡩࡸࡩࡷࡧࡵ࠾ࠥࡴ࡯ࠡࡲࡤ࡫ࡪࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᎳ") + str(kwargs) + bstack11l111_opy_ (u"ࠦࠧᎴ"))
            return
        return page
    def bstack1ll11111ll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11ll_opy_,
        bstack1llll11llll_opy_: Tuple[bstack1lll111l1l1_opy_, bstack1ll1l11l11l_opy_],
        *args,
        **kwargs
    ):
        caps = {}
        bstack1l11ll1l1l1_opy_ = {}
        for bstack1l11lll1111_opy_ in bstack1ll1l11111l_opy_.bstack1lllll1ll1l_opy_.values():
            caps = bstack1ll1l11111l_opy_.bstack1llll1ll11l_opy_(bstack1l11lll1111_opy_, bstack1ll1l11111l_opy_.bstack1l11lllllll_opy_, bstack11l111_opy_ (u"ࠧࠨᎵ"))
        bstack1l11ll1l1l1_opy_[bstack11l111_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠦᎶ")] = caps.get(bstack11l111_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࠣᎷ"), bstack11l111_opy_ (u"ࠣࠤᎸ"))
        bstack1l11ll1l1l1_opy_[bstack11l111_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠣᎹ")] = caps.get(bstack11l111_opy_ (u"ࠥࡳࡸࠨᎺ"), bstack11l111_opy_ (u"ࠦࠧᎻ"))
        bstack1l11ll1l1l1_opy_[bstack11l111_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠢᎼ")] = caps.get(bstack11l111_opy_ (u"ࠨ࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠥᎽ"), bstack11l111_opy_ (u"ࠢࠣᎾ"))
        bstack1l11ll1l1l1_opy_[bstack11l111_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠤᎿ")] = caps.get(bstack11l111_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠦᏀ"), bstack11l111_opy_ (u"ࠥࠦᏁ"))
        return bstack1l11ll1l1l1_opy_
    def bstack1ll1111111l_opy_(self, page: object, bstack1ll11l111l1_opy_, args={}):
        try:
            bstack1l11ll1llll_opy_ = bstack11l111_opy_ (u"ࠦࠧࠨࠨࡧࡷࡱࡧࡹ࡯࡯࡯ࠢࠫ࠲࠳࠴ࡢࡴࡶࡤࡧࡰ࡙ࡤ࡬ࡃࡵ࡫ࡸ࠯ࠠࡼࡽࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡸࡥࡵࡷࡵࡲࠥࡴࡥࡸࠢࡓࡶࡴࡳࡩࡴࡧࠫࠬࡷ࡫ࡳࡰ࡮ࡹࡩ࠱ࠦࡲࡦ࡬ࡨࡧࡹ࠯ࠠ࠾ࡀࠣࡿࢀࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡳࡵࡣࡦ࡯ࡘࡪ࡫ࡂࡴࡪࡷ࠳ࡶࡵࡴࡪࠫࡶࡪࡹ࡯࡭ࡸࡨ࠭ࡀࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࢁࡦ࡯ࡡࡥࡳࡩࡿࡽࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࢁࢂ࠯࠻ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡽࡾࠫࠫࡿࡦࡸࡧࡠ࡬ࡶࡳࡳࢃࠩࠣࠤࠥᏂ")
            bstack1ll11l111l1_opy_ = bstack1ll11l111l1_opy_.replace(bstack11l111_opy_ (u"ࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣᏃ"), bstack11l111_opy_ (u"ࠨࡢࡴࡶࡤࡧࡰ࡙ࡤ࡬ࡃࡵ࡫ࡸࠨᏄ"))
            script = bstack1l11ll1llll_opy_.format(fn_body=bstack1ll11l111l1_opy_, arg_json=json.dumps(args))
            return page.evaluate(script)
        except Exception as e:
            self.logger.error(bstack11l111_opy_ (u"ࠢࡢ࠳࠴ࡽࡤࡹࡣࡳ࡫ࡳࡸࡤ࡫ࡸࡦࡥࡸࡸࡪࡀࠠࡆࡴࡵࡳࡷࠦࡥࡹࡧࡦࡹࡹ࡯࡮ࡨࠢࡷ࡬ࡪࠦࡡ࠲࠳ࡼࠤࡸࡩࡲࡪࡲࡷ࠰ࠥࠨᏅ") + str(e) + bstack11l111_opy_ (u"ࠣࠤᏆ"))