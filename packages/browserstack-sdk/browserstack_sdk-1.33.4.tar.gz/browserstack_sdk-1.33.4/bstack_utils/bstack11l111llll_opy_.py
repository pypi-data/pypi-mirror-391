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
from browserstack_sdk.bstack11l11llll1_opy_ import bstack1l1ll11111_opy_
from browserstack_sdk.bstack1111lll111_opy_ import RobotHandler
def bstack11l1111l11_opy_(framework):
    if framework.lower() == bstack11l111_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ᭤"):
        return bstack1l1ll11111_opy_.version()
    elif framework.lower() == bstack11l111_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ᭥"):
        return RobotHandler.version()
    elif framework.lower() == bstack11l111_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧ᭦"):
        import behave
        return behave.__version__
    else:
        return bstack11l111_opy_ (u"ࠨࡷࡱ࡯ࡳࡵࡷ࡯ࠩ᭧")
def bstack1l1l1lll11_opy_():
    import importlib.metadata
    framework_name = []
    framework_version = []
    try:
        from selenium import webdriver
        framework_name.append(bstack11l111_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰࠫ᭨"))
        framework_version.append(importlib.metadata.version(bstack11l111_opy_ (u"ࠥࡷࡪࡲࡥ࡯࡫ࡸࡱࠧ᭩")))
    except:
        pass
    try:
        import playwright
        framework_name.append(bstack11l111_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨ᭪"))
        framework_version.append(importlib.metadata.version(bstack11l111_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤ᭫")))
    except:
        pass
    return {
        bstack11l111_opy_ (u"࠭࡮ࡢ࡯ࡨ᭬ࠫ"): bstack11l111_opy_ (u"ࠧࡠࠩ᭭").join(framework_name),
        bstack11l111_opy_ (u"ࠨࡸࡨࡶࡸ࡯࡯࡯ࠩ᭮"): bstack11l111_opy_ (u"ࠩࡢࠫ᭯").join(framework_version)
    }