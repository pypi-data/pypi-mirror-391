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
import json
import logging
import datetime
import threading
from bstack_utils.helper import bstack11ll11l11l1_opy_, bstack1l1lllllll_opy_, get_host_info, bstack111lll111l1_opy_, \
 bstack11l11l1l1l_opy_, bstack1l11lll1l1_opy_, error_handler, bstack11l111111ll_opy_, bstack1l11ll11l_opy_
import bstack_utils.accessibility as bstack1lllll11l_opy_
from bstack_utils.bstack1llll11ll_opy_ import bstack1l1ll1ll1l_opy_
from bstack_utils.bstack111ll1l1l1_opy_ import bstack1l11lllll1_opy_
from bstack_utils.percy import bstack1ll1l111ll_opy_
from bstack_utils.config import Config
bstack11l11ll1l_opy_ = Config.bstack111llll1_opy_()
logger = logging.getLogger(__name__)
percy = bstack1ll1l111ll_opy_()
@error_handler(class_method=False)
def bstack1llll111l1l1_opy_(bs_config, bstack1ll1lllll_opy_):
  try:
    data = {
        bstack11l111_opy_ (u"࠭ࡦࡰࡴࡰࡥࡹ࠭∻"): bstack11l111_opy_ (u"ࠧ࡫ࡵࡲࡲࠬ∼"),
        bstack11l111_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡡࡱࡥࡲ࡫ࠧ∽"): bs_config.get(bstack11l111_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧ∾"), bstack11l111_opy_ (u"ࠪࠫ∿")),
        bstack11l111_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ≀"): bs_config.get(bstack11l111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ≁"), os.path.basename(os.path.abspath(os.getcwd()))),
        bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ≂"): bs_config.get(bstack11l111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ≃")),
        bstack11l111_opy_ (u"ࠨࡦࡨࡷࡨࡸࡩࡱࡶ࡬ࡳࡳ࠭≄"): bs_config.get(bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡅࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬ≅"), bstack11l111_opy_ (u"ࠪࠫ≆")),
        bstack11l111_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ≇"): bstack1l11ll11l_opy_(),
        bstack11l111_opy_ (u"ࠬࡺࡡࡨࡵࠪ≈"): bstack111lll111l1_opy_(bs_config),
        bstack11l111_opy_ (u"࠭ࡨࡰࡵࡷࡣ࡮ࡴࡦࡰࠩ≉"): get_host_info(),
        bstack11l111_opy_ (u"ࠧࡤ࡫ࡢ࡭ࡳ࡬࡯ࠨ≊"): bstack1l1lllllll_opy_(),
        bstack11l111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡳࡷࡱࡣ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ≋"): os.environ.get(bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡘࡍࡑࡊ࡟ࡓࡗࡑࡣࡎࡊࡅࡏࡖࡌࡊࡎࡋࡒࠨ≌")),
        bstack11l111_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࡢࡸࡪࡹࡴࡴࡡࡵࡩࡷࡻ࡮ࠨ≍"): os.environ.get(bstack11l111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡖࡊࡘࡕࡏࠩ≎"), False),
        bstack11l111_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳࡥࡣࡰࡰࡷࡶࡴࡲࠧ≏"): bstack11ll11l11l1_opy_(),
        bstack11l111_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭≐"): bstack1lll1lll1111_opy_(bs_config),
        bstack11l111_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡨࡪࡺࡡࡪ࡮ࡶࠫ≑"): bstack1lll1lll11l1_opy_(bstack1ll1lllll_opy_),
        bstack11l111_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࡡࡰࡥࡵ࠭≒"): bstack1lll1lll1l11_opy_(bs_config, bstack1ll1lllll_opy_.get(bstack11l111_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡻࡳࡦࡦࠪ≓"), bstack11l111_opy_ (u"ࠪࠫ≔"))),
        bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭≕"): bstack11l11l1l1l_opy_(bs_config),
        bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠪ≖"): bstack1lll1lll1l1l_opy_(bs_config)
    }
    return data
  except Exception as error:
    logger.error(bstack11l111_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡺ࡬࡮ࡲࡥࠡࡥࡵࡩࡦࡺࡩ࡯ࡩࠣࡴࡦࡿ࡬ࡰࡣࡧࠤ࡫ࡵࡲࠡࡖࡨࡷࡹࡎࡵࡣ࠼ࠣࠤࢀࢃࠢ≗").format(str(error)))
    return None
def bstack1lll1lll11l1_opy_(framework):
  return {
    bstack11l111_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡑࡥࡲ࡫ࠧ≘"): framework.get(bstack11l111_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦࠩ≙"), bstack11l111_opy_ (u"ࠩࡓࡽࡹ࡫ࡳࡵࠩ≚")),
    bstack11l111_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࡜ࡥࡳࡵ࡬ࡳࡳ࠭≛"): framework.get(bstack11l111_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ≜")),
    bstack11l111_opy_ (u"ࠬࡹࡤ࡬ࡘࡨࡶࡸ࡯࡯࡯ࠩ≝"): framework.get(bstack11l111_opy_ (u"࠭ࡳࡥ࡭ࡢࡺࡪࡸࡳࡪࡱࡱࠫ≞")),
    bstack11l111_opy_ (u"ࠧ࡭ࡣࡱ࡫ࡺࡧࡧࡦࠩ≟"): bstack11l111_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨ≠"),
    bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࠩ≡"): framework.get(bstack11l111_opy_ (u"ࠪࡸࡪࡹࡴࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪ≢"))
  }
def bstack1lll1lll1l1l_opy_(bs_config):
  bstack11l111_opy_ (u"ࠦࠧࠨࠊࠡࠢࡕࡩࡹࡻࡲ࡯ࡵࠣࡸ࡭࡫ࠠࡵࡧࡶࡸࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࠥࡪࡡࡵࡣࠣࡪࡴࡸࠠࡣࡷ࡬ࡰࡩࠦࡳࡵࡣࡵࡸ࠳ࠐࠠࠡࠤࠥࠦ≣")
  if not bs_config:
    return {}
  bstack1111ll1llll_opy_ = bstack1l1ll1ll1l_opy_(bs_config).bstack1111ll11lll_opy_(bs_config)
  return bstack1111ll1llll_opy_
def bstack11ll1l111_opy_(bs_config, framework):
  bstack1l11llll11_opy_ = False
  bstack1ll1ll11l_opy_ = False
  bstack1lll1ll1llll_opy_ = False
  if bstack11l111_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩ≤") in bs_config:
    bstack1lll1ll1llll_opy_ = True
  elif bstack11l111_opy_ (u"࠭ࡡࡱࡲࠪ≥") in bs_config:
    bstack1l11llll11_opy_ = True
  else:
    bstack1ll1ll11l_opy_ = True
  bstack11l11lll1l_opy_ = {
    bstack11l111_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧ≦"): bstack1l11lllll1_opy_.bstack1lll1llll111_opy_(bs_config, framework),
    bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ≧"): bstack1lllll11l_opy_.bstack1lll1111ll_opy_(bs_config),
    bstack11l111_opy_ (u"ࠩࡳࡩࡷࡩࡹࠨ≨"): bs_config.get(bstack11l111_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩ≩"), False),
    bstack11l111_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭≪"): bstack1ll1ll11l_opy_,
    bstack11l111_opy_ (u"ࠬࡧࡰࡱࡡࡤࡹࡹࡵ࡭ࡢࡶࡨࠫ≫"): bstack1l11llll11_opy_,
    bstack11l111_opy_ (u"࠭ࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧࠪ≬"): bstack1lll1ll1llll_opy_
  }
  return bstack11l11lll1l_opy_
@error_handler(class_method=False)
def bstack1lll1lll1111_opy_(bs_config):
  try:
    bstack1lll1lll1ll1_opy_ = json.loads(os.getenv(bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨ≭"), bstack11l111_opy_ (u"ࠨࡽࢀࠫ≮")))
    bstack1lll1lll1ll1_opy_ = bstack1lll1ll1lll1_opy_(bs_config, bstack1lll1lll1ll1_opy_)
    return {
        bstack11l111_opy_ (u"ࠩࡶࡩࡹࡺࡩ࡯ࡩࡶࠫ≯"): bstack1lll1lll1ll1_opy_
    }
  except Exception as error:
    logger.error(bstack11l111_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡩࡲࡦࡣࡷ࡭ࡳ࡭ࠠࡨࡧࡷࡣࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡣࡸ࡫ࡴࡵ࡫ࡱ࡫ࡸࠦࡦࡰࡴࠣࡘࡪࡹࡴࡉࡷࡥ࠾ࠥࠦࡻࡾࠤ≰").format(str(error)))
    return {}
def bstack1lll1ll1lll1_opy_(bs_config, bstack1lll1lll1ll1_opy_):
  if ((bstack11l111_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨ≱") in bs_config or not bstack11l11l1l1l_opy_(bs_config)) and bstack1lllll11l_opy_.bstack1lll1111ll_opy_(bs_config)):
    bstack1lll1lll1ll1_opy_[bstack11l111_opy_ (u"ࠧ࡯࡮ࡤ࡮ࡸࡨࡪࡋ࡮ࡤࡱࡧࡩࡩࡋࡸࡵࡧࡱࡷ࡮ࡵ࡮ࠣ≲")] = True
  return bstack1lll1lll1ll1_opy_
def bstack1llll1111ll1_opy_(array, bstack1lll1lll1lll_opy_, bstack1lll1ll1ll1l_opy_):
  result = {}
  for o in array:
    key = o[bstack1lll1lll1lll_opy_]
    result[key] = o[bstack1lll1ll1ll1l_opy_]
  return result
def bstack1llll111ll11_opy_(bstack1l111llll_opy_=bstack11l111_opy_ (u"࠭ࠧ≳")):
  bstack1lll1ll1l1ll_opy_ = bstack1lllll11l_opy_.on()
  bstack1lll1lll11ll_opy_ = bstack1l11lllll1_opy_.on()
  bstack1lll1lll111l_opy_ = percy.bstack1l1l1ll111_opy_()
  if bstack1lll1lll111l_opy_ and not bstack1lll1lll11ll_opy_ and not bstack1lll1ll1l1ll_opy_:
    return bstack1l111llll_opy_ not in [bstack11l111_opy_ (u"ࠧࡄࡄࡗࡗࡪࡹࡳࡪࡱࡱࡇࡷ࡫ࡡࡵࡧࡧࠫ≴"), bstack11l111_opy_ (u"ࠨࡎࡲ࡫ࡈࡸࡥࡢࡶࡨࡨࠬ≵")]
  elif bstack1lll1ll1l1ll_opy_ and not bstack1lll1lll11ll_opy_:
    return bstack1l111llll_opy_ not in [bstack11l111_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡖࡸࡦࡸࡴࡦࡦࠪ≶"), bstack11l111_opy_ (u"ࠪࡌࡴࡵ࡫ࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ≷"), bstack11l111_opy_ (u"ࠫࡑࡵࡧࡄࡴࡨࡥࡹ࡫ࡤࠨ≸")]
  return bstack1lll1ll1l1ll_opy_ or bstack1lll1lll11ll_opy_ or bstack1lll1lll111l_opy_
@error_handler(class_method=False)
def bstack1llll111111l_opy_(bstack1l111llll_opy_, test=None):
  bstack1lll1ll1ll11_opy_ = bstack1lllll11l_opy_.on()
  if not bstack1lll1ll1ll11_opy_ or bstack1l111llll_opy_ not in [bstack11l111_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ≹")] or test == None:
    return None
  return {
    bstack11l111_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭≺"): bstack1lll1ll1ll11_opy_ and bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭≻"), None) == True and bstack1lllll11l_opy_.bstack11l1ll1l1_opy_(test[bstack11l111_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭≼")])
  }
def bstack1lll1lll1l11_opy_(bs_config, framework):
  bstack1l11llll11_opy_ = False
  bstack1ll1ll11l_opy_ = False
  bstack1lll1ll1llll_opy_ = False
  if bstack11l111_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭≽") in bs_config:
    bstack1lll1ll1llll_opy_ = True
  elif bstack11l111_opy_ (u"ࠪࡥࡵࡶࠧ≾") in bs_config:
    bstack1l11llll11_opy_ = True
  else:
    bstack1ll1ll11l_opy_ = True
  bstack11l11lll1l_opy_ = {
    bstack11l111_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ≿"): bstack1l11lllll1_opy_.bstack1lll1llll111_opy_(bs_config, framework),
    bstack11l111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ⊀"): bstack1lllll11l_opy_.bstack111lllll11_opy_(bs_config),
    bstack11l111_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬ⊁"): bs_config.get(bstack11l111_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠭⊂"), False),
    bstack11l111_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵࡧࠪ⊃"): bstack1ll1ll11l_opy_,
    bstack11l111_opy_ (u"ࠩࡤࡴࡵࡥࡡࡶࡶࡲࡱࡦࡺࡥࠨ⊄"): bstack1l11llll11_opy_,
    bstack11l111_opy_ (u"ࠪࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫ࠧ⊅"): bstack1lll1ll1llll_opy_
  }
  return bstack11l11lll1l_opy_