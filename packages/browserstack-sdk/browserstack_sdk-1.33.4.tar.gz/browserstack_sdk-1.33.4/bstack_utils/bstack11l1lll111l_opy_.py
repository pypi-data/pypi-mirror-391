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
import requests
from urllib.parse import urljoin, urlencode
from datetime import datetime
import os
import logging
import json
from bstack_utils.constants import bstack11l1l111lll_opy_
logger = logging.getLogger(__name__)
class bstack11l1lll1ll1_opy_:
    @staticmethod
    def results(builder,params=None):
        bstack1lllll111111_opy_ = urljoin(builder, bstack11l111_opy_ (u"ࠪ࡭ࡸࡹࡵࡦࡵࠪ‹"))
        if params:
            bstack1lllll111111_opy_ += bstack11l111_opy_ (u"ࠦࡄࢁࡽࠣ›").format(urlencode({bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ※"): params.get(bstack11l111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭‼"))}))
        return bstack11l1lll1ll1_opy_.bstack1llll1llll1l_opy_(bstack1lllll111111_opy_)
    @staticmethod
    def bstack11l1lll1l1l_opy_(builder,params=None):
        bstack1lllll111111_opy_ = urljoin(builder, bstack11l111_opy_ (u"ࠧࡪࡵࡶࡹࡪࡹ࠭ࡴࡷࡰࡱࡦࡸࡹࠨ‽"))
        if params:
            bstack1lllll111111_opy_ += bstack11l111_opy_ (u"ࠣࡁࡾࢁࠧ‾").format(urlencode({bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ‿"): params.get(bstack11l111_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⁀"))}))
        return bstack11l1lll1ll1_opy_.bstack1llll1llll1l_opy_(bstack1lllll111111_opy_)
    @staticmethod
    def bstack1llll1llll1l_opy_(bstack1llll1lllll1_opy_):
        bstack1lllll11111l_opy_ = os.environ.get(bstack11l111_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩ⁁"), os.environ.get(bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩ⁂"), bstack11l111_opy_ (u"࠭ࠧ⁃")))
        headers = {bstack11l111_opy_ (u"ࠧࡂࡷࡷ࡬ࡴࡸࡩࡻࡣࡷ࡭ࡴࡴࠧ⁄"): bstack11l111_opy_ (u"ࠨࡄࡨࡥࡷ࡫ࡲࠡࡽࢀࠫ⁅").format(bstack1lllll11111l_opy_)}
        response = requests.get(bstack1llll1lllll1_opy_, headers=headers)
        bstack1llll1llllll_opy_ = {}
        try:
            bstack1llll1llllll_opy_ = response.json()
        except Exception as e:
            logger.debug(bstack11l111_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡶࡡࡳࡵࡨࠤࡏ࡙ࡏࡏࠢࡵࡩࡸࡶ࡯࡯ࡵࡨ࠾ࠥࢁࡽࠣ⁆").format(e))
            pass
        if bstack1llll1llllll_opy_ is not None:
            bstack1llll1llllll_opy_[bstack11l111_opy_ (u"ࠪࡲࡪࡾࡴࡠࡲࡲࡰࡱࡥࡴࡪ࡯ࡨࠫ⁇")] = response.headers.get(bstack11l111_opy_ (u"ࠫࡳ࡫ࡸࡵࡡࡳࡳࡱࡲ࡟ࡵ࡫ࡰࡩࠬ⁈"), str(int(datetime.now().timestamp() * 1000)))
            bstack1llll1llllll_opy_[bstack11l111_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ⁉")] = response.status_code
        return bstack1llll1llllll_opy_
    @staticmethod
    def bstack1lllll111ll1_opy_(bstack1lllll111l11_opy_, data):
        logger.debug(bstack11l111_opy_ (u"ࠨࡐࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡖࡪࡷࡵࡦࡵࡷࠤ࡫ࡵࡲࠡࡶࡨࡷࡹࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡘࡶ࡬ࡪࡶࡗࡩࡸࡺࡳࠣ⁊"))
        return bstack11l1lll1ll1_opy_.bstack1lllll111l1l_opy_(bstack11l111_opy_ (u"ࠧࡑࡑࡖࡘࠬ⁋"), bstack1lllll111l11_opy_, data=data)
    @staticmethod
    def bstack1lllll1111l1_opy_(bstack1lllll111l11_opy_, data):
        logger.debug(bstack11l111_opy_ (u"ࠣࡒࡵࡳࡨ࡫ࡳࡴ࡫ࡱ࡫ࠥࡘࡥࡲࡷࡨࡷࡹࠦࡦࡰࡴࠣ࡫ࡪࡺࡔࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡶࡩ࡫ࡲࡦࡦࡗࡩࡸࡺࡳࠣ⁌"))
        res = bstack11l1lll1ll1_opy_.bstack1lllll111l1l_opy_(bstack11l111_opy_ (u"ࠩࡊࡉ࡙࠭⁍"), bstack1lllll111l11_opy_, data=data)
        return res
    @staticmethod
    def bstack1lllll111l1l_opy_(method, bstack1lllll111l11_opy_, data=None, params=None, extra_headers=None):
        bstack1lllll11111l_opy_ = os.environ.get(bstack11l111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ⁎"), bstack11l111_opy_ (u"ࠫࠬ⁏"))
        headers = {
            bstack11l111_opy_ (u"ࠬࡧࡵࡵࡪࡲࡶ࡮ࢀࡡࡵ࡫ࡲࡲࠬ⁐"): bstack11l111_opy_ (u"࠭ࡂࡦࡣࡵࡩࡷࠦࡻࡾࠩ⁑").format(bstack1lllll11111l_opy_),
            bstack11l111_opy_ (u"ࠧࡄࡱࡱࡸࡪࡴࡴ࠮ࡖࡼࡴࡪ࠭⁒"): bstack11l111_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠫ⁓"),
            bstack11l111_opy_ (u"ࠩࡄࡧࡨ࡫ࡰࡵࠩ⁔"): bstack11l111_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭⁕")
        }
        if extra_headers:
            headers.update(extra_headers)
        url = bstack11l1l111lll_opy_ + bstack11l111_opy_ (u"ࠦ࠴ࠨ⁖") + bstack1lllll111l11_opy_.lstrip(bstack11l111_opy_ (u"ࠬ࠵ࠧ⁗"))
        try:
            if method == bstack11l111_opy_ (u"࠭ࡇࡆࡖࠪ⁘"):
                response = requests.get(url, headers=headers, params=params, json=data)
            elif method == bstack11l111_opy_ (u"ࠧࡑࡑࡖࡘࠬ⁙"):
                response = requests.post(url, headers=headers, json=data)
            elif method == bstack11l111_opy_ (u"ࠨࡒࡘࡘࠬ⁚"):
                response = requests.put(url, headers=headers, json=data)
            else:
                raise ValueError(bstack11l111_opy_ (u"ࠤࡘࡲࡸࡻࡰࡱࡱࡵࡸࡪࡪࠠࡉࡖࡗࡔࠥࡳࡥࡵࡪࡲࡨ࠿ࠦࡻࡾࠤ⁛").format(method))
            logger.debug(bstack11l111_opy_ (u"ࠥࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣࡶࡪࡷࡵࡦࡵࡷࠤࡲࡧࡤࡦࠢࡷࡳ࡛ࠥࡒࡍ࠼ࠣࡿࢂࠦࡷࡪࡶ࡫ࠤࡲ࡫ࡴࡩࡱࡧ࠾ࠥࢁࡽࠣ⁜").format(url, method))
            bstack1llll1llllll_opy_ = {}
            try:
                bstack1llll1llllll_opy_ = response.json()
            except Exception as e:
                logger.debug(bstack11l111_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡱࡣࡵࡷࡪࠦࡊࡔࡑࡑࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࡀࠠࡼࡿࠣ࠱ࠥࢁࡽࠣ⁝").format(e, response.text))
            if bstack1llll1llllll_opy_ is not None:
                bstack1llll1llllll_opy_[bstack11l111_opy_ (u"ࠬࡴࡥࡹࡶࡢࡴࡴࡲ࡬ࡠࡶ࡬ࡱࡪ࠭⁞")] = response.headers.get(
                    bstack11l111_opy_ (u"࠭࡮ࡦࡺࡷࡣࡵࡵ࡬࡭ࡡࡷ࡭ࡲ࡫ࠧ "), str(int(datetime.now().timestamp() * 1000))
                )
                bstack1llll1llllll_opy_[bstack11l111_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ⁠")] = response.status_code
            return bstack1llll1llllll_opy_
        except Exception as e:
            logger.error(bstack11l111_opy_ (u"ࠣࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡩࡥ࡮ࡲࡥࡥ࠼ࠣࡿࢂࠦ࠭ࠡࡽࢀࠦ⁡").format(e, url))
            return None
    @staticmethod
    def bstack11l11lll1l1_opy_(bstack1llll1lllll1_opy_, data):
        bstack11l111_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡓࡦࡰࡧࡷࠥࡧࠠࡑࡗࡗࠤࡷ࡫ࡱࡶࡧࡶࡸࠥࡺ࡯ࠡࡵࡷࡳࡷ࡫ࠠࡵࡪࡨࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡹ࡫ࡳࡵࡵࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢ⁢")
        bstack1lllll11111l_opy_ = os.environ.get(bstack11l111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ⁣"), bstack11l111_opy_ (u"ࠫࠬ⁤"))
        headers = {
            bstack11l111_opy_ (u"ࠬࡧࡵࡵࡪࡲࡶ࡮ࢀࡡࡵ࡫ࡲࡲࠬ⁥"): bstack11l111_opy_ (u"࠭ࡂࡦࡣࡵࡩࡷࠦࡻࡾࠩ⁦").format(bstack1lllll11111l_opy_),
            bstack11l111_opy_ (u"ࠧࡄࡱࡱࡸࡪࡴࡴ࠮ࡖࡼࡴࡪ࠭⁧"): bstack11l111_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠫ⁨")
        }
        response = requests.put(bstack1llll1lllll1_opy_, headers=headers, json=data)
        bstack1llll1llllll_opy_ = {}
        try:
            bstack1llll1llllll_opy_ = response.json()
        except Exception as e:
            logger.debug(bstack11l111_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡶࡡࡳࡵࡨࠤࡏ࡙ࡏࡏࠢࡵࡩࡸࡶ࡯࡯ࡵࡨ࠾ࠥࢁࡽࠣ⁩").format(e))
            pass
        logger.debug(bstack11l111_opy_ (u"ࠥࡖࡪࡷࡵࡦࡵࡷ࡙ࡹ࡯࡬ࡴ࠼ࠣࡴࡺࡺ࡟ࡧࡣ࡬ࡰࡪࡪ࡟ࡵࡧࡶࡸࡸࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠻ࠢࡾࢁࠧ⁪").format(bstack1llll1llllll_opy_))
        if bstack1llll1llllll_opy_ is not None:
            bstack1llll1llllll_opy_[bstack11l111_opy_ (u"ࠫࡳ࡫ࡸࡵࡡࡳࡳࡱࡲ࡟ࡵ࡫ࡰࡩࠬ⁫")] = response.headers.get(
                bstack11l111_opy_ (u"ࠬࡴࡥࡹࡶࡢࡴࡴࡲ࡬ࡠࡶ࡬ࡱࡪ࠭⁬"), str(int(datetime.now().timestamp() * 1000))
            )
            bstack1llll1llllll_opy_[bstack11l111_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭⁭")] = response.status_code
        return bstack1llll1llllll_opy_
    @staticmethod
    def bstack11l11ll111l_opy_(bstack1llll1lllll1_opy_):
        bstack11l111_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡘ࡫࡮ࡥࡵࠣࡥࠥࡍࡅࡕࠢࡵࡩࡶࡻࡥࡴࡶࠣࡸࡴࠦࡧࡦࡶࠣࡸ࡭࡫ࠠࡤࡱࡸࡲࡹࠦ࡯ࡧࠢࡩࡥ࡮ࡲࡥࡥࠢࡷࡩࡸࡺࡳࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧ⁮")
        bstack1lllll11111l_opy_ = os.environ.get(bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬ⁯"), bstack11l111_opy_ (u"ࠩࠪ⁰"))
        headers = {
            bstack11l111_opy_ (u"ࠪࡥࡺࡺࡨࡰࡴ࡬ࡾࡦࡺࡩࡰࡰࠪⁱ"): bstack11l111_opy_ (u"ࠫࡇ࡫ࡡࡳࡧࡵࠤࢀࢃࠧ⁲").format(bstack1lllll11111l_opy_),
            bstack11l111_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡔࡺࡲࡨࠫ⁳"): bstack11l111_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩ⁴")
        }
        response = requests.get(bstack1llll1lllll1_opy_, headers=headers)
        bstack1llll1llllll_opy_ = {}
        try:
            bstack1llll1llllll_opy_ = response.json()
            logger.debug(bstack11l111_opy_ (u"ࠢࡓࡧࡴࡹࡪࡹࡴࡖࡶ࡬ࡰࡸࡀࠠࡨࡧࡷࡣ࡫ࡧࡩ࡭ࡧࡧࡣࡹ࡫ࡳࡵࡵࠣࡶࡪࡹࡰࡰࡰࡶࡩ࠿ࠦࡻࡾࠤ⁵").format(bstack1llll1llllll_opy_))
        except Exception as e:
            logger.debug(bstack11l111_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵࡧࡲࡴࡧࠣࡎࡘࡕࡎࠡࡴࡨࡷࡵࡵ࡮ࡴࡧ࠽ࠤࢀࢃࠠ࠮ࠢࡾࢁࠧ⁶").format(e, response.text))
            pass
        if bstack1llll1llllll_opy_ is not None:
            bstack1llll1llllll_opy_[bstack11l111_opy_ (u"ࠩࡱࡩࡽࡺ࡟ࡱࡱ࡯ࡰࡤࡺࡩ࡮ࡧࠪ⁷")] = response.headers.get(
                bstack11l111_opy_ (u"ࠪࡲࡪࡾࡴࡠࡲࡲࡰࡱࡥࡴࡪ࡯ࡨࠫ⁸"), str(int(datetime.now().timestamp() * 1000))
            )
            bstack1llll1llllll_opy_[bstack11l111_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ⁹")] = response.status_code
        return bstack1llll1llllll_opy_
    @staticmethod
    def bstack1111l1l1ll1_opy_(bstack11l1llll1l1_opy_, payload):
        bstack11l111_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡐࡥࡰ࡫ࡳࠡࡣࠣࡔࡔ࡙ࡔࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡷࡳࠥࡺࡨࡦࠢࡦࡳࡱࡲࡥࡤࡶ࠰ࡦࡺ࡯࡬ࡥ࠯ࡧࡥࡹࡧࠠࡦࡰࡧࡴࡴ࡯࡮ࡵ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡆࡸࡧࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡧࡱࡨࡵࡵࡩ࡯ࡶࠣࠬࡸࡺࡲࠪ࠼ࠣࡘ࡭࡫ࠠࡂࡒࡌࠤࡪࡴࡤࡱࡱ࡬ࡲࡹࠦࡰࡢࡶ࡫࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡴࡦࡿ࡬ࡰࡣࡧࠤ࠭ࡪࡩࡤࡶࠬ࠾࡚ࠥࡨࡦࠢࡵࡩࡶࡻࡥࡴࡶࠣࡴࡦࡿ࡬ࡰࡣࡧ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡒࡦࡶࡸࡶࡳࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡤࡪࡥࡷ࠾ࠥࡘࡥࡴࡲࡲࡲࡸ࡫ࠠࡧࡴࡲࡱࠥࡺࡨࡦࠢࡄࡔࡎ࠲ࠠࡰࡴࠣࡒࡴࡴࡥࠡ࡫ࡩࠤ࡫ࡧࡩ࡭ࡧࡧ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤ⁺")
        try:
            url = bstack11l111_opy_ (u"ࠨࡻࡾ࠱ࡾࢁࠧ⁻").format(bstack11l1l111lll_opy_, bstack11l1llll1l1_opy_)
            bstack1lllll11111l_opy_ = os.environ.get(bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ⁼"), bstack11l111_opy_ (u"ࠨࠩ⁽"))
            headers = {
                bstack11l111_opy_ (u"ࠩࡤࡹࡹ࡮࡯ࡳ࡫ࡽࡥࡹ࡯࡯࡯ࠩ⁾"): bstack11l111_opy_ (u"ࠪࡆࡪࡧࡲࡦࡴࠣࡿࢂ࠭ⁿ").format(bstack1lllll11111l_opy_),
                bstack11l111_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪ₀"): bstack11l111_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠨ₁")
            }
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            bstack1lllll1111ll_opy_ = [200, 202]
            if response.status_code in bstack1lllll1111ll_opy_:
                return response.json()
            else:
                logger.error(bstack11l111_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡦࡳࡱࡲࡥࡤࡶࠣࡦࡺ࡯࡬ࡥࠢࡧࡥࡹࡧ࠮ࠡࡕࡷࡥࡹࡻࡳ࠻ࠢࡾࢁ࠱ࠦࡒࡦࡵࡳࡳࡳࡹࡥ࠻ࠢࡾࢁࠧ₂").format(
                    response.status_code, response.text))
                return None
        except Exception as e:
            logger.error(bstack11l111_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡰࡵࡷࡣࡨࡵ࡬࡭ࡧࡦࡸࡤࡨࡵࡪ࡮ࡧࡣࡩࡧࡴࡢ࠼ࠣࡿࢂࠨ₃").format(e))
            return None