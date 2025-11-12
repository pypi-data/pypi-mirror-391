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
from bstack_utils.bstack11l111111l_opy_ import get_logger
logger = get_logger(__name__)
class bstack11l1lllll11_opy_(object):
  bstack1ll11l1ll_opy_ = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"࠭ࡾࠨឭ")), bstack11l111_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧឮ"))
  bstack11l1lllllll_opy_ = os.path.join(bstack1ll11l1ll_opy_, bstack11l111_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࡵ࠱࡮ࡸࡵ࡮ࠨឯ"))
  commands_to_wrap = None
  perform_scan = None
  bstack1l111l1111_opy_ = None
  bstack1l1llll1l1_opy_ = None
  bstack11ll11l1ll1_opy_ = None
  bstack11ll1111l1l_opy_ = None
  def __new__(cls):
    if not hasattr(cls, bstack11l111_opy_ (u"ࠩ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠫឰ")):
      cls.instance = super(bstack11l1lllll11_opy_, cls).__new__(cls)
      cls.instance.bstack11l1lllll1l_opy_()
    return cls.instance
  def bstack11l1lllll1l_opy_(self):
    try:
      with open(self.bstack11l1lllllll_opy_, bstack11l111_opy_ (u"ࠪࡶࠬឱ")) as bstack11l1ll11ll_opy_:
        bstack11ll1111111_opy_ = bstack11l1ll11ll_opy_.read()
        data = json.loads(bstack11ll1111111_opy_)
        if bstack11l111_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡸ࠭ឲ") in data:
          self.bstack11ll11ll1l1_opy_(data[bstack11l111_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹࠧឳ")])
        if bstack11l111_opy_ (u"࠭ࡳࡤࡴ࡬ࡴࡹࡹࠧ឴") in data:
          self.bstack111lllll1_opy_(data[bstack11l111_opy_ (u"ࠧࡴࡥࡵ࡭ࡵࡺࡳࠨ឵")])
        if bstack11l111_opy_ (u"ࠨࡰࡲࡲࡇ࡙ࡴࡢࡥ࡮ࡍࡳ࡬ࡲࡢࡃ࠴࠵ࡾࡉࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬា") in data:
          self.bstack11l1llllll1_opy_(data[bstack11l111_opy_ (u"ࠩࡱࡳࡳࡈࡓࡵࡣࡦ࡯ࡎࡴࡦࡳࡣࡄ࠵࠶ࡿࡃࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ិ")])
    except:
      pass
  def bstack11l1llllll1_opy_(self, bstack11ll1111l1l_opy_):
    if bstack11ll1111l1l_opy_ != None:
      self.bstack11ll1111l1l_opy_ = bstack11ll1111l1l_opy_
  def bstack111lllll1_opy_(self, scripts):
    if scripts != None:
      self.perform_scan = scripts.get(bstack11l111_opy_ (u"ࠪࡷࡨࡧ࡮ࠨី"),bstack11l111_opy_ (u"ࠫࠬឹ"))
      self.bstack1l111l1111_opy_ = scripts.get(bstack11l111_opy_ (u"ࠬ࡭ࡥࡵࡔࡨࡷࡺࡲࡴࡴࠩឺ"),bstack11l111_opy_ (u"࠭ࠧុ"))
      self.bstack1l1llll1l1_opy_ = scripts.get(bstack11l111_opy_ (u"ࠧࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࡗࡺࡳ࡭ࡢࡴࡼࠫូ"),bstack11l111_opy_ (u"ࠨࠩួ"))
      self.bstack11ll11l1ll1_opy_ = scripts.get(bstack11l111_opy_ (u"ࠩࡶࡥࡻ࡫ࡒࡦࡵࡸࡰࡹࡹࠧើ"),bstack11l111_opy_ (u"ࠪࠫឿ"))
  def bstack11ll11ll1l1_opy_(self, commands_to_wrap):
    if commands_to_wrap != None and len(commands_to_wrap) != 0:
      self.commands_to_wrap = commands_to_wrap
  def store(self):
    try:
      with open(self.bstack11l1lllllll_opy_, bstack11l111_opy_ (u"ࠫࡼ࠭ៀ")) as file:
        json.dump({
          bstack11l111_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡹࠢេ"): self.commands_to_wrap,
          bstack11l111_opy_ (u"ࠨࡳࡤࡴ࡬ࡴࡹࡹࠢែ"): {
            bstack11l111_opy_ (u"ࠢࡴࡥࡤࡲࠧៃ"): self.perform_scan,
            bstack11l111_opy_ (u"ࠣࡩࡨࡸࡗ࡫ࡳࡶ࡮ࡷࡷࠧោ"): self.bstack1l111l1111_opy_,
            bstack11l111_opy_ (u"ࠤࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸ࡙ࡵ࡮࡯ࡤࡶࡾࠨៅ"): self.bstack1l1llll1l1_opy_,
            bstack11l111_opy_ (u"ࠥࡷࡦࡼࡥࡓࡧࡶࡹࡱࡺࡳࠣំ"): self.bstack11ll11l1ll1_opy_
          },
          bstack11l111_opy_ (u"ࠦࡳࡵ࡮ࡃࡕࡷࡥࡨࡱࡉ࡯ࡨࡵࡥࡆ࠷࠱ࡺࡅ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠣះ"): self.bstack11ll1111l1l_opy_
        }, file)
    except Exception as e:
      logger.error(bstack11l111_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡷࡹࡵࡲࡪࡰࡪࠤࡨࡵ࡭࡮ࡣࡱࡨࡸࡀࠠࡼࡿࠥៈ").format(e))
      pass
  def bstack111111l1_opy_(self, command_name):
    try:
      return any(command.get(bstack11l111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ៉")) == command_name for command in self.commands_to_wrap)
    except:
      return False
bstack1ll11l1lll_opy_ = bstack11l1lllll11_opy_()