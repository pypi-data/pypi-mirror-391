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
import sys
import logging
import tarfile
import io
import os
import time
import requests
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bstack_utils.constants import bstack11l1l1llll1_opy_, bstack11l1l1ll11l_opy_, bstack11l1l11l1l1_opy_
import tempfile
import json
bstack111l11ll11l_opy_ = os.getenv(bstack11l111_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡉࡢࡊࡎࡒࡅࠣḔ"), None) or os.path.join(tempfile.gettempdir(), bstack11l111_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡥࡧࡥࡹ࡬࠴࡬ࡰࡩࠥḕ"))
bstack111l11l1ll1_opy_ = os.path.join(bstack11l111_opy_ (u"ࠤ࡯ࡳ࡬ࠨḖ"), bstack11l111_opy_ (u"ࠪࡷࡩࡱ࠭ࡤ࡮࡬࠱ࡩ࡫ࡢࡶࡩ࠱ࡰࡴ࡭ࠧḗ"))
logging.Formatter.converter = time.gmtime
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack11l111_opy_ (u"ࠫࠪ࠮ࡡࡴࡥࡷ࡭ࡲ࡫ࠩࡴࠢ࡞ࠩ࠭ࡴࡡ࡮ࡧࠬࡷࡢࡡࠥࠩ࡮ࡨࡺࡪࡲ࡮ࡢ࡯ࡨ࠭ࡸࡣࠠ࠮ࠢࠨࠬࡲ࡫ࡳࡴࡣࡪࡩ࠮ࡹࠧḘ"),
      datefmt=bstack11l111_opy_ (u"࡙ࠬࠫ࠮ࠧࡰ࠱ࠪࡪࡔࠦࡊ࠽ࠩࡒࡀࠥࡔ࡜ࠪḙ"),
      stream=sys.stdout
    )
  return logger
