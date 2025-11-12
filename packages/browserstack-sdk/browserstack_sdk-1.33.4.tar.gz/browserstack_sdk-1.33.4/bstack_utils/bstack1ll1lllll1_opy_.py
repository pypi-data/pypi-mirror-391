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
from bstack_utils.constants import bstack11l1llll1ll_opy_
def bstack1l1l1111l1_opy_(bstack11l1llll1l1_opy_):
    from browserstack_sdk.sdk_cli.cli import cli
    from bstack_utils.helper import bstack111111ll_opy_
    host = bstack111111ll_opy_(cli.config, [bstack11l111_opy_ (u"ࠢࡢࡲ࡬ࡷࠧ៊"), bstack11l111_opy_ (u"ࠣࡣࡸࡸࡴࡳࡡࡵࡧࠥ់"), bstack11l111_opy_ (u"ࠤࡤࡴ࡮ࠨ៌")], bstack11l1llll1ll_opy_)
    return bstack11l111_opy_ (u"ࠪࡿࢂ࠵ࡻࡾࠩ៍").format(host, bstack11l1llll1l1_opy_)