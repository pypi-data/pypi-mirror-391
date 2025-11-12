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
import logging
import abc
from browserstack_sdk.sdk_cli.bstack1llllll1l11_opy_ import bstack1llllll111l_opy_
class bstack1lll1ll1l11_opy_(abc.ABC):
    bin_session_id: str
    bstack1llllll1l11_opy_: bstack1llllll111l_opy_
    def __init__(self):
        self.bstack1lll111llll_opy_ = None
        self.config = None
        self.bin_session_id = None
        self.bstack1llllll1l11_opy_ = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    def bstack1ll11llllll_opy_(self):
        return (self.bstack1lll111llll_opy_ != None and self.bin_session_id != None and self.bstack1llllll1l11_opy_ != None)
    def configure(self, bstack1lll111llll_opy_, config, bin_session_id: str, bstack1llllll1l11_opy_: bstack1llllll111l_opy_):
        self.bstack1lll111llll_opy_ = bstack1lll111llll_opy_
        self.config = config
        self.bin_session_id = bin_session_id
        self.bstack1llllll1l11_opy_ = bstack1llllll1l11_opy_
        if self.bin_session_id:
            self.logger.debug(bstack11l111_opy_ (u"ࠨ࡛ࡼ࡫ࡧࠬࡸ࡫࡬ࡧࠫࢀࡡࠥࡩ࡯࡯ࡨ࡬࡫ࡺࡸࡥࡥࠢࡰࡳࡩࡻ࡬ࡦࠢࡾࡷࡪࡲࡦ࠯ࡡࡢࡧࡱࡧࡳࡴࡡࡢ࠲ࡤࡥ࡮ࡢ࡯ࡨࡣࡤࢃ࠺ࠡࡤ࡬ࡲࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡩࡥ࠿ࠥእ") + str(self.bin_session_id) + bstack11l111_opy_ (u"ࠢࠣኦ"))
    def bstack1ll111111l1_opy_(self):
        if not self.bin_session_id:
            raise ValueError(bstack11l111_opy_ (u"ࠣࡤ࡬ࡲࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡩࡥࠢࡦࡥࡳࡴ࡯ࡵࠢࡥࡩࠥࡔ࡯࡯ࡧࠥኧ"))
    @abc.abstractmethod
    def is_enabled(self) -> bool:
        return False