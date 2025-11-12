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
from bstack_utils.constants import *
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.bstack111l1111l1l_opy_ import bstack111l111l11l_opy_
from bstack_utils.bstack1llll11ll_opy_ import bstack1l1ll1ll1l_opy_
from bstack_utils.helper import bstack111ll1lll_opy_
import json
class bstack1ll1l11l11_opy_:
    _1ll1l111111_opy_ = None
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.bstack111l1111lll_opy_ = bstack111l111l11l_opy_(self.config, logger)
        self.bstack1llll11ll_opy_ = bstack1l1ll1ll1l_opy_.bstack111llll1_opy_(config=self.config)
        self.bstack1111llllll1_opy_ = {}
        self.bstack11111l11l1_opy_ = False
        self.bstack111l111l111_opy_ = (
            self.__1111llll1ll_opy_()
            and self.bstack1llll11ll_opy_ is not None
            and self.bstack1llll11ll_opy_.bstack1l11111l11_opy_()
            and config.get(bstack11l111_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠩẤ"), None) is not None
            and config.get(bstack11l111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨấ"), os.path.basename(os.getcwd())) is not None
        )
    @classmethod
    def bstack111llll1_opy_(cls, config, logger):
        if cls._1ll1l111111_opy_ is None and config is not None:
            cls._1ll1l111111_opy_ = bstack1ll1l11l11_opy_(config, logger)
        return cls._1ll1l111111_opy_
    def bstack1l11111l11_opy_(self):
        bstack11l111_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡈࡴࠦ࡮ࡰࡶࠣࡥࡵࡶ࡬ࡺࠢࡷࡩࡸࡺࠠࡰࡴࡧࡩࡷ࡯࡮ࡨࠢࡺ࡬ࡪࡴ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡏ࠲࠳ࡼࠤ࡮ࡹࠠ࡯ࡱࡷࠤࡪࡴࡡࡣ࡮ࡨࡨࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡓࡷࡪࡥࡳ࡫ࡱ࡫ࠥ࡯ࡳࠡࡰࡲࡸࠥ࡫࡮ࡢࡤ࡯ࡩࡩࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠢ࡬ࡷࠥࡔ࡯࡯ࡧࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠤ࡮ࡹࠠࡏࡱࡱࡩࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤẦ")
        return self.bstack111l111l111_opy_ and self.bstack111l1111111_opy_()
    def bstack111l1111111_opy_(self):
        bstack1111lllllll_opy_ = os.getenv(bstack11l111_opy_ (u"ࠧࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࡢ࡙ࡘࡋࡄࠨầ"), self.config.get(bstack11l111_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫẨ"), None))
        return bstack1111lllllll_opy_ in bstack11l1l1111ll_opy_
    def __1111llll1ll_opy_(self):
        bstack11l1ll1l1l1_opy_ = False
        for fw in bstack11l1l111l11_opy_:
            if fw in self.config.get(bstack11l111_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬẩ"), bstack11l111_opy_ (u"ࠪࠫẪ")):
                bstack11l1ll1l1l1_opy_ = True
        return bstack111ll1lll_opy_(self.config.get(bstack11l111_opy_ (u"ࠫࡹ࡫ࡳࡵࡑࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨẫ"), bstack11l1ll1l1l1_opy_))
    def bstack111l11111ll_opy_(self):
        return (not self.bstack1l11111l11_opy_() and
                self.bstack1llll11ll_opy_ is not None and self.bstack1llll11ll_opy_.bstack1l11111l11_opy_())
    def bstack1111llll1l1_opy_(self):
        if not self.bstack111l11111ll_opy_():
            return
        if self.config.get(bstack11l111_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪẬ"), None) is None or self.config.get(bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩậ"), os.path.basename(os.getcwd())) is None:
            self.logger.info(bstack11l111_opy_ (u"ࠢࡕࡧࡶࡸࠥࡘࡥࡰࡴࡧࡩࡷ࡯࡮ࡨࠢࡦࡥࡳ࠭ࡴࠡࡹࡲࡶࡰࠦࡡࡴࠢࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠥࡵࡲࠡࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪࠦࡩࡴࠢࡱࡹࡱࡲ࠮ࠡࡒ࡯ࡩࡦࡹࡥࠡࡵࡨࡸࠥࡧࠠ࡯ࡱࡱ࠱ࡳࡻ࡬࡭ࠢࡹࡥࡱࡻࡥ࠯ࠤẮ"))
        if not self.__1111llll1ll_opy_():
            self.logger.info(bstack11l111_opy_ (u"ࠣࡖࡨࡷࡹࠦࡒࡦࡱࡵࡨࡪࡸࡩ࡯ࡩࠣࡧࡦࡴࠧࡵࠢࡺࡳࡷࡱࠠࡢࡵࠣࡸࡪࡹࡴࡓࡧࡳࡳࡷࡺࡩ࡯ࡩࠣ࡭ࡸࠦࡤࡪࡵࡤࡦࡱ࡫ࡤ࠯ࠢࡓࡰࡪࡧࡳࡦࠢࡨࡲࡦࡨ࡬ࡦࠢ࡬ࡸࠥ࡬ࡲࡰ࡯ࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡼࡱࡱࠦࡦࡪ࡮ࡨ࠲ࠧắ"))
    def bstack1111lllll1l_opy_(self):
        return self.bstack11111l11l1_opy_
    def bstack1111111ll1_opy_(self, bstack1111lllll11_opy_):
        self.bstack11111l11l1_opy_ = bstack1111lllll11_opy_
        self.bstack11111l1lll_opy_(bstack11l111_opy_ (u"ࠤࡤࡴࡵࡲࡩࡦࡦࠥẰ"), bstack1111lllll11_opy_)
    def bstack111111ll1l_opy_(self, test_files):
        try:
            if test_files is None:
                self.logger.debug(bstack11l111_opy_ (u"ࠥ࡟ࡷ࡫࡯ࡳࡦࡨࡶࡤࡺࡥࡴࡶࡢࡪ࡮ࡲࡥࡴ࡟ࠣࡒࡴࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵࠣࡴࡷࡵࡶࡪࡦࡨࡨࠥ࡬࡯ࡳࠢࡲࡶࡩ࡫ࡲࡪࡰࡪ࠲ࠧằ"))
                return None
            orchestration_strategy = None
            orchestration_metadata = self.bstack1llll11ll_opy_.bstack111l1111l11_opy_()
            if self.bstack1llll11ll_opy_ is not None:
                orchestration_strategy = self.bstack1llll11ll_opy_.bstack1l11111ll_opy_()
            if orchestration_strategy is None:
                self.logger.error(bstack11l111_opy_ (u"ࠦࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࠤࡸࡺࡲࡢࡶࡨ࡫ࡾࠦࡩࡴࠢࡑࡳࡳ࡫࠮ࠡࡅࡤࡲࡳࡵࡴࠡࡲࡵࡳࡨ࡫ࡥࡥࠢࡺ࡭ࡹ࡮ࠠࡵࡧࡶࡸࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࠥࡹࡥࡴࡵ࡬ࡳࡳ࠴ࠢẲ"))
                return None
            self.logger.info(bstack11l111_opy_ (u"ࠧࡘࡥࡰࡴࡧࡩࡷ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡧ࡫࡯ࡩࡸࠦࡷࡪࡶ࡫ࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࠤࡸࡺࡲࡢࡶࡨ࡫ࡾࡀࠠࡼࡿࠥẳ").format(orchestration_strategy))
            if cli.is_running():
                self.logger.debug(bstack11l111_opy_ (u"ࠨࡕࡴ࡫ࡱ࡫ࠥࡉࡌࡊࠢࡩࡰࡴࡽࠠࡧࡱࡵࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠯ࠤẴ"))
                ordered_test_files = cli.test_orchestration_session(test_files, orchestration_strategy, json.dumps(orchestration_metadata))
            else:
                self.logger.debug(bstack11l111_opy_ (u"ࠢࡖࡵ࡬ࡲ࡬ࠦࡳࡥ࡭ࠣࡪࡱࡵࡷࠡࡨࡲࡶࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴࠢࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯࠰ࠥẵ"))
                self.bstack111l1111lll_opy_.bstack111l11111l1_opy_(test_files, orchestration_strategy, orchestration_metadata)
                ordered_test_files = self.bstack111l1111lll_opy_.bstack111l111111l_opy_()
            if not ordered_test_files:
                return None
            self.bstack11111l1lll_opy_(bstack11l111_opy_ (u"ࠣࡷࡳࡰࡴࡧࡤࡦࡦࡗࡩࡸࡺࡆࡪ࡮ࡨࡷࡈࡵࡵ࡯ࡶࠥẶ"), len(test_files))
            self.bstack11111l1lll_opy_(bstack11l111_opy_ (u"ࠤࡱࡳࡩ࡫ࡉ࡯ࡦࡨࡼࠧặ"), int(os.environ.get(bstack11l111_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡑࡓࡉࡋ࡟ࡊࡐࡇࡉ࡝ࠨẸ")) or bstack11l111_opy_ (u"ࠦ࠵ࠨẹ")))
            self.bstack11111l1lll_opy_(bstack11l111_opy_ (u"ࠧࡺ࡯ࡵࡣ࡯ࡒࡴࡪࡥࡴࠤẺ"), int(os.environ.get(bstack11l111_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡔࡏࡅࡇࡢࡇࡔ࡛ࡎࡕࠤẻ")) or bstack11l111_opy_ (u"ࠢ࠲ࠤẼ")))
            self.bstack11111l1lll_opy_(bstack11l111_opy_ (u"ࠣࡦࡲࡻࡳࡲ࡯ࡢࡦࡨࡨ࡙࡫ࡳࡵࡈ࡬ࡰࡪࡹࡃࡰࡷࡱࡸࠧẽ"), len(ordered_test_files))
            self.bstack11111l1lll_opy_(bstack11l111_opy_ (u"ࠤࡶࡴࡱ࡯ࡴࡕࡧࡶࡸࡸࡇࡐࡊࡅࡤࡰࡱࡉ࡯ࡶࡰࡷࠦẾ"), self.bstack111l1111lll_opy_.bstack111l1111ll1_opy_())
            return ordered_test_files
        except Exception as e:
            self.logger.debug(bstack11l111_opy_ (u"ࠥ࡟ࡷ࡫࡯ࡳࡦࡨࡶࡤࡺࡥࡴࡶࡢࡪ࡮ࡲࡥࡴ࡟ࠣࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡵࡲࡥࡧࡵ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡩ࡬ࡢࡵࡶࡩࡸࡀࠠࡼࡿࠥế").format(e))
        return None
    def bstack11111l1lll_opy_(self, key, value):
        self.bstack1111llllll1_opy_[key] = value
    def bstack1ll1l11l1_opy_(self):
        return self.bstack1111llllll1_opy_