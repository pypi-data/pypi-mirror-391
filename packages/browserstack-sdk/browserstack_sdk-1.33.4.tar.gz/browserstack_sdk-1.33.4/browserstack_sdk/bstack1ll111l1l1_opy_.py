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
import multiprocessing
import os
from bstack_utils.config import Config
class bstack1l1l1l11l_opy_():
  def __init__(self, args, logger, bstack11111l1ll1_opy_, bstack1111111lll_opy_, bstack1lllllll1l1_opy_):
    self.args = args
    self.logger = logger
    self.bstack11111l1ll1_opy_ = bstack11111l1ll1_opy_
    self.bstack1111111lll_opy_ = bstack1111111lll_opy_
    self.bstack1lllllll1l1_opy_ = bstack1lllllll1l1_opy_
  def bstack111lll1ll1_opy_(self, bstack111111l111_opy_, bstack11lll1111_opy_, bstack1lllllll11l_opy_=False):
    bstack1l11ll1ll_opy_ = []
    manager = multiprocessing.Manager()
    bstack11111ll1l1_opy_ = manager.list()
    bstack11l11ll1l_opy_ = Config.bstack111llll1_opy_()
    if bstack1lllllll11l_opy_:
      for index, platform in enumerate(self.bstack11111l1ll1_opy_[bstack11l111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫგ")]):
        if index == 0:
          bstack11lll1111_opy_[bstack11l111_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬდ")] = self.args
        bstack1l11ll1ll_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack111111l111_opy_,
                                                    args=(bstack11lll1111_opy_, bstack11111ll1l1_opy_)))
    else:
      for index, platform in enumerate(self.bstack11111l1ll1_opy_[bstack11l111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ე")]):
        bstack1l11ll1ll_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack111111l111_opy_,
                                                    args=(bstack11lll1111_opy_, bstack11111ll1l1_opy_)))
    i = 0
    for t in bstack1l11ll1ll_opy_:
      try:
        if bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠬვ")):
          os.environ[bstack11l111_opy_ (u"ࠬࡉࡕࡓࡔࡈࡒ࡙ࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡆࡄࡘࡆ࠭ზ")] = json.dumps(self.bstack11111l1ll1_opy_[bstack11l111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩთ")][i % self.bstack1lllllll1l1_opy_])
      except Exception as e:
        self.logger.debug(bstack11l111_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡹࡴࡰࡴ࡬ࡲ࡬ࠦࡣࡶࡴࡵࡩࡳࡺࠠࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠢࡧࡩࡹࡧࡩ࡭ࡵ࠽ࠤࢀࢃࠢი").format(str(e)))
      i += 1
      t.start()
    for t in bstack1l11ll1ll_opy_:
      t.join()
    return list(bstack11111ll1l1_opy_)