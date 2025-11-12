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
import os
import threading
from bstack_utils.config import Config
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack111lllll111_opy_, bstack1l1ll1l1_opy_, bstack1l11lll1l1_opy_, bstack11l11l1l1_opy_, \
    bstack111lll1llll_opy_
from bstack_utils.measure import measure
def bstack1ll11ll1ll_opy_(bstack1llll1lll111_opy_):
    for driver in bstack1llll1lll111_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1lll1ll1_opy_, stage=STAGE.bstack1l1l111l1_opy_)
def bstack1ll11l1ll1_opy_(driver, status, reason=bstack11l111_opy_ (u"ࠪࠫ₆")):
    bstack11l11ll1l_opy_ = Config.bstack111llll1_opy_()
    if bstack11l11ll1l_opy_.bstack1llllllllll_opy_():
        return
    bstack1l1lll1ll1_opy_ = bstack1l11111l1_opy_(bstack11l111_opy_ (u"ࠫࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠧ₇"), bstack11l111_opy_ (u"ࠬ࠭₈"), status, reason, bstack11l111_opy_ (u"࠭ࠧ₉"), bstack11l111_opy_ (u"ࠧࠨ₊"))
    driver.execute_script(bstack1l1lll1ll1_opy_)
@measure(event_name=EVENTS.bstack1lll1ll1_opy_, stage=STAGE.bstack1l1l111l1_opy_)
def bstack11lll111_opy_(page, status, reason=bstack11l111_opy_ (u"ࠨࠩ₋")):
    try:
        if page is None:
            return
        bstack11l11ll1l_opy_ = Config.bstack111llll1_opy_()
        if bstack11l11ll1l_opy_.bstack1llllllllll_opy_():
            return
        bstack1l1lll1ll1_opy_ = bstack1l11111l1_opy_(bstack11l111_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠬ₌"), bstack11l111_opy_ (u"ࠪࠫ₍"), status, reason, bstack11l111_opy_ (u"ࠫࠬ₎"), bstack11l111_opy_ (u"ࠬ࠭₏"))
        page.evaluate(bstack11l111_opy_ (u"ࠨ࡟ࠡ࠿ࡁࠤࢀࢃࠢₐ"), bstack1l1lll1ll1_opy_)
    except Exception as e:
        print(bstack11l111_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡳࡦࡶࡷ࡭ࡳ࡭ࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡵࡷࡥࡹࡻࡳࠡࡨࡲࡶࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡾࢁࠧₑ"), e)
def bstack1l11111l1_opy_(type, name, status, reason, bstack1l1lllll1_opy_, bstack1ll111l1ll_opy_):
    bstack1l111111l1_opy_ = {
        bstack11l111_opy_ (u"ࠨࡣࡦࡸ࡮ࡵ࡮ࠨₒ"): type,
        bstack11l111_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬₓ"): {}
    }
    if type == bstack11l111_opy_ (u"ࠪࡥࡳࡴ࡯ࡵࡣࡷࡩࠬₔ"):
        bstack1l111111l1_opy_[bstack11l111_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧₕ")][bstack11l111_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫₖ")] = bstack1l1lllll1_opy_
        bstack1l111111l1_opy_[bstack11l111_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩₗ")][bstack11l111_opy_ (u"ࠧࡥࡣࡷࡥࠬₘ")] = json.dumps(str(bstack1ll111l1ll_opy_))
    if type == bstack11l111_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩₙ"):
        bstack1l111111l1_opy_[bstack11l111_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬₚ")][bstack11l111_opy_ (u"ࠪࡲࡦࡳࡥࠨₛ")] = name
    if type == bstack11l111_opy_ (u"ࠫࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠧₜ"):
        bstack1l111111l1_opy_[bstack11l111_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨ₝")][bstack11l111_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭₞")] = status
        if status == bstack11l111_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ₟") and str(reason) != bstack11l111_opy_ (u"ࠣࠤ₠"):
            bstack1l111111l1_opy_[bstack11l111_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬ₡")][bstack11l111_opy_ (u"ࠪࡶࡪࡧࡳࡰࡰࠪ₢")] = json.dumps(str(reason))
    bstack11ll11ll1_opy_ = bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࡾࠩ₣").format(json.dumps(bstack1l111111l1_opy_))
    return bstack11ll11ll1_opy_
def bstack1llll11ll1_opy_(url, config, logger, bstack1lll11l1l1_opy_=False):
    hostname = bstack1l1ll1l1_opy_(url)
    is_private = bstack11l11l1l1_opy_(hostname)
    try:
        if is_private or bstack1lll11l1l1_opy_:
            file_path = bstack111lllll111_opy_(bstack11l111_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬ₤"), bstack11l111_opy_ (u"࠭࠮ࡣࡵࡷࡥࡨࡱ࠭ࡤࡱࡱࡪ࡮࡭࠮࡫ࡵࡲࡲࠬ₥"), logger)
            if os.environ.get(bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࡤࡔࡏࡕࡡࡖࡉ࡙ࡥࡅࡓࡔࡒࡖࠬ₦")) and eval(
                    os.environ.get(bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡍࡑࡆࡅࡑࡥࡎࡐࡖࡢࡗࡊ࡚࡟ࡆࡔࡕࡓࡗ࠭₧"))):
                return
            if (bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭₨") in config and not config[bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ₩")]):
                os.environ[bstack11l111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡑࡓ࡙ࡥࡓࡆࡖࡢࡉࡗࡘࡏࡓࠩ₪")] = str(True)
                bstack1llll1ll1lll_opy_ = {bstack11l111_opy_ (u"ࠬ࡮࡯ࡴࡶࡱࡥࡲ࡫ࠧ₫"): hostname}
                bstack111lll1llll_opy_(bstack11l111_opy_ (u"࠭࠮ࡣࡵࡷࡥࡨࡱ࠭ࡤࡱࡱࡪ࡮࡭࠮࡫ࡵࡲࡲࠬ€"), bstack11l111_opy_ (u"ࠧ࡯ࡷࡧ࡫ࡪࡥ࡬ࡰࡥࡤࡰࠬ₭"), bstack1llll1ll1lll_opy_, logger)
    except Exception as e:
        pass
def bstack1ll111llll_opy_(caps, bstack1llll1ll1ll1_opy_):
    if bstack11l111_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ₮") in caps:
        caps[bstack11l111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪ₯")][bstack11l111_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࠩ₰")] = True
        if bstack1llll1ll1ll1_opy_:
            caps[bstack11l111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬ₱")][bstack11l111_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ₲")] = bstack1llll1ll1ll1_opy_
    else:
        caps[bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡲ࡯ࡤࡣ࡯ࠫ₳")] = True
        if bstack1llll1ll1ll1_opy_:
            caps[bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ₴")] = bstack1llll1ll1ll1_opy_
def bstack1lllll1l11l1_opy_(bstack111l11l111_opy_):
    bstack1llll1ll1l1l_opy_ = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠨࡶࡨࡷࡹ࡙ࡴࡢࡶࡸࡷࠬ₵"), bstack11l111_opy_ (u"ࠩࠪ₶"))
    if bstack1llll1ll1l1l_opy_ == bstack11l111_opy_ (u"ࠪࠫ₷") or bstack1llll1ll1l1l_opy_ == bstack11l111_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ₸"):
        threading.current_thread().testStatus = bstack111l11l111_opy_
    else:
        if bstack111l11l111_opy_ == bstack11l111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ₹"):
            threading.current_thread().testStatus = bstack111l11l111_opy_