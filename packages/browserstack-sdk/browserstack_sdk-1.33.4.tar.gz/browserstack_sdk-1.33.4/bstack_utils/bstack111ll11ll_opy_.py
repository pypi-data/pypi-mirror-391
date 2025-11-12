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
import threading
import logging
import bstack_utils.accessibility as bstack1lllll11l_opy_
from bstack_utils.helper import bstack1l11lll1l1_opy_
logger = logging.getLogger(__name__)
def bstack11l1111ll_opy_(bstack11l1l111_opy_):
  return True if bstack11l1l111_opy_ in threading.current_thread().__dict__.keys() else False
def bstack11l1l1l1l_opy_(context, *args):
    tags = getattr(args[0], bstack11l111_opy_ (u"ࠧࡵࡣࡪࡷࠬ៘"), [])
    bstack11ll1l1l1_opy_ = bstack1lllll11l_opy_.bstack11l1ll1l1_opy_(tags)
    threading.current_thread().isA11yTest = bstack11ll1l1l1_opy_
    try:
      bstack11l1llll1_opy_ = threading.current_thread().bstackSessionDriver if bstack11l1111ll_opy_(bstack11l111_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧ៙")) else context.browser
      if bstack11l1llll1_opy_ and bstack11l1llll1_opy_.session_id and bstack11ll1l1l1_opy_ and bstack1l11lll1l1_opy_(
              threading.current_thread(), bstack11l111_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ៚"), None):
          threading.current_thread().isA11yTest = bstack1lllll11l_opy_.bstack1lll11l111_opy_(bstack11l1llll1_opy_, bstack11ll1l1l1_opy_)
    except Exception as e:
       logger.debug(bstack11l111_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡧ࠱࠲ࡻࠣ࡭ࡳࠦࡢࡦࡪࡤࡺࡪࡀࠠࡼࡿࠪ៛").format(str(e)))
def bstack1l1l1lll1l_opy_(bstack11l1llll1_opy_):
    if bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨៜ"), None) and bstack1l11lll1l1_opy_(
      threading.current_thread(), bstack11l111_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ៝"), None) and not bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"࠭ࡡ࠲࠳ࡼࡣࡸࡺ࡯ࡱࠩ៞"), False):
      threading.current_thread().a11y_stop = True
      bstack1lllll11l_opy_.bstack1l1ll11ll1_opy_(bstack11l1llll1_opy_, name=bstack11l111_opy_ (u"ࠢࠣ៟"), path=bstack11l111_opy_ (u"ࠣࠤ០"))