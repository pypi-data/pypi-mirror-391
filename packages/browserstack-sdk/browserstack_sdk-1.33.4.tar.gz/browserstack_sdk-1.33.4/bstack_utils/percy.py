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
import re
import sys
import json
import time
import shutil
import tempfile
import requests
import subprocess
from threading import Thread
from os.path import expanduser
from bstack_utils.constants import *
from requests.auth import HTTPBasicAuth
from bstack_utils.helper import bstack111lllll1l_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1ll1lllll1_opy_ import bstack1l1l1111l1_opy_
class bstack1ll1l111ll_opy_:
  working_dir = os.getcwd()
  bstack1l1l111lll_opy_ = False
  config = {}
  bstack111lll1l1l1_opy_ = bstack11l111_opy_ (u"ࠫࠬἾ")
  binary_path = bstack11l111_opy_ (u"ࠬ࠭Ἷ")
  bstack11111ll11ll_opy_ = bstack11l111_opy_ (u"࠭ࠧὀ")
  bstack111111111_opy_ = False
  bstack11111l11lll_opy_ = None
  bstack1111l111111_opy_ = {}
  bstack11111l1lll1_opy_ = 300
  bstack111111l1lll_opy_ = False
  logger = None
  bstack11111lllll1_opy_ = False
  bstack1l1ll11l1l_opy_ = False
  percy_build_id = None
  bstack11111l111l1_opy_ = bstack11l111_opy_ (u"ࠧࠨὁ")
  bstack111111l1ll1_opy_ = {
    bstack11l111_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࠨὂ") : 1,
    bstack11l111_opy_ (u"ࠩࡩ࡭ࡷ࡫ࡦࡰࡺࠪὃ") : 2,
    bstack11l111_opy_ (u"ࠪࡩࡩ࡭ࡥࠨὄ") : 3,
    bstack11l111_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬ࠫὅ") : 4
  }
  def __init__(self) -> None: pass
  def bstack11111l111ll_opy_(self):
    bstack11111ll11l1_opy_ = bstack11l111_opy_ (u"ࠬ࠭὆")
    bstack11111ll111l_opy_ = sys.platform
    bstack111111l111l_opy_ = bstack11l111_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬ὇")
    if re.match(bstack11l111_opy_ (u"ࠢࡥࡣࡵࡻ࡮ࡴࡼ࡮ࡣࡦࠤࡴࡹࠢὈ"), bstack11111ll111l_opy_) != None:
      bstack11111ll11l1_opy_ = bstack11l1l1lll1l_opy_ + bstack11l111_opy_ (u"ࠣ࠱ࡳࡩࡷࡩࡹ࠮ࡱࡶࡼ࠳ࢀࡩࡱࠤὉ")
      self.bstack11111l111l1_opy_ = bstack11l111_opy_ (u"ࠩࡰࡥࡨ࠭Ὂ")
    elif re.match(bstack11l111_opy_ (u"ࠥࡱࡸࡽࡩ࡯ࡾࡰࡷࡾࡹࡼ࡮࡫ࡱ࡫ࡼࢂࡣࡺࡩࡺ࡭ࡳࢂࡢࡤࡥࡺ࡭ࡳࢂࡷࡪࡰࡦࡩࢁ࡫࡭ࡤࡾࡺ࡭ࡳ࠹࠲ࠣὋ"), bstack11111ll111l_opy_) != None:
      bstack11111ll11l1_opy_ = bstack11l1l1lll1l_opy_ + bstack11l111_opy_ (u"ࠦ࠴ࡶࡥࡳࡥࡼ࠱ࡼ࡯࡮࠯ࡼ࡬ࡴࠧὌ")
      bstack111111l111l_opy_ = bstack11l111_opy_ (u"ࠧࡶࡥࡳࡥࡼ࠲ࡪࡾࡥࠣὍ")
      self.bstack11111l111l1_opy_ = bstack11l111_opy_ (u"࠭ࡷࡪࡰࠪ὎")
    else:
      bstack11111ll11l1_opy_ = bstack11l1l1lll1l_opy_ + bstack11l111_opy_ (u"ࠢ࠰ࡲࡨࡶࡨࡿ࠭࡭࡫ࡱࡹࡽ࠴ࡺࡪࡲࠥ὏")
      self.bstack11111l111l1_opy_ = bstack11l111_opy_ (u"ࠨ࡮࡬ࡲࡺࡾࠧὐ")
    return bstack11111ll11l1_opy_, bstack111111l111l_opy_
  def bstack1111111l111_opy_(self):
    try:
      bstack1111111lll1_opy_ = [os.path.join(expanduser(bstack11l111_opy_ (u"ࠤࢁࠦὑ")), bstack11l111_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪὒ")), self.working_dir, tempfile.gettempdir()]
      for path in bstack1111111lll1_opy_:
        if(self.bstack11111l11l11_opy_(path)):
          return path
      raise bstack11l111_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡥࡱࡺࡲࡱࡵࡡࡥࠢࡳࡩࡷࡩࡹࠡࡤ࡬ࡲࡦࡸࡹࠣὓ")
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡨ࡬ࡲࡩࠦࡡࡷࡣ࡬ࡰࡦࡨ࡬ࡦࠢࡳࡥࡹ࡮ࠠࡧࡱࡵࠤࡵ࡫ࡲࡤࡻࠣࡨࡴࡽ࡮࡭ࡱࡤࡨ࠱ࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࠰ࠤࢀࢃࠢὔ").format(e))
  def bstack11111l11l11_opy_(self, path):
    try:
      if not os.path.exists(path):
        os.makedirs(path)
      return True
    except:
      return False
  def bstack11111111lll_opy_(self, bstack111111lll1l_opy_):
    return os.path.join(bstack111111lll1l_opy_, self.bstack111lll1l1l1_opy_ + bstack11l111_opy_ (u"ࠨ࠮ࡦࡶࡤ࡫ࠧὕ"))
  def bstack111111111ll_opy_(self, bstack111111lll1l_opy_, bstack11111llll1l_opy_):
    if not bstack11111llll1l_opy_: return
    try:
      bstack11111l1l11l_opy_ = self.bstack11111111lll_opy_(bstack111111lll1l_opy_)
      with open(bstack11111l1l11l_opy_, bstack11l111_opy_ (u"ࠢࡸࠤὖ")) as f:
        f.write(bstack11111llll1l_opy_)
        self.logger.debug(bstack11l111_opy_ (u"ࠣࡕࡤࡺࡪࡪࠠ࡯ࡧࡺࠤࡊ࡚ࡡࡨࠢࡩࡳࡷࠦࡰࡦࡴࡦࡽࠧὗ"))
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡹࡡࡷࡧࠣࡸ࡭࡫ࠠࡦࡶࡤ࡫࠱ࠦࡥࡳࡴࡲࡶ࠿ࠦࡻࡾࠤ὘").format(e))
  def bstack11111111111_opy_(self, bstack111111lll1l_opy_):
    try:
      bstack11111l1l11l_opy_ = self.bstack11111111lll_opy_(bstack111111lll1l_opy_)
      if os.path.exists(bstack11111l1l11l_opy_):
        with open(bstack11111l1l11l_opy_, bstack11l111_opy_ (u"ࠥࡶࠧὙ")) as f:
          bstack11111llll1l_opy_ = f.read().strip()
          return bstack11111llll1l_opy_ if bstack11111llll1l_opy_ else None
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡱࡵࡡࡥ࡫ࡱ࡫ࠥࡋࡔࡢࡩ࠯ࠤࡪࡸࡲࡰࡴ࠽ࠤࢀࢃࠢ὚").format(e))
  def bstack11111llllll_opy_(self, bstack111111lll1l_opy_, bstack11111ll11l1_opy_):
    bstack11111ll1lll_opy_ = self.bstack11111111111_opy_(bstack111111lll1l_opy_)
    if bstack11111ll1lll_opy_:
      try:
        bstack11111ll1l1l_opy_ = self.bstack11111111l1l_opy_(bstack11111ll1lll_opy_, bstack11111ll11l1_opy_)
        if not bstack11111ll1l1l_opy_:
          self.logger.debug(bstack11l111_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠤ࡮ࡹࠠࡶࡲࠣࡸࡴࠦࡤࡢࡶࡨࠤ࠭ࡋࡔࡢࡩࠣࡹࡳࡩࡨࡢࡰࡪࡩࡩ࠯ࠢὛ"))
          return True
        self.logger.debug(bstack11l111_opy_ (u"ࠨࡎࡦࡹࠣࡔࡪࡸࡣࡺࠢࡥ࡭ࡳࡧࡲࡺࠢࡹࡩࡷࡹࡩࡰࡰࠣࡥࡻࡧࡩ࡭ࡣࡥࡰࡪ࠲ࠠࡥࡱࡺࡲࡱࡵࡡࡥ࡫ࡱ࡫ࠥࡻࡰࡥࡣࡷࡩࠧ὜"))
        return False
      except Exception as e:
        self.logger.warn(bstack11l111_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡧ࡭࡫ࡣ࡬ࠢࡩࡳࡷࠦࡢࡪࡰࡤࡶࡾࠦࡵࡱࡦࡤࡸࡪࡹࠬࠡࡷࡶ࡭ࡳ࡭ࠠࡦࡺ࡬ࡷࡹ࡯࡮ࡨࠢࡥ࡭ࡳࡧࡲࡺ࠼ࠣࡿࢂࠨὝ").format(e))
    return False
  def bstack11111111l1l_opy_(self, bstack11111ll1lll_opy_, bstack11111ll11l1_opy_):
    try:
      headers = {
        bstack11l111_opy_ (u"ࠣࡋࡩ࠱ࡓࡵ࡮ࡦ࠯ࡐࡥࡹࡩࡨࠣ὞"): bstack11111ll1lll_opy_
      }
      response = bstack111lllll1l_opy_(bstack11l111_opy_ (u"ࠩࡊࡉ࡙࠭Ὗ"), bstack11111ll11l1_opy_, {}, {bstack11l111_opy_ (u"ࠥ࡬ࡪࡧࡤࡦࡴࡶࠦὠ"): headers})
      if response.status_code == 304:
        return False
      return True
    except Exception as e:
      raise(bstack11l111_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡧ࡭࡫ࡣ࡬࡫ࡱ࡫ࠥ࡬࡯ࡳࠢࡓࡩࡷࡩࡹࠡࡤ࡬ࡲࡦࡸࡹࠡࡷࡳࡨࡦࡺࡥࡴ࠼ࠣࡿࢂࠨὡ").format(e))
  @measure(event_name=EVENTS.bstack11l1l111ll1_opy_, stage=STAGE.bstack1l1l111l1_opy_)
  def bstack111111ll111_opy_(self, bstack11111ll11l1_opy_, bstack111111l111l_opy_):
    try:
      bstack111111ll11l_opy_ = self.bstack1111111l111_opy_()
      bstack11111lll1l1_opy_ = os.path.join(bstack111111ll11l_opy_, bstack11l111_opy_ (u"ࠬࡶࡥࡳࡥࡼ࠲ࡿ࡯ࡰࠨὢ"))
      bstack111111l11l1_opy_ = os.path.join(bstack111111ll11l_opy_, bstack111111l111l_opy_)
      if self.bstack11111llllll_opy_(bstack111111ll11l_opy_, bstack11111ll11l1_opy_): # if bstack11111l1111l_opy_, bstack1l11llll11l_opy_ bstack11111llll1l_opy_ is bstack111111l11ll_opy_ to bstack11l11l1111l_opy_ version available (response 304)
        if os.path.exists(bstack111111l11l1_opy_):
          self.logger.info(bstack11l111_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࡨࡩ࡯ࡣࡵࡽࠥ࡬࡯ࡶࡰࡧࠤ࡮ࡴࠠࡼࡿ࠯ࠤࡸࡱࡩࡱࡲ࡬ࡲ࡬ࠦࡤࡰࡹࡱࡰࡴࡧࡤࠣὣ").format(bstack111111l11l1_opy_))
          return bstack111111l11l1_opy_
        if os.path.exists(bstack11111lll1l1_opy_):
          self.logger.info(bstack11l111_opy_ (u"ࠢࡑࡧࡵࡧࡾࠦࡺࡪࡲࠣࡪࡴࡻ࡮ࡥࠢ࡬ࡲࠥࢁࡽ࠭ࠢࡸࡲࡿ࡯ࡰࡱ࡫ࡱ࡫ࠧὤ").format(bstack11111lll1l1_opy_))
          return self.bstack11111111l11_opy_(bstack11111lll1l1_opy_, bstack111111l111l_opy_)
      self.logger.info(bstack11l111_opy_ (u"ࠣࡆࡲࡻࡳࡲ࡯ࡢࡦ࡬ࡲ࡬ࠦࡰࡦࡴࡦࡽࠥࡨࡩ࡯ࡣࡵࡽࠥ࡬ࡲࡰ࡯ࠣࡿࢂࠨὥ").format(bstack11111ll11l1_opy_))
      response = bstack111lllll1l_opy_(bstack11l111_opy_ (u"ࠩࡊࡉ࡙࠭ὦ"), bstack11111ll11l1_opy_, {}, {})
      if response.status_code == 200:
        bstack111111ll1ll_opy_ = response.headers.get(bstack11l111_opy_ (u"ࠥࡉ࡙ࡧࡧࠣὧ"), bstack11l111_opy_ (u"ࠦࠧὨ"))
        if bstack111111ll1ll_opy_:
          self.bstack111111111ll_opy_(bstack111111ll11l_opy_, bstack111111ll1ll_opy_)
        with open(bstack11111lll1l1_opy_, bstack11l111_opy_ (u"ࠬࡽࡢࠨὩ")) as file:
          file.write(response.content)
        self.logger.info(bstack11l111_opy_ (u"ࠨࡄࡰࡹࡱࡰࡴࡧࡤࡦࡦࠣࡴࡪࡸࡣࡺࠢࡥ࡭ࡳࡧࡲࡺࠢࡤࡲࡩࠦࡳࡢࡸࡨࡨࠥࡧࡴࠡࡽࢀࠦὪ").format(bstack11111lll1l1_opy_))
        return self.bstack11111111l11_opy_(bstack11111lll1l1_opy_, bstack111111l111l_opy_)
      else:
        raise(bstack11l111_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡨࡴࡽ࡮࡭ࡱࡤࡨࠥࡺࡨࡦࠢࡩ࡭ࡱ࡫࠮ࠡࡕࡷࡥࡹࡻࡳࠡࡥࡲࡨࡪࡀࠠࡼࡿࠥὫ").format(response.status_code))
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡩࡵࡷ࡯࡮ࡲࡥࡩࠦࡰࡦࡴࡦࡽࠥࡨࡩ࡯ࡣࡵࡽ࠿ࠦࡻࡾࠤὬ").format(e))
  def bstack111111lll11_opy_(self, bstack11111ll11l1_opy_, bstack111111l111l_opy_):
    try:
      retry = 2
      bstack111111l11l1_opy_ = None
      bstack11111l1l111_opy_ = False
      while retry > 0:
        bstack111111l11l1_opy_ = self.bstack111111ll111_opy_(bstack11111ll11l1_opy_, bstack111111l111l_opy_)
        bstack11111l1l111_opy_ = self.bstack111111ll1l1_opy_(bstack11111ll11l1_opy_, bstack111111l111l_opy_, bstack111111l11l1_opy_)
        if bstack11111l1l111_opy_:
          break
        retry -= 1
      return bstack111111l11l1_opy_, bstack11111l1l111_opy_
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥ࡭ࡥࡵࠢࡳࡩࡷࡩࡹࠡࡤ࡬ࡲࡦࡸࡹࠡࡲࡤࡸ࡭ࠨὭ").format(e))
    return bstack111111l11l1_opy_, False
  def bstack111111ll1l1_opy_(self, bstack11111ll11l1_opy_, bstack111111l111l_opy_, bstack111111l11l1_opy_, bstack11111l11ll1_opy_ = 0):
    if bstack11111l11ll1_opy_ > 1:
      return False
    if bstack111111l11l1_opy_ == None or os.path.exists(bstack111111l11l1_opy_) == False:
      self.logger.warn(bstack11l111_opy_ (u"ࠥࡔࡪࡸࡣࡺࠢࡳࡥࡹ࡮ࠠ࡯ࡱࡷࠤ࡫ࡵࡵ࡯ࡦ࠯ࠤࡷ࡫ࡴࡳࡻ࡬ࡲ࡬ࠦࡤࡰࡹࡱࡰࡴࡧࡤࠣὮ"))
      return False
    bstack1111111l1ll_opy_ = bstack11l111_opy_ (u"ࡶࠧࡤ࠮ࠫࡂࡳࡩࡷࡩࡹ࠰ࡥ࡯࡭ࠥࡢࡤࠬ࡞࠱ࡠࡩ࠱࡜࠯࡞ࡧ࠯ࠧὯ")
    command = bstack11l111_opy_ (u"ࠬࢁࡽࠡ࠯࠰ࡺࡪࡸࡳࡪࡱࡱࠫὰ").format(bstack111111l11l1_opy_)
    bstack11111l1llll_opy_ = subprocess.check_output(command, shell=True, text=True)
    if re.match(bstack1111111l1ll_opy_, bstack11111l1llll_opy_) != None:
      return True
    else:
      self.logger.error(bstack11l111_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࡼࡥࡳࡵ࡬ࡳࡳࠦࡣࡩࡧࡦ࡯ࠥ࡬ࡡࡪ࡮ࡨࡨࠧά"))
      return False
  def bstack11111111l11_opy_(self, bstack11111lll1l1_opy_, bstack111111l111l_opy_):
    try:
      working_dir = os.path.dirname(bstack11111lll1l1_opy_)
      shutil.unpack_archive(bstack11111lll1l1_opy_, working_dir)
      bstack111111l11l1_opy_ = os.path.join(working_dir, bstack111111l111l_opy_)
      os.chmod(bstack111111l11l1_opy_, 0o755)
      return bstack111111l11l1_opy_
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡹࡳࢀࡩࡱࠢࡳࡩࡷࡩࡹࠡࡤ࡬ࡲࡦࡸࡹࠣὲ"))
  def bstack11111ll1111_opy_(self):
    try:
      bstack111111111l1_opy_ = self.config.get(bstack11l111_opy_ (u"ࠨࡲࡨࡶࡨࡿࠧέ"))
      bstack11111ll1111_opy_ = bstack111111111l1_opy_ or (bstack111111111l1_opy_ is None and self.bstack1l1l111lll_opy_)
      if not bstack11111ll1111_opy_ or self.config.get(bstack11l111_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬὴ"), None) not in bstack11l1l1lllll_opy_:
        return False
      self.bstack111111111_opy_ = True
      return True
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡤࡦࡶࡨࡧࡹࠦࡰࡦࡴࡦࡽ࠱ࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡾࢁࠧή").format(e))
  def bstack11111ll1ll1_opy_(self):
    try:
      bstack11111ll1ll1_opy_ = self.percy_capture_mode
      return bstack11111ll1ll1_opy_
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡥࡧࡷࡩࡨࡺࠠࡱࡧࡵࡧࡾࠦࡣࡢࡲࡷࡹࡷ࡫ࠠ࡮ࡱࡧࡩ࠱ࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡾࢁࠧὶ").format(e))
  def init(self, bstack1l1l111lll_opy_, config, logger):
    self.bstack1l1l111lll_opy_ = bstack1l1l111lll_opy_
    self.config = config
    self.logger = logger
    if not self.bstack11111ll1111_opy_():
      return
    self.bstack1111l111111_opy_ = config.get(bstack11l111_opy_ (u"ࠬࡶࡥࡳࡥࡼࡓࡵࡺࡩࡰࡰࡶࠫί"), {})
    self.percy_capture_mode = config.get(bstack11l111_opy_ (u"࠭ࡰࡦࡴࡦࡽࡈࡧࡰࡵࡷࡵࡩࡒࡵࡤࡦࠩὸ"))
    try:
      bstack11111ll11l1_opy_, bstack111111l111l_opy_ = self.bstack11111l111ll_opy_()
      self.bstack111lll1l1l1_opy_ = bstack111111l111l_opy_
      bstack111111l11l1_opy_, bstack11111l1l111_opy_ = self.bstack111111lll11_opy_(bstack11111ll11l1_opy_, bstack111111l111l_opy_)
      if bstack11111l1l111_opy_:
        self.binary_path = bstack111111l11l1_opy_
        thread = Thread(target=self.bstack1111111l1l1_opy_)
        thread.start()
      else:
        self.bstack11111lllll1_opy_ = True
        self.logger.error(bstack11l111_opy_ (u"ࠢࡊࡰࡹࡥࡱ࡯ࡤࠡࡲࡨࡶࡨࡿࠠࡱࡣࡷ࡬ࠥ࡬࡯ࡶࡰࡧࠤ࠲ࠦࡻࡾ࠮࡙ࠣࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡖࡥࡳࡥࡼࠦό").format(bstack111111l11l1_opy_))
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡺࡡࡳࡶࠣࡴࡪࡸࡣࡺ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡻࡾࠤὺ").format(e))
  def bstack11111l11l1l_opy_(self):
    try:
      logfile = os.path.join(self.working_dir, bstack11l111_opy_ (u"ࠩ࡯ࡳ࡬࠭ύ"), bstack11l111_opy_ (u"ࠪࡴࡪࡸࡣࡺ࠰࡯ࡳ࡬࠭ὼ"))
      os.makedirs(os.path.dirname(logfile)) if not os.path.exists(os.path.dirname(logfile)) else None
      self.logger.debug(bstack11l111_opy_ (u"ࠦࡕࡻࡳࡩ࡫ࡱ࡫ࠥࡶࡥࡳࡥࡼࠤࡱࡵࡧࡴࠢࡤࡸࠥࢁࡽࠣώ").format(logfile))
      self.bstack11111ll11ll_opy_ = logfile
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡨࡸࠥࡶࡥࡳࡥࡼࠤࡱࡵࡧࠡࡲࡤࡸ࡭࠲ࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡿࢂࠨ὾").format(e))
  @measure(event_name=EVENTS.bstack11l1l111111_opy_, stage=STAGE.bstack1l1l111l1_opy_)
  def bstack1111111l1l1_opy_(self):
    bstack11111llll11_opy_ = self.bstack1111111111l_opy_()
    if bstack11111llll11_opy_ == None:
      self.bstack11111lllll1_opy_ = True
      self.logger.error(bstack11l111_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࡺ࡯࡬ࡧࡱࠤࡳࡵࡴࠡࡨࡲࡹࡳࡪࠬࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸࡺࡡࡳࡶࠣࡴࡪࡸࡣࡺࠤ὿"))
      return False
    bstack1111111llll_opy_ = [bstack11l111_opy_ (u"ࠢࡢࡲࡳ࠾ࡪࡾࡥࡤ࠼ࡶࡸࡦࡸࡴࠣᾀ") if self.bstack1l1l111lll_opy_ else bstack11l111_opy_ (u"ࠨࡧࡻࡩࡨࡀࡳࡵࡣࡵࡸࠬᾁ")]
    bstack111l11l11l1_opy_ = self.bstack1111111ll11_opy_()
    if bstack111l11l11l1_opy_ != None:
      bstack1111111llll_opy_.append(bstack11l111_opy_ (u"ࠤ࠰ࡧࠥࢁࡽࠣᾂ").format(bstack111l11l11l1_opy_))
    env = os.environ.copy()
    env[bstack11l111_opy_ (u"ࠥࡔࡊࡘࡃ࡚ࡡࡗࡓࡐࡋࡎࠣᾃ")] = bstack11111llll11_opy_
    env[bstack11l111_opy_ (u"࡙ࠦࡎ࡟ࡃࡗࡌࡐࡉࡥࡕࡖࡋࡇࠦᾄ")] = os.environ.get(bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪᾅ"), bstack11l111_opy_ (u"࠭ࠧᾆ"))
    bstack111111l1l11_opy_ = [self.binary_path]
    self.bstack11111l11l1l_opy_()
    self.bstack11111l11lll_opy_ = self.bstack111111l1l1l_opy_(bstack111111l1l11_opy_ + bstack1111111llll_opy_, env)
    self.logger.debug(bstack11l111_opy_ (u"ࠢࡔࡶࡤࡶࡹ࡯࡮ࡨࠢࡋࡩࡦࡲࡴࡩࠢࡆ࡬ࡪࡩ࡫ࠣᾇ"))
    bstack11111l11ll1_opy_ = 0
    while self.bstack11111l11lll_opy_.poll() == None:
      bstack11111l1l1ll_opy_ = self.bstack1lllllllllll_opy_()
      if bstack11111l1l1ll_opy_:
        self.logger.debug(bstack11l111_opy_ (u"ࠣࡊࡨࡥࡱࡺࡨࠡࡅ࡫ࡩࡨࡱࠠࡴࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࠦᾈ"))
        self.bstack111111l1lll_opy_ = True
        return True
      bstack11111l11ll1_opy_ += 1
      self.logger.debug(bstack11l111_opy_ (u"ࠤࡋࡩࡦࡲࡴࡩࠢࡆ࡬ࡪࡩ࡫ࠡࡔࡨࡸࡷࡿࠠ࠮ࠢࡾࢁࠧᾉ").format(bstack11111l11ll1_opy_))
      time.sleep(2)
    self.logger.error(bstack11l111_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡶࡥࡳࡥࡼ࠰ࠥࡎࡥࡢ࡮ࡷ࡬ࠥࡉࡨࡦࡥ࡮ࠤࡋࡧࡩ࡭ࡧࡧࠤࡦ࡬ࡴࡦࡴࠣࡿࢂࠦࡡࡵࡶࡨࡱࡵࡺࡳࠣᾊ").format(bstack11111l11ll1_opy_))
    self.bstack11111lllll1_opy_ = True
    return False
  def bstack1lllllllllll_opy_(self, bstack11111l11ll1_opy_ = 0):
    if bstack11111l11ll1_opy_ > 10:
      return False
    try:
      bstack111111l1111_opy_ = os.environ.get(bstack11l111_opy_ (u"ࠫࡕࡋࡒࡄ࡛ࡢࡗࡊࡘࡖࡆࡔࡢࡅࡉࡊࡒࡆࡕࡖࠫᾋ"), bstack11l111_opy_ (u"ࠬ࡮ࡴࡵࡲ࠽࠳࠴ࡲ࡯ࡤࡣ࡯࡬ࡴࡹࡴ࠻࠷࠶࠷࠽࠭ᾌ"))
      bstack11111l1ll1l_opy_ = bstack111111l1111_opy_ + bstack11l1l1ll1ll_opy_
      response = requests.get(bstack11111l1ll1l_opy_)
      data = response.json()
      self.percy_build_id = data.get(bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࠬᾍ"), {}).get(bstack11l111_opy_ (u"ࠧࡪࡦࠪᾎ"), None)
      return True
    except:
      self.logger.debug(bstack11l111_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡰࡥࡦࡹࡷࡸࡥࡥࠢࡺ࡬࡮ࡲࡥࠡࡲࡵࡳࡨ࡫ࡳࡴ࡫ࡱ࡫ࠥ࡮ࡥࡢ࡮ࡷ࡬ࠥࡩࡨࡦࡥ࡮ࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࠨᾏ"))
      return False
  def bstack1111111111l_opy_(self):
    bstack11111ll1l11_opy_ = bstack11l111_opy_ (u"ࠩࡤࡴࡵ࠭ᾐ") if self.bstack1l1l111lll_opy_ else bstack11l111_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷࡩࠬᾑ")
    bstack1111111ll1l_opy_ = bstack11l111_opy_ (u"ࠦࡺࡴࡤࡦࡨ࡬ࡲࡪࡪࠢᾒ") if self.config.get(bstack11l111_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫᾓ")) is None else True
    bstack11l1llll1l1_opy_ = bstack11l111_opy_ (u"ࠨࡡࡱ࡫࠲ࡥࡵࡶ࡟ࡱࡧࡵࡧࡾ࠵ࡧࡦࡶࡢࡴࡷࡵࡪࡦࡥࡷࡣࡹࡵ࡫ࡦࡰࡂࡲࡦࡳࡥ࠾ࡽࢀࠪࡹࡿࡰࡦ࠿ࡾࢁࠫࡶࡥࡳࡥࡼࡁࢀࢃࠢᾔ").format(self.config[bstack11l111_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬᾕ")], bstack11111ll1l11_opy_, bstack1111111ll1l_opy_)
    if self.percy_capture_mode:
      bstack11l1llll1l1_opy_ += bstack11l111_opy_ (u"ࠣࠨࡳࡩࡷࡩࡹࡠࡥࡤࡴࡹࡻࡲࡦࡡࡰࡳࡩ࡫࠽ࡼࡿࠥᾖ").format(self.percy_capture_mode)
    uri = bstack1l1l1111l1_opy_(bstack11l1llll1l1_opy_)
    try:
      response = bstack111lllll1l_opy_(bstack11l111_opy_ (u"ࠩࡊࡉ࡙࠭ᾗ"), uri, {}, {bstack11l111_opy_ (u"ࠪࡥࡺࡺࡨࠨᾘ"): (self.config[bstack11l111_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ᾙ")], self.config[bstack11l111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨᾚ")])})
      if response.status_code == 200:
        data = response.json()
        self.bstack111111111_opy_ = data.get(bstack11l111_opy_ (u"࠭ࡳࡶࡥࡦࡩࡸࡹࠧᾛ"))
        self.percy_capture_mode = data.get(bstack11l111_opy_ (u"ࠧࡱࡧࡵࡧࡾࡥࡣࡢࡲࡷࡹࡷ࡫࡟࡮ࡱࡧࡩࠬᾜ"))
        os.environ[bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡇࡕࡇ࡞࠭ᾝ")] = str(self.bstack111111111_opy_)
        os.environ[bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡈࡖࡈ࡟࡟ࡄࡃࡓࡘ࡚ࡘࡅࡠࡏࡒࡈࡊ࠭ᾞ")] = str(self.percy_capture_mode)
        if bstack1111111ll1l_opy_ == bstack11l111_opy_ (u"ࠥࡹࡳࡪࡥࡧ࡫ࡱࡩࡩࠨᾟ") and str(self.bstack111111111_opy_).lower() == bstack11l111_opy_ (u"ࠦࡹࡸࡵࡦࠤᾠ"):
          self.bstack1l1ll11l1l_opy_ = True
        if bstack11l111_opy_ (u"ࠧࡺ࡯࡬ࡧࡱࠦᾡ") in data:
          return data[bstack11l111_opy_ (u"ࠨࡴࡰ࡭ࡨࡲࠧᾢ")]
        else:
          raise bstack11l111_opy_ (u"ࠧࡕࡱ࡮ࡩࡳࠦࡎࡰࡶࠣࡊࡴࡻ࡮ࡥࠢ࠰ࠤࢀࢃࠧᾣ").format(data)
      else:
        raise bstack11l111_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤ࡫࡫ࡴࡤࡪࠣࡴࡪࡸࡣࡺࠢࡷࡳࡰ࡫࡮࠭ࠢࡕࡩࡸࡶ࡯࡯ࡵࡨࠤࡸࡺࡡࡵࡷࡶࠤ࠲ࠦࡻࡾ࠮ࠣࡖࡪࡹࡰࡰࡰࡶࡩࠥࡈ࡯ࡥࡻࠣ࠱ࠥࢁࡽࠣᾤ").format(response.status_code, response.json())
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡥࡵࡩࡦࡺࡩ࡯ࡩࠣࡴࡪࡸࡣࡺࠢࡳࡶࡴࡰࡥࡤࡶࠥᾥ").format(e))
  def bstack1111111ll11_opy_(self):
    bstack1111111l11l_opy_ = os.path.join(tempfile.gettempdir(), bstack11l111_opy_ (u"ࠥࡴࡪࡸࡣࡺࡅࡲࡲ࡫࡯ࡧ࠯࡬ࡶࡳࡳࠨᾦ"))
    try:
      if bstack11l111_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࠬᾧ") not in self.bstack1111l111111_opy_:
        self.bstack1111l111111_opy_[bstack11l111_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳ࠭ᾨ")] = 2
      with open(bstack1111111l11l_opy_, bstack11l111_opy_ (u"࠭ࡷࠨᾩ")) as fp:
        json.dump(self.bstack1111l111111_opy_, fp)
      return bstack1111111l11l_opy_
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡧࡷ࡫ࡡࡵࡧࠣࡴࡪࡸࡣࡺࠢࡦࡳࡳ࡬ࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢᾪ").format(e))
  def bstack111111l1l1l_opy_(self, cmd, env = os.environ.copy()):
    try:
      if self.bstack11111l111l1_opy_ == bstack11l111_opy_ (u"ࠨࡹ࡬ࡲࠬᾫ"):
        bstack1llllllllll1_opy_ = [bstack11l111_opy_ (u"ࠩࡦࡱࡩ࠴ࡥࡹࡧࠪᾬ"), bstack11l111_opy_ (u"ࠪ࠳ࡨ࠭ᾭ")]
        cmd = bstack1llllllllll1_opy_ + cmd
      cmd = bstack11l111_opy_ (u"ࠫࠥ࠭ᾮ").join(cmd)
      self.logger.debug(bstack11l111_opy_ (u"ࠧࡘࡵ࡯ࡰ࡬ࡲ࡬ࠦࡻࡾࠤᾯ").format(cmd))
      with open(self.bstack11111ll11ll_opy_, bstack11l111_opy_ (u"ࠨࡡࠣᾰ")) as bstack111111llll1_opy_:
        process = subprocess.Popen(cmd, shell=True, stdout=bstack111111llll1_opy_, text=True, stderr=bstack111111llll1_opy_, env=env, universal_newlines=True)
      return process
    except Exception as e:
      self.bstack11111lllll1_opy_ = True
      self.logger.error(bstack11l111_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡹࡧࡲࡵࠢࡳࡩࡷࡩࡹࠡࡹ࡬ࡸ࡭ࠦࡣ࡮ࡦࠣ࠱ࠥࢁࡽ࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲ࠿ࠦࡻࡾࠤᾱ").format(cmd, e))
  def shutdown(self):
    try:
      if self.bstack111111l1lll_opy_:
        self.logger.info(bstack11l111_opy_ (u"ࠣࡕࡷࡳࡵࡶࡩ࡯ࡩࠣࡔࡪࡸࡣࡺࠤᾲ"))
        cmd = [self.binary_path, bstack11l111_opy_ (u"ࠤࡨࡼࡪࡩ࠺ࡴࡶࡲࡴࠧᾳ")]
        self.bstack111111l1l1l_opy_(cmd)
        self.bstack111111l1lll_opy_ = False
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡵࡱࡳࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡽࡩࡵࡪࠣࡧࡴࡳ࡭ࡢࡰࡧࠤ࠲ࠦࡻࡾ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࡀࠠࡼࡿࠥᾴ").format(cmd, e))
  def bstack1l1l1lllll_opy_(self):
    if not self.bstack111111111_opy_:
      return
    try:
      bstack11111lll1ll_opy_ = 0
      while not self.bstack111111l1lll_opy_ and bstack11111lll1ll_opy_ < self.bstack11111l1lll1_opy_:
        if self.bstack11111lllll1_opy_:
          self.logger.info(bstack11l111_opy_ (u"ࠦࡕ࡫ࡲࡤࡻࠣࡷࡪࡺࡵࡱࠢࡩࡥ࡮ࡲࡥࡥࠤ᾵"))
          return
        time.sleep(1)
        bstack11111lll1ll_opy_ += 1
      os.environ[bstack11l111_opy_ (u"ࠬࡖࡅࡓࡅ࡜ࡣࡇࡋࡓࡕࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࠫᾶ")] = str(self.bstack11111l11111_opy_())
      self.logger.info(bstack11l111_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࡹࡥࡵࡷࡳࠤࡨࡵ࡭ࡱ࡮ࡨࡸࡪࡪࠢᾷ"))
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡪࡺࡵࡱࠢࡳࡩࡷࡩࡹ࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࢁࡽࠣᾸ").format(e))
  def bstack11111l11111_opy_(self):
    if self.bstack1l1l111lll_opy_:
      return
    try:
      bstack11111111ll1_opy_ = [platform[bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭Ᾱ")].lower() for platform in self.config.get(bstack11l111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬᾺ"), [])]
      bstack11111lll11l_opy_ = sys.maxsize
      bstack11111lll111_opy_ = bstack11l111_opy_ (u"ࠪࠫΆ")
      for browser in bstack11111111ll1_opy_:
        if browser in self.bstack111111l1ll1_opy_:
          bstack11111l1ll11_opy_ = self.bstack111111l1ll1_opy_[browser]
        if bstack11111l1ll11_opy_ < bstack11111lll11l_opy_:
          bstack11111lll11l_opy_ = bstack11111l1ll11_opy_
          bstack11111lll111_opy_ = browser
      return bstack11111lll111_opy_
    except Exception as e:
      self.logger.error(bstack11l111_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡧ࡫ࡱࡨࠥࡨࡥࡴࡶࠣࡴࡱࡧࡴࡧࡱࡵࡱ࠱ࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡾࢁࠧᾼ").format(e))
  @classmethod
  def bstack1l1l1ll111_opy_(self):
    return os.getenv(bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡋࡒࡄ࡛ࠪ᾽"), bstack11l111_opy_ (u"࠭ࡆࡢ࡮ࡶࡩࠬι")).lower()
  @classmethod
  def bstack1llll1llll_opy_(self):
    return os.getenv(bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡆࡔࡆ࡝ࡤࡉࡁࡑࡖࡘࡖࡊࡥࡍࡐࡆࡈࠫ᾿"), bstack11l111_opy_ (u"ࠨࠩ῀"))
  @classmethod
  def bstack1l1l111l11l_opy_(cls, value):
    cls.bstack1l1ll11l1l_opy_ = value
  @classmethod
  def bstack111111lllll_opy_(cls):
    return cls.bstack1l1ll11l1l_opy_
  @classmethod
  def bstack1l1l111l111_opy_(cls, value):
    cls.percy_build_id = value
  @classmethod
  def bstack11111l1l1l1_opy_(cls):
    return cls.percy_build_id