def bstack1lll1lll111_opy_():
  bstack111l11l1l1l_opy_ = os.environ.get(bstack11l111_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡉࡏࡃࡕ࡝ࡤࡊࡅࡃࡗࡊࠦḚ"), bstack11l111_opy_ (u"ࠢࡧࡣ࡯ࡷࡪࠨḛ"))
  return logging.DEBUG if bstack111l11l1l1l_opy_.lower() == bstack11l111_opy_ (u"ࠣࡶࡵࡹࡪࠨḜ") else logging.INFO
def bstack1l1l1l1lll1_opy_():
  global bstack111l11ll11l_opy_
  if os.path.exists(bstack111l11ll11l_opy_):
    os.remove(bstack111l11ll11l_opy_)
  if os.path.exists(bstack111l11l1ll1_opy_):
    os.remove(bstack111l11l1ll1_opy_)
def bstack11ll1ll11l_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def configure_logger(config, log_level):
  bstack111l11l1111_opy_ = log_level
  if bstack11l111_opy_ (u"ࠩ࡯ࡳ࡬ࡒࡥࡷࡧ࡯ࠫḝ") in config and config[bstack11l111_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬḞ")] in bstack11l1l1ll11l_opy_:
    bstack111l11l1111_opy_ = bstack11l1l1ll11l_opy_[config[bstack11l111_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭ḟ")]]
  if config.get(bstack11l111_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡇࡵࡵࡱࡆࡥࡵࡺࡵࡳࡧࡏࡳ࡬ࡹࠧḠ"), False):
    logging.getLogger().setLevel(bstack111l11l1111_opy_)
    return bstack111l11l1111_opy_
  global bstack111l11ll11l_opy_
  bstack11ll1ll11l_opy_()
  bstack111l1l111ll_opy_ = logging.Formatter(
    fmt=bstack11l111_opy_ (u"࠭ࠥࠩࡣࡶࡧࡹ࡯࡭ࡦࠫࡶࠤࡠࠫࠨ࡯ࡣࡰࡩ࠮ࡹ࡝࡜ࠧࠫࡰࡪࡼࡥ࡭ࡰࡤࡱࡪ࠯ࡳ࡞ࠢ࠰ࠤࠪ࠮࡭ࡦࡵࡶࡥ࡬࡫ࠩࡴࠩḡ"),
    datefmt=bstack11l111_opy_ (u"࡛ࠧࠦ࠰ࠩࡲ࠳ࠥࡥࡖࠨࡌ࠿ࠫࡍ࠻ࠧࡖ࡞ࠬḢ"),
  )
  bstack111l111llll_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack111l11ll11l_opy_)
  file_handler.setFormatter(bstack111l1l111ll_opy_)
  bstack111l111llll_opy_.setFormatter(bstack111l1l111ll_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack111l111llll_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack11l111_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࠱ࡻࡪࡨࡤࡳ࡫ࡹࡩࡷ࠴ࡲࡦ࡯ࡲࡸࡪ࠴ࡲࡦ࡯ࡲࡸࡪࡥࡣࡰࡰࡱࡩࡨࡺࡩࡰࡰࠪḣ"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack111l111llll_opy_.setLevel(bstack111l11l1111_opy_)
  logging.getLogger().addHandler(bstack111l111llll_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack111l11l1111_opy_
def bstack111l11ll111_opy_(config):
  try:
    bstack111l11lllll_opy_ = set(bstack11l1l11l1l1_opy_)
    bstack111l11lll1l_opy_ = bstack11l111_opy_ (u"ࠩࠪḤ")
    with open(bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡼࡱࡱ࠭ḥ")) as bstack111l11ll1ll_opy_:
      bstack111l1l1111l_opy_ = bstack111l11ll1ll_opy_.read()
      bstack111l11lll1l_opy_ = re.sub(bstack11l111_opy_ (u"ࡶࠬࡤࠨ࡝ࡵ࠮࠭ࡄࠩ࠮ࠫࠦ࡟ࡲࠬḦ"), bstack11l111_opy_ (u"ࠬ࠭ḧ"), bstack111l1l1111l_opy_, flags=re.M)
      bstack111l11lll1l_opy_ = re.sub(
        bstack11l111_opy_ (u"ࡸࠧ࡟ࠪ࡟ࡷ࠰࠯࠿ࠩࠩḨ") + bstack11l111_opy_ (u"ࠧࡽࠩḩ").join(bstack111l11lllll_opy_) + bstack11l111_opy_ (u"ࠨࠫ࠱࠮ࠩ࠭Ḫ"),
        bstack11l111_opy_ (u"ࡴࠪࡠ࠷ࡀࠠ࡜ࡔࡈࡈࡆࡉࡔࡆࡆࡠࠫḫ"),
        bstack111l11lll1l_opy_, flags=re.M | re.I
      )
    def bstack111l11lll11_opy_(dic):
      bstack111l1l11ll1_opy_ = {}
      for key, value in dic.items():
        if key in bstack111l11lllll_opy_:
          bstack111l1l11ll1_opy_[key] = bstack11l111_opy_ (u"ࠪ࡟ࡗࡋࡄࡂࡅࡗࡉࡉࡣࠧḬ")
        else:
          if isinstance(value, dict):
            bstack111l1l11ll1_opy_[key] = bstack111l11lll11_opy_(value)
          else:
            bstack111l1l11ll1_opy_[key] = value
      return bstack111l1l11ll1_opy_
    bstack111l1l11ll1_opy_ = bstack111l11lll11_opy_(config)
    return {
      bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡽࡲࡲࠧḭ"): bstack111l11lll1l_opy_,
      bstack11l111_opy_ (u"ࠬ࡬ࡩ࡯ࡣ࡯ࡧࡴࡴࡦࡪࡩ࠱࡮ࡸࡵ࡮ࠨḮ"): json.dumps(bstack111l1l11ll1_opy_)
    }
  except Exception as e:
    return {}
def bstack111l1l11l11_opy_(inipath, rootpath):
  log_dir = os.path.join(os.getcwd(), bstack11l111_opy_ (u"࠭࡬ࡰࡩࠪḯ"))
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  bstack111l11l11l1_opy_ = os.path.join(log_dir, bstack11l111_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࡟ࡤࡱࡱࡪ࡮࡭ࡳࠨḰ"))
  if not os.path.exists(bstack111l11l11l1_opy_):
    bstack111l11l111l_opy_ = {
      bstack11l111_opy_ (u"ࠣ࡫ࡱ࡭ࡵࡧࡴࡩࠤḱ"): str(inipath),
      bstack11l111_opy_ (u"ࠤࡵࡳࡴࡺࡰࡢࡶ࡫ࠦḲ"): str(rootpath)
    }
    with open(os.path.join(log_dir, bstack11l111_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࡢࡧࡴࡴࡦࡪࡩࡶ࠲࡯ࡹ࡯࡯ࠩḳ")), bstack11l111_opy_ (u"ࠫࡼ࠭Ḵ")) as bstack111l1l11111_opy_:
      bstack111l1l11111_opy_.write(json.dumps(bstack111l11l111l_opy_))
def bstack111l11ll1l1_opy_():
  try:
    bstack111l11l11l1_opy_ = os.path.join(os.getcwd(), bstack11l111_opy_ (u"ࠬࡲ࡯ࡨࠩḵ"), bstack11l111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡣࡰࡰࡩ࡭࡬ࡹ࠮࡫ࡵࡲࡲࠬḶ"))
    if os.path.exists(bstack111l11l11l1_opy_):
      with open(bstack111l11l11l1_opy_, bstack11l111_opy_ (u"ࠧࡳࠩḷ")) as bstack111l1l11111_opy_:
        bstack111l1l11l1l_opy_ = json.load(bstack111l1l11111_opy_)
      return bstack111l1l11l1l_opy_.get(bstack11l111_opy_ (u"ࠨ࡫ࡱ࡭ࡵࡧࡴࡩࠩḸ"), bstack11l111_opy_ (u"ࠩࠪḹ")), bstack111l1l11l1l_opy_.get(bstack11l111_opy_ (u"ࠪࡶࡴࡵࡴࡱࡣࡷ࡬ࠬḺ"), bstack11l111_opy_ (u"ࠫࠬḻ"))
  except:
    pass
  return None, None
def bstack111l11l1l11_opy_():
  try:
    bstack111l11l11l1_opy_ = os.path.join(os.getcwd(), bstack11l111_opy_ (u"ࠬࡲ࡯ࡨࠩḼ"), bstack11l111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡣࡰࡰࡩ࡭࡬ࡹ࠮࡫ࡵࡲࡲࠬḽ"))
    if os.path.exists(bstack111l11l11l1_opy_):
      os.remove(bstack111l11l11l1_opy_)
  except:
    pass
def bstack1l111lll1_opy_(config):
  try:
    from bstack_utils.helper import bstack11l11ll1l_opy_, bstack111111ll_opy_
    from browserstack_sdk.sdk_cli.cli import cli
    global bstack111l11ll11l_opy_
    if config.get(bstack11l111_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡂࡷࡷࡳࡈࡧࡰࡵࡷࡵࡩࡑࡵࡧࡴࠩḾ"), False):
      return
    uuid = os.getenv(bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ḿ")) if os.getenv(bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧṀ")) else bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠥࡷࡩࡱࡒࡶࡰࡌࡨࠧṁ"))
    if not uuid or uuid == bstack11l111_opy_ (u"ࠫࡳࡻ࡬࡭ࠩṂ"):
      return
    bstack111l1l111l1_opy_ = [bstack11l111_opy_ (u"ࠬࡸࡥࡲࡷ࡬ࡶࡪࡳࡥ࡯ࡶࡶ࠲ࡹࡾࡴࠨṃ"), bstack11l111_opy_ (u"࠭ࡐࡪࡲࡩ࡭ࡱ࡫ࠧṄ"), bstack11l111_opy_ (u"ࠧࡱࡻࡳࡶࡴࡰࡥࡤࡶ࠱ࡸࡴࡳ࡬ࠨṅ"), bstack111l11ll11l_opy_, bstack111l11l1ll1_opy_]
    bstack111l11l1lll_opy_, root_path = bstack111l11ll1l1_opy_()
    if bstack111l11l1lll_opy_ != None:
      bstack111l1l111l1_opy_.append(bstack111l11l1lll_opy_)
    if root_path != None:
      bstack111l1l111l1_opy_.append(os.path.join(root_path, bstack11l111_opy_ (u"ࠨࡥࡲࡲ࡫ࡺࡥࡴࡶ࠱ࡴࡾ࠭Ṇ")))
    bstack11ll1ll11l_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack11l111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠯࡯ࡳ࡬ࡹ࠭ࠨṇ") + uuid + bstack11l111_opy_ (u"ࠪ࠲ࡹࡧࡲ࠯ࡩࡽࠫṈ"))
    with tarfile.open(output_file, bstack11l111_opy_ (u"ࠦࡼࡀࡧࡻࠤṉ")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack111l1l111l1_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack111l11ll111_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack111l11l11ll_opy_ = data.encode()
        tarinfo.size = len(bstack111l11l11ll_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack111l11l11ll_opy_))
    bstack11lll11l11_opy_ = MultipartEncoder(
      fields= {
        bstack11l111_opy_ (u"ࠬࡪࡡࡵࡣࠪṊ"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack11l111_opy_ (u"࠭ࡲࡣࠩṋ")), bstack11l111_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡾ࠭ࡨࡼ࡬ࡴࠬṌ")),
        bstack11l111_opy_ (u"ࠨࡥ࡯࡭ࡪࡴࡴࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪṍ"): uuid
      }
    )
    bstack111l11llll1_opy_ = bstack111111ll_opy_(cli.config, [bstack11l111_opy_ (u"ࠤࡤࡴ࡮ࡹࠢṎ"), bstack11l111_opy_ (u"ࠥࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠥṏ"), bstack11l111_opy_ (u"ࠦࡺࡶ࡬ࡰࡣࡧࠦṐ")], bstack11l1l1llll1_opy_)
    response = requests.post(
      bstack11l111_opy_ (u"ࠧࢁࡽ࠰ࡥ࡯࡭ࡪࡴࡴ࠮࡮ࡲ࡫ࡸ࠵ࡵࡱ࡮ࡲࡥࡩࠨṑ").format(bstack111l11llll1_opy_),
      data=bstack11lll11l11_opy_,
      headers={bstack11l111_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬṒ"): bstack11lll11l11_opy_.content_type},
      auth=(config[bstack11l111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩṓ")], config[bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫṔ")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack11l111_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡࡷࡳࡰࡴࡧࡤࠡ࡮ࡲ࡫ࡸࡀࠠࠨṕ") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack11l111_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡶࡩࡳࡪࡩ࡯ࡩࠣࡰࡴ࡭ࡳ࠻ࠩṖ") + str(e))
  finally:
    try:
      bstack1l1l1l1lll1_opy_()
      bstack111l11l1l11_opy_()
    except:
      pass