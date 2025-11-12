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
import logging
import os
import datetime
import threading
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11ll11l1l11_opy_, bstack11ll1l1l1ll_opy_, bstack111lllll1l_opy_, error_handler, bstack111llll1111_opy_, bstack111ll111lll_opy_, bstack11l111111ll_opy_, bstack1l11ll11l_opy_, bstack1l11lll1l1_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1lllll1l1111_opy_ import bstack1lllll11llll_opy_
import bstack_utils.bstack1ll1ll1l_opy_ as bstack11ll11lll_opy_
from bstack_utils.bstack111ll1l1l1_opy_ import bstack1l11lllll1_opy_
import bstack_utils.accessibility as bstack1lllll11l_opy_
from bstack_utils.bstack1ll11l1lll_opy_ import bstack1ll11l1lll_opy_
from bstack_utils.bstack111ll1l111_opy_ import bstack1111l1l11l_opy_
from bstack_utils.constants import bstack11l11ll1ll_opy_
bstack1lll1llll1l1_opy_ = bstack11l111_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡣࡰ࡮࡯ࡩࡨࡺ࡯ࡳ࠯ࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱࠬℾ")
logger = logging.getLogger(__name__)
class bstack11l11l1l_opy_:
    bstack1lllll1l1111_opy_ = None
    bs_config = None
    bstack1ll1lllll_opy_ = None
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack11l1l1111l1_opy_, stage=STAGE.bstack1l1l111l1_opy_)
    def launch(cls, bs_config, bstack1ll1lllll_opy_):
        cls.bs_config = bs_config
        cls.bstack1ll1lllll_opy_ = bstack1ll1lllll_opy_
        try:
            cls.bstack1llll111llll_opy_()
            bstack11ll1l11ll1_opy_ = bstack11ll11l1l11_opy_(bs_config)
            bstack11ll111l1l1_opy_ = bstack11ll1l1l1ll_opy_(bs_config)
            data = bstack11ll11lll_opy_.bstack1llll111l1l1_opy_(bs_config, bstack1ll1lllll_opy_)
            config = {
                bstack11l111_opy_ (u"࠭ࡡࡶࡶ࡫ࠫℿ"): (bstack11ll1l11ll1_opy_, bstack11ll111l1l1_opy_),
                bstack11l111_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨ⅀"): cls.default_headers()
            }
            response = bstack111lllll1l_opy_(bstack11l111_opy_ (u"ࠨࡒࡒࡗ࡙࠭⅁"), cls.request_url(bstack11l111_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠳࠱ࡥࡹ࡮ࡲࡤࡴࠩ⅂")), data, config)
            if response.status_code != 200:
                bstack1l11l11l_opy_ = response.json()
                if bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠪࡷࡺࡩࡣࡦࡵࡶࠫ⅃")] == False:
                    cls.bstack1llll1111111_opy_(bstack1l11l11l_opy_)
                    return
                cls.bstack1llll11l1111_opy_(bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ⅄")])
                cls.bstack1llll11l111l_opy_(bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬⅅ")])
                return None
            bstack1lll1lllll1l_opy_ = cls.bstack1llll111lll1_opy_(response)
            return bstack1lll1lllll1l_opy_, response.json()
        except Exception as error:
            logger.error(bstack11l111_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡺ࡬࡮ࡲࡥࠡࡥࡵࡩࡦࡺࡩ࡯ࡩࠣࡦࡺ࡯࡬ࡥࠢࡩࡳࡷࠦࡔࡦࡵࡷࡌࡺࡨ࠺ࠡࡽࢀࠦⅆ").format(str(error)))
            return None
    @classmethod
    @error_handler(class_method=True)
    def stop(cls, bstack1llll1111l11_opy_=None):
        if not bstack1l11lllll1_opy_.on() and not bstack1lllll11l_opy_.on():
            return
        if os.environ.get(bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫⅇ")) == bstack11l111_opy_ (u"ࠣࡰࡸࡰࡱࠨⅈ") or os.environ.get(bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧⅉ")) == bstack11l111_opy_ (u"ࠥࡲࡺࡲ࡬ࠣ⅊"):
            logger.error(bstack11l111_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡷࡹࡵࡰࠡࡤࡸ࡭ࡱࡪࠠࡳࡧࡴࡹࡪࡹࡴࠡࡶࡲࠤ࡙࡫ࡳࡵࡊࡸࡦ࠿ࠦࡍࡪࡵࡶ࡭ࡳ࡭ࠠࡢࡷࡷ࡬ࡪࡴࡴࡪࡥࡤࡸ࡮ࡵ࡮ࠡࡶࡲ࡯ࡪࡴࠧ⅋"))
            return {
                bstack11l111_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ⅌"): bstack11l111_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ⅍"),
                bstack11l111_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨⅎ"): bstack11l111_opy_ (u"ࠨࡖࡲ࡯ࡪࡴ࠯ࡣࡷ࡬ࡰࡩࡏࡄࠡ࡫ࡶࠤࡺࡴࡤࡦࡨ࡬ࡲࡪࡪࠬࠡࡤࡸ࡭ࡱࡪࠠࡤࡴࡨࡥࡹ࡯࡯࡯ࠢࡰ࡭࡬࡮ࡴࠡࡪࡤࡺࡪࠦࡦࡢ࡫࡯ࡩࡩ࠭⅏")
            }
        try:
            cls.bstack1lllll1l1111_opy_.shutdown()
            data = {
                bstack11l111_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⅐"): bstack1l11ll11l_opy_()
            }
            if not bstack1llll1111l11_opy_ is None:
                data[bstack11l111_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡳࡥࡵࡣࡧࡥࡹࡧࠧ⅑")] = [{
                    bstack11l111_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫ⅒"): bstack11l111_opy_ (u"ࠬࡻࡳࡦࡴࡢ࡯࡮ࡲ࡬ࡦࡦࠪ⅓"),
                    bstack11l111_opy_ (u"࠭ࡳࡪࡩࡱࡥࡱ࠭⅔"): bstack1llll1111l11_opy_
                }]
            config = {
                bstack11l111_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨ⅕"): cls.default_headers()
            }
            bstack11l1llll1l1_opy_ = bstack11l111_opy_ (u"ࠨࡣࡳ࡭࠴ࡼ࠱࠰ࡤࡸ࡭ࡱࡪࡳ࠰ࡽࢀ࠳ࡸࡺ࡯ࡱࠩ⅖").format(os.environ[bstack11l111_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠢ⅗")])
            bstack1lll1llllll1_opy_ = cls.request_url(bstack11l1llll1l1_opy_)
            response = bstack111lllll1l_opy_(bstack11l111_opy_ (u"ࠪࡔ࡚࡚ࠧ⅘"), bstack1lll1llllll1_opy_, data, config)
            if not response.ok:
                raise Exception(bstack11l111_opy_ (u"ࠦࡘࡺ࡯ࡱࠢࡵࡩࡶࡻࡥࡴࡶࠣࡲࡴࡺࠠࡰ࡭ࠥ⅙"))
        except Exception as error:
            logger.error(bstack11l111_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸࡺ࡯ࡱࠢࡥࡹ࡮ࡲࡤࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡷࡳ࡚ࠥࡥࡴࡶࡋࡹࡧࡀ࠺ࠡࠤ⅚") + str(error))
            return {
                bstack11l111_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭⅛"): bstack11l111_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭⅜"),
                bstack11l111_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ⅝"): str(error)
            }
    @classmethod
    @error_handler(class_method=True)
    def bstack1llll111lll1_opy_(cls, response):
        bstack1l11l11l_opy_ = response.json() if not isinstance(response, dict) else response
        bstack1lll1lllll1l_opy_ = {}
        if bstack1l11l11l_opy_.get(bstack11l111_opy_ (u"ࠩ࡭ࡻࡹ࠭⅞")) is None:
            os.environ[bstack11l111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ⅟")] = bstack11l111_opy_ (u"ࠫࡳࡻ࡬࡭ࠩⅠ")
        else:
            os.environ[bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩⅡ")] = bstack1l11l11l_opy_.get(bstack11l111_opy_ (u"࠭ࡪࡸࡶࠪⅢ"), bstack11l111_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬⅣ"))
        os.environ[bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭Ⅴ")] = bstack1l11l11l_opy_.get(bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫⅥ"), bstack11l111_opy_ (u"ࠪࡲࡺࡲ࡬ࠨⅦ"))
        logger.info(bstack11l111_opy_ (u"࡙ࠫ࡫ࡳࡵࡪࡸࡦࠥࡹࡴࡢࡴࡷࡩࡩࠦࡷࡪࡶ࡫ࠤ࡮ࡪ࠺ࠡࠩⅧ") + os.getenv(bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪⅨ")));
        if bstack1l11lllll1_opy_.bstack1lll1lllll11_opy_(cls.bs_config, cls.bstack1ll1lllll_opy_.get(bstack11l111_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡸࡷࡪࡪࠧⅩ"), bstack11l111_opy_ (u"ࠧࠨⅪ"))) is True:
            bstack1lllll11111l_opy_, build_hashed_id, bstack1llll1111l1l_opy_ = cls.bstack1llll111l11l_opy_(bstack1l11l11l_opy_)
            if bstack1lllll11111l_opy_ != None and build_hashed_id != None:
                bstack1lll1lllll1l_opy_[bstack11l111_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨⅫ")] = {
                    bstack11l111_opy_ (u"ࠩ࡭ࡻࡹࡥࡴࡰ࡭ࡨࡲࠬⅬ"): bstack1lllll11111l_opy_,
                    bstack11l111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬⅭ"): build_hashed_id,
                    bstack11l111_opy_ (u"ࠫࡦࡲ࡬ࡰࡹࡢࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࡳࠨⅮ"): bstack1llll1111l1l_opy_
                }
            else:
                bstack1lll1lllll1l_opy_[bstack11l111_opy_ (u"ࠬࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬⅯ")] = {}
        else:
            bstack1lll1lllll1l_opy_[bstack11l111_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭ⅰ")] = {}
        bstack1llll111l111_opy_, build_hashed_id = cls.bstack1llll111ll1l_opy_(bstack1l11l11l_opy_)
        if bstack1llll111l111_opy_ != None and build_hashed_id != None:
            bstack1lll1lllll1l_opy_[bstack11l111_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧⅱ")] = {
                bstack11l111_opy_ (u"ࠨࡣࡸࡸ࡭ࡥࡴࡰ࡭ࡨࡲࠬⅲ"): bstack1llll111l111_opy_,
                bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫⅳ"): build_hashed_id,
            }
        else:
            bstack1lll1lllll1l_opy_[bstack11l111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪⅴ")] = {}
        if bstack1lll1lllll1l_opy_[bstack11l111_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫⅵ")].get(bstack11l111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧⅶ")) != None or bstack1lll1lllll1l_opy_[bstack11l111_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ⅷ")].get(bstack11l111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩⅸ")) != None:
            cls.bstack1lll1lllllll_opy_(bstack1l11l11l_opy_.get(bstack11l111_opy_ (u"ࠨ࡬ࡺࡸࠬⅹ")), bstack1l11l11l_opy_.get(bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫⅺ")))
        return bstack1lll1lllll1l_opy_
    @classmethod
    def bstack1llll111l11l_opy_(cls, bstack1l11l11l_opy_):
        if bstack1l11l11l_opy_.get(bstack11l111_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪⅻ")) == None:
            cls.bstack1llll11l1111_opy_()
            return [None, None, None]
        if bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫⅼ")][bstack11l111_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭ⅽ")] != True:
            cls.bstack1llll11l1111_opy_(bstack1l11l11l_opy_[bstack11l111_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭ⅾ")])
            return [None, None, None]
        logger.debug(bstack11l111_opy_ (u"ࠧࡼࡿࠣࡆࡺ࡯࡬ࡥࠢࡦࡶࡪࡧࡴࡪࡱࡱࠤࡘࡻࡣࡤࡧࡶࡷ࡫ࡻ࡬ࠢࠩⅿ").format(bstack11l11ll1ll_opy_))
        os.environ[bstack11l111_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡈࡕࡍࡑࡎࡈࡘࡊࡊࠧↀ")] = bstack11l111_opy_ (u"ࠩࡷࡶࡺ࡫ࠧↁ")
        if bstack1l11l11l_opy_.get(bstack11l111_opy_ (u"ࠪ࡮ࡼࡺࠧↂ")):
            os.environ[bstack11l111_opy_ (u"ࠫࡈࡘࡅࡅࡇࡑࡘࡎࡇࡌࡔࡡࡉࡓࡗࡥࡃࡓࡃࡖࡌࡤࡘࡅࡑࡑࡕࡘࡎࡔࡇࠨↃ")] = json.dumps({
                bstack11l111_opy_ (u"ࠬࡻࡳࡦࡴࡱࡥࡲ࡫ࠧↄ"): bstack11ll11l1l11_opy_(cls.bs_config),
                bstack11l111_opy_ (u"࠭ࡰࡢࡵࡶࡻࡴࡸࡤࠨↅ"): bstack11ll1l1l1ll_opy_(cls.bs_config)
            })
        if bstack1l11l11l_opy_.get(bstack11l111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩↆ")):
            os.environ[bstack11l111_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡍࡇࡓࡉࡇࡇࡣࡎࡊࠧↇ")] = bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫↈ")]
        if bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪ↉")].get(bstack11l111_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬ↊"), {}).get(bstack11l111_opy_ (u"ࠬࡧ࡬࡭ࡱࡺࡣࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࡴࠩ↋")):
            os.environ[bstack11l111_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡅࡑࡒࡏࡘࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࡙ࠧ↌")] = str(bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧ↍")][bstack11l111_opy_ (u"ࠨࡱࡳࡸ࡮ࡵ࡮ࡴࠩ↎")][bstack11l111_opy_ (u"ࠩࡤࡰࡱࡵࡷࡠࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࡸ࠭↏")])
        else:
            os.environ[bstack11l111_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡂࡎࡏࡓ࡜ࡥࡓࡄࡔࡈࡉࡓ࡙ࡈࡐࡖࡖࠫ←")] = bstack11l111_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ↑")
        return [bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠬࡰࡷࡵࠩ→")], bstack1l11l11l_opy_[bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨ↓")], os.environ[bstack11l111_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡆࡒࡌࡐ࡙ࡢࡗࡈࡘࡅࡆࡐࡖࡌࡔ࡚ࡓࠨ↔")]]
    @classmethod
    def bstack1llll111ll1l_opy_(cls, bstack1l11l11l_opy_):
        if bstack1l11l11l_opy_.get(bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ↕")) == None:
            cls.bstack1llll11l111l_opy_()
            return [None, None]
        if bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ↖")][bstack11l111_opy_ (u"ࠪࡷࡺࡩࡣࡦࡵࡶࠫ↗")] != True:
            cls.bstack1llll11l111l_opy_(bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ↘")])
            return [None, None]
        if bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ↙")].get(bstack11l111_opy_ (u"࠭࡯ࡱࡶ࡬ࡳࡳࡹࠧ↚")):
            logger.debug(bstack11l111_opy_ (u"ࠧࡕࡧࡶࡸࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡈࡵࡪ࡮ࡧࠤࡨࡸࡥࡢࡶ࡬ࡳࡳࠦࡓࡶࡥࡦࡩࡸࡹࡦࡶ࡮ࠤࠫ↛"))
            parsed = json.loads(os.getenv(bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩ↜"), bstack11l111_opy_ (u"ࠩࡾࢁࠬ↝")))
            capabilities = bstack11ll11lll_opy_.bstack1llll1111ll1_opy_(bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ↞")][bstack11l111_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬ↟")][bstack11l111_opy_ (u"ࠬࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫ↠")], bstack11l111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ↡"), bstack11l111_opy_ (u"ࠧࡷࡣ࡯ࡹࡪ࠭↢"))
            bstack1llll111l111_opy_ = capabilities[bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡕࡱ࡮ࡩࡳ࠭↣")]
            os.environ[bstack11l111_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧ↤")] = bstack1llll111l111_opy_
            if bstack11l111_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷࡩࠧ↥") in bstack1l11l11l_opy_ and bstack1l11l11l_opy_.get(bstack11l111_opy_ (u"ࠦࡦࡶࡰࡠࡣࡸࡸࡴࡳࡡࡵࡧࠥ↦")) is None:
                parsed[bstack11l111_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭↧")] = capabilities[bstack11l111_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ↨")]
            os.environ[bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨ↩")] = json.dumps(parsed)
            scripts = bstack11ll11lll_opy_.bstack1llll1111ll1_opy_(bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ↪")][bstack11l111_opy_ (u"ࠩࡲࡴࡹ࡯࡯࡯ࡵࠪ↫")][bstack11l111_opy_ (u"ࠪࡷࡨࡸࡩࡱࡶࡶࠫ↬")], bstack11l111_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ↭"), bstack11l111_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩ࠭↮"))
            bstack1ll11l1lll_opy_.bstack111lllll1_opy_(scripts)
            commands = bstack1l11l11l_opy_[bstack11l111_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭↯")][bstack11l111_opy_ (u"ࠧࡰࡲࡷ࡭ࡴࡴࡳࠨ↰")][bstack11l111_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࡵࡗࡳ࡜ࡸࡡࡱࠩ↱")].get(bstack11l111_opy_ (u"ࠩࡦࡳࡲࡳࡡ࡯ࡦࡶࠫ↲"))
            bstack1ll11l1lll_opy_.bstack11ll11ll1l1_opy_(commands)
            bstack11ll1111l1l_opy_ = capabilities.get(bstack11l111_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨ↳"))
            bstack1ll11l1lll_opy_.bstack11l1llllll1_opy_(bstack11ll1111l1l_opy_)
            bstack1ll11l1lll_opy_.store()
        return [bstack1llll111l111_opy_, bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭↴")]]
    @classmethod
    def bstack1llll11l1111_opy_(cls, response=None):
        os.environ[bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪ↵")] = bstack11l111_opy_ (u"࠭࡮ࡶ࡮࡯ࠫ↶")
        os.environ[bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ↷")] = bstack11l111_opy_ (u"ࠨࡰࡸࡰࡱ࠭↸")
        os.environ[bstack11l111_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡂࡖࡋࡏࡈࡤࡉࡏࡎࡒࡏࡉ࡙ࡋࡄࠨ↹")] = bstack11l111_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩ↺")
        os.environ[bstack11l111_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡔࡖࡓࡠࡄࡘࡍࡑࡊ࡟ࡉࡃࡖࡌࡊࡊ࡟ࡊࡆࠪ↻")] = bstack11l111_opy_ (u"ࠧࡴࡵ࡭࡮ࠥ↼")
        os.environ[bstack11l111_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡅࡑࡒࡏࡘࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࡙ࠧ↽")] = bstack11l111_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧ↾")
        cls.bstack1llll1111111_opy_(response, bstack11l111_opy_ (u"ࠣࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠣ↿"))
        return [None, None, None]
    @classmethod
    def bstack1llll11l111l_opy_(cls, response=None):
        os.environ[bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ⇀")] = bstack11l111_opy_ (u"ࠪࡲࡺࡲ࡬ࠨ⇁")
        os.environ[bstack11l111_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩ⇂")] = bstack11l111_opy_ (u"ࠬࡴࡵ࡭࡮ࠪ⇃")
        os.environ[bstack11l111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ⇄")] = bstack11l111_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬ⇅")
        cls.bstack1llll1111111_opy_(response, bstack11l111_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠣ⇆"))
        return [None, None, None]
    @classmethod
    def bstack1lll1lllllll_opy_(cls, jwt, build_hashed_id):
        os.environ[bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭⇇")] = jwt
        os.environ[bstack11l111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨ⇈")] = build_hashed_id
    @classmethod
    def bstack1llll1111111_opy_(cls, response=None, product=bstack11l111_opy_ (u"ࠦࠧ⇉")):
        if response == None or response.get(bstack11l111_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࡷࠬ⇊")) == None:
            logger.error(product + bstack11l111_opy_ (u"ࠨࠠࡃࡷ࡬ࡰࡩࠦࡣࡳࡧࡤࡸ࡮ࡵ࡮ࠡࡨࡤ࡭ࡱ࡫ࡤࠣ⇋"))
            return
        for error in response[bstack11l111_opy_ (u"ࠧࡦࡴࡵࡳࡷࡹࠧ⇌")]:
            bstack11l1111l111_opy_ = error[bstack11l111_opy_ (u"ࠨ࡭ࡨࡽࠬ⇍")]
            error_message = error[bstack11l111_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ⇎")]
            if error_message:
                if bstack11l1111l111_opy_ == bstack11l111_opy_ (u"ࠥࡉࡗࡘࡏࡓࡡࡄࡇࡈࡋࡓࡔࡡࡇࡉࡓࡏࡅࡅࠤ⇏"):
                    logger.info(error_message)
                else:
                    logger.error(error_message)
            else:
                logger.error(bstack11l111_opy_ (u"ࠦࡉࡧࡴࡢࠢࡸࡴࡱࡵࡡࡥࠢࡷࡳࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࠧ⇐") + product + bstack11l111_opy_ (u"ࠧࠦࡦࡢ࡫࡯ࡩࡩࠦࡤࡶࡧࠣࡸࡴࠦࡳࡰ࡯ࡨࠤࡪࡸࡲࡰࡴࠥ⇑"))
    @classmethod
    def bstack1llll111llll_opy_(cls):
        if cls.bstack1lllll1l1111_opy_ is not None:
            return
        cls.bstack1lllll1l1111_opy_ = bstack1lllll11llll_opy_(cls.bstack1llll11111l1_opy_)
        cls.bstack1lllll1l1111_opy_.start()
    @classmethod
    def bstack1111lll1ll_opy_(cls):
        if cls.bstack1lllll1l1111_opy_ is None:
            return
        cls.bstack1lllll1l1111_opy_.shutdown()
    @classmethod
    @error_handler(class_method=True)
    def bstack1llll11111l1_opy_(cls, bstack1111ll11ll_opy_, event_url=bstack11l111_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠶࠵ࡢࡢࡶࡦ࡬ࠬ⇒")):
        config = {
            bstack11l111_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨ⇓"): cls.default_headers()
        }
        logger.debug(bstack11l111_opy_ (u"ࠣࡲࡲࡷࡹࡥࡤࡢࡶࡤ࠾࡙ࠥࡥ࡯ࡦ࡬ࡲ࡬ࠦࡤࡢࡶࡤࠤࡹࡵࠠࡵࡧࡶࡸ࡭ࡻࡢࠡࡨࡲࡶࠥ࡫ࡶࡦࡰࡷࡷࠥࢁࡽࠣ⇔").format(bstack11l111_opy_ (u"ࠩ࠯ࠤࠬ⇕").join([event[bstack11l111_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ⇖")] for event in bstack1111ll11ll_opy_])))
        response = bstack111lllll1l_opy_(bstack11l111_opy_ (u"ࠫࡕࡕࡓࡕࠩ⇗"), cls.request_url(event_url), bstack1111ll11ll_opy_, config)
        bstack11ll11lll11_opy_ = response.json()
    @classmethod
    def bstack1llll11l_opy_(cls, bstack1111ll11ll_opy_, event_url=bstack11l111_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠵࠴ࡨࡡࡵࡥ࡫ࠫ⇘")):
        logger.debug(bstack11l111_opy_ (u"ࠨࡳࡦࡰࡧࡣࡩࡧࡴࡢ࠼ࠣࡅࡹࡺࡥ࡮ࡲࡷ࡭ࡳ࡭ࠠࡵࡱࠣࡥࡩࡪࠠࡥࡣࡷࡥࠥࡺ࡯ࠡࡤࡤࡸࡨ࡮ࠠࡸ࡫ࡷ࡬ࠥ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦ࠼ࠣࡿࢂࠨ⇙").format(bstack1111ll11ll_opy_[bstack11l111_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ⇚")]))
        if not bstack11ll11lll_opy_.bstack1llll111ll11_opy_(bstack1111ll11ll_opy_[bstack11l111_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬ⇛")]):
            logger.debug(bstack11l111_opy_ (u"ࠤࡶࡩࡳࡪ࡟ࡥࡣࡷࡥ࠿ࠦࡎࡰࡶࠣࡥࡩࡪࡩ࡯ࡩࠣࡨࡦࡺࡡࠡࡹ࡬ࡸ࡭ࠦࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧ࠽ࠤࢀࢃࠢ⇜").format(bstack1111ll11ll_opy_[bstack11l111_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ⇝")]))
            return
        bstack11l11lll1l_opy_ = bstack11ll11lll_opy_.bstack1llll111111l_opy_(bstack1111ll11ll_opy_[bstack11l111_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ⇞")], bstack1111ll11ll_opy_.get(bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴࠧ⇟")))
        if bstack11l11lll1l_opy_ != None:
            if bstack1111ll11ll_opy_.get(bstack11l111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࠨ⇠")) != None:
                bstack1111ll11ll_opy_[bstack11l111_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࠩ⇡")][bstack11l111_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࡡࡰࡥࡵ࠭⇢")] = bstack11l11lll1l_opy_
            else:
                bstack1111ll11ll_opy_[bstack11l111_opy_ (u"ࠩࡳࡶࡴࡪࡵࡤࡶࡢࡱࡦࡶࠧ⇣")] = bstack11l11lll1l_opy_
        if event_url == bstack11l111_opy_ (u"ࠪࡥࡵ࡯࠯ࡷ࠳࠲ࡦࡦࡺࡣࡩࠩ⇤"):
            cls.bstack1llll111llll_opy_()
            logger.debug(bstack11l111_opy_ (u"ࠦࡸ࡫࡮ࡥࡡࡧࡥࡹࡧ࠺ࠡࡃࡧࡨ࡮ࡴࡧࠡࡦࡤࡸࡦࠦࡴࡰࠢࡥࡥࡹࡩࡨࠡࡹ࡬ࡸ࡭ࠦࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧ࠽ࠤࢀࢃࠢ⇥").format(bstack1111ll11ll_opy_[bstack11l111_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ⇦")]))
            cls.bstack1lllll1l1111_opy_.add(bstack1111ll11ll_opy_)
        elif event_url == bstack11l111_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠶࠵ࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࡶࠫ⇧"):
            cls.bstack1llll11111l1_opy_([bstack1111ll11ll_opy_], event_url)
    @classmethod
    @error_handler(class_method=True)
    def bstack1l111lll1_opy_(cls, logs):
        for log in logs:
            bstack1lll1llll1ll_opy_ = {
                bstack11l111_opy_ (u"ࠧ࡬࡫ࡱࡨࠬ⇨"): bstack11l111_opy_ (u"ࠨࡖࡈࡗ࡙ࡥࡌࡐࡉࠪ⇩"),
                bstack11l111_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ⇪"): log[bstack11l111_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩ⇫")],
                bstack11l111_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧ⇬"): log[bstack11l111_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨ⇭")],
                bstack11l111_opy_ (u"࠭ࡨࡵࡶࡳࡣࡷ࡫ࡳࡱࡱࡱࡷࡪ࠭⇮"): {},
                bstack11l111_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ⇯"): log[bstack11l111_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ⇰")],
            }
            if bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⇱") in log:
                bstack1lll1llll1ll_opy_[bstack11l111_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⇲")] = log[bstack11l111_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ⇳")]
            elif bstack11l111_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⇴") in log:
                bstack1lll1llll1ll_opy_[bstack11l111_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⇵")] = log[bstack11l111_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ⇶")]
            cls.bstack1llll11l_opy_({
                bstack11l111_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬ⇷"): bstack11l111_opy_ (u"ࠩࡏࡳ࡬ࡉࡲࡦࡣࡷࡩࡩ࠭⇸"),
                bstack11l111_opy_ (u"ࠪࡰࡴ࡭ࡳࠨ⇹"): [bstack1lll1llll1ll_opy_]
            })
    @classmethod
    @error_handler(class_method=True)
    def bstack1llll111l1ll_opy_(cls, steps):
        bstack1llll11l11l1_opy_ = []
        for step in steps:
            bstack1llll1111lll_opy_ = {
                bstack11l111_opy_ (u"ࠫࡰ࡯࡮ࡥࠩ⇺"): bstack11l111_opy_ (u"࡚ࠬࡅࡔࡖࡢࡗ࡙ࡋࡐࠨ⇻"),
                bstack11l111_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬ⇼"): step[bstack11l111_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭⇽")],
                bstack11l111_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ⇾"): step[bstack11l111_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬ⇿")],
                bstack11l111_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ∀"): step[bstack11l111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ∁")],
                bstack11l111_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴࠧ∂"): step[bstack11l111_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࠨ∃")]
            }
            if bstack11l111_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ∄") in step:
                bstack1llll1111lll_opy_[bstack11l111_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ∅")] = step[bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ∆")]
            elif bstack11l111_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ∇") in step:
                bstack1llll1111lll_opy_[bstack11l111_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ∈")] = step[bstack11l111_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ∉")]
            bstack1llll11l11l1_opy_.append(bstack1llll1111lll_opy_)
        cls.bstack1llll11l_opy_({
            bstack11l111_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪ∊"): bstack11l111_opy_ (u"ࠧࡍࡱࡪࡇࡷ࡫ࡡࡵࡧࡧࠫ∋"),
            bstack11l111_opy_ (u"ࠨ࡮ࡲ࡫ࡸ࠭∌"): bstack1llll11l11l1_opy_
        })
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack1l111lll11_opy_, stage=STAGE.bstack1l1l111l1_opy_)
    def bstack11l11111ll_opy_(cls, screenshot):
        cls.bstack1llll11l_opy_({
            bstack11l111_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭∍"): bstack11l111_opy_ (u"ࠪࡐࡴ࡭ࡃࡳࡧࡤࡸࡪࡪࠧ∎"),
            bstack11l111_opy_ (u"ࠫࡱࡵࡧࡴࠩ∏"): [{
                bstack11l111_opy_ (u"ࠬࡱࡩ࡯ࡦࠪ∐"): bstack11l111_opy_ (u"࠭ࡔࡆࡕࡗࡣࡘࡉࡒࡆࡇࡑࡗࡍࡕࡔࠨ∑"),
                bstack11l111_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪ−"): datetime.datetime.utcnow().isoformat() + bstack11l111_opy_ (u"ࠨ࡜ࠪ∓"),
                bstack11l111_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ∔"): screenshot[bstack11l111_opy_ (u"ࠪ࡭ࡲࡧࡧࡦࠩ∕")],
                bstack11l111_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ∖"): screenshot[bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ∗")]
            }]
        }, event_url=bstack11l111_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠶࠵ࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࡶࠫ∘"))
    @classmethod
    @error_handler(class_method=True)
    def bstack11ll1lll11_opy_(cls, driver):
        current_test_uuid = cls.current_test_uuid()
        if not current_test_uuid:
            return
        cls.bstack1llll11l_opy_({
            bstack11l111_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ∙"): bstack11l111_opy_ (u"ࠨࡅࡅࡘࡘ࡫ࡳࡴ࡫ࡲࡲࡈࡸࡥࡢࡶࡨࡨࠬ√"),
            bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࠫ∛"): {
                bstack11l111_opy_ (u"ࠥࡹࡺ࡯ࡤࠣ∜"): cls.current_test_uuid(),
                bstack11l111_opy_ (u"ࠦ࡮ࡴࡴࡦࡩࡵࡥࡹ࡯࡯࡯ࡵࠥ∝"): cls.bstack111l1ll11l_opy_(driver)
            }
        })
    @classmethod
    def bstack111ll11lll_opy_(cls, event: str, bstack1111ll11ll_opy_: bstack1111l1l11l_opy_):
        bstack111l111ll1_opy_ = {
            bstack11l111_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ∞"): event,
            bstack1111ll11ll_opy_.bstack111l11111l_opy_(): bstack1111ll11ll_opy_.bstack111l1l1ll1_opy_(event)
        }
        cls.bstack1llll11l_opy_(bstack111l111ll1_opy_)
        result = getattr(bstack1111ll11ll_opy_, bstack11l111_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭∟"), None)
        if event == bstack11l111_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ∠"):
            threading.current_thread().bstackTestMeta = {bstack11l111_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ∡"): bstack11l111_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪ∢")}
        elif event == bstack11l111_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ∣"):
            threading.current_thread().bstackTestMeta = {bstack11l111_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ∤"): getattr(result, bstack11l111_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ∥"), bstack11l111_opy_ (u"࠭ࠧ∦"))}
    @classmethod
    def on(cls):
        if (os.environ.get(bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ∧"), None) is None or os.environ[bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬ∨")] == bstack11l111_opy_ (u"ࠤࡱࡹࡱࡲࠢ∩")) and (os.environ.get(bstack11l111_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨ∪"), None) is None or os.environ[bstack11l111_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩ∫")] == bstack11l111_opy_ (u"ࠧࡴࡵ࡭࡮ࠥ∬")):
            return False
        return True
    @staticmethod
    def bstack1llll11111ll_opy_(func):
        def wrap(*args, **kwargs):
            if bstack11l11l1l_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def default_headers():
        headers = {
            bstack11l111_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬ∭"): bstack11l111_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪ∮"),
            bstack11l111_opy_ (u"ࠨ࡚࠰ࡆࡘ࡚ࡁࡄࡍ࠰ࡘࡊ࡙ࡔࡐࡒࡖࠫ∯"): bstack11l111_opy_ (u"ࠩࡷࡶࡺ࡫ࠧ∰")
        }
        if os.environ.get(bstack11l111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ∱"), None):
            headers[bstack11l111_opy_ (u"ࠫࡆࡻࡴࡩࡱࡵ࡭ࡿࡧࡴࡪࡱࡱࠫ∲")] = bstack11l111_opy_ (u"ࠬࡈࡥࡢࡴࡨࡶࠥࢁࡽࠨ∳").format(os.environ[bstack11l111_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠥ∴")])
        return headers
    @staticmethod
    def request_url(url):
        return bstack11l111_opy_ (u"ࠧࡼࡿ࠲ࡿࢂ࠭∵").format(bstack1lll1llll1l1_opy_, url)
    @staticmethod
    def current_test_uuid():
        return getattr(threading.current_thread(), bstack11l111_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬ∶"), None)
    @staticmethod
    def bstack111l1ll11l_opy_(driver):
        return {
            bstack111llll1111_opy_(): bstack111ll111lll_opy_(driver)
        }
    @staticmethod
    def bstack1lll1llll11l_opy_(exception_info, report):
        return [{bstack11l111_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬ∷"): [exception_info.exconly(), report.longreprtext]}]
    @staticmethod
    def bstack1llllll1lll_opy_(typename):
        if bstack11l111_opy_ (u"ࠥࡅࡸࡹࡥࡳࡶ࡬ࡳࡳࠨ∸") in typename:
            return bstack11l111_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࡅࡳࡴࡲࡶࠧ∹")
        return bstack11l111_opy_ (u"࡛ࠧ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷࠨ∺")