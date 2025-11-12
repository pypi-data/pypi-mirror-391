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
import time
from bstack_utils.bstack11l1lll111l_opy_ import bstack11l1lll1ll1_opy_
from bstack_utils.constants import bstack11l1l111lll_opy_
from bstack_utils.helper import get_host_info, bstack111ll1111l1_opy_
class bstack111l111l11l_opy_:
    bstack11l111_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡈࡢࡰࡧࡰࡪࡹࠠࡵࡧࡶࡸࠥࡵࡲࡥࡧࡵ࡭ࡳ࡭ࠠࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠠࡸ࡫ࡷ࡬ࠥࡺࡨࡦࠢࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠡࡵࡨࡶࡻ࡫ࡲ࠯ࠌࠣࠤࠥࠦࠢࠣࠤ⃹")
    def __init__(self, config, logger):
        bstack11l111_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤ࠿ࡶࡡࡳࡣࡰࠤࡨࡵ࡮ࡧ࡫ࡪ࠾ࠥࡪࡩࡤࡶ࠯ࠤࡹ࡫ࡳࡵࠢࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠢࡦࡳࡳ࡬ࡩࡨࠌࠣࠤࠥࠦࠠࠡࠢࠣ࠾ࡵࡧࡲࡢ࡯ࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡢࡷࡹࡸࡡࡵࡧࡪࡽ࠿ࠦࡳࡵࡴ࠯ࠤࡹ࡫ࡳࡵࠢࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡸࡺࡲࡢࡶࡨ࡫ࡾࠦ࡮ࡢ࡯ࡨࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣ⃺")
        self.config = config
        self.logger = logger
        self.bstack1llll11llll1_opy_ = bstack11l111_opy_ (u"ࠣࡶࡨࡷࡹࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲ࠴ࡧࡰࡪ࠱ࡹ࠵࠴ࡹࡰ࡭࡫ࡷ࠱ࡹ࡫ࡳࡵࡵࠥ⃻")
        self.bstack1llll11l1ll1_opy_ = None
        self.bstack1llll11l1l1l_opy_ = 60
        self.bstack1llll11l1lll_opy_ = 5
        self.bstack1llll1l1111l_opy_ = 0
    def bstack111l11111l1_opy_(self, test_files, orchestration_strategy, orchestration_metadata={}):
        bstack11l111_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡉ࡯࡫ࡷ࡭ࡦࡺࡥࡴࠢࡷ࡬ࡪࠦࡳࡱ࡮࡬ࡸࠥࡺࡥࡴࡶࡶࠤࡷ࡫ࡱࡶࡧࡶࡸࠥࡧ࡮ࡥࠢࡶࡸࡴࡸࡥࡴࠢࡷ࡬ࡪࠦࡲࡦࡵࡳࡳࡳࡹࡥࠡࡦࡤࡸࡦࠦࡦࡰࡴࠣࡴࡴࡲ࡬ࡪࡰࡪ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤ⃼")
        self.logger.debug(bstack11l111_opy_ (u"ࠥ࡟ࡸࡶ࡬ࡪࡶࡗࡩࡸࡺࡳ࡞ࠢࡌࡲ࡮ࡺࡩࡢࡶ࡬ࡲ࡬ࠦࡳࡱ࡮࡬ࡸࠥࡺࡥࡴࡶࡶࠤࡼ࡯ࡴࡩࠢࡶࡸࡷࡧࡴࡦࡩࡼ࠾ࠥࢁࡽࠣ⃽").format(orchestration_strategy))
        try:
            bstack1llll11lllll_opy_ = []
            bstack11l111_opy_ (u"ࠦࠧࠨࡗࡦࠢࡺ࡭ࡱࡲࠠ࡯ࡱࡷࠤ࡫࡫ࡴࡤࡪࠣ࡫࡮ࡺࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢ࡬ࡷࠥࡹ࡯ࡶࡴࡦࡩࠥ࡯ࡳࠡࡶࡼࡴࡪࠦ࡯ࡧࠢࡤࡶࡷࡧࡹࠡࡣࡱࡨࠥ࡯ࡴࠨࡵࠣࡩࡱ࡫࡭ࡦࡰࡷࡷࠥࡧࡲࡦࠢࡲࡪࠥࡺࡹࡱࡧࠣࡨ࡮ࡩࡴࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡢࡦࡥࡤࡹࡸ࡫ࠠࡪࡰࠣࡸ࡭ࡧࡴࠡࡥࡤࡷࡪ࠲ࠠࡶࡵࡨࡶࠥ࡮ࡡࡴࠢࡳࡶࡴࡼࡩࡥࡧࡧࠤࡲࡻ࡬ࡵ࡫࠰ࡶࡪࡶ࡯ࠡࡵࡲࡹࡷࡩࡥࠡࡹ࡬ࡸ࡭ࠦࡦࡦࡣࡷࡹࡷ࡫ࡂࡳࡣࡱࡧ࡭ࠦࡩ࡯ࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠣࠤࠥ⃾")
            source = orchestration_metadata[bstack11l111_opy_ (u"ࠬࡸࡵ࡯ࡡࡶࡱࡦࡸࡴࡠࡵࡨࡰࡪࡩࡴࡪࡱࡱࠫ⃿")].get(bstack11l111_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭℀"), [])
            bstack1llll11lll1l_opy_ = isinstance(source, list) and all(isinstance(src, dict) and src is not None for src in source) and len(source) > 0
            if orchestration_metadata[bstack11l111_opy_ (u"ࠧࡳࡷࡱࡣࡸࡳࡡࡳࡶࡢࡷࡪࡲࡥࡤࡶ࡬ࡳࡳ࠭℁")].get(bstack11l111_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩℂ"), False) and not bstack1llll11lll1l_opy_:
                bstack1llll11lllll_opy_ = bstack111ll1111l1_opy_(source) # bstack1llll11lll11_opy_-repo is handled bstack1llll11l1l11_opy_
            payload = {
                bstack11l111_opy_ (u"ࠤࡷࡩࡸࡺࡳࠣ℃"): [{bstack11l111_opy_ (u"ࠥࡪ࡮ࡲࡥࡑࡣࡷ࡬ࠧ℄"): f} for f in test_files],
                bstack11l111_opy_ (u"ࠦࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡗࡹࡸࡡࡵࡧࡪࡽࠧ℅"): orchestration_strategy,
                bstack11l111_opy_ (u"ࠧࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡒ࡫ࡴࡢࡦࡤࡸࡦࠨ℆"): orchestration_metadata,
                bstack11l111_opy_ (u"ࠨ࡮ࡰࡦࡨࡍࡳࡪࡥࡹࠤℇ"): int(os.environ.get(bstack11l111_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡎࡐࡆࡈࡣࡎࡔࡄࡆ࡚ࠥ℈")) or bstack11l111_opy_ (u"ࠣ࠲ࠥ℉")),
                bstack11l111_opy_ (u"ࠤࡷࡳࡹࡧ࡬ࡏࡱࡧࡩࡸࠨℊ"): int(os.environ.get(bstack11l111_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡓ࡙ࡇࡌࡠࡐࡒࡈࡊࡥࡃࡐࡗࡑࡘࠧℋ")) or bstack11l111_opy_ (u"ࠦ࠶ࠨℌ")),
                bstack11l111_opy_ (u"ࠧࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠥℍ"): self.config.get(bstack11l111_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫℎ"), bstack11l111_opy_ (u"ࠧࠨℏ")),
                bstack11l111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠦℐ"): self.config.get(bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬℑ"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack11l111_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡔࡸࡲࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠣℒ"): os.environ.get(bstack11l111_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆ࡚ࡏࡌࡅࡡࡕ࡙ࡓࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠥℓ"), bstack11l111_opy_ (u"ࠧࠨ℔")),
                bstack11l111_opy_ (u"ࠨࡨࡰࡵࡷࡍࡳ࡬࡯ࠣℕ"): get_host_info(),
                bstack11l111_opy_ (u"ࠢࡱࡴࡇࡩࡹࡧࡩ࡭ࡵࠥ№"): bstack1llll11lllll_opy_
            }
            self.logger.debug(bstack11l111_opy_ (u"ࠣ࡝ࡶࡴࡱ࡯ࡴࡕࡧࡶࡸࡸࡣࠠࡔࡧࡱࡨ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷ࠿ࠦࡻࡾࠤ℗").format(payload))
            response = bstack11l1lll1ll1_opy_.bstack1lllll111ll1_opy_(self.bstack1llll11llll1_opy_, payload)
            if response:
                self.bstack1llll11l1ll1_opy_ = self._1llll1l11111_opy_(response)
                self.logger.debug(bstack11l111_opy_ (u"ࠤ࡞ࡷࡵࡲࡩࡵࡖࡨࡷࡹࡹ࡝ࠡࡕࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠻ࠢࡾࢁࠧ℘").format(self.bstack1llll11l1ll1_opy_))
            else:
                self.logger.error(bstack11l111_opy_ (u"ࠥ࡟ࡸࡶ࡬ࡪࡶࡗࡩࡸࡺࡳ࡞ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡭ࡥࡵࠢࡶࡴࡱ࡯ࡴࠡࡶࡨࡷࡹࡹࠠࡳࡧࡶࡴࡴࡴࡳࡦ࠰ࠥℙ"))
        except Exception as e:
            self.logger.error(bstack11l111_opy_ (u"ࠦࡠࡹࡰ࡭࡫ࡷࡘࡪࡹࡴࡴ࡟ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡶࡩࡳࡪࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡨ࡬ࡰࡪࡹ࠺࠻ࠢࡾࢁࠧℚ").format(e))
    def _1llll1l11111_opy_(self, response):
        bstack11l111_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡓࡶࡴࡩࡥࡴࡵࡨࡷࠥࡺࡨࡦࠢࡶࡴࡱ࡯ࡴࠡࡶࡨࡷࡹࡹࠠࡂࡒࡌࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࠦࡡ࡯ࡦࠣࡩࡽࡺࡲࡢࡥࡷࡷࠥࡸࡥ࡭ࡧࡹࡥࡳࡺࠠࡧ࡫ࡨࡰࡩࡹ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧℛ")
        bstack1l11l11l_opy_ = {}
        bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࠢℜ")] = response.get(bstack11l111_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࠣℝ"), self.bstack1llll11l1l1l_opy_)
        bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡋࡱࡸࡪࡸࡶࡢ࡮ࠥ℞")] = response.get(bstack11l111_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࡌࡲࡹ࡫ࡲࡷࡣ࡯ࠦ℟"), self.bstack1llll11l1lll_opy_)
        bstack1llll11ll1ll_opy_ = response.get(bstack11l111_opy_ (u"ࠥࡶࡪࡹࡵ࡭ࡶࡘࡶࡱࠨ℠"))
        bstack1llll11ll11l_opy_ = response.get(bstack11l111_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸ࡚ࡸ࡬ࠣ℡"))
        if bstack1llll11ll1ll_opy_:
            bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠧࡸࡥࡴࡷ࡯ࡸ࡚ࡸ࡬ࠣ™")] = bstack1llll11ll1ll_opy_.split(bstack11l1l111lll_opy_ + bstack11l111_opy_ (u"ࠨ࠯ࠣ℣"))[1] if bstack11l1l111lll_opy_ + bstack11l111_opy_ (u"ࠢ࠰ࠤℤ") in bstack1llll11ll1ll_opy_ else bstack1llll11ll1ll_opy_
        else:
            bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠣࡴࡨࡷࡺࡲࡴࡖࡴ࡯ࠦ℥")] = None
        if bstack1llll11ll11l_opy_:
            bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࡘࡶࡱࠨΩ")] = bstack1llll11ll11l_opy_.split(bstack11l1l111lll_opy_ + bstack11l111_opy_ (u"ࠥ࠳ࠧ℧"))[1] if bstack11l1l111lll_opy_ + bstack11l111_opy_ (u"ࠦ࠴ࠨℨ") in bstack1llll11ll11l_opy_ else bstack1llll11ll11l_opy_
        else:
            bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹ࡛ࡲ࡭ࠤ℩")] = None
        if (
            response.get(bstack11l111_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࠢK")) is None or
            response.get(bstack11l111_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡊࡰࡷࡩࡷࡼࡡ࡭ࠤÅ")) is None or
            response.get(bstack11l111_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡗࡵࡰࠧℬ")) is None or
            response.get(bstack11l111_opy_ (u"ࠤࡵࡩࡸࡻ࡬ࡵࡗࡵࡰࠧℭ")) is None
        ):
            self.logger.debug(bstack11l111_opy_ (u"ࠥ࡟ࡵࡸ࡯ࡤࡧࡶࡷࡤࡹࡰ࡭࡫ࡷࡣࡹ࡫ࡳࡵࡵࡢࡶࡪࡹࡰࡰࡰࡶࡩࡢࠦࡒࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡰࡸࡰࡱࠦࡶࡢ࡮ࡸࡩ࠭ࡹࠩࠡࡨࡲࡶࠥࡹ࡯࡮ࡧࠣࡥࡹࡺࡲࡪࡤࡸࡸࡪࡹࠠࡪࡰࠣࡷࡵࡲࡩࡵࠢࡷࡩࡸࡺࡳࠡࡃࡓࡍࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠢ℮"))
        return bstack1l11l11l_opy_
    def bstack111l111111l_opy_(self):
        if not self.bstack1llll11l1ll1_opy_:
            self.logger.error(bstack11l111_opy_ (u"ࠦࡠ࡭ࡥࡵࡑࡵࡨࡪࡸࡥࡥࡖࡨࡷࡹࡌࡩ࡭ࡧࡶࡡࠥࡔ࡯ࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡧࡥࡹࡧࠠࡢࡸࡤ࡭ࡱࡧࡢ࡭ࡧࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡵࡲࡥࡧࡵࡩࡩࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵ࠱ࠦℯ"))
            return None
        bstack1llll1l111l1_opy_ = None
        test_files = []
        bstack1llll1l111ll_opy_ = int(time.time() * 1000) # bstack1llll11ll111_opy_ sec
        bstack1llll11l11ll_opy_ = int(self.bstack1llll11l1ll1_opy_.get(bstack11l111_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࡏ࡮ࡵࡧࡵࡺࡦࡲࠢℰ"), self.bstack1llll11l1lll_opy_))
        bstack1llll11ll1l1_opy_ = int(self.bstack1llll11l1ll1_opy_.get(bstack11l111_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࠢℱ"), self.bstack1llll11l1l1l_opy_)) * 1000
        bstack1llll11ll11l_opy_ = self.bstack1llll11l1ll1_opy_.get(bstack11l111_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡖࡴ࡯ࠦℲ"), None)
        bstack1llll11ll1ll_opy_ = self.bstack1llll11l1ll1_opy_.get(bstack11l111_opy_ (u"ࠣࡴࡨࡷࡺࡲࡴࡖࡴ࡯ࠦℳ"), None)
        if bstack1llll11ll1ll_opy_ is None and bstack1llll11ll11l_opy_ is None:
            return None
        try:
            while bstack1llll11ll1ll_opy_ and (time.time() * 1000 - bstack1llll1l111ll_opy_) < bstack1llll11ll1l1_opy_:
                response = bstack11l1lll1ll1_opy_.bstack1lllll1111l1_opy_(bstack1llll11ll1ll_opy_, {})
                if response and response.get(bstack11l111_opy_ (u"ࠤࡷࡩࡸࡺࡳࠣℴ")):
                    bstack1llll1l111l1_opy_ = response.get(bstack11l111_opy_ (u"ࠥࡸࡪࡹࡴࡴࠤℵ"))
                self.bstack1llll1l1111l_opy_ += 1
                if bstack1llll1l111l1_opy_:
                    break
                time.sleep(bstack1llll11l11ll_opy_)
                self.logger.debug(bstack11l111_opy_ (u"ࠦࡠ࡭ࡥࡵࡑࡵࡨࡪࡸࡥࡥࡖࡨࡷࡹࡌࡩ࡭ࡧࡶࡡࠥࡌࡥࡵࡥ࡫࡭ࡳ࡭ࠠࡰࡴࡧࡩࡷ࡫ࡤࠡࡶࡨࡷࡹࡹࠠࡧࡴࡲࡱࠥࡸࡥࡴࡷ࡯ࡸ࡛ࠥࡒࡍࠢࡤࡪࡹ࡫ࡲࠡࡹࡤ࡭ࡹ࡯࡮ࡨࠢࡩࡳࡷࠦࡻࡾࠢࡶࡩࡨࡵ࡮ࡥࡵ࠱ࠦℶ").format(bstack1llll11l11ll_opy_))
            if bstack1llll11ll11l_opy_ and not bstack1llll1l111l1_opy_:
                self.logger.debug(bstack11l111_opy_ (u"ࠧࡡࡧࡦࡶࡒࡶࡩ࡫ࡲࡦࡦࡗࡩࡸࡺࡆࡪ࡮ࡨࡷࡢࠦࡆࡦࡶࡦ࡬࡮ࡴࡧࠡࡱࡵࡨࡪࡸࡥࡥࠢࡷࡩࡸࡺࡳࠡࡨࡵࡳࡲࠦࡴࡪ࡯ࡨࡳࡺࡺࠠࡖࡔࡏࠦℷ"))
                response = bstack11l1lll1ll1_opy_.bstack1lllll1111l1_opy_(bstack1llll11ll11l_opy_, {})
                if response and response.get(bstack11l111_opy_ (u"ࠨࡴࡦࡵࡷࡷࠧℸ")):
                    bstack1llll1l111l1_opy_ = response.get(bstack11l111_opy_ (u"ࠢࡵࡧࡶࡸࡸࠨℹ"))
            if bstack1llll1l111l1_opy_ and len(bstack1llll1l111l1_opy_) > 0:
                for bstack111ll1l111_opy_ in bstack1llll1l111l1_opy_:
                    file_path = bstack111ll1l111_opy_.get(bstack11l111_opy_ (u"ࠣࡨ࡬ࡰࡪࡖࡡࡵࡪࠥ℺"))
                    if file_path:
                        test_files.append(file_path)
            if not bstack1llll1l111l1_opy_:
                return None
            self.logger.debug(bstack11l111_opy_ (u"ࠤ࡞࡫ࡪࡺࡏࡳࡦࡨࡶࡪࡪࡔࡦࡵࡷࡊ࡮ࡲࡥࡴ࡟ࠣࡓࡷࡪࡥࡳࡧࡧࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡴࡨࡧࡪ࡯ࡶࡦࡦ࠽ࠤࢀࢃࠢ℻").format(test_files))
            return test_files
        except Exception as e:
            self.logger.error(bstack11l111_opy_ (u"ࠥ࡟࡬࡫ࡴࡐࡴࡧࡩࡷ࡫ࡤࡕࡧࡶࡸࡋ࡯࡬ࡦࡵࡠࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡪࡪࡺࡣࡩ࡫ࡱ࡫ࠥࡵࡲࡥࡧࡵࡩࡩࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵ࠽ࠤࢀࢃࠢℼ").format(e))
            return None
    def bstack111l1111ll1_opy_(self):
        bstack11l111_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴࠢࡷ࡬ࡪࠦࡣࡰࡷࡱࡸࠥࡵࡦࠡࡵࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡁࡑࡋࠣࡧࡦࡲ࡬ࡴࠢࡰࡥࡩ࡫࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧℽ")
        return self.bstack1llll1l1111l_opy_