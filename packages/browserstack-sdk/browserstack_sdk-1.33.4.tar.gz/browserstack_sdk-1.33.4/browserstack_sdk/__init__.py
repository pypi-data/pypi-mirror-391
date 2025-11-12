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
import atexit
import shlex
import signal
import yaml
import socket
import datetime
import string
import random
import collections.abc
import traceback
import copy
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import json
from packaging import version
from browserstack.local import Local
from urllib.parse import urlparse
from dotenv import load_dotenv
from browserstack_sdk.bstack1ll111l1l1_opy_ import bstack1l1l1l11l_opy_
from browserstack_sdk.bstack1lll11ll_opy_ import *
import time
import requests
from bstack_utils.constants import EVENTS, STAGE, bstack1ll1l11111_opy_
from bstack_utils.messages import bstack11lll1l111_opy_, bstack1lll1llll1_opy_, bstack11lll11lll_opy_, bstack11llll1111_opy_, bstack1l1ll1111_opy_, bstack11ll1ll1l_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack11l111111l_opy_ import get_logger
from bstack_utils.helper import bstack11111llll_opy_
from browserstack_sdk.bstack1l111l11l1_opy_ import bstack1l11llll1l_opy_
logger = get_logger(__name__)
def bstack11l1ll111_opy_():
  global CONFIG
  headers = {
        bstack11l111_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩࡶ"): bstack11l111_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧࡷ"),
      }
  proxies = bstack11111llll_opy_(CONFIG, bstack1ll1l11111_opy_)
  try:
    response = requests.get(bstack1ll1l11111_opy_, headers=headers, proxies=proxies, timeout=5)
    if response.json():
      bstack1ll11lll1_opy_ = response.json()[bstack11l111_opy_ (u"ࠬ࡮ࡵࡣࡵࠪࡸ")]
      logger.debug(bstack11lll1l111_opy_.format(response.json()))
      return bstack1ll11lll1_opy_
    else:
      logger.debug(bstack1lll1llll1_opy_.format(bstack11l111_opy_ (u"ࠨࡒࡦࡵࡳࡳࡳࡹࡥࠡࡌࡖࡓࡓࠦࡰࡢࡴࡶࡩࠥ࡫ࡲࡳࡱࡵࠤࠧࡹ")))
  except Exception as e:
    logger.debug(bstack1lll1llll1_opy_.format(e))
def bstack11l11111l_opy_(hub_url):
  global CONFIG
  url = bstack11l111_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤࡺ")+  hub_url + bstack11l111_opy_ (u"ࠣ࠱ࡦ࡬ࡪࡩ࡫ࠣࡻ")
  headers = {
        bstack11l111_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨࡼ"): bstack11l111_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ࡽ"),
      }
  proxies = bstack11111llll_opy_(CONFIG, url)
  try:
    start_time = time.perf_counter()
    requests.get(url, headers=headers, proxies=proxies, timeout=5)
    latency = time.perf_counter() - start_time
    logger.debug(bstack11lll11lll_opy_.format(hub_url, latency))
    return dict(hub_url=hub_url, latency=latency)
  except Exception as e:
    logger.debug(bstack11llll1111_opy_.format(hub_url, e))
@measure(event_name=EVENTS.bstack11l1111111_opy_, stage=STAGE.bstack1l1l111l1_opy_)
def bstack1l1l11111l_opy_():
  try:
    global bstack1l1l11lll1_opy_
    global CONFIG
    if bstack11l111_opy_ (u"ࠫ࡭ࡻࡢࡓࡧࡪ࡭ࡴࡴࠧࡾ") in CONFIG and CONFIG[bstack11l111_opy_ (u"ࠬ࡮ࡵࡣࡔࡨ࡫࡮ࡵ࡮ࠨࡿ")]:
      from bstack_utils.constants import bstack1l1l111l11_opy_
      bstack1l1111l1_opy_ = CONFIG[bstack11l111_opy_ (u"࠭ࡨࡶࡤࡕࡩ࡬࡯࡯࡯ࠩࢀ")]
      if bstack1l1111l1_opy_ in bstack1l1l111l11_opy_:
        bstack1l1l11lll1_opy_ = bstack1l1l111l11_opy_[bstack1l1111l1_opy_]
        logger.debug(bstack1l1ll1111_opy_.format(bstack1l1l11lll1_opy_))
        return
      else:
        logger.debug(bstack11l111_opy_ (u"ࠢࡉࡷࡥࠤࡰ࡫ࡹࠡࠩࡾࢁࠬࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥࠢ࡬ࡲࠥࡎࡕࡃࡡࡘࡖࡑࡥࡍࡂࡒ࠯ࠤ࡫ࡧ࡬࡭࡫ࡱ࡫ࠥࡨࡡࡤ࡭ࠣࡸࡴࠦ࡯ࡱࡶ࡬ࡱࡦࡲࠠࡩࡷࡥࠤࡩ࡫ࡴࡦࡥࡷ࡭ࡴࡴࠢࢁ").format(bstack1l1111l1_opy_))
    bstack1ll11lll1_opy_ = bstack11l1ll111_opy_()
    bstack11lll111l_opy_ = []
    results = []
    for bstack1ll1ll1l1l_opy_ in bstack1ll11lll1_opy_:
      bstack11lll111l_opy_.append(bstack1l11llll1l_opy_(target=bstack11l11111l_opy_,args=(bstack1ll1ll1l1l_opy_,)))
    for t in bstack11lll111l_opy_:
      t.start()
    for t in bstack11lll111l_opy_:
      results.append(t.join())
    bstack11l1l1l1ll_opy_ = {}
    for item in results:
      hub_url = item[bstack11l111_opy_ (u"ࠨࡪࡸࡦࡤࡻࡲ࡭ࠩࢂ")]
      latency = item[bstack11l111_opy_ (u"ࠩ࡯ࡥࡹ࡫࡮ࡤࡻࠪࢃ")]
      bstack11l1l1l1ll_opy_[hub_url] = latency
    bstack1llll1lll_opy_ = min(bstack11l1l1l1ll_opy_, key= lambda x: bstack11l1l1l1ll_opy_[x])
    bstack1l1l11lll1_opy_ = bstack1llll1lll_opy_
    logger.debug(bstack1l1ll1111_opy_.format(bstack1llll1lll_opy_))
  except Exception as e:
    logger.debug(bstack11ll1ll1l_opy_.format(e))
from browserstack_sdk.bstack11l11llll1_opy_ import *
from browserstack_sdk.bstack1l111l11l1_opy_ import *
from browserstack_sdk.bstack11l1l11l1_opy_ import *
import logging
import requests
from bstack_utils.constants import *
from bstack_utils.bstack11l111111l_opy_ import get_logger
from bstack_utils.measure import measure
logger = get_logger(__name__)
@measure(event_name=EVENTS.bstack1ll1ll11ll_opy_, stage=STAGE.bstack1l1l111l1_opy_)
def bstack11l1lll1_opy_():
    global bstack1l1l11lll1_opy_
    try:
        bstack11l1l1ll_opy_ = bstack1llllll11_opy_()
        bstack1ll11l1l11_opy_(bstack11l1l1ll_opy_)
        hub_url = bstack11l1l1ll_opy_.get(bstack11l111_opy_ (u"ࠥࡹࡷࡲࠢࢄ"), bstack11l111_opy_ (u"ࠦࠧࢅ"))
        if hub_url.endswith(bstack11l111_opy_ (u"ࠬ࠵ࡷࡥ࠱࡫ࡹࡧ࠭ࢆ")):
            hub_url = hub_url.rsplit(bstack11l111_opy_ (u"࠭࠯ࡸࡦ࠲࡬ࡺࡨࠧࢇ"), 1)[0]
        if hub_url.startswith(bstack11l111_opy_ (u"ࠧࡩࡶࡷࡴ࠿࠵࠯ࠨ࢈")):
            hub_url = hub_url[7:]
        elif hub_url.startswith(bstack11l111_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࠪࢉ")):
            hub_url = hub_url[8:]
        bstack1l1l11lll1_opy_ = hub_url
    except Exception as e:
        raise RuntimeError(e)
def bstack1llllll11_opy_():
    global CONFIG
    bstack1l11ll1l1_opy_ = CONFIG.get(bstack11l111_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢊ"), {}).get(bstack11l111_opy_ (u"ࠪ࡫ࡷ࡯ࡤࡏࡣࡰࡩࠬࢋ"), bstack11l111_opy_ (u"ࠫࡓࡕ࡟ࡈࡔࡌࡈࡤࡔࡁࡎࡇࡢࡔࡆ࡙ࡓࡆࡆࠪࢌ"))
    if not isinstance(bstack1l11ll1l1_opy_, str):
        raise ValueError(bstack11l111_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡌࡸࡩࡥࠢࡱࡥࡲ࡫ࠠ࡮ࡷࡶࡸࠥࡨࡥࠡࡣࠣࡺࡦࡲࡩࡥࠢࡶࡸࡷ࡯࡮ࡨࠤࢍ"))
    try:
        bstack11l1l1ll_opy_ = bstack111l111ll_opy_(bstack1l11ll1l1_opy_)
        return bstack11l1l1ll_opy_
    except Exception as e:
        logger.error(bstack11l111_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡩࡵ࡭ࡩࠦࡤࡦࡶࡤ࡭ࡱࡹࠠ࠻ࠢࡾࢁࠧࢎ").format(str(e)))
        return {}
def bstack111l111ll_opy_(bstack1l11ll1l1_opy_):
    global CONFIG
    try:
        if not CONFIG[bstack11l111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ࢏")] or not CONFIG[bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ࢐")]:
            raise ValueError(bstack11l111_opy_ (u"ࠤࡐ࡭ࡸࡹࡩ࡯ࡩࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡸࡷࡪࡸ࡮ࡢ࡯ࡨࠤࡴࡸࠠࡢࡥࡦࡩࡸࡹࠠ࡬ࡧࡼࠦ࢑"))
        url = bstack11ll111l_opy_ + bstack1l11ll1l1_opy_
        auth = (CONFIG[bstack11l111_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ࢒")], CONFIG[bstack11l111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ࢓")])
        response = requests.get(url, auth=auth)
        if response.status_code == 200 and response.text:
            bstack11ll1lll1l_opy_ = json.loads(response.text)
            return bstack11ll1lll1l_opy_
    except ValueError as ve:
        logger.error(bstack11l111_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡦࡦࡶࡦ࡬࡮ࡴࡧࠡࡩࡵ࡭ࡩࠦࡤࡦࡶࡤ࡭ࡱࡹࠠ࠻ࠢࡾࢁࠧ࢔").format(str(ve)))
        raise ValueError(ve)
    except Exception as e:
        logger.error(bstack11l111_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡧࡧࡷࡧ࡭࡯࡮ࡨࠢࡪࡶ࡮ࡪࠠࡥࡧࡷࡥ࡮ࡲࡳࠡ࠼ࠣࡿࢂࠨ࢕").format(str(e)))
        raise RuntimeError(e)
    return {}
def bstack1ll11l1l11_opy_(bstack11ll1ll1ll_opy_):
    global CONFIG
    if bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ࢖") not in CONFIG or str(CONFIG[bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬࢗ")]).lower() == bstack11l111_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨ࢘"):
        CONFIG[bstack11l111_opy_ (u"ࠪࡰࡴࡩࡡ࡭࢙ࠩ")] = False
    elif bstack11l111_opy_ (u"ࠫ࡮ࡹࡔࡳ࡫ࡤࡰࡌࡸࡩࡥ࢚ࠩ") in bstack11ll1ll1ll_opy_:
        bstack1ll11lllll_opy_ = CONFIG.get(bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴ࢛ࠩ"), {})
        logger.debug(bstack11l111_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡸࡪࡵࡷ࡭ࡳ࡭ࠠ࡭ࡱࡦࡥࡱࠦ࡯ࡱࡶ࡬ࡳࡳࡹ࠺ࠡࠧࡶࠦ࢜"), bstack1ll11lllll_opy_)
        bstack11111lll_opy_ = bstack11ll1ll1ll_opy_.get(bstack11l111_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳࡒࡦࡲࡨࡥࡹ࡫ࡲࡴࠤ࢝"), [])
        bstack1l1l11ll11_opy_ = bstack11l111_opy_ (u"ࠣ࠮ࠥ࢞").join(bstack11111lll_opy_)
        logger.debug(bstack11l111_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡅࡸࡷࡹࡵ࡭ࠡࡴࡨࡴࡪࡧࡴࡦࡴࠣࡷࡹࡸࡩ࡯ࡩ࠽ࠤࠪࡹࠢ࢟"), bstack1l1l11ll11_opy_)
        bstack1111lll11_opy_ = {
            bstack11l111_opy_ (u"ࠥࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠧࢠ"): bstack11l111_opy_ (u"ࠦࡦࡺࡳ࠮ࡴࡨࡴࡪࡧࡴࡦࡴࠥࢡ"),
            bstack11l111_opy_ (u"ࠧ࡬࡯ࡳࡥࡨࡐࡴࡩࡡ࡭ࠤࢢ"): bstack11l111_opy_ (u"ࠨࡴࡳࡷࡨࠦࢣ"),
            bstack11l111_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳ࠭ࡳࡧࡳࡩࡦࡺࡥࡳࠤࢤ"): bstack1l1l11ll11_opy_
        }
        bstack1ll11lllll_opy_.update(bstack1111lll11_opy_)
        logger.debug(bstack11l111_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡖࡲࡧࡥࡹ࡫ࡤࠡ࡮ࡲࡧࡦࡲࠠࡰࡲࡷ࡭ࡴࡴࡳ࠻ࠢࠨࡷࠧࢥ"), bstack1ll11lllll_opy_)
        CONFIG[bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢦ")] = bstack1ll11lllll_opy_
        logger.debug(bstack11l111_opy_ (u"ࠥࡅ࡙࡙ࠠ࠻ࠢࡉ࡭ࡳࡧ࡬ࠡࡅࡒࡒࡋࡏࡇ࠻ࠢࠨࡷࠧࢧ"), CONFIG)
def bstack11l1l11ll1_opy_():
    bstack11l1l1ll_opy_ = bstack1llllll11_opy_()
    if not bstack11l1l1ll_opy_[bstack11l111_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࡖࡴ࡯ࠫࢨ")]:
      raise ValueError(bstack11l111_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࡗࡵࡰࠥ࡯ࡳࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࡩࡶࡴࡳࠠࡨࡴ࡬ࡨࠥࡪࡥࡵࡣ࡬ࡰࡸ࠴ࠢࢩ"))
    return bstack11l1l1ll_opy_[bstack11l111_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡘࡶࡱ࠭ࢪ")] + bstack11l111_opy_ (u"ࠧࡀࡥࡤࡴࡸࡃࠧࢫ")
@measure(event_name=EVENTS.bstack11l1l1llll_opy_, stage=STAGE.bstack1l1l111l1_opy_)
def bstack111111lll_opy_() -> list:
    global CONFIG
    result = []
    if CONFIG:
        auth = (CONFIG[bstack11l111_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪࢬ")], CONFIG[bstack11l111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬࢭ")])
        url = bstack11ll11llll_opy_
        logger.debug(bstack11l111_opy_ (u"ࠥࡅࡹࡺࡥ࡮ࡲࡷ࡭ࡳ࡭ࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴࠢࡩࡶࡴࡳࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡔࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠣࡅࡕࡏࠢࢮ"))
        try:
            response = requests.get(url, auth=auth, headers={bstack11l111_opy_ (u"ࠦࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠥࢯ"): bstack11l111_opy_ (u"ࠧࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠣࢰ")})
            if response.status_code == 200:
                bstack1ll11111_opy_ = json.loads(response.text)
                bstack11ll111111_opy_ = bstack1ll11111_opy_.get(bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡸ࠭ࢱ"), [])
                if bstack11ll111111_opy_:
                    bstack11lll11ll_opy_ = bstack11ll111111_opy_[0]
                    build_hashed_id = bstack11lll11ll_opy_.get(bstack11l111_opy_ (u"ࠧࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪࢲ"))
                    bstack1llll111l_opy_ = bstack11l1lll111_opy_ + build_hashed_id
                    result.extend([build_hashed_id, bstack1llll111l_opy_])
                    logger.info(bstack11lll1ll1l_opy_.format(bstack1llll111l_opy_))
                    bstack1111ll11l_opy_ = CONFIG[bstack11l111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫࢳ")]
                    if bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࢴ") in CONFIG:
                      bstack1111ll11l_opy_ += bstack11l111_opy_ (u"ࠪࠤࠬࢵ") + CONFIG[bstack11l111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ࢶ")]
                    if bstack1111ll11l_opy_ != bstack11lll11ll_opy_.get(bstack11l111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪࢷ")):
                      logger.debug(bstack1ll1llll11_opy_.format(bstack11lll11ll_opy_.get(bstack11l111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫࢸ")), bstack1111ll11l_opy_))
                    return result
                else:
                    logger.debug(bstack11l111_opy_ (u"ࠢࡂࡖࡖࠤ࠿ࠦࡎࡰࠢࡥࡹ࡮ࡲࡤࡴࠢࡩࡳࡺࡴࡤࠡ࡫ࡱࠤࡹ࡮ࡥࠡࡴࡨࡷࡵࡵ࡮ࡴࡧ࠱ࠦࢹ"))
            else:
                logger.debug(bstack11l111_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴ࠰ࠥࢺ"))
        except Exception as e:
            logger.error(bstack11l111_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡇࡵࡶࡴࡸࠠࡪࡰࠣ࡫ࡪࡺࡴࡪࡰࡪࠤࡧࡻࡩ࡭ࡦࡶࠤ࠿ࠦࡻࡾࠤࢻ").format(str(e)))
    else:
        logger.debug(bstack11l111_opy_ (u"ࠥࡅ࡙࡙ࠠ࠻ࠢࡆࡓࡓࡌࡉࡈࠢ࡬ࡷࠥࡴ࡯ࡵࠢࡶࡩࡹ࠴ࠠࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴ࠰ࠥࢼ"))
    return [None, None]
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack11111l1l1_opy_ import bstack11111l1l1_opy_, bstack1llllll11l_opy_, bstack11lll11ll1_opy_, bstack11ll11l11l_opy_
from bstack_utils.measure import bstack1llllll1l_opy_
from bstack_utils.measure import measure
from bstack_utils.percy import *
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.bstack1ll11llll_opy_ import bstack111l1l11_opy_
from bstack_utils.messages import *
from bstack_utils import bstack11l111111l_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack1l1ll1l1l1_opy_, bstack111lllll1l_opy_, bstack111111ll_opy_, bstack1l11lll1l1_opy_, \
  bstack11l11l1l1l_opy_, \
  Notset, bstack11l1lll1ll_opy_, \
  bstack1ll1lll11l_opy_, bstack11l11lll11_opy_, bstack11llll1l_opy_, bstack1l1lllllll_opy_, bstack1lll1ll111_opy_, bstack1l1lll1l1_opy_, \
  bstack11l1111lll_opy_, \
  bstack11llll111_opy_, bstack1ll1l1111_opy_, bstack1lll1ll1l_opy_, bstack1ll11l1l_opy_, \
  bstack1l1111ll_opy_, bstack11ll11ll1l_opy_, bstack111ll1lll_opy_, bstack1l11lll11l_opy_
from bstack_utils.bstack1ll1lllll1_opy_ import bstack1l1l1111l1_opy_
from bstack_utils.bstack11l111llll_opy_ import bstack11l1111l11_opy_, bstack1l1l1lll11_opy_
from bstack_utils.bstack1llll1ll1l_opy_ import bstack1l111111_opy_
from bstack_utils.bstack111l1lll_opy_ import bstack1ll11l1ll1_opy_, bstack11lll111_opy_
from bstack_utils.bstack1ll11l1lll_opy_ import bstack1ll11l1lll_opy_
from bstack_utils.bstack1ll1ll1111_opy_ import bstack111l1l1ll_opy_
from bstack_utils.proxy import bstack1lllll1ll_opy_, bstack11111llll_opy_, bstack1lll111lll_opy_, bstack11lll1ll_opy_
from bstack_utils.bstack1ll1l1ll1_opy_ import bstack1ll1l1l111_opy_
import bstack_utils.bstack1ll1ll1l_opy_ as bstack11ll11lll_opy_
import bstack_utils.bstack111ll11ll_opy_ as bstack11ll1lllll_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.utils.bstack1l111l11_opy_ import bstack1l111l111_opy_
from bstack_utils.bstack1llll11ll_opy_ import bstack1l1ll1ll1l_opy_
from bstack_utils.bstack1l11l1l1l1_opy_ import bstack11ll1llll_opy_
if os.getenv(bstack11l111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡑࡏ࡟ࡉࡑࡒࡏࡘ࠭ࢽ")):
  cli.bstack11l1ll11_opy_()
else:
  os.environ[bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡈࡒࡉࡠࡊࡒࡓࡐ࡙ࠧࢾ")] = bstack11l111_opy_ (u"࠭ࡴࡳࡷࡨࠫࢿ")
bstack1111l1111_opy_ = bstack11l111_opy_ (u"ࠧࠡࠢ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࡡࡴࠠࠡ࡫ࡩࠬࡵࡧࡧࡦࠢࡀࡁࡂࠦࡶࡰ࡫ࡧࠤ࠵࠯ࠠࡼ࡞ࡱࠤࠥࠦࡴࡳࡻࡾࡠࡳࠦࡣࡰࡰࡶࡸࠥ࡬ࡳࠡ࠿ࠣࡶࡪࡷࡵࡪࡴࡨࠬࡡ࠭ࡦࡴ࡞ࠪ࠭ࡀࡢ࡮ࠡࠢࠣࠤࠥ࡬ࡳ࠯ࡣࡳࡴࡪࡴࡤࡇ࡫࡯ࡩࡘࡿ࡮ࡤࠪࡥࡷࡹࡧࡣ࡬ࡡࡳࡥࡹ࡮ࠬࠡࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡳࡣ࡮ࡴࡤࡦࡺࠬࠤ࠰ࠦࠢ࠻ࠤࠣ࠯ࠥࡐࡓࡐࡐ࠱ࡷࡹࡸࡩ࡯ࡩ࡬ࡪࡾ࠮ࡊࡔࡑࡑ࠲ࡵࡧࡲࡴࡧࠫࠬࡦࡽࡡࡪࡶࠣࡲࡪࡽࡐࡢࡩࡨ࠶࠳࡫ࡶࡢ࡮ࡸࡥࡹ࡫ࠨࠣࠪࠬࠤࡂࡄࠠࡼࡿࠥ࠰ࠥࡢࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡨࡧࡷࡗࡪࡹࡳࡪࡱࡱࡈࡪࡺࡡࡪ࡮ࡶࠦࢂࡢࠧࠪࠫࠬ࡟ࠧ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠣ࡟ࠬࠤ࠰ࠦࠢ࠭࡞࡟ࡲࠧ࠯࡜࡯ࠢࠣࠤࠥࢃࡣࡢࡶࡦ࡬࠭࡫ࡸࠪࡽ࡟ࡲࠥࠦࠠࠡࡿ࡟ࡲࠥࠦࡽ࡝ࡰࠣࠤ࠴࠰ࠠ࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࠤ࠯࠵ࠧࣀ")
bstack111lll111_opy_ = bstack11l111_opy_ (u"ࠨ࡞ࡱ࠳࠯ࠦ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࠣ࠮࠴ࡢ࡮ࡤࡱࡱࡷࡹࠦࡢࡴࡶࡤࡧࡰࡥࡰࡢࡶ࡫ࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺࡠࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠳࡞࡞ࡱࡧࡴࡴࡳࡵࠢࡥࡷࡹࡧࡣ࡬ࡡࡦࡥࡵࡹࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࡜ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮࡭ࡧࡱ࡫ࡹ࡮ࠠ࠮ࠢ࠴ࡡࡡࡴࡣࡰࡰࡶࡸࠥࡶ࡟ࡪࡰࡧࡩࡽࠦ࠽ࠡࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࡛ࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠴ࡠࡠࡳࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡹ࡬ࡪࡥࡨࠬ࠵࠲ࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠵ࠬࡠࡳࡩ࡯࡯ࡵࡷࠤ࡮ࡳࡰࡰࡴࡷࡣࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴ࠵ࡡࡥࡷࡹࡧࡣ࡬ࠢࡀࠤࡷ࡫ࡱࡶ࡫ࡵࡩ࠭ࠨࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥ࠭ࡀࡢ࡮ࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮࡭ࡣࡸࡲࡨ࡮ࠠ࠾ࠢࡤࡷࡾࡴࡣࠡࠪ࡯ࡥࡺࡴࡣࡩࡑࡳࡸ࡮ࡵ࡮ࡴࠫࠣࡁࡃࠦࡻ࡝ࡰ࡯ࡩࡹࠦࡣࡢࡲࡶ࠿ࡡࡴࡴࡳࡻࠣࡿࡡࡴࡣࡢࡲࡶࠤࡂࠦࡊࡔࡑࡑ࠲ࡵࡧࡲࡴࡧࠫࡦࡸࡺࡡࡤ࡭ࡢࡧࡦࡶࡳࠪ࡞ࡱࠤࠥࢃࠠࡤࡣࡷࡧ࡭࠮ࡥࡹࠫࠣࡿࡡࡴࠠࠡࠢࠣࢁࡡࡴࠠࠡࡴࡨࡸࡺࡸ࡮ࠡࡣࡺࡥ࡮ࡺࠠࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮ࡤࡱࡱࡲࡪࡩࡴࠩࡽ࡟ࡲࠥࠦࠠࠡࡹࡶࡉࡳࡪࡰࡰ࡫ࡱࡸ࠿ࠦࡠࡸࡵࡶ࠾࠴࠵ࡣࡥࡲ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡂࡧࡦࡶࡳ࠾ࠦࡾࡩࡳࡩ࡯ࡥࡧࡘࡖࡎࡉ࡯࡮ࡲࡲࡲࡪࡴࡴࠩࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡦࡥࡵࡹࠩࠪࡿࡣ࠰ࡡࡴࠠࠡࠢࠣ࠲࠳࠴࡬ࡢࡷࡱࡧ࡭ࡕࡰࡵ࡫ࡲࡲࡸࡢ࡮ࠡࠢࢀ࠭ࡡࡴࡽ࡝ࡰ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࡡࡴࠧࣁ")
from ._version import __version__
bstack11l111ll_opy_ = None
CONFIG = {}
bstack1l11lll11_opy_ = {}
bstack11l111l11l_opy_ = {}
bstack1l1l11ll_opy_ = None
bstack1l1111ll11_opy_ = None
bstack1ll1l111l1_opy_ = None
bstack1l11l111l1_opy_ = -1
bstack1l1ll1lll_opy_ = 0
bstack1l1ll1l111_opy_ = bstack11ll11l1ll_opy_
bstack1l111l1ll1_opy_ = 1
bstack1ll1ll1ll_opy_ = False
bstack1lll111l1l_opy_ = False
bstack1ll1111l_opy_ = bstack11l111_opy_ (u"ࠩࠪࣂ")
bstack111lllllll_opy_ = bstack11l111_opy_ (u"ࠪࠫࣃ")
bstack1l1l1l11_opy_ = False
bstack111111l11_opy_ = True
bstack11l1l1l111_opy_ = bstack11l111_opy_ (u"ࠫࠬࣄ")
bstack1l1ll111l1_opy_ = []
bstack11l11l11l_opy_ = threading.Lock()
bstack1l11ll11ll_opy_ = threading.Lock()
bstack1l1l11lll1_opy_ = bstack11l111_opy_ (u"ࠬ࠭ࣅ")
bstack1l11lll1ll_opy_ = False
bstack1lll1l1111_opy_ = None
bstack11llllll_opy_ = None
bstack11l1l11ll_opy_ = None
bstack1l111l1l1l_opy_ = -1
bstack1111llll_opy_ = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"࠭ࡾࠨࣆ")), bstack11l111_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧࣇ"), bstack11l111_opy_ (u"ࠨ࠰ࡵࡳࡧࡵࡴ࠮ࡴࡨࡴࡴࡸࡴ࠮ࡪࡨࡰࡵ࡫ࡲ࠯࡬ࡶࡳࡳ࠭ࣈ"))
bstack11lll1111l_opy_ = 0
bstack11l1ll111l_opy_ = 0
bstack1l1111l1l1_opy_ = []
bstack1l1ll1ll_opy_ = []
bstack1ll1l1ll_opy_ = []
bstack1l11llll1_opy_ = []
bstack1l1ll11ll_opy_ = bstack11l111_opy_ (u"ࠩࠪࣉ")
bstack11ll1l11ll_opy_ = bstack11l111_opy_ (u"ࠪࠫ࣊")
bstack1l11l111l_opy_ = False
bstack1l11ll1lll_opy_ = False
bstack11l11l111_opy_ = {}
bstack1l1l1l1l_opy_ = None
bstack11lll1l1_opy_ = None
bstack111l1ll1l_opy_ = None
bstack1ll11lll_opy_ = None
bstack1l11lll111_opy_ = None
bstack11ll11ll11_opy_ = None
bstack1l11ll1111_opy_ = None
bstack11lll1l1ll_opy_ = None
bstack1ll11ll1l1_opy_ = None
bstack1lll1lll1l_opy_ = None
bstack1l11111l_opy_ = None
bstack1ll1lll11_opy_ = None
bstack11ll111lll_opy_ = None
bstack1l1111llll_opy_ = None
bstack1111l111_opy_ = None
bstack1lll111ll_opy_ = None
bstack1lll11l1ll_opy_ = None
bstack1l1lll1l1l_opy_ = None
bstack11ll11l11_opy_ = None
bstack1l11ll1ll1_opy_ = None
bstack1111ll1l1_opy_ = None
bstack111llll11_opy_ = None
bstack1ll1ll1lll_opy_ = None
thread_local = threading.local()
bstack1l11llllll_opy_ = False
bstack1l1l111ll_opy_ = bstack11l111_opy_ (u"ࠦࠧ࣋")
logger = bstack11l111111l_opy_.get_logger(__name__, bstack1l1ll1l111_opy_)
bstack11l11ll1l_opy_ = Config.bstack111llll1_opy_()
percy = bstack1ll1l111ll_opy_()
bstack111111111_opy_ = bstack111l1l11_opy_()
bstack1ll1l111l_opy_ = bstack11l1l11l1_opy_()
def bstack1lll11l1_opy_():
  global CONFIG
  global bstack1l11l111l_opy_
  global bstack11l11ll1l_opy_
  testContextOptions = bstack1111l1l1l_opy_(CONFIG)
  if bstack11l11l1l1l_opy_(CONFIG):
    if (bstack11l111_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ࣌") in testContextOptions and str(testContextOptions[bstack11l111_opy_ (u"࠭ࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ࣍")]).lower() == bstack11l111_opy_ (u"ࠧࡵࡴࡸࡩࠬ࣎")):
      bstack1l11l111l_opy_ = True
    bstack11l11ll1l_opy_.bstack1lllll11l1_opy_(testContextOptions.get(bstack11l111_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷ࣏ࠬ"), False))
  else:
    bstack1l11l111l_opy_ = True
    bstack11l11ll1l_opy_.bstack1lllll11l1_opy_(True)
def bstack1ll1111ll_opy_():
  from appium.version import version as appium_version
  return version.parse(appium_version)
def bstack1lllll1l1_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack111lll1l1l_opy_():
  args = sys.argv
  for i in range(len(args)):
    if bstack11l111_opy_ (u"ࠤ࠰࠱ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡦࡳࡳ࡬ࡩࡨࡨ࡬ࡰࡪࠨ࣐") == args[i].lower() or bstack11l111_opy_ (u"ࠥ࠱࠲ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡮ࡧ࡫ࡪ࣑ࠦ") == args[i].lower():
      path = args[i + 1]
      sys.argv.remove(args[i])
      sys.argv.remove(path)
      global bstack11l1l1l111_opy_
      bstack11l1l1l111_opy_ += bstack11l111_opy_ (u"ࠫ࠲࠳ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡈࡵ࡮ࡧ࡫ࡪࡊ࡮ࡲࡥ࣒ࠡࠩ") + shlex.quote(path)
      return path
  return None
bstack1l1l11lll_opy_ = re.compile(bstack11l111_opy_ (u"ࡷࠨ࠮ࠫࡁ࡟ࠨࢀ࠮࠮ࠫࡁࠬࢁ࠳࠰࠿࣓ࠣ"))
def bstack1l111lll1l_opy_(loader, node):
  value = loader.construct_scalar(node)
  for group in bstack1l1l11lll_opy_.findall(value):
    if group is not None and os.environ.get(group) is not None:
      value = value.replace(bstack11l111_opy_ (u"ࠨࠤࡼࠤࣔ") + group + bstack11l111_opy_ (u"ࠢࡾࠤࣕ"), os.environ.get(group))
  return value
def bstack1llll11l11_opy_():
  global bstack1ll1ll1lll_opy_
  if bstack1ll1ll1lll_opy_ is None:
        bstack1ll1ll1lll_opy_ = bstack111lll1l1l_opy_()
  bstack1ll1l111_opy_ = bstack1ll1ll1lll_opy_
  if bstack1ll1l111_opy_ and os.path.exists(os.path.abspath(bstack1ll1l111_opy_)):
    fileName = bstack1ll1l111_opy_
  if bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍ࡟ࡇࡋࡏࡉࠬࣖ") in os.environ and os.path.exists(
          os.path.abspath(os.environ[bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡅࡒࡒࡋࡏࡇࡠࡈࡌࡐࡊ࠭ࣗ")])) and not bstack11l111_opy_ (u"ࠪࡪ࡮ࡲࡥࡏࡣࡰࡩࠬࣘ") in locals():
    fileName = os.environ[bstack11l111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࡢࡊࡎࡒࡅࠨࣙ")]
  if bstack11l111_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡑࡥࡲ࡫ࠧࣚ") in locals():
    bstack111111l_opy_ = os.path.abspath(fileName)
  else:
    bstack111111l_opy_ = bstack11l111_opy_ (u"࠭ࠧࣛ")
  bstack1l111ll1l1_opy_ = os.getcwd()
  bstack1llllllll_opy_ = bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹ࡮࡮ࠪࣜ")
  bstack111llll111_opy_ = bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡺࡣࡰࡰࠬࣝ")
  while (not os.path.exists(bstack111111l_opy_)) and bstack1l111ll1l1_opy_ != bstack11l111_opy_ (u"ࠤࠥࣞ"):
    bstack111111l_opy_ = os.path.join(bstack1l111ll1l1_opy_, bstack1llllllll_opy_)
    if not os.path.exists(bstack111111l_opy_):
      bstack111111l_opy_ = os.path.join(bstack1l111ll1l1_opy_, bstack111llll111_opy_)
    if bstack1l111ll1l1_opy_ != os.path.dirname(bstack1l111ll1l1_opy_):
      bstack1l111ll1l1_opy_ = os.path.dirname(bstack1l111ll1l1_opy_)
    else:
      bstack1l111ll1l1_opy_ = bstack11l111_opy_ (u"ࠥࠦࣟ")
  bstack1ll1ll1lll_opy_ = bstack111111l_opy_ if os.path.exists(bstack111111l_opy_) else None
  return bstack1ll1ll1lll_opy_
def bstack1ll11lll11_opy_(config):
    if bstack11l111_opy_ (u"ࠫࡹ࡫ࡳࡵࡔࡨࡴࡴࡸࡴࡪࡰࡪࠫ࣠") in config:
      config[bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶࡒࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ࣡")] = config[bstack11l111_opy_ (u"࠭ࡴࡦࡵࡷࡖࡪࡶ࡯ࡳࡶ࡬ࡲ࡬࠭࣢")]
    if bstack11l111_opy_ (u"ࠧࡵࡧࡶࡸࡗ࡫ࡰࡰࡴࡷ࡭ࡳ࡭ࡏࡱࡶ࡬ࡳࡳࡹࣣࠧ") in config:
      config[bstack11l111_opy_ (u"ࠨࡶࡨࡷࡹࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬࣤ")] = config[bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺࡒࡦࡲࡲࡶࡹ࡯࡮ࡨࡑࡳࡸ࡮ࡵ࡮ࡴࠩࣥ")]
def bstack1l1111lll1_opy_():
  bstack111111l_opy_ = bstack1llll11l11_opy_()
  if not os.path.exists(bstack111111l_opy_):
    bstack1l1l1lll_opy_(
      bstack1l1l11llll_opy_.format(os.getcwd()))
  try:
    with open(bstack111111l_opy_, bstack11l111_opy_ (u"ࠪࡶࣦࠬ")) as stream:
      yaml.add_implicit_resolver(bstack11l111_opy_ (u"ࠦࠦࡶࡡࡵࡪࡨࡼࠧࣧ"), bstack1l1l11lll_opy_)
      yaml.add_constructor(bstack11l111_opy_ (u"ࠧࠧࡰࡢࡶ࡫ࡩࡽࠨࣨ"), bstack1l111lll1l_opy_)
      config = yaml.load(stream, yaml.FullLoader)
      bstack1ll11lll11_opy_(config)
      return config
  except:
    with open(bstack111111l_opy_, bstack11l111_opy_ (u"࠭ࡲࠨࣩ")) as stream:
      try:
        config = yaml.safe_load(stream)
        bstack1ll11lll11_opy_(config)
        return config
      except yaml.YAMLError as exc:
        bstack1l1l1lll_opy_(bstack1111ll11_opy_.format(str(exc)))
def bstack111ll1ll1_opy_(config):
  bstack111lll11_opy_ = bstack11l1ll1l1l_opy_(config)
  for option in list(bstack111lll11_opy_):
    if option.lower() in bstack1ll1lll1ll_opy_ and option != bstack1ll1lll1ll_opy_[option.lower()]:
      bstack111lll11_opy_[bstack1ll1lll1ll_opy_[option.lower()]] = bstack111lll11_opy_[option]
      del bstack111lll11_opy_[option]
  return config
def bstack1l1llllll_opy_():
  global bstack11l111l11l_opy_
  for key, bstack11lll11l1_opy_ in bstack1ll1ll1ll1_opy_.items():
    if isinstance(bstack11lll11l1_opy_, list):
      for var in bstack11lll11l1_opy_:
        if var in os.environ and os.environ[var] and str(os.environ[var]).strip():
          bstack11l111l11l_opy_[key] = os.environ[var]
          break
    elif bstack11lll11l1_opy_ in os.environ and os.environ[bstack11lll11l1_opy_] and str(os.environ[bstack11lll11l1_opy_]).strip():
      bstack11l111l11l_opy_[key] = os.environ[bstack11lll11l1_opy_]
  if bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩ࣪") in os.environ:
    bstack11l111l11l_opy_[bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ࣫")] = {}
    bstack11l111l11l_opy_[bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭࣬")][bstack11l111_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶ࣭ࠬ")] = os.environ[bstack11l111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࣮࠭")]
def bstack11lll1l1l1_opy_():
  global bstack1l11lll11_opy_
  global bstack11l1l1l111_opy_
  bstack1l1lll111_opy_ = []
  for idx, val in enumerate(sys.argv):
    if idx < len(sys.argv) - 1 and bstack11l111_opy_ (u"ࠬ࠳࠭ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ࣯").lower() == val.lower():
      bstack1l11lll11_opy_[bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࣰࠪ")] = {}
      bstack1l11lll11_opy_[bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࣱࠫ")][bstack11l111_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࣲࠪ")] = sys.argv[idx + 1]
      bstack1l1lll111_opy_.extend([idx, idx + 1])
      break
  for key, bstack111lll1l_opy_ in bstack1ll11ll1l_opy_.items():
    if isinstance(bstack111lll1l_opy_, list):
      for idx, val in enumerate(sys.argv):
        if idx >= len(sys.argv) - 1:
          continue
        for var in bstack111lll1l_opy_:
          if bstack11l111_opy_ (u"ࠩ࠰࠱ࠬࣳ") + var.lower() == val.lower() and key not in bstack1l11lll11_opy_:
            bstack1l11lll11_opy_[key] = sys.argv[idx + 1]
            bstack11l1l1l111_opy_ += bstack11l111_opy_ (u"ࠪࠤ࠲࠳ࠧࣴ") + var + bstack11l111_opy_ (u"ࠫࠥ࠭ࣵ") + shlex.quote(sys.argv[idx + 1])
            bstack1l1lll111_opy_.extend([idx, idx + 1])
            break
    else:
      for idx, val in enumerate(sys.argv):
        if idx >= len(sys.argv) - 1:
          continue
        if bstack11l111_opy_ (u"ࠬ࠳࠭ࠨࣶ") + bstack111lll1l_opy_.lower() == val.lower() and key not in bstack1l11lll11_opy_:
          bstack1l11lll11_opy_[key] = sys.argv[idx + 1]
          bstack11l1l1l111_opy_ += bstack11l111_opy_ (u"࠭ࠠ࠮࠯ࠪࣷ") + bstack111lll1l_opy_ + bstack11l111_opy_ (u"ࠧࠡࠩࣸ") + shlex.quote(sys.argv[idx + 1])
          bstack1l1lll111_opy_.extend([idx, idx + 1])
  for idx in sorted(set(bstack1l1lll111_opy_), reverse=True):
    if idx < len(sys.argv):
      del sys.argv[idx]
def bstack1l1lllll11_opy_(config):
  bstack1ll11l11l1_opy_ = config.keys()
  for bstack11l1lll1l1_opy_, bstack1l1llllll1_opy_ in bstack1l111111ll_opy_.items():
    if bstack1l1llllll1_opy_ in bstack1ll11l11l1_opy_:
      config[bstack11l1lll1l1_opy_] = config[bstack1l1llllll1_opy_]
      del config[bstack1l1llllll1_opy_]
  for bstack11l1lll1l1_opy_, bstack1l1llllll1_opy_ in bstack11ll1l1l_opy_.items():
    if isinstance(bstack1l1llllll1_opy_, list):
      for bstack1l1l1l1111_opy_ in bstack1l1llllll1_opy_:
        if bstack1l1l1l1111_opy_ in bstack1ll11l11l1_opy_:
          config[bstack11l1lll1l1_opy_] = config[bstack1l1l1l1111_opy_]
          del config[bstack1l1l1l1111_opy_]
          break
    elif bstack1l1llllll1_opy_ in bstack1ll11l11l1_opy_:
      config[bstack11l1lll1l1_opy_] = config[bstack1l1llllll1_opy_]
      del config[bstack1l1llllll1_opy_]
  for bstack1l1l1l1111_opy_ in list(config):
    for bstack1ll111lll_opy_ in bstack1111l1lll_opy_:
      if bstack1l1l1l1111_opy_.lower() == bstack1ll111lll_opy_.lower() and bstack1l1l1l1111_opy_ != bstack1ll111lll_opy_:
        config[bstack1ll111lll_opy_] = config[bstack1l1l1l1111_opy_]
        del config[bstack1l1l1l1111_opy_]
  bstack1l1l111111_opy_ = [{}]
  if not config.get(bstack11l111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࣹࠫ")):
    config[bstack11l111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࣺࠬ")] = [{}]
  bstack1l1l111111_opy_ = config[bstack11l111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ࣻ")]
  for platform in bstack1l1l111111_opy_:
    for bstack1l1l1l1111_opy_ in list(platform):
      for bstack1ll111lll_opy_ in bstack1111l1lll_opy_:
        if bstack1l1l1l1111_opy_.lower() == bstack1ll111lll_opy_.lower() and bstack1l1l1l1111_opy_ != bstack1ll111lll_opy_:
          platform[bstack1ll111lll_opy_] = platform[bstack1l1l1l1111_opy_]
          del platform[bstack1l1l1l1111_opy_]
  for bstack11l1lll1l1_opy_, bstack1l1llllll1_opy_ in bstack11ll1l1l_opy_.items():
    for platform in bstack1l1l111111_opy_:
      if isinstance(bstack1l1llllll1_opy_, list):
        for bstack1l1l1l1111_opy_ in bstack1l1llllll1_opy_:
          if bstack1l1l1l1111_opy_ in platform:
            platform[bstack11l1lll1l1_opy_] = platform[bstack1l1l1l1111_opy_]
            del platform[bstack1l1l1l1111_opy_]
            break
      elif bstack1l1llllll1_opy_ in platform:
        platform[bstack11l1lll1l1_opy_] = platform[bstack1l1llllll1_opy_]
        del platform[bstack1l1llllll1_opy_]
  for bstack11llllll1_opy_ in bstack111ll111_opy_:
    if bstack11llllll1_opy_ in config:
      if not bstack111ll111_opy_[bstack11llllll1_opy_] in config:
        config[bstack111ll111_opy_[bstack11llllll1_opy_]] = {}
      config[bstack111ll111_opy_[bstack11llllll1_opy_]].update(config[bstack11llllll1_opy_])
      del config[bstack11llllll1_opy_]
  for platform in bstack1l1l111111_opy_:
    for bstack11llllll1_opy_ in bstack111ll111_opy_:
      if bstack11llllll1_opy_ in list(platform):
        if not bstack111ll111_opy_[bstack11llllll1_opy_] in platform:
          platform[bstack111ll111_opy_[bstack11llllll1_opy_]] = {}
        platform[bstack111ll111_opy_[bstack11llllll1_opy_]].update(platform[bstack11llllll1_opy_])
        del platform[bstack11llllll1_opy_]
  config = bstack111ll1ll1_opy_(config)
  return config
def bstack11l111ll1l_opy_(config):
  global bstack111lllllll_opy_
  bstack111lllll_opy_ = False
  if bstack11l111_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨࣼ") in config and str(config[bstack11l111_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩࣽ")]).lower() != bstack11l111_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬࣾ"):
    if bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫࣿ") not in config or str(config[bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬऀ")]).lower() == bstack11l111_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨँ"):
      config[bstack11l111_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࠩं")] = False
    else:
      bstack11l1l1ll_opy_ = bstack1llllll11_opy_()
      if bstack11l111_opy_ (u"ࠫ࡮ࡹࡔࡳ࡫ࡤࡰࡌࡸࡩࡥࠩः") in bstack11l1l1ll_opy_:
        if not bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩऄ") in config:
          config[bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪअ")] = {}
        config[bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫआ")][bstack11l111_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪइ")] = bstack11l111_opy_ (u"ࠩࡤࡸࡸ࠳ࡲࡦࡲࡨࡥࡹ࡫ࡲࠨई")
        bstack111lllll_opy_ = True
        bstack111lllllll_opy_ = config[bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧउ")].get(bstack11l111_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ऊ"))
  if bstack11l11l1l1l_opy_(config) and bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩऋ") in config and str(config[bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪऌ")]).lower() != bstack11l111_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭ऍ") and not bstack111lllll_opy_:
    if not bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬऎ") in config:
      config[bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ए")] = {}
    if not config[bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧऐ")].get(bstack11l111_opy_ (u"ࠫࡸࡱࡩࡱࡄ࡬ࡲࡦࡸࡹࡊࡰ࡬ࡸ࡮ࡧ࡬ࡪࡵࡤࡸ࡮ࡵ࡮ࠨऑ")) and not bstack11l111_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧऒ") in config[bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪओ")]:
      bstack1l11ll11l_opy_ = datetime.datetime.now()
      bstack1ll1l1l1l_opy_ = bstack1l11ll11l_opy_.strftime(bstack11l111_opy_ (u"ࠧࠦࡦࡢࠩࡧࡥࠥࡉࠧࡐࠫऔ"))
      hostname = socket.gethostname()
      bstack111ll1l11_opy_ = bstack11l111_opy_ (u"ࠨࠩक").join(random.choices(string.ascii_lowercase + string.digits, k=4))
      identifier = bstack11l111_opy_ (u"ࠩࡾࢁࡤࢁࡽࡠࡽࢀࠫख").format(bstack1ll1l1l1l_opy_, hostname, bstack111ll1l11_opy_)
      config[bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧग")][bstack11l111_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭घ")] = identifier
    bstack111lllllll_opy_ = config[bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩङ")].get(bstack11l111_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨच"))
  return config
def bstack1lll1lll1_opy_():
  bstack1l1111111_opy_ =  bstack1l1lllllll_opy_()[bstack11l111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷ࠭छ")]
  return bstack1l1111111_opy_ if bstack1l1111111_opy_ else -1
def bstack1ll11ll1_opy_(bstack1l1111111_opy_):
  global CONFIG
  if not bstack11l111_opy_ (u"ࠨࠦࡾࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࡿࠪज") in CONFIG[bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫझ")]:
    return
  CONFIG[bstack11l111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬञ")] = CONFIG[bstack11l111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ट")].replace(
    bstack11l111_opy_ (u"ࠬࠪࡻࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࢃࠧठ"),
    str(bstack1l1111111_opy_)
  )
def bstack1ll1llllll_opy_():
  global CONFIG
  if not bstack11l111_opy_ (u"࠭ࠤࡼࡆࡄࡘࡊࡥࡔࡊࡏࡈࢁࠬड") in CONFIG[bstack11l111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩढ")]:
    return
  bstack1l11ll11l_opy_ = datetime.datetime.now()
  bstack1ll1l1l1l_opy_ = bstack1l11ll11l_opy_.strftime(bstack11l111_opy_ (u"ࠨࠧࡧ࠱ࠪࡨ࠭ࠦࡊ࠽ࠩࡒ࠭ण"))
  CONFIG[bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫत")] = CONFIG[bstack11l111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬथ")].replace(
    bstack11l111_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪद"),
    bstack1ll1l1l1l_opy_
  )
def bstack1l11l11l1_opy_():
  global CONFIG
  if bstack11l111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧध") in CONFIG and not bool(CONFIG[bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨन")]):
    del CONFIG[bstack11l111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩऩ")]
    return
  if not bstack11l111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪप") in CONFIG:
    CONFIG[bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫफ")] = bstack11l111_opy_ (u"ࠪࠧࠩࢁࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࢂ࠭ब")
  if bstack11l111_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪभ") in CONFIG[bstack11l111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧम")]:
    bstack1ll1llllll_opy_()
    os.environ[bstack11l111_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡥࡃࡐࡏࡅࡍࡓࡋࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠪय")] = CONFIG[bstack11l111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩर")]
  if not bstack11l111_opy_ (u"ࠨࠦࡾࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࡿࠪऱ") in CONFIG[bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫल")]:
    return
  bstack1l1111111_opy_ = bstack11l111_opy_ (u"ࠪࠫळ")
  bstack111l11l11_opy_ = bstack1lll1lll1_opy_()
  if bstack111l11l11_opy_ != -1:
    bstack1l1111111_opy_ = bstack11l111_opy_ (u"ࠫࡈࡏࠠࠨऴ") + str(bstack111l11l11_opy_)
  if bstack1l1111111_opy_ == bstack11l111_opy_ (u"ࠬ࠭व"):
    bstack1111llll1_opy_ = bstack1111l1ll_opy_(CONFIG[bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩश")])
    if bstack1111llll1_opy_ != -1:
      bstack1l1111111_opy_ = str(bstack1111llll1_opy_)
  if bstack1l1111111_opy_:
    bstack1ll11ll1_opy_(bstack1l1111111_opy_)
    os.environ[bstack11l111_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑ࡟ࡄࡑࡐࡆࡎࡔࡅࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠫष")] = CONFIG[bstack11l111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪस")]
def bstack1l1ll1l1l_opy_(bstack11l1ll1111_opy_, bstack1l1l1111_opy_, path):
  bstack11llllllll_opy_ = {
    bstack11l111_opy_ (u"ࠩ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ह"): bstack1l1l1111_opy_
  }
  if os.path.exists(path):
    bstack111l1l1l1_opy_ = json.load(open(path, bstack11l111_opy_ (u"ࠪࡶࡧ࠭ऺ")))
  else:
    bstack111l1l1l1_opy_ = {}
  bstack111l1l1l1_opy_[bstack11l1ll1111_opy_] = bstack11llllllll_opy_
  with open(path, bstack11l111_opy_ (u"ࠦࡼ࠱ࠢऻ")) as outfile:
    json.dump(bstack111l1l1l1_opy_, outfile)
def bstack1111l1ll_opy_(bstack11l1ll1111_opy_):
  bstack11l1ll1111_opy_ = str(bstack11l1ll1111_opy_)
  bstack1ll11l1ll_opy_ = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"ࠬࢄ़ࠧ")), bstack11l111_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ऽ"))
  try:
    if not os.path.exists(bstack1ll11l1ll_opy_):
      os.makedirs(bstack1ll11l1ll_opy_)
    file_path = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"ࠧࡿࠩा")), bstack11l111_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨि"), bstack11l111_opy_ (u"ࠩ࠱ࡦࡺ࡯࡬ࡥ࠯ࡱࡥࡲ࡫࠭ࡤࡣࡦ࡬ࡪ࠴ࡪࡴࡱࡱࠫी"))
    if not os.path.isfile(file_path):
      with open(file_path, bstack11l111_opy_ (u"ࠪࡻࠬु")):
        pass
      with open(file_path, bstack11l111_opy_ (u"ࠦࡼ࠱ࠢू")) as outfile:
        json.dump({}, outfile)
    with open(file_path, bstack11l111_opy_ (u"ࠬࡸࠧृ")) as bstack11l1ll11ll_opy_:
      bstack1111lll1_opy_ = json.load(bstack11l1ll11ll_opy_)
    if bstack11l1ll1111_opy_ in bstack1111lll1_opy_:
      bstack111l1llll_opy_ = bstack1111lll1_opy_[bstack11l1ll1111_opy_][bstack11l111_opy_ (u"࠭ࡩࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪॄ")]
      bstack11l111ll1_opy_ = int(bstack111l1llll_opy_) + 1
      bstack1l1ll1l1l_opy_(bstack11l1ll1111_opy_, bstack11l111ll1_opy_, file_path)
      return bstack11l111ll1_opy_
    else:
      bstack1l1ll1l1l_opy_(bstack11l1ll1111_opy_, 1, file_path)
      return 1
  except Exception as e:
    logger.warn(bstack11lll11l_opy_.format(str(e)))
    return -1
def bstack1l11l1ll1l_opy_(config):
  if not config[bstack11l111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩॅ")] or not config[bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫॆ")]:
    return True
  else:
    return False
def bstack11ll11ll_opy_(config, index=0):
  global bstack1l1l1l11_opy_
  bstack1l1111l1l_opy_ = {}
  caps = bstack11l111l1_opy_ + bstack11l1l1l11_opy_
  if config.get(bstack11l111_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭े"), False):
    bstack1l1111l1l_opy_[bstack11l111_opy_ (u"ࠪࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫ࠧै")] = True
    bstack1l1111l1l_opy_[bstack11l111_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࡐࡲࡷ࡭ࡴࡴࡳࠨॉ")] = config.get(bstack11l111_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩॊ"), {})
  if bstack1l1l1l11_opy_:
    caps += bstack1111l1l11_opy_
  for key in config:
    if key in caps + [bstack11l111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩो")]:
      continue
    bstack1l1111l1l_opy_[key] = config[key]
  if bstack11l111_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪौ") in config:
    for bstack11l1llll1l_opy_ in config[bstack11l111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶ्ࠫ")][index]:
      if bstack11l1llll1l_opy_ in caps:
        continue
      bstack1l1111l1l_opy_[bstack11l1llll1l_opy_] = config[bstack11l111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬॎ")][index][bstack11l1llll1l_opy_]
  bstack1l1111l1l_opy_[bstack11l111_opy_ (u"ࠪ࡬ࡴࡹࡴࡏࡣࡰࡩࠬॏ")] = socket.gethostname()
  if bstack11l111_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࠬॐ") in bstack1l1111l1l_opy_:
    del (bstack1l1111l1l_opy_[bstack11l111_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳ࠭॑")])
  return bstack1l1111l1l_opy_
def bstack11llll1l11_opy_(config):
  global bstack1l1l1l11_opy_
  bstack11l11l1ll_opy_ = {}
  caps = bstack11l1l1l11_opy_
  if bstack1l1l1l11_opy_:
    caps += bstack1111l1l11_opy_
  for key in caps:
    if key in config:
      bstack11l11l1ll_opy_[key] = config[key]
  return bstack11l11l1ll_opy_
def bstack11111ll11_opy_(bstack1l1111l1l_opy_, bstack11l11l1ll_opy_):
  bstack1l1l11l1_opy_ = {}
  for key in bstack1l1111l1l_opy_.keys():
    if key in bstack1l111111ll_opy_:
      bstack1l1l11l1_opy_[bstack1l111111ll_opy_[key]] = bstack1l1111l1l_opy_[key]
    else:
      bstack1l1l11l1_opy_[key] = bstack1l1111l1l_opy_[key]
  for key in bstack11l11l1ll_opy_:
    if key in bstack1l111111ll_opy_:
      bstack1l1l11l1_opy_[bstack1l111111ll_opy_[key]] = bstack11l11l1ll_opy_[key]
    else:
      bstack1l1l11l1_opy_[key] = bstack11l11l1ll_opy_[key]
  return bstack1l1l11l1_opy_
def bstack1ll1111ll1_opy_(config, index=0):
  global bstack1l1l1l11_opy_
  caps = {}
  config = copy.deepcopy(config)
  bstack1ll11llll1_opy_ = bstack1l1ll1l1l1_opy_(bstack1lllll1l1l_opy_, config, logger)
  bstack11l11l1ll_opy_ = bstack11llll1l11_opy_(config)
  bstack1l1llll11_opy_ = bstack11l1l1l11_opy_
  bstack1l1llll11_opy_ += bstack11l1ll11l_opy_
  bstack11l11l1ll_opy_ = update(bstack11l11l1ll_opy_, bstack1ll11llll1_opy_)
  if bstack1l1l1l11_opy_:
    bstack1l1llll11_opy_ += bstack1111l1l11_opy_
  if bstack11l111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴ॒ࠩ") in config:
    if bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ॓") in config[bstack11l111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ॔")][index]:
      caps[bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧॕ")] = config[bstack11l111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ॖ")][index][bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩॗ")]
    if bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭क़") in config[bstack11l111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩख़")][index]:
      caps[bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨग़")] = str(config[bstack11l111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫज़")][index][bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪड़")])
    bstack11l1l1111_opy_ = bstack1l1ll1l1l1_opy_(bstack1lllll1l1l_opy_, config[bstack11l111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ढ़")][index], logger)
    bstack1l1llll11_opy_ += list(bstack11l1l1111_opy_.keys())
    for bstack1l1l1111l_opy_ in bstack1l1llll11_opy_:
      if bstack1l1l1111l_opy_ in config[bstack11l111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧफ़")][index]:
        if bstack1l1l1111l_opy_ == bstack11l111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧय़"):
          try:
            bstack11l1l1111_opy_[bstack1l1l1111l_opy_] = str(config[bstack11l111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩॠ")][index][bstack1l1l1111l_opy_] * 1.0)
          except:
            bstack11l1l1111_opy_[bstack1l1l1111l_opy_] = str(config[bstack11l111_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪॡ")][index][bstack1l1l1111l_opy_])
        else:
          bstack11l1l1111_opy_[bstack1l1l1111l_opy_] = config[bstack11l111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫॢ")][index][bstack1l1l1111l_opy_]
        del (config[bstack11l111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬॣ")][index][bstack1l1l1111l_opy_])
    bstack11l11l1ll_opy_ = update(bstack11l11l1ll_opy_, bstack11l1l1111_opy_)
  bstack1l1111l1l_opy_ = bstack11ll11ll_opy_(config, index)
  for bstack1l1l1l1111_opy_ in bstack11l1l1l11_opy_ + list(bstack1ll11llll1_opy_.keys()):
    if bstack1l1l1l1111_opy_ in bstack1l1111l1l_opy_:
      bstack11l11l1ll_opy_[bstack1l1l1l1111_opy_] = bstack1l1111l1l_opy_[bstack1l1l1l1111_opy_]
      del (bstack1l1111l1l_opy_[bstack1l1l1l1111_opy_])
  if bstack11l1lll1ll_opy_(config):
    bstack1l1111l1l_opy_[bstack11l111_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪ।")] = True
    caps.update(bstack11l11l1ll_opy_)
    caps[bstack11l111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬ॥")] = bstack1l1111l1l_opy_
  else:
    bstack1l1111l1l_opy_[bstack11l111_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬ०")] = False
    caps.update(bstack11111ll11_opy_(bstack1l1111l1l_opy_, bstack11l11l1ll_opy_))
    if bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫ१") in caps:
      caps[bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨ२")] = caps[bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭३")]
      del (caps[bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧ४")])
    if bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ५") in caps:
      caps[bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭६")] = caps[bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭७")]
      del (caps[bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ८")])
  return caps
def bstack1ll1ll1l1_opy_():
  global bstack1l1l11lll1_opy_
  global CONFIG
  if bstack1lllll1l1_opy_() <= version.parse(bstack11l111_opy_ (u"ࠧ࠴࠰࠴࠷࠳࠶ࠧ९")):
    if bstack1l1l11lll1_opy_ != bstack11l111_opy_ (u"ࠨࠩ॰"):
      return bstack11l111_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥॱ") + bstack1l1l11lll1_opy_ + bstack11l111_opy_ (u"ࠥ࠾࠽࠶࠯ࡸࡦ࠲࡬ࡺࡨࠢॲ")
    return bstack1ll1l1ll11_opy_
  if bstack1l1l11lll1_opy_ != bstack11l111_opy_ (u"ࠫࠬॳ"):
    return bstack11l111_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࠢॴ") + bstack1l1l11lll1_opy_ + bstack11l111_opy_ (u"ࠨ࠯ࡸࡦ࠲࡬ࡺࡨࠢॵ")
  return bstack1l111l11l_opy_
def bstack11lll1l1l_opy_(options):
  return hasattr(options, bstack11l111_opy_ (u"ࠧࡴࡧࡷࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡹࠨॶ"))
def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = update(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack1ll1lll1l_opy_(options, bstack1ll11l111l_opy_):
  for bstack1lll111111_opy_ in bstack1ll11l111l_opy_:
    if bstack1lll111111_opy_ in [bstack11l111_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ॷ"), bstack11l111_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭ॸ")]:
      continue
    if bstack1lll111111_opy_ in options._experimental_options:
      options._experimental_options[bstack1lll111111_opy_] = update(options._experimental_options[bstack1lll111111_opy_],
                                                         bstack1ll11l111l_opy_[bstack1lll111111_opy_])
    else:
      options.add_experimental_option(bstack1lll111111_opy_, bstack1ll11l111l_opy_[bstack1lll111111_opy_])
  if bstack11l111_opy_ (u"ࠪࡥࡷ࡭ࡳࠨॹ") in bstack1ll11l111l_opy_:
    for arg in bstack1ll11l111l_opy_[bstack11l111_opy_ (u"ࠫࡦࡸࡧࡴࠩॺ")]:
      options.add_argument(arg)
    del (bstack1ll11l111l_opy_[bstack11l111_opy_ (u"ࠬࡧࡲࡨࡵࠪॻ")])
  if bstack11l111_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪॼ") in bstack1ll11l111l_opy_:
    for ext in bstack1ll11l111l_opy_[bstack11l111_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫॽ")]:
      try:
        options.add_extension(ext)
      except OSError:
        options.add_encoded_extension(ext)
    del (bstack1ll11l111l_opy_[bstack11l111_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬॾ")])
def bstack1lll1lll11_opy_(options, bstack1l11ll111_opy_):
  if bstack11l111_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨॿ") in bstack1l11ll111_opy_:
    for bstack1l11l11l1l_opy_ in bstack1l11ll111_opy_[bstack11l111_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩঀ")]:
      if bstack1l11l11l1l_opy_ in options._preferences:
        options._preferences[bstack1l11l11l1l_opy_] = update(options._preferences[bstack1l11l11l1l_opy_], bstack1l11ll111_opy_[bstack11l111_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪঁ")][bstack1l11l11l1l_opy_])
      else:
        options.set_preference(bstack1l11l11l1l_opy_, bstack1l11ll111_opy_[bstack11l111_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫং")][bstack1l11l11l1l_opy_])
  if bstack11l111_opy_ (u"࠭ࡡࡳࡩࡶࠫঃ") in bstack1l11ll111_opy_:
    for arg in bstack1l11ll111_opy_[bstack11l111_opy_ (u"ࠧࡢࡴࡪࡷࠬ঄")]:
      options.add_argument(arg)
def bstack1lllllll1_opy_(options, bstack1l11111ll1_opy_):
  if bstack11l111_opy_ (u"ࠨࡹࡨࡦࡻ࡯ࡥࡸࠩঅ") in bstack1l11111ll1_opy_:
    options.use_webview(bool(bstack1l11111ll1_opy_[bstack11l111_opy_ (u"ࠩࡺࡩࡧࡼࡩࡦࡹࠪআ")]))
  bstack1ll1lll1l_opy_(options, bstack1l11111ll1_opy_)
def bstack1l1l1l111_opy_(options, bstack1ll1ll1l11_opy_):
  for bstack1l1111l11l_opy_ in bstack1ll1ll1l11_opy_:
    if bstack1l1111l11l_opy_ in [bstack11l111_opy_ (u"ࠪࡸࡪࡩࡨ࡯ࡱ࡯ࡳ࡬ࡿࡐࡳࡧࡹ࡭ࡪࡽࠧই"), bstack11l111_opy_ (u"ࠫࡦࡸࡧࡴࠩঈ")]:
      continue
    options.set_capability(bstack1l1111l11l_opy_, bstack1ll1ll1l11_opy_[bstack1l1111l11l_opy_])
  if bstack11l111_opy_ (u"ࠬࡧࡲࡨࡵࠪউ") in bstack1ll1ll1l11_opy_:
    for arg in bstack1ll1ll1l11_opy_[bstack11l111_opy_ (u"࠭ࡡࡳࡩࡶࠫঊ")]:
      options.add_argument(arg)
  if bstack11l111_opy_ (u"ࠧࡵࡧࡦ࡬ࡳࡵ࡬ࡰࡩࡼࡔࡷ࡫ࡶࡪࡧࡺࠫঋ") in bstack1ll1ll1l11_opy_:
    options.bstack11l1l1lll_opy_(bool(bstack1ll1ll1l11_opy_[bstack11l111_opy_ (u"ࠨࡶࡨࡧ࡭ࡴ࡯࡭ࡱࡪࡽࡕࡸࡥࡷ࡫ࡨࡻࠬঌ")]))
def bstack1ll1111l1_opy_(options, bstack1111l1ll1_opy_):
  for bstack1l111l1ll_opy_ in bstack1111l1ll1_opy_:
    if bstack1l111l1ll_opy_ in [bstack11l111_opy_ (u"ࠩࡤࡨࡩ࡯ࡴࡪࡱࡱࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭঍"), bstack11l111_opy_ (u"ࠪࡥࡷ࡭ࡳࠨ঎")]:
      continue
    options._options[bstack1l111l1ll_opy_] = bstack1111l1ll1_opy_[bstack1l111l1ll_opy_]
  if bstack11l111_opy_ (u"ࠫࡦࡪࡤࡪࡶ࡬ࡳࡳࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨএ") in bstack1111l1ll1_opy_:
    for bstack11lllll1ll_opy_ in bstack1111l1ll1_opy_[bstack11l111_opy_ (u"ࠬࡧࡤࡥ࡫ࡷ࡭ࡴࡴࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩঐ")]:
      options.bstack11l1ll1ll_opy_(
        bstack11lllll1ll_opy_, bstack1111l1ll1_opy_[bstack11l111_opy_ (u"࠭ࡡࡥࡦ࡬ࡸ࡮ࡵ࡮ࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ঑")][bstack11lllll1ll_opy_])
  if bstack11l111_opy_ (u"ࠧࡢࡴࡪࡷࠬ঒") in bstack1111l1ll1_opy_:
    for arg in bstack1111l1ll1_opy_[bstack11l111_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ও")]:
      options.add_argument(arg)
def bstack11lll1llll_opy_(options, caps):
  if not hasattr(options, bstack11l111_opy_ (u"ࠩࡎࡉ࡞࠭ঔ")):
    return
  if options.KEY == bstack11l111_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨক"):
    options = bstack1lllll11l_opy_.bstack1lll1l1ll1_opy_(bstack1llll1111_opy_=options, config=CONFIG)
  if options.KEY == bstack11l111_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩখ") and options.KEY in caps:
    bstack1ll1lll1l_opy_(options, caps[bstack11l111_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪগ")])
  elif options.KEY == bstack11l111_opy_ (u"࠭࡭ࡰࡼ࠽ࡪ࡮ࡸࡥࡧࡱࡻࡓࡵࡺࡩࡰࡰࡶࠫঘ") and options.KEY in caps:
    bstack1lll1lll11_opy_(options, caps[bstack11l111_opy_ (u"ࠧ࡮ࡱࡽ࠾࡫࡯ࡲࡦࡨࡲࡼࡔࡶࡴࡪࡱࡱࡷࠬঙ")])
  elif options.KEY == bstack11l111_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩ࠯ࡱࡳࡸ࡮ࡵ࡮ࡴࠩচ") and options.KEY in caps:
    bstack1l1l1l111_opy_(options, caps[bstack11l111_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪ࠰ࡲࡴࡹ࡯࡯࡯ࡵࠪছ")])
  elif options.KEY == bstack11l111_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫজ") and options.KEY in caps:
    bstack1lllllll1_opy_(options, caps[bstack11l111_opy_ (u"ࠫࡲࡹ࠺ࡦࡦࡪࡩࡔࡶࡴࡪࡱࡱࡷࠬঝ")])
  elif options.KEY == bstack11l111_opy_ (u"ࠬࡹࡥ࠻࡫ࡨࡓࡵࡺࡩࡰࡰࡶࠫঞ") and options.KEY in caps:
    bstack1ll1111l1_opy_(options, caps[bstack11l111_opy_ (u"࠭ࡳࡦ࠼࡬ࡩࡔࡶࡴࡪࡱࡱࡷࠬট")])
def bstack1l1l1l1l1l_opy_(caps):
  global bstack1l1l1l11_opy_
  if isinstance(os.environ.get(bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡉࡔࡡࡄࡔࡕࡥࡁࡖࡖࡒࡑࡆ࡚ࡅࠨঠ")), str):
    bstack1l1l1l11_opy_ = eval(os.getenv(bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩড")))
  if bstack1l1l1l11_opy_:
    if bstack1ll1111ll_opy_() < version.parse(bstack11l111_opy_ (u"ࠩ࠵࠲࠸࠴࠰ࠨঢ")):
      return None
    else:
      from appium.options.common.base import AppiumOptions
      options = AppiumOptions().load_capabilities(caps)
      return options
  else:
    browser = bstack11l111_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪণ")
    if bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩত") in caps:
      browser = caps[bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪথ")]
    elif bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧদ") in caps:
      browser = caps[bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨধ")]
    browser = str(browser).lower()
    if browser == bstack11l111_opy_ (u"ࠨ࡫ࡳ࡬ࡴࡴࡥࠨন") or browser == bstack11l111_opy_ (u"ࠩ࡬ࡴࡦࡪࠧ঩"):
      browser = bstack11l111_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪপ")
    if browser == bstack11l111_opy_ (u"ࠫࡸࡧ࡭ࡴࡷࡱ࡫ࠬফ"):
      browser = bstack11l111_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬব")
    if browser not in [bstack11l111_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭ভ"), bstack11l111_opy_ (u"ࠧࡦࡦࡪࡩࠬম"), bstack11l111_opy_ (u"ࠨ࡫ࡨࠫয"), bstack11l111_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࠩর"), bstack11l111_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫ঱")]:
      return None
    try:
      package = bstack11l111_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠴ࡷࡦࡤࡧࡶ࡮ࡼࡥࡳ࠰ࡾࢁ࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭ল").format(browser)
      name = bstack11l111_opy_ (u"ࠬࡕࡰࡵ࡫ࡲࡲࡸ࠭঳")
      browser_options = getattr(__import__(package, fromlist=[name]), name)
      options = browser_options()
      if not bstack11lll1l1l_opy_(options):
        return None
      for bstack1l1l1l1111_opy_ in caps.keys():
        options.set_capability(bstack1l1l1l1111_opy_, caps[bstack1l1l1l1111_opy_])
      bstack11lll1llll_opy_(options, caps)
      return options
    except Exception as e:
      logger.debug(str(e))
      return None
def bstack1lll1l11_opy_(options, bstack11ll1llll1_opy_):
  if not bstack11lll1l1l_opy_(options):
    return
  for bstack1l1l1l1111_opy_ in bstack11ll1llll1_opy_.keys():
    if bstack1l1l1l1111_opy_ in bstack11l1ll11l_opy_:
      continue
    if bstack1l1l1l1111_opy_ in options._caps and type(options._caps[bstack1l1l1l1111_opy_]) in [dict, list]:
      options._caps[bstack1l1l1l1111_opy_] = update(options._caps[bstack1l1l1l1111_opy_], bstack11ll1llll1_opy_[bstack1l1l1l1111_opy_])
    else:
      options.set_capability(bstack1l1l1l1111_opy_, bstack11ll1llll1_opy_[bstack1l1l1l1111_opy_])
  bstack11lll1llll_opy_(options, bstack11ll1llll1_opy_)
  if bstack11l111_opy_ (u"࠭࡭ࡰࡼ࠽ࡨࡪࡨࡵࡨࡩࡨࡶࡆࡪࡤࡳࡧࡶࡷࠬ঴") in options._caps:
    if options._caps[bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ঵")] and options._caps[bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭শ")].lower() != bstack11l111_opy_ (u"ࠩࡩ࡭ࡷ࡫ࡦࡰࡺࠪষ"):
      del options._caps[bstack11l111_opy_ (u"ࠪࡱࡴࢀ࠺ࡥࡧࡥࡹ࡬࡭ࡥࡳࡃࡧࡨࡷ࡫ࡳࡴࠩস")]
def bstack11l1111ll1_opy_(proxy_config):
  if bstack11l111_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨহ") in proxy_config:
    proxy_config[bstack11l111_opy_ (u"ࠬࡹࡳ࡭ࡒࡵࡳࡽࡿࠧ঺")] = proxy_config[bstack11l111_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪ঻")]
    del (proxy_config[bstack11l111_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼ়ࠫ")])
  if bstack11l111_opy_ (u"ࠨࡲࡵࡳࡽࡿࡔࡺࡲࡨࠫঽ") in proxy_config and proxy_config[bstack11l111_opy_ (u"ࠩࡳࡶࡴࡾࡹࡕࡻࡳࡩࠬা")].lower() != bstack11l111_opy_ (u"ࠪࡨ࡮ࡸࡥࡤࡶࠪি"):
    proxy_config[bstack11l111_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡗࡽࡵ࡫ࠧী")] = bstack11l111_opy_ (u"ࠬࡳࡡ࡯ࡷࡤࡰࠬু")
  if bstack11l111_opy_ (u"࠭ࡰࡳࡱࡻࡽࡆࡻࡴࡰࡥࡲࡲ࡫࡯ࡧࡖࡴ࡯ࠫূ") in proxy_config:
    proxy_config[bstack11l111_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡚ࡹࡱࡧࠪৃ")] = bstack11l111_opy_ (u"ࠨࡲࡤࡧࠬৄ")
  return proxy_config
def bstack1lll1l1lll_opy_(config, proxy):
  from selenium.webdriver.common.proxy import Proxy
  if not bstack11l111_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨ৅") in config:
    return proxy
  config[bstack11l111_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩ৆")] = bstack11l1111ll1_opy_(config[bstack11l111_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࠪে")])
  if proxy == None:
    proxy = Proxy(config[bstack11l111_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫৈ")])
  return proxy
def bstack1ll1ll111_opy_(self):
  global CONFIG
  global bstack1ll1lll11_opy_
  try:
    proxy = bstack1lll111lll_opy_(CONFIG)
    if proxy:
      if proxy.endswith(bstack11l111_opy_ (u"࠭࠮ࡱࡣࡦࠫ৉")):
        proxies = bstack1lllll1ll_opy_(proxy, bstack1ll1ll1l1_opy_())
        if len(proxies) > 0:
          protocol, bstack1ll11l11l_opy_ = proxies.popitem()
          if bstack11l111_opy_ (u"ࠢ࠻࠱࠲ࠦ৊") in bstack1ll11l11l_opy_:
            return bstack1ll11l11l_opy_
          else:
            return bstack11l111_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤো") + bstack1ll11l11l_opy_
      else:
        return proxy
  except Exception as e:
    logger.error(bstack11l111_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡶࡲࡰࡺࡼࠤࡺࡸ࡬ࠡ࠼ࠣࡿࢂࠨৌ").format(str(e)))
  return bstack1ll1lll11_opy_(self)
def bstack1lllll11_opy_():
  global CONFIG
  return bstack11lll1ll_opy_(CONFIG) and bstack1l1lll1l1_opy_() and bstack1lllll1l1_opy_() >= version.parse(bstack1lll1l1l1l_opy_)
def bstack11l1lll1l_opy_():
  global CONFIG
  return (bstack11l111_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ্࠭") in CONFIG or bstack11l111_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨৎ") in CONFIG) and bstack11l1111lll_opy_()
def bstack11l1ll1l1l_opy_(config):
  bstack111lll11_opy_ = {}
  if bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ৏") in config:
    bstack111lll11_opy_ = config[bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ৐")]
  if bstack11l111_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭৑") in config:
    bstack111lll11_opy_ = config[bstack11l111_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ৒")]
  proxy = bstack1lll111lll_opy_(config)
  if proxy:
    if proxy.endswith(bstack11l111_opy_ (u"ࠩ࠱ࡴࡦࡩࠧ৓")) and os.path.isfile(proxy):
      bstack111lll11_opy_[bstack11l111_opy_ (u"ࠪ࠱ࡵࡧࡣ࠮ࡨ࡬ࡰࡪ࠭৔")] = proxy
    else:
      parsed_url = None
      if proxy.endswith(bstack11l111_opy_ (u"ࠫ࠳ࡶࡡࡤࠩ৕")):
        proxies = bstack11111llll_opy_(config, bstack1ll1ll1l1_opy_())
        if len(proxies) > 0:
          protocol, bstack1ll11l11l_opy_ = proxies.popitem()
          if bstack11l111_opy_ (u"ࠧࡀ࠯࠰ࠤ৖") in bstack1ll11l11l_opy_:
            parsed_url = urlparse(bstack1ll11l11l_opy_)
          else:
            parsed_url = urlparse(protocol + bstack11l111_opy_ (u"ࠨ࠺࠰࠱ࠥৗ") + bstack1ll11l11l_opy_)
      else:
        parsed_url = urlparse(proxy)
      if parsed_url and parsed_url.hostname: bstack111lll11_opy_[bstack11l111_opy_ (u"ࠧࡱࡴࡲࡼࡾࡎ࡯ࡴࡶࠪ৘")] = str(parsed_url.hostname)
      if parsed_url and parsed_url.port: bstack111lll11_opy_[bstack11l111_opy_ (u"ࠨࡲࡵࡳࡽࡿࡐࡰࡴࡷࠫ৙")] = str(parsed_url.port)
      if parsed_url and parsed_url.username: bstack111lll11_opy_[bstack11l111_opy_ (u"ࠩࡳࡶࡴࡾࡹࡖࡵࡨࡶࠬ৚")] = str(parsed_url.username)
      if parsed_url and parsed_url.password: bstack111lll11_opy_[bstack11l111_opy_ (u"ࠪࡴࡷࡵࡸࡺࡒࡤࡷࡸ࠭৛")] = str(parsed_url.password)
  return bstack111lll11_opy_
def bstack1111l1l1l_opy_(config):
  if bstack11l111_opy_ (u"ࠫࡹ࡫ࡳࡵࡅࡲࡲࡹ࡫ࡸࡵࡑࡳࡸ࡮ࡵ࡮ࡴࠩড়") in config:
    return config[bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶࡆࡳࡳࡺࡥࡹࡶࡒࡴࡹ࡯࡯࡯ࡵࠪঢ়")]
  return {}
def bstack1ll111llll_opy_(caps):
  global bstack111lllllll_opy_
  if bstack11l111_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ৞") in caps:
    caps[bstack11l111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨয়")][bstack11l111_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࠧৠ")] = True
    if bstack111lllllll_opy_:
      caps[bstack11l111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪৡ")][bstack11l111_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬৢ")] = bstack111lllllll_opy_
  else:
    caps[bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࠩৣ")] = True
    if bstack111lllllll_opy_:
      caps[bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭৤")] = bstack111lllllll_opy_
@measure(event_name=EVENTS.bstack11l111l1l1_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack11ll1l11l_opy_():
  global CONFIG
  if not bstack11l11l1l1l_opy_(CONFIG) or cli.is_enabled(CONFIG):
    return
  if bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ৥") in CONFIG and bstack111ll1lll_opy_(CONFIG[bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ০")]):
    if (
      bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ১") in CONFIG
      and bstack111ll1lll_opy_(CONFIG[bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭২")].get(bstack11l111_opy_ (u"ࠪࡷࡰ࡯ࡰࡃ࡫ࡱࡥࡷࡿࡉ࡯࡫ࡷ࡭ࡦࡲࡩࡴࡣࡷ࡭ࡴࡴࠧ৩")))
    ):
      logger.debug(bstack11l111_opy_ (u"ࠦࡑࡵࡣࡢ࡮ࠣࡦ࡮ࡴࡡࡳࡻࠣࡲࡴࡺࠠࡴࡶࡤࡶࡹ࡫ࡤࠡࡣࡶࠤࡸࡱࡩࡱࡄ࡬ࡲࡦࡸࡹࡊࡰ࡬ࡸ࡮ࡧ࡬ࡪࡵࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤࡪࡴࡡࡣ࡮ࡨࡨࠧ৪"))
      return
    bstack111lll11_opy_ = bstack11l1ll1l1l_opy_(CONFIG)
    bstack1l1l111l1l_opy_(CONFIG[bstack11l111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ৫")], bstack111lll11_opy_)
def bstack1l1l111l1l_opy_(key, bstack111lll11_opy_):
  global bstack11l111ll_opy_
  logger.info(bstack11l111l111_opy_)
  try:
    bstack11l111ll_opy_ = Local()
    bstack1l11l1llll_opy_ = {bstack11l111_opy_ (u"࠭࡫ࡦࡻࠪ৬"): key}
    bstack1l11l1llll_opy_.update(bstack111lll11_opy_)
    logger.debug(bstack11l1l1l1l1_opy_.format(str(bstack1l11l1llll_opy_)).replace(key, bstack11l111_opy_ (u"ࠧ࡜ࡔࡈࡈࡆࡉࡔࡆࡆࡠࠫ৭")))
    bstack11l111ll_opy_.start(**bstack1l11l1llll_opy_)
    if bstack11l111ll_opy_.isRunning():
      logger.info(bstack11l11l1l11_opy_)
  except Exception as e:
    bstack1l1l1lll_opy_(bstack11lllll11_opy_.format(str(e)))
def bstack11ll111l1_opy_():
  global bstack11l111ll_opy_
  if bstack11l111ll_opy_.isRunning():
    logger.info(bstack1llll1l1_opy_)
    bstack11l111ll_opy_.stop()
  bstack11l111ll_opy_ = None
def bstack1ll1111l11_opy_(bstack11111ll1_opy_=[]):
  global CONFIG
  bstack1l1l111l_opy_ = []
  bstack11lll11111_opy_ = [bstack11l111_opy_ (u"ࠨࡱࡶࠫ৮"), bstack11l111_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬ৯"), bstack11l111_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧৰ"), bstack11l111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ৱ"), bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ৲"), bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ৳")]
  try:
    for err in bstack11111ll1_opy_:
      bstack1l1lll11_opy_ = {}
      for k in bstack11lll11111_opy_:
        val = CONFIG[bstack11l111_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ৴")][int(err[bstack11l111_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧ৵")])].get(k)
        if val:
          bstack1l1lll11_opy_[k] = val
      if(err[bstack11l111_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨ৶")] != bstack11l111_opy_ (u"ࠪࠫ৷")):
        bstack1l1lll11_opy_[bstack11l111_opy_ (u"ࠫࡹ࡫ࡳࡵࡵࠪ৸")] = {
          err[bstack11l111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ৹")]: err[bstack11l111_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ৺")]
        }
        bstack1l1l111l_opy_.append(bstack1l1lll11_opy_)
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡩࡳࡷࡳࡡࡵࡶ࡬ࡲ࡬ࠦࡤࡢࡶࡤࠤ࡫ࡵࡲࠡࡧࡹࡩࡳࡺ࠺ࠡࠩ৻") + str(e))
  finally:
    return bstack1l1l111l_opy_
def bstack1l1l1l11l1_opy_(file_name):
  bstack1ll1l1llll_opy_ = []
  try:
    bstack11ll1l1ll1_opy_ = os.path.join(tempfile.gettempdir(), file_name)
    if os.path.exists(bstack11ll1l1ll1_opy_):
      with open(bstack11ll1l1ll1_opy_) as f:
        bstack1ll1llll1l_opy_ = json.load(f)
        bstack1ll1l1llll_opy_ = bstack1ll1llll1l_opy_
      os.remove(bstack11ll1l1ll1_opy_)
    return bstack1ll1l1llll_opy_
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡪ࡮ࡴࡤࡪࡰࡪࠤࡪࡸࡲࡰࡴࠣࡰ࡮ࡹࡴ࠻ࠢࠪৼ") + str(e))
    return bstack1ll1l1llll_opy_
def bstack1l1ll11l1_opy_():
  try:
      from bstack_utils.constants import bstack111l111l1_opy_, EVENTS
      from bstack_utils.helper import bstack111lllll1l_opy_, get_host_info, bstack11l11ll1l_opy_
      from datetime import datetime
      from filelock import FileLock
      bstack11l1l1ll1l_opy_ = os.path.join(os.getcwd(), bstack11l111_opy_ (u"ࠩ࡯ࡳ࡬࠭৽"), bstack11l111_opy_ (u"ࠪ࡯ࡪࡿ࠭࡮ࡧࡷࡶ࡮ࡩࡳ࠯࡬ࡶࡳࡳ࠭৾"))
      lock = FileLock(bstack11l1l1ll1l_opy_+bstack11l111_opy_ (u"ࠦ࠳ࡲ࡯ࡤ࡭ࠥ৿"))
      def bstack1llll11l_opy_():
          try:
              with lock:
                  with open(bstack11l1l1ll1l_opy_, bstack11l111_opy_ (u"ࠧࡸࠢ਀"), encoding=bstack11l111_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧਁ")) as file:
                      data = json.load(file)
                      config = {
                          bstack11l111_opy_ (u"ࠢࡩࡧࡤࡨࡪࡸࡳࠣਂ"): {
                              bstack11l111_opy_ (u"ࠣࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠢਃ"): bstack11l111_opy_ (u"ࠤࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠧ਄"),
                          }
                      }
                      bstack1llll1ll11_opy_ = datetime.utcnow()
                      bstack1l11ll11l_opy_ = bstack1llll1ll11_opy_.strftime(bstack11l111_opy_ (u"ࠥࠩ࡞࠳ࠥ࡮࠯ࠨࡨ࡙ࠫࡈ࠻ࠧࡐ࠾࡙ࠪ࠮ࠦࡨ࡙࡙ࠣࡉࠢਅ"))
                      bstack1l11l1l11l_opy_ = os.environ.get(bstack11l111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩਆ")) if os.environ.get(bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪਇ")) else bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠨࡳࡥ࡭ࡕࡹࡳࡏࡤࠣਈ"))
                      payload = {
                          bstack11l111_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠦਉ"): bstack11l111_opy_ (u"ࠣࡵࡧ࡯ࡤ࡫ࡶࡦࡰࡷࡷࠧਊ"),
                          bstack11l111_opy_ (u"ࠤࡧࡥࡹࡧࠢ਋"): {
                              bstack11l111_opy_ (u"ࠥࡸࡪࡹࡴࡩࡷࡥࡣࡺࡻࡩࡥࠤ਌"): bstack1l11l1l11l_opy_,
                              bstack11l111_opy_ (u"ࠦࡨࡸࡥࡢࡶࡨࡨࡤࡪࡡࡺࠤ਍"): bstack1l11ll11l_opy_,
                              bstack11l111_opy_ (u"ࠧ࡫ࡶࡦࡰࡷࡣࡳࡧ࡭ࡦࠤ਎"): bstack11l111_opy_ (u"ࠨࡓࡅࡍࡉࡩࡦࡺࡵࡳࡧࡓࡩࡷ࡬࡯ࡳ࡯ࡤࡲࡨ࡫ࠢਏ"),
                              bstack11l111_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡪࡴࡱࡱࠦਐ"): {
                                  bstack11l111_opy_ (u"ࠣ࡯ࡨࡥࡸࡻࡲࡦࡵࠥ਑"): data,
                                  bstack11l111_opy_ (u"ࠤࡶࡨࡰࡘࡵ࡯ࡋࡧࠦ਒"): bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠥࡷࡩࡱࡒࡶࡰࡌࡨࠧਓ"))
                              },
                              bstack11l111_opy_ (u"ࠦࡺࡹࡥࡳࡡࡧࡥࡹࡧࠢਔ"): bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠧࡻࡳࡦࡴࡑࡥࡲ࡫ࠢਕ")),
                              bstack11l111_opy_ (u"ࠨࡨࡰࡵࡷࡣ࡮ࡴࡦࡰࠤਖ"): get_host_info()
                          }
                      }
                      bstack1l11l1l1l_opy_ = bstack111111ll_opy_(cli.config, [bstack11l111_opy_ (u"ࠢࡢࡲ࡬ࡷࠧਗ"), bstack11l111_opy_ (u"ࠣࡧࡧࡷࡎࡴࡳࡵࡴࡸࡱࡪࡴࡴࡢࡶ࡬ࡳࡳࠨਘ"), bstack11l111_opy_ (u"ࠤࡤࡴ࡮ࠨਙ")], bstack111l111l1_opy_)
                      response = bstack111lllll1l_opy_(bstack11l111_opy_ (u"ࠥࡔࡔ࡙ࡔࠣਚ"), bstack1l11l1l1l_opy_, payload, config)
                      if(response.status_code >= 200 and response.status_code < 300):
                          logger.debug(bstack11l111_opy_ (u"ࠦࡉࡧࡴࡢࠢࡶࡩࡳࡺࠠࡴࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࡰࡾࠦࡴࡰࠢࡾࢁࠥࡽࡩࡵࡪࠣࡨࡦࡺࡡࠡࡽࢀࠦਛ").format(bstack111l111l1_opy_, payload))
                      else:
                          logger.debug(bstack11l111_opy_ (u"ࠧࡘࡥࡲࡷࡨࡷࡹࠦࡦࡢ࡫࡯ࡩࡩࠦࡦࡰࡴࠣࡿࢂࠦࡷࡪࡶ࡫ࠤࡩࡧࡴࡢࠢࡾࢁࠧਜ").format(bstack111l111l1_opy_, payload))
          except Exception as e:
              logger.debug(bstack11l111_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡳࡪࠠ࡬ࡧࡼࠤࡲ࡫ࡴࡳ࡫ࡦࡷࠥࡪࡡࡵࡣࠣࡻ࡮ࡺࡨࠡࡧࡵࡶࡴࡸࠠࡼࡿࠥਝ").format(e))
      bstack1llll11l_opy_()
      bstack11l11lll11_opy_(bstack11l1l1ll1l_opy_, logger)
  except:
    pass
def bstack1ll11ll1ll_opy_():
  global bstack1l1l111ll_opy_
  global bstack1l1ll111l1_opy_
  global bstack1l1111l1l1_opy_
  global bstack1l1ll1ll_opy_
  global bstack1ll1l1ll_opy_
  global bstack11ll1l11ll_opy_
  global CONFIG
  bstack1l1ll111l_opy_ = os.environ.get(bstack11l111_opy_ (u"ࠧࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࡢ࡙ࡘࡋࡄࠨਞ"))
  if bstack1l1ll111l_opy_ in [bstack11l111_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧਟ"), bstack11l111_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨਠ")]:
    bstack1l1l1ll1l1_opy_()
  percy.shutdown()
  if bstack1l1l111ll_opy_:
    logger.warning(bstack1l111l1l11_opy_.format(str(bstack1l1l111ll_opy_)))
  else:
    try:
      bstack111l1l1l1_opy_ = bstack1ll1lll11l_opy_(bstack11l111_opy_ (u"ࠪ࠲ࡧࡹࡴࡢࡥ࡮࠱ࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩਡ"), logger)
      if bstack111l1l1l1_opy_.get(bstack11l111_opy_ (u"ࠫࡳࡻࡤࡨࡧࡢࡰࡴࡩࡡ࡭ࠩਢ")) and bstack111l1l1l1_opy_.get(bstack11l111_opy_ (u"ࠬࡴࡵࡥࡩࡨࡣࡱࡵࡣࡢ࡮ࠪਣ")).get(bstack11l111_opy_ (u"࠭ࡨࡰࡵࡷࡲࡦࡳࡥࠨਤ")):
        logger.warning(bstack1l111l1l11_opy_.format(str(bstack111l1l1l1_opy_[bstack11l111_opy_ (u"ࠧ࡯ࡷࡧ࡫ࡪࡥ࡬ࡰࡥࡤࡰࠬਥ")][bstack11l111_opy_ (u"ࠨࡪࡲࡷࡹࡴࡡ࡮ࡧࠪਦ")])))
    except Exception as e:
      logger.error(e)
  if cli.is_running():
    bstack11111l1l1_opy_.invoke(bstack1llllll11l_opy_.bstack11l1lll11_opy_)
  logger.info(bstack1lll1l1ll_opy_)
  global bstack11l111ll_opy_
  if bstack11l111ll_opy_:
    bstack11ll111l1_opy_()
  try:
    with bstack11l11l11l_opy_:
      bstack11ll111l1l_opy_ = bstack1l1ll111l1_opy_.copy()
    for driver in bstack11ll111l1l_opy_:
      driver.quit()
  except Exception as e:
    pass
  logger.info(bstack11ll1111l_opy_)
  if bstack11ll1l11ll_opy_ == bstack11l111_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨਧ"):
    bstack1ll1l1ll_opy_ = bstack1l1l1l11l1_opy_(bstack11l111_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠴ࡪࡴࡱࡱࠫਨ"))
  if bstack11ll1l11ll_opy_ == bstack11l111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ਩") and len(bstack1l1ll1ll_opy_) == 0:
    bstack1l1ll1ll_opy_ = bstack1l1l1l11l1_opy_(bstack11l111_opy_ (u"ࠬࡶࡷࡠࡲࡼࡸࡪࡹࡴࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸ࠳ࡰࡳࡰࡰࠪਪ"))
    if len(bstack1l1ll1ll_opy_) == 0:
      bstack1l1ll1ll_opy_ = bstack1l1l1l11l1_opy_(bstack11l111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡰࡱࡲࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬਫ"))
  bstack1ll11l111_opy_ = bstack11l111_opy_ (u"ࠧࠨਬ")
  if len(bstack1l1111l1l1_opy_) > 0:
    bstack1ll11l111_opy_ = bstack1ll1111l11_opy_(bstack1l1111l1l1_opy_)
  elif len(bstack1l1ll1ll_opy_) > 0:
    bstack1ll11l111_opy_ = bstack1ll1111l11_opy_(bstack1l1ll1ll_opy_)
  elif len(bstack1ll1l1ll_opy_) > 0:
    bstack1ll11l111_opy_ = bstack1ll1111l11_opy_(bstack1ll1l1ll_opy_)
  elif len(bstack1l11llll1_opy_) > 0:
    bstack1ll11l111_opy_ = bstack1ll1111l11_opy_(bstack1l11llll1_opy_)
  if bool(bstack1ll11l111_opy_):
    bstack111l1111l_opy_(bstack1ll11l111_opy_)
  else:
    bstack111l1111l_opy_()
  bstack11l11lll11_opy_(bstack1l11lll1l_opy_, logger)
  if bstack1l1ll111l_opy_ not in [bstack11l111_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩਭ")]:
    bstack1l1ll11l1_opy_()
  bstack11l111111l_opy_.bstack1l111lll1_opy_(CONFIG)
  if len(bstack1ll1l1ll_opy_) > 0:
    sys.exit(len(bstack1ll1l1ll_opy_))
def bstack111l1ll1_opy_(bstack1l11ll1l_opy_, frame):
  global bstack11l11ll1l_opy_
  logger.error(bstack1l11l1l11_opy_)
  bstack11l11ll1l_opy_.bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡑࡳࠬਮ"), bstack1l11ll1l_opy_)
  if hasattr(signal, bstack11l111_opy_ (u"ࠪࡗ࡮࡭࡮ࡢ࡮ࡶࠫਯ")):
    bstack11l11ll1l_opy_.bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"ࠫࡸࡪ࡫ࡌ࡫࡯ࡰࡘ࡯ࡧ࡯ࡣ࡯ࠫਰ"), signal.Signals(bstack1l11ll1l_opy_).name)
  else:
    bstack11l11ll1l_opy_.bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"ࠬࡹࡤ࡬ࡍ࡬ࡰࡱ࡙ࡩࡨࡰࡤࡰࠬ਱"), bstack11l111_opy_ (u"࠭ࡓࡊࡉࡘࡒࡐࡔࡏࡘࡐࠪਲ"))
  if cli.is_running():
    bstack11111l1l1_opy_.invoke(bstack1llllll11l_opy_.bstack11l1lll11_opy_)
  bstack1l1ll111l_opy_ = os.environ.get(bstack11l111_opy_ (u"ࠧࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࡢ࡙ࡘࡋࡄࠨਲ਼"))
  if bstack1l1ll111l_opy_ == bstack11l111_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ਴") and not cli.is_enabled(CONFIG):
    bstack11l11l1l_opy_.stop(bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡖ࡭࡬ࡴࡡ࡭ࠩਵ")))
  bstack1ll11ll1ll_opy_()
  sys.exit(1)
def bstack1l1l1lll_opy_(err):
  logger.critical(bstack111lll1l11_opy_.format(str(err)))
  bstack111l1111l_opy_(bstack111lll1l11_opy_.format(str(err)), True)
  atexit.unregister(bstack1ll11ll1ll_opy_)
  bstack1l1l1ll1l1_opy_()
  sys.exit(1)
def bstack11l1lll11l_opy_(error, message):
  logger.critical(str(error))
  logger.critical(message)
  bstack111l1111l_opy_(message, True)
  atexit.unregister(bstack1ll11ll1ll_opy_)
  bstack1l1l1ll1l1_opy_()
  sys.exit(1)
def bstack1l1111111l_opy_():
  global CONFIG
  global bstack1l11lll11_opy_
  global bstack11l111l11l_opy_
  global bstack111111l11_opy_
  CONFIG = bstack1l1111lll1_opy_()
  load_dotenv(CONFIG.get(bstack11l111_opy_ (u"ࠪࡩࡳࡼࡆࡪ࡮ࡨࠫਸ਼")))
  bstack1l1llllll_opy_()
  bstack11lll1l1l1_opy_()
  CONFIG = bstack1l1lllll11_opy_(CONFIG)
  update(CONFIG, bstack11l111l11l_opy_)
  update(CONFIG, bstack1l11lll11_opy_)
  if not cli.is_enabled(CONFIG):
    CONFIG = bstack11l111ll1l_opy_(CONFIG)
  bstack111111l11_opy_ = bstack11l11l1l1l_opy_(CONFIG)
  os.environ[bstack11l111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧ਷")] = bstack111111l11_opy_.__str__().lower()
  bstack11l11ll1l_opy_.bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ਸ"), bstack111111l11_opy_)
  if (bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩਹ") in CONFIG and bstack11l111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ਺") in bstack1l11lll11_opy_) or (
          bstack11l111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ਻") in CONFIG and bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩ਼ࠬ") not in bstack11l111l11l_opy_):
    if os.getenv(bstack11l111_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡢࡇࡔࡓࡂࡊࡐࡈࡈࡤࡈࡕࡊࡎࡇࡣࡎࡊࠧ਽")):
      CONFIG[bstack11l111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ਾ")] = os.getenv(bstack11l111_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡤࡉࡏࡎࡄࡌࡒࡊࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠩਿ"))
    else:
      if not CONFIG.get(bstack11l111_opy_ (u"ࠨࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠤੀ"), bstack11l111_opy_ (u"ࠢࠣੁ")) in bstack11ll1l1l1l_opy_:
        bstack1l11l11l1_opy_()
  elif (bstack11l111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫੂ") not in CONFIG and bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ੃") in CONFIG) or (
          bstack11l111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭੄") in bstack11l111l11l_opy_ and bstack11l111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ੅") not in bstack1l11lll11_opy_):
    del (CONFIG[bstack11l111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ੆")])
  if bstack1l11l1ll1l_opy_(CONFIG):
    bstack1l1l1lll_opy_(bstack1l1ll1l11l_opy_)
  Config.bstack111llll1_opy_().bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"ࠨࡵࡴࡧࡵࡒࡦࡳࡥࠣੇ"), CONFIG[bstack11l111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩੈ")])
  bstack11ll1lll_opy_()
  bstack1l1l11l111_opy_()
  if bstack1l1l1l11_opy_ and not CONFIG.get(bstack11l111_opy_ (u"ࠣࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠦ੉"), bstack11l111_opy_ (u"ࠤࠥ੊")) in bstack11ll1l1l1l_opy_:
    CONFIG[bstack11l111_opy_ (u"ࠪࡥࡵࡶࠧੋ")] = bstack1l1l1llll_opy_(CONFIG)
    logger.info(bstack111l11l1_opy_.format(CONFIG[bstack11l111_opy_ (u"ࠫࡦࡶࡰࠨੌ")]))
  if not bstack111111l11_opy_:
    CONFIG[bstack11l111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ੍")] = [{}]
def bstack11ll1111ll_opy_(config, bstack1l1l111lll_opy_):
  global CONFIG
  global bstack1l1l1l11_opy_
  CONFIG = config
  bstack1l1l1l11_opy_ = bstack1l1l111lll_opy_
def bstack1l1l11l111_opy_():
  global CONFIG
  global bstack1l1l1l11_opy_
  if bstack11l111_opy_ (u"࠭ࡡࡱࡲࠪ੎") in CONFIG:
    try:
      from appium import version
    except Exception as e:
      bstack11l1lll11l_opy_(e, bstack11l11ll11l_opy_)
    bstack1l1l1l11_opy_ = True
    bstack11l11ll1l_opy_.bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭੏"), True)
def bstack1l1l1llll_opy_(config):
  bstack11l11lllll_opy_ = bstack11l111_opy_ (u"ࠨࠩ੐")
  app = config[bstack11l111_opy_ (u"ࠩࡤࡴࡵ࠭ੑ")]
  if isinstance(app, str):
    if os.path.splitext(app)[1] in bstack11lll1lll_opy_:
      if os.path.exists(app):
        bstack11l11lllll_opy_ = bstack11llll1lll_opy_(config, app)
      elif bstack1l1111ll1l_opy_(app):
        bstack11l11lllll_opy_ = app
      else:
        bstack1l1l1lll_opy_(bstack1111l11l_opy_.format(app))
    else:
      if bstack1l1111ll1l_opy_(app):
        bstack11l11lllll_opy_ = app
      elif os.path.exists(app):
        bstack11l11lllll_opy_ = bstack11llll1lll_opy_(app)
      else:
        bstack1l1l1lll_opy_(bstack1lll11llll_opy_)
  else:
    if len(app) > 2:
      bstack1l1l1lll_opy_(bstack11l11l11_opy_)
    elif len(app) == 2:
      if bstack11l111_opy_ (u"ࠪࡴࡦࡺࡨࠨ੒") in app and bstack11l111_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡣ࡮ࡪࠧ੓") in app:
        if os.path.exists(app[bstack11l111_opy_ (u"ࠬࡶࡡࡵࡪࠪ੔")]):
          bstack11l11lllll_opy_ = bstack11llll1lll_opy_(config, app[bstack11l111_opy_ (u"࠭ࡰࡢࡶ࡫ࠫ੕")], app[bstack11l111_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳ࡟ࡪࡦࠪ੖")])
        else:
          bstack1l1l1lll_opy_(bstack1111l11l_opy_.format(app))
      else:
        bstack1l1l1lll_opy_(bstack11l11l11_opy_)
    else:
      for key in app:
        if key in bstack1ll1ll111l_opy_:
          if key == bstack11l111_opy_ (u"ࠨࡲࡤࡸ࡭࠭੗"):
            if os.path.exists(app[key]):
              bstack11l11lllll_opy_ = bstack11llll1lll_opy_(config, app[key])
            else:
              bstack1l1l1lll_opy_(bstack1111l11l_opy_.format(app))
          else:
            bstack11l11lllll_opy_ = app[key]
        else:
          bstack1l1l1lll_opy_(bstack1l1l11111_opy_)
  return bstack11l11lllll_opy_
def bstack1l1111ll1l_opy_(bstack11l11lllll_opy_):
  import re
  bstack1lll111ll1_opy_ = re.compile(bstack11l111_opy_ (u"ࡴࠥࡢࡠࡧ࠭ࡻࡃ࠰࡞࠵࠳࠹࡝ࡡ࠱ࡠ࠲ࡣࠪࠥࠤ੘"))
  bstack11l1ll1l11_opy_ = re.compile(bstack11l111_opy_ (u"ࡵࠦࡣࡡࡡ࠮ࡼࡄ࠱࡟࠶࠭࠺࡞ࡢ࠲ࡡ࠳࡝ࠫ࠱࡞ࡥ࠲ࢀࡁ࠮࡜࠳࠱࠾ࡢ࡟࠯࡞࠰ࡡ࠯ࠪࠢਖ਼"))
  if bstack11l111_opy_ (u"ࠫࡧࡹ࠺࠰࠱ࠪਗ਼") in bstack11l11lllll_opy_ or re.fullmatch(bstack1lll111ll1_opy_, bstack11l11lllll_opy_) or re.fullmatch(bstack11l1ll1l11_opy_, bstack11l11lllll_opy_):
    return True
  else:
    return False
@measure(event_name=EVENTS.bstack1ll111111l_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack11llll1lll_opy_(config, path, bstack11l11ll1_opy_=None):
  import requests
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  import hashlib
  md5_hash = hashlib.md5(open(os.path.abspath(path), bstack11l111_opy_ (u"ࠬࡸࡢࠨਜ਼")).read()).hexdigest()
  bstack1l11l1lll_opy_ = bstack1lllll111_opy_(md5_hash)
  bstack11l11lllll_opy_ = None
  if bstack1l11l1lll_opy_:
    logger.info(bstack1l111lllll_opy_.format(bstack1l11l1lll_opy_, md5_hash))
    return bstack1l11l1lll_opy_
  bstack11l1l11l1l_opy_ = datetime.datetime.now()
  bstack11lll11l11_opy_ = MultipartEncoder(
    fields={
      bstack11l111_opy_ (u"࠭ࡦࡪ࡮ࡨࠫੜ"): (os.path.basename(path), open(os.path.abspath(path), bstack11l111_opy_ (u"ࠧࡳࡤࠪ੝")), bstack11l111_opy_ (u"ࠨࡶࡨࡼࡹ࠵ࡰ࡭ࡣ࡬ࡲࠬਫ਼")),
      bstack11l111_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡡ࡬ࡨࠬ੟"): bstack11l11ll1_opy_
    }
  )
  response = requests.post(bstack1ll1l11ll_opy_, data=bstack11lll11l11_opy_,
                           headers={bstack11l111_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩ੠"): bstack11lll11l11_opy_.content_type},
                           auth=(config[bstack11l111_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭੡")], config[bstack11l111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ੢")]))
  try:
    res = json.loads(response.text)
    bstack11l11lllll_opy_ = res[bstack11l111_opy_ (u"࠭ࡡࡱࡲࡢࡹࡷࡲࠧ੣")]
    logger.info(bstack1l11111111_opy_.format(bstack11l11lllll_opy_))
    bstack1lll1l1l_opy_(md5_hash, bstack11l11lllll_opy_)
    cli.bstack1l11lllll_opy_(bstack11l111_opy_ (u"ࠢࡩࡶࡷࡴ࠿ࡻࡰ࡭ࡱࡤࡨࡤࡧࡰࡱࠤ੤"), datetime.datetime.now() - bstack11l1l11l1l_opy_)
  except ValueError as err:
    bstack1l1l1lll_opy_(bstack11l1ll11l1_opy_.format(str(err)))
  return bstack11l11lllll_opy_
def bstack11ll1lll_opy_(framework_name=None, args=None):
  global CONFIG
  global bstack1l111l1ll1_opy_
  bstack11ll1l1111_opy_ = 1
  bstack11ll1ll1l1_opy_ = 1
  if bstack11l111_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ੥") in CONFIG:
    bstack11ll1ll1l1_opy_ = CONFIG[bstack11l111_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ੦")]
  else:
    bstack11ll1ll1l1_opy_ = bstack1l11l11ll_opy_(framework_name, args) or 1
  if bstack11l111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭੧") in CONFIG:
    bstack11ll1l1111_opy_ = len(CONFIG[bstack11l111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ੨")])
  bstack1l111l1ll1_opy_ = int(bstack11ll1ll1l1_opy_) * int(bstack11ll1l1111_opy_)
def bstack1l11l11ll_opy_(framework_name, args):
  if framework_name == bstack1l11ll111l_opy_ and args and bstack11l111_opy_ (u"ࠬ࠳࠭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪ੩") in args:
      bstack1l1l1ll1ll_opy_ = args.index(bstack11l111_opy_ (u"࠭࠭࠮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫ੪"))
      return int(args[bstack1l1l1ll1ll_opy_ + 1]) or 1
  return 1
def bstack1lllll111_opy_(md5_hash):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11l111_opy_ (u"ࠧࡧ࡫࡯ࡩࡱࡵࡣ࡬ࠢࡱࡳࡹࠦࡡࡷࡣ࡬ࡰࡦࡨ࡬ࡦ࠮ࠣࡹࡸ࡯࡮ࡨࠢࡥࡥࡸ࡯ࡣࠡࡨ࡬ࡰࡪࠦ࡯ࡱࡧࡵࡥࡹ࡯࡯࡯ࡵࠪ੫"))
    bstack1l11l1111_opy_ = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"ࠨࢀࠪ੬")), bstack11l111_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ੭"), bstack11l111_opy_ (u"ࠪࡥࡵࡶࡕࡱ࡮ࡲࡥࡩࡓࡄ࠶ࡊࡤࡷ࡭࠴ࡪࡴࡱࡱࠫ੮"))
    if os.path.exists(bstack1l11l1111_opy_):
      try:
        bstack11l11ll111_opy_ = json.load(open(bstack1l11l1111_opy_, bstack11l111_opy_ (u"ࠫࡷࡨࠧ੯")))
        if md5_hash in bstack11l11ll111_opy_:
          bstack11ll1ll11_opy_ = bstack11l11ll111_opy_[md5_hash]
          bstack1l11l1111l_opy_ = datetime.datetime.now()
          bstack1l111l11ll_opy_ = datetime.datetime.strptime(bstack11ll1ll11_opy_[bstack11l111_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨੰ")], bstack11l111_opy_ (u"࠭ࠥࡥ࠱ࠨࡱ࠴࡙ࠫࠡࠧࡋ࠾ࠪࡓ࠺ࠦࡕࠪੱ"))
          if (bstack1l11l1111l_opy_ - bstack1l111l11ll_opy_).days > 30:
            return None
          elif version.parse(str(__version__)) > version.parse(bstack11ll1ll11_opy_[bstack11l111_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬੲ")]):
            return None
          return bstack11ll1ll11_opy_[bstack11l111_opy_ (u"ࠨ࡫ࡧࠫੳ")]
      except Exception as e:
        logger.debug(bstack11l111_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡࡴࡨࡥࡩ࡯࡮ࡨࠢࡐࡈ࠺ࠦࡨࡢࡵ࡫ࠤ࡫࡯࡬ࡦ࠼ࠣࡿࢂ࠭ੴ").format(str(e)))
    return None
  bstack1l11l1111_opy_ = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"ࠪࢂࠬੵ")), bstack11l111_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ੶"), bstack11l111_opy_ (u"ࠬࡧࡰࡱࡗࡳࡰࡴࡧࡤࡎࡆ࠸ࡌࡦࡹࡨ࠯࡬ࡶࡳࡳ࠭੷"))
  lock_file = bstack1l11l1111_opy_ + bstack11l111_opy_ (u"࠭࠮࡭ࡱࡦ࡯ࠬ੸")
  try:
    with FileLock(lock_file, timeout=10):
      if os.path.exists(bstack1l11l1111_opy_):
        with open(bstack1l11l1111_opy_, bstack11l111_opy_ (u"ࠧࡳࠩ੹")) as f:
          content = f.read().strip()
          if content:
            bstack11l11ll111_opy_ = json.loads(content)
            if md5_hash in bstack11l11ll111_opy_:
              bstack11ll1ll11_opy_ = bstack11l11ll111_opy_[md5_hash]
              bstack1l11l1111l_opy_ = datetime.datetime.now()
              bstack1l111l11ll_opy_ = datetime.datetime.strptime(bstack11ll1ll11_opy_[bstack11l111_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ੺")], bstack11l111_opy_ (u"ࠩࠨࡨ࠴ࠫ࡭࠰ࠧ࡜ࠤࠪࡎ࠺ࠦࡏ࠽ࠩࡘ࠭੻"))
              if (bstack1l11l1111l_opy_ - bstack1l111l11ll_opy_).days > 30:
                return None
              elif version.parse(str(__version__)) > version.parse(bstack11ll1ll11_opy_[bstack11l111_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ੼")]):
                return None
              return bstack11ll1ll11_opy_[bstack11l111_opy_ (u"ࠫ࡮ࡪࠧ੽")]
      return None
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤࡼ࡯ࡴࡩࠢࡩ࡭ࡱ࡫ࠠ࡭ࡱࡦ࡯࡮ࡴࡧࠡࡨࡲࡶࠥࡓࡄ࠶ࠢ࡫ࡥࡸ࡮࠺ࠡࡽࢀࠫ੾").format(str(e)))
    return None
def bstack1lll1l1l_opy_(md5_hash, bstack11l11lllll_opy_):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11l111_opy_ (u"࠭ࡦࡪ࡮ࡨࡰࡴࡩ࡫ࠡࡰࡲࡸࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥ࠭ࠢࡸࡷ࡮ࡴࡧࠡࡤࡤࡷ࡮ࡩࠠࡧ࡫࡯ࡩࠥࡵࡰࡦࡴࡤࡸ࡮ࡵ࡮ࡴࠩ੿"))
    bstack1ll11l1ll_opy_ = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"ࠧࡿࠩ઀")), bstack11l111_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨઁ"))
    if not os.path.exists(bstack1ll11l1ll_opy_):
      os.makedirs(bstack1ll11l1ll_opy_)
    bstack1l11l1111_opy_ = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"ࠩࢁࠫં")), bstack11l111_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪઃ"), bstack11l111_opy_ (u"ࠫࡦࡶࡰࡖࡲ࡯ࡳࡦࡪࡍࡅ࠷ࡋࡥࡸ࡮࠮࡫ࡵࡲࡲࠬ઄"))
    bstack1l1l1l1lll_opy_ = {
      bstack11l111_opy_ (u"ࠬ࡯ࡤࠨઅ"): bstack11l11lllll_opy_,
      bstack11l111_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩઆ"): datetime.datetime.strftime(datetime.datetime.now(), bstack11l111_opy_ (u"ࠧࠦࡦ࠲ࠩࡲ࠵࡚ࠥࠢࠨࡌ࠿ࠫࡍ࠻ࠧࡖࠫઇ")),
      bstack11l111_opy_ (u"ࠨࡵࡧ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ઈ"): str(__version__)
    }
    try:
      bstack11l11ll111_opy_ = {}
      if os.path.exists(bstack1l11l1111_opy_):
        bstack11l11ll111_opy_ = json.load(open(bstack1l11l1111_opy_, bstack11l111_opy_ (u"ࠩࡵࡦࠬઉ")))
      bstack11l11ll111_opy_[md5_hash] = bstack1l1l1l1lll_opy_
      with open(bstack1l11l1111_opy_, bstack11l111_opy_ (u"ࠥࡻ࠰ࠨઊ")) as outfile:
        json.dump(bstack11l11ll111_opy_, outfile)
    except Exception as e:
      logger.debug(bstack11l111_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣࡹࡵࡪࡡࡵ࡫ࡱ࡫ࠥࡓࡄ࠶ࠢ࡫ࡥࡸ࡮ࠠࡧ࡫࡯ࡩ࠿ࠦࡻࡾࠩઋ").format(str(e)))
    return
  bstack1ll11l1ll_opy_ = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"ࠬࢄࠧઌ")), bstack11l111_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ઍ"))
  if not os.path.exists(bstack1ll11l1ll_opy_):
    os.makedirs(bstack1ll11l1ll_opy_)
  bstack1l11l1111_opy_ = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"ࠧࡿࠩ઎")), bstack11l111_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨએ"), bstack11l111_opy_ (u"ࠩࡤࡴࡵ࡛ࡰ࡭ࡱࡤࡨࡒࡊ࠵ࡉࡣࡶ࡬࠳ࡰࡳࡰࡰࠪઐ"))
  lock_file = bstack1l11l1111_opy_ + bstack11l111_opy_ (u"ࠪ࠲ࡱࡵࡣ࡬ࠩઑ")
  bstack1l1l1l1lll_opy_ = {
    bstack11l111_opy_ (u"ࠫ࡮ࡪࠧ઒"): bstack11l11lllll_opy_,
    bstack11l111_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨઓ"): datetime.datetime.strftime(datetime.datetime.now(), bstack11l111_opy_ (u"࠭ࠥࡥ࠱ࠨࡱ࠴࡙ࠫࠡࠧࡋ࠾ࠪࡓ࠺ࠦࡕࠪઔ")),
    bstack11l111_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬક"): str(__version__)
  }
  try:
    with FileLock(lock_file, timeout=10):
      bstack11l11ll111_opy_ = {}
      if os.path.exists(bstack1l11l1111_opy_):
        with open(bstack1l11l1111_opy_, bstack11l111_opy_ (u"ࠨࡴࠪખ")) as f:
          content = f.read().strip()
          if content:
            bstack11l11ll111_opy_ = json.loads(content)
      bstack11l11ll111_opy_[md5_hash] = bstack1l1l1l1lll_opy_
      with open(bstack1l11l1111_opy_, bstack11l111_opy_ (u"ࠤࡺࠦગ")) as outfile:
        json.dump(bstack11l11ll111_opy_, outfile)
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢࡺ࡭ࡹ࡮ࠠࡧ࡫࡯ࡩࠥࡲ࡯ࡤ࡭࡬ࡲ࡬ࠦࡦࡰࡴࠣࡑࡉ࠻ࠠࡩࡣࡶ࡬ࠥࡻࡰࡥࡣࡷࡩ࠿ࠦࡻࡾࠩઘ").format(str(e)))
def bstack11111l1l_opy_(self):
  return
def bstack1111111ll_opy_(self):
  return
def bstack11l11llll_opy_():
  global bstack11l1l11ll_opy_
  bstack11l1l11ll_opy_ = True
@measure(event_name=EVENTS.bstack1111ll1ll_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack1ll11l1l1l_opy_(self):
  global bstack1ll1111l_opy_
  global bstack1l1l11ll_opy_
  global bstack11lll1l1_opy_
  try:
    if bstack11l111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫઙ") in bstack1ll1111l_opy_ and self.session_id != None and bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶࡖࡸࡦࡺࡵࡴࠩચ"), bstack11l111_opy_ (u"࠭ࠧછ")) != bstack11l111_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨજ"):
      bstack1lll11l11l_opy_ = bstack11l111_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨઝ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack11l111_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩઞ")
      if bstack1lll11l11l_opy_ == bstack11l111_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪટ"):
        bstack1l1111ll_opy_(logger)
      if self != None:
        bstack1ll11l1ll1_opy_(self, bstack1lll11l11l_opy_, bstack11l111_opy_ (u"ࠫ࠱ࠦࠧઠ").join(threading.current_thread().bstackTestErrorMessages))
    threading.current_thread().testStatus = bstack11l111_opy_ (u"ࠬ࠭ડ")
    if bstack11l111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ઢ") in bstack1ll1111l_opy_ and getattr(threading.current_thread(), bstack11l111_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭ણ"), None):
      bstack1l1ll11111_opy_.bstack11lll1lll1_opy_(self, bstack11l11l111_opy_, logger, wait=True)
    if bstack11l111_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨત") in bstack1ll1111l_opy_:
      if not threading.currentThread().behave_test_status:
        bstack1ll11l1ll1_opy_(self, bstack11l111_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤથ"))
      bstack11ll1lllll_opy_.bstack1l1l1lll1l_opy_(self)
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡ࡯ࡤࡶࡰ࡯࡮ࡨࠢࡶࡸࡦࡺࡵࡴ࠼ࠣࠦદ") + str(e))
  bstack11lll1l1_opy_(self)
  self.session_id = None
def bstack11l1l111l_opy_(self, *args, **kwargs):
  try:
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    from bstack_utils.helper import bstack11111l11l_opy_
    global bstack1ll1111l_opy_
    command_executor = kwargs.get(bstack11l111_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠧધ"), bstack11l111_opy_ (u"ࠬ࠭ન"))
    bstack1lll1lll_opy_ = False
    if type(command_executor) == str and bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩ઩") in command_executor:
      bstack1lll1lll_opy_ = True
    elif isinstance(command_executor, RemoteConnection) and bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠪપ") in str(getattr(command_executor, bstack11l111_opy_ (u"ࠨࡡࡸࡶࡱ࠭ફ"), bstack11l111_opy_ (u"ࠩࠪબ"))):
      bstack1lll1lll_opy_ = True
    else:
      kwargs = bstack1lllll11l_opy_.bstack1lll1l1ll1_opy_(bstack1llll1111_opy_=kwargs, config=CONFIG)
      return bstack1l1l1l1l_opy_(self, *args, **kwargs)
    if bstack1lll1lll_opy_:
      bstack11l11lll1l_opy_ = bstack11ll11lll_opy_.bstack11ll1l111_opy_(CONFIG, bstack1ll1111l_opy_)
      if kwargs.get(bstack11l111_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫભ")):
        kwargs[bstack11l111_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬમ")] = bstack11111l11l_opy_(kwargs[bstack11l111_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭ય")], bstack1ll1111l_opy_, CONFIG, bstack11l11lll1l_opy_)
      elif kwargs.get(bstack11l111_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ર")):
        kwargs[bstack11l111_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ઱")] = bstack11111l11l_opy_(kwargs[bstack11l111_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨલ")], bstack1ll1111l_opy_, CONFIG, bstack11l11lll1l_opy_)
  except Exception as e:
    logger.error(bstack11l111_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫ࡩࡳࠦࡰࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡗࡉࡑࠠࡤࡣࡳࡷ࠿ࠦࡻࡾࠤળ").format(str(e)))
  return bstack1l1l1l1l_opy_(self, *args, **kwargs)
@measure(event_name=EVENTS.bstack1ll1l1111l_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack1ll1ll11_opy_(self, command_executor=bstack11l111_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲࠵࠷࠽࠮࠱࠰࠳࠲࠶ࡀ࠴࠵࠶࠷ࠦ઴"), *args, **kwargs):
  global bstack1l1l11ll_opy_
  global bstack1l1ll111l1_opy_
  bstack11l1l11111_opy_ = bstack11l1l111l_opy_(self, command_executor=command_executor, *args, **kwargs)
  if not bstack1l11lllll1_opy_.on():
    return bstack11l1l11111_opy_
  try:
    logger.debug(bstack11l111_opy_ (u"ࠫࡈࡵ࡭࡮ࡣࡱࡨࠥࡋࡸࡦࡥࡸࡸࡴࡸࠠࡸࡪࡨࡲࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤ࡫ࡧ࡬ࡴࡧࠣ࠱ࠥࢁࡽࠨવ").format(str(command_executor)))
    logger.debug(bstack11l111_opy_ (u"ࠬࡎࡵࡣࠢࡘࡖࡑࠦࡩࡴࠢ࠰ࠤࢀࢃࠧશ").format(str(command_executor._url)))
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    if isinstance(command_executor, RemoteConnection) and bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩષ") in command_executor._url:
      bstack11l11ll1l_opy_.bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠨસ"), True)
  except:
    pass
  if (isinstance(command_executor, str) and bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫહ") in command_executor):
    bstack11l11ll1l_opy_.bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪ઺"), True)
  threading.current_thread().bstackSessionDriver = self
  bstack1llll111_opy_ = getattr(threading.current_thread(), bstack11l111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡗࡩࡸࡺࡍࡦࡶࡤࠫ઻"), None)
  bstack1llll111l1_opy_ = {}
  if self.capabilities is not None:
    bstack1llll111l1_opy_[bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡴࡡ࡮ࡧ઼ࠪ")] = self.capabilities.get(bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪઽ"))
    bstack1llll111l1_opy_[bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨા")] = self.capabilities.get(bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨિ"))
    bstack1llll111l1_opy_[bstack11l111_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡠࡱࡳࡸ࡮ࡵ࡮ࡴࠩી")] = self.capabilities.get(bstack11l111_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧુ"))
  if CONFIG.get(bstack11l111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪૂ"), False) and bstack1lllll11l_opy_.bstack1111l11l1_opy_(bstack1llll111l1_opy_):
    threading.current_thread().a11yPlatform = True
  if bstack11l111_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫૃ") in bstack1ll1111l_opy_ or bstack11l111_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫૄ") in bstack1ll1111l_opy_:
    bstack11l11l1l_opy_.bstack11ll1lll11_opy_(self)
  if bstack11l111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ૅ") in bstack1ll1111l_opy_ and bstack1llll111_opy_ and bstack1llll111_opy_.get(bstack11l111_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ૆"), bstack11l111_opy_ (u"ࠨࠩે")) == bstack11l111_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪૈ"):
    bstack11l11l1l_opy_.bstack11ll1lll11_opy_(self)
  bstack1l1l11ll_opy_ = self.session_id
  with bstack11l11l11l_opy_:
    bstack1l1ll111l1_opy_.append(self)
  return bstack11l1l11111_opy_
def bstack11l111lll_opy_(args):
  return bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵࠫૉ") in str(args)
def bstack1l1ll1llll_opy_(self, driver_command, *args, **kwargs):
  global bstack1l11ll1ll1_opy_
  global bstack1l11llllll_opy_
  bstack1ll11lll1l_opy_ = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨ૊"), None) and bstack1l11lll1l1_opy_(
          threading.current_thread(), bstack11l111_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫો"), None)
  bstack111ll111l_opy_ = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"࠭ࡩࡴࡃࡳࡴࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭ૌ"), None) and bstack1l11lll1l1_opy_(
          threading.current_thread(), bstack11l111_opy_ (u"ࠧࡢࡲࡳࡅ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮્ࠩ"), None)
  bstack1lllllll1l_opy_ = getattr(self, bstack11l111_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨ૎"), None) != None and getattr(self, bstack11l111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩ૏"), None) == True
  if not bstack1l11llllll_opy_ and bstack11l111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪૐ") in CONFIG and CONFIG[bstack11l111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ૑")] == True and bstack1ll11l1lll_opy_.bstack111111l1_opy_(driver_command) and (bstack1lllllll1l_opy_ or bstack1ll11lll1l_opy_ or bstack111ll111l_opy_) and not bstack11l111lll_opy_(args):
    try:
      bstack1l11llllll_opy_ = True
      logger.debug(bstack11l111_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡧࡱࡵࠤࢀࢃࠧ૒").format(driver_command))
      logger.debug(perform_scan(self, driver_command=driver_command))
    except Exception as err:
      logger.debug(bstack11l111_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡳࡩࡷ࡬࡯ࡳ࡯ࠣࡷࡨࡧ࡮ࠡࡽࢀࠫ૓").format(str(err)))
    bstack1l11llllll_opy_ = False
  response = bstack1l11ll1ll1_opy_(self, driver_command, *args, **kwargs)
  if (bstack11l111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭૔") in str(bstack1ll1111l_opy_).lower() or bstack11l111_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨ૕") in str(bstack1ll1111l_opy_).lower()) and bstack1l11lllll1_opy_.on():
    try:
      if driver_command == bstack11l111_opy_ (u"ࠩࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹ࠭૖"):
        bstack11l11l1l_opy_.bstack11l11111ll_opy_({
            bstack11l111_opy_ (u"ࠪ࡭ࡲࡧࡧࡦࠩ૗"): response[bstack11l111_opy_ (u"ࠫࡻࡧ࡬ࡶࡧࠪ૘")],
            bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ૙"): bstack11l11l1l_opy_.current_test_uuid() if bstack11l11l1l_opy_.current_test_uuid() else bstack1l11lllll1_opy_.current_hook_uuid()
        })
    except:
      pass
  return response
@measure(event_name=EVENTS.bstack11lllll1_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack1111ll111_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None, *args, **kwargs):
  global CONFIG
  global bstack1l1l11ll_opy_
  global bstack1l11l111l1_opy_
  global bstack1ll1l111l1_opy_
  global bstack1ll1ll1ll_opy_
  global bstack1lll111l1l_opy_
  global bstack1ll1111l_opy_
  global bstack1l1l1l1l_opy_
  global bstack1l1ll111l1_opy_
  global bstack1l111l1l1l_opy_
  global bstack11l11l111_opy_
  if os.getenv(bstack11l111_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫ૚")) is not None and bstack1lllll11l_opy_.bstack111lllll11_opy_(CONFIG) is None:
    CONFIG[bstack11l111_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ૛")] = True
  CONFIG[bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪ૜")] = str(bstack1ll1111l_opy_) + str(__version__)
  bstack11ll11111_opy_ = os.environ[bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ૝")]
  bstack11l11lll1l_opy_ = bstack11ll11lll_opy_.bstack11ll1l111_opy_(CONFIG, bstack1ll1111l_opy_)
  CONFIG[bstack11l111_opy_ (u"ࠪࡸࡪࡹࡴࡩࡷࡥࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭૞")] = bstack11ll11111_opy_
  CONFIG[bstack11l111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡓࡶࡴࡪࡵࡤࡶࡐࡥࡵ࠭૟")] = bstack11l11lll1l_opy_
  if CONFIG.get(bstack11l111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬૠ"),bstack11l111_opy_ (u"࠭ࠧૡ")) and bstack11l111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ૢ") in bstack1ll1111l_opy_:
    CONFIG[bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨૣ")].pop(bstack11l111_opy_ (u"ࠩ࡬ࡲࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧ૤"), None)
    CONFIG[bstack11l111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ૥")].pop(bstack11l111_opy_ (u"ࠫࡪࡾࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩ૦"), None)
  command_executor = bstack1ll1ll1l1_opy_()
  logger.debug(bstack1l11111lll_opy_.format(command_executor))
  proxy = bstack1lll1l1lll_opy_(CONFIG, proxy)
  bstack1l111ll1ll_opy_ = 0 if bstack1l11l111l1_opy_ < 0 else bstack1l11l111l1_opy_
  try:
    if bstack1ll1ll1ll_opy_ is True:
      bstack1l111ll1ll_opy_ = int(multiprocessing.current_process().name)
    elif bstack1lll111l1l_opy_ is True:
      bstack1l111ll1ll_opy_ = int(threading.current_thread().name)
  except:
    bstack1l111ll1ll_opy_ = 0
  bstack11ll1llll1_opy_ = bstack1ll1111ll1_opy_(CONFIG, bstack1l111ll1ll_opy_)
  logger.debug(bstack1ll11l11_opy_.format(str(bstack11ll1llll1_opy_)))
  if bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ૧") in CONFIG and bstack111ll1lll_opy_(CONFIG[bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ૨")]):
    bstack1ll111llll_opy_(bstack11ll1llll1_opy_)
  if bstack1lllll11l_opy_.bstack11l1l11l11_opy_(CONFIG, bstack1l111ll1ll_opy_) and bstack1lllll11l_opy_.bstack11l1llll11_opy_(bstack11ll1llll1_opy_, options, desired_capabilities, CONFIG):
    threading.current_thread().a11yPlatform = True
    if (cli.accessibility is None or not cli.accessibility.is_enabled()):
      bstack1lllll11l_opy_.set_capabilities(bstack11ll1llll1_opy_, CONFIG)
  if desired_capabilities:
    bstack11lllllll1_opy_ = bstack1l1lllll11_opy_(desired_capabilities)
    bstack11lllllll1_opy_[bstack11l111_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧ૩")] = bstack11l1lll1ll_opy_(CONFIG)
    bstack11l1ll1l_opy_ = bstack1ll1111ll1_opy_(bstack11lllllll1_opy_)
    if bstack11l1ll1l_opy_:
      bstack11ll1llll1_opy_ = update(bstack11l1ll1l_opy_, bstack11ll1llll1_opy_)
    desired_capabilities = None
  if options:
    bstack1lll1l11_opy_(options, bstack11ll1llll1_opy_)
  if not options:
    options = bstack1l1l1l1l1l_opy_(bstack11ll1llll1_opy_)
  bstack11l11l111_opy_ = CONFIG.get(bstack11l111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ૪"))[bstack1l111ll1ll_opy_]
  if proxy and bstack1lllll1l1_opy_() >= version.parse(bstack11l111_opy_ (u"ࠩ࠷࠲࠶࠶࠮࠱ࠩ૫")):
    options.proxy(proxy)
  if options and bstack1lllll1l1_opy_() >= version.parse(bstack11l111_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩ૬")):
    desired_capabilities = None
  if (
          not options and not desired_capabilities
  ) or (
          bstack1lllll1l1_opy_() < version.parse(bstack11l111_opy_ (u"ࠫ࠸࠴࠸࠯࠲ࠪ૭")) and not desired_capabilities
  ):
    desired_capabilities = {}
    desired_capabilities.update(bstack11ll1llll1_opy_)
  logger.info(bstack1llllll1l1_opy_)
  bstack1llllll1l_opy_.end(EVENTS.bstack1ll1111lll_opy_.value, EVENTS.bstack1ll1111lll_opy_.value + bstack11l111_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧ૮"), EVENTS.bstack1ll1111lll_opy_.value + bstack11l111_opy_ (u"ࠨ࠺ࡦࡰࡧࠦ૯"), status=True, failure=None, test_name=bstack1ll1l111l1_opy_)
  if bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡲࡵࡳ࡫࡯࡬ࡦࠩ૰") in kwargs:
    del kwargs[bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡳࡶࡴ࡬ࡩ࡭ࡧࠪ૱")]
  try:
    if bstack1lllll1l1_opy_() >= version.parse(bstack11l111_opy_ (u"ࠩ࠷࠲࠶࠶࠮࠱ࠩ૲")):
      bstack1l1l1l1l_opy_(self, command_executor=command_executor,
                options=options, keep_alive=keep_alive, file_detector=file_detector, *args, **kwargs)
    elif bstack1lllll1l1_opy_() >= version.parse(bstack11l111_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩ૳")):
      bstack1l1l1l1l_opy_(self, command_executor=command_executor,
                desired_capabilities=desired_capabilities, options=options,
                browser_profile=browser_profile, proxy=proxy,
                keep_alive=keep_alive, file_detector=file_detector)
    elif bstack1lllll1l1_opy_() >= version.parse(bstack11l111_opy_ (u"ࠫ࠷࠴࠵࠴࠰࠳ࠫ૴")):
      bstack1l1l1l1l_opy_(self, command_executor=command_executor,
                desired_capabilities=desired_capabilities,
                browser_profile=browser_profile, proxy=proxy,
                keep_alive=keep_alive, file_detector=file_detector)
    else:
      bstack1l1l1l1l_opy_(self, command_executor=command_executor,
                desired_capabilities=desired_capabilities,
                browser_profile=browser_profile, proxy=proxy,
                keep_alive=keep_alive)
  except Exception as bstack11llllll1l_opy_:
    logger.error(bstack11l1llllll_opy_.format(bstack11l111_opy_ (u"ࠬࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠫ૵"), str(bstack11llllll1l_opy_)))
    raise bstack11llllll1l_opy_
  if bstack1lllll11l_opy_.bstack11l1l11l11_opy_(CONFIG, bstack1l111ll1ll_opy_) and bstack1lllll11l_opy_.bstack11l1llll11_opy_(self.caps, options, desired_capabilities):
    if CONFIG[bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡕࡸ࡯ࡥࡷࡦࡸࡒࡧࡰࠨ૶")][bstack11l111_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭૷")] == True:
      threading.current_thread().appA11yPlatform = True
      if cli.accessibility is None or not cli.accessibility.is_enabled():
        bstack1lllll11l_opy_.set_capabilities(bstack11ll1llll1_opy_, CONFIG)
  try:
    bstack1llll1111l_opy_ = bstack11l111_opy_ (u"ࠨࠩ૸")
    if bstack1lllll1l1_opy_() >= version.parse(bstack11l111_opy_ (u"ࠩ࠷࠲࠵࠴࠰ࡣ࠳ࠪૹ")):
      if self.caps is not None:
        bstack1llll1111l_opy_ = self.caps.get(bstack11l111_opy_ (u"ࠥࡳࡵࡺࡩ࡮ࡣ࡯ࡌࡺࡨࡕࡳ࡮ࠥૺ"))
    else:
      if self.capabilities is not None:
        bstack1llll1111l_opy_ = self.capabilities.get(bstack11l111_opy_ (u"ࠦࡴࡶࡴࡪ࡯ࡤࡰࡍࡻࡢࡖࡴ࡯ࠦૻ"))
    if bstack1llll1111l_opy_:
      bstack1lll1ll1l_opy_(bstack1llll1111l_opy_)
      if bstack1lllll1l1_opy_() <= version.parse(bstack11l111_opy_ (u"ࠬ࠹࠮࠲࠵࠱࠴ࠬૼ")):
        self.command_executor._url = bstack11l111_opy_ (u"ࠨࡨࡵࡶࡳ࠾࠴࠵ࠢ૽") + bstack1l1l11lll1_opy_ + bstack11l111_opy_ (u"ࠢ࠻࠺࠳࠳ࡼࡪ࠯ࡩࡷࡥࠦ૾")
      else:
        self.command_executor._url = bstack11l111_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࠥ૿") + bstack1llll1111l_opy_ + bstack11l111_opy_ (u"ࠤ࠲ࡻࡩ࠵ࡨࡶࡤࠥ଀")
      logger.debug(bstack1lllllll11_opy_.format(bstack1llll1111l_opy_))
    else:
      logger.debug(bstack1ll1l1lll1_opy_.format(bstack11l111_opy_ (u"ࠥࡓࡵࡺࡩ࡮ࡣ࡯ࠤࡍࡻࡢࠡࡰࡲࡸࠥ࡬࡯ࡶࡰࡧࠦଁ")))
  except Exception as e:
    logger.debug(bstack1ll1l1lll1_opy_.format(e))
  if bstack11l111_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪଂ") in bstack1ll1111l_opy_:
    bstack11llll11l1_opy_(bstack1l11l111l1_opy_, bstack1l111l1l1l_opy_)
  bstack1l1l11ll_opy_ = self.session_id
  if bstack11l111_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬଃ") in bstack1ll1111l_opy_ or bstack11l111_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭଄") in bstack1ll1111l_opy_ or bstack11l111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ଅ") in bstack1ll1111l_opy_:
    threading.current_thread().bstackSessionId = self.session_id
    threading.current_thread().bstackSessionDriver = self
    threading.current_thread().bstackTestErrorMessages = []
  bstack1llll111_opy_ = getattr(threading.current_thread(), bstack11l111_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡕࡧࡶࡸࡒ࡫ࡴࡢࠩଆ"), None)
  if bstack11l111_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩଇ") in bstack1ll1111l_opy_ or bstack11l111_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩଈ") in bstack1ll1111l_opy_:
    bstack11l11l1l_opy_.bstack11ll1lll11_opy_(self)
  if bstack11l111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫଉ") in bstack1ll1111l_opy_ and bstack1llll111_opy_ and bstack1llll111_opy_.get(bstack11l111_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬଊ"), bstack11l111_opy_ (u"࠭ࠧଋ")) == bstack11l111_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨଌ"):
    bstack11l11l1l_opy_.bstack11ll1lll11_opy_(self)
  with bstack11l11l11l_opy_:
    bstack1l1ll111l1_opy_.append(self)
  if bstack11l111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ଍") in CONFIG and bstack11l111_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ଎") in CONFIG[bstack11l111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଏ")][bstack1l111ll1ll_opy_]:
    bstack1ll1l111l1_opy_ = CONFIG[bstack11l111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧଐ")][bstack1l111ll1ll_opy_][bstack11l111_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ଑")]
  logger.debug(bstack1l11ll1l1l_opy_.format(bstack1l1l11ll_opy_))
try:
  try:
    import Browser
    from subprocess import Popen
    from browserstack_sdk.__init__ import bstack11l1l11ll1_opy_
    def bstack1l1l1l111l_opy_(self, args, bufsize=-1, executable=None,
              stdin=None, stdout=None, stderr=None,
              preexec_fn=None, close_fds=True,
              shell=False, cwd=None, env=None, universal_newlines=None,
              startupinfo=None, creationflags=0,
              restore_signals=True, start_new_session=False,
              pass_fds=(), *, user=None, group=None, extra_groups=None,
              encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
      global CONFIG
      global bstack1l11lll1ll_opy_
      if(bstack11l111_opy_ (u"ࠨࡩ࡯ࡦࡨࡼ࠳ࡰࡳࠣ଒") in args[1]):
        with open(os.path.join(os.path.expanduser(bstack11l111_opy_ (u"ࠧࡿࠩଓ")), bstack11l111_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨଔ"), bstack11l111_opy_ (u"ࠩ࠱ࡷࡪࡹࡳࡪࡱࡱ࡭ࡩࡹ࠮ࡵࡺࡷࠫକ")), bstack11l111_opy_ (u"ࠪࡻࠬଖ")) as fp:
          fp.write(bstack11l111_opy_ (u"ࠦࠧଗ"))
        if(not os.path.exists(os.path.join(os.path.dirname(args[1]), bstack11l111_opy_ (u"ࠧ࡯࡮ࡥࡧࡻࡣࡧࡹࡴࡢࡥ࡮࠲࡯ࡹࠢଘ")))):
          with open(args[1], bstack11l111_opy_ (u"࠭ࡲࠨଙ")) as f:
            lines = f.readlines()
            index = next((i for i, line in enumerate(lines) if bstack11l111_opy_ (u"ࠧࡢࡵࡼࡲࡨࠦࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠡࡡࡱࡩࡼࡖࡡࡨࡧࠫࡧࡴࡴࡴࡦࡺࡷ࠰ࠥࡶࡡࡨࡧࠣࡁࠥࡼ࡯ࡪࡦࠣ࠴࠮࠭ଚ") in line), None)
            if index is not None:
                lines.insert(index+2, bstack1111l1111_opy_)
            if bstack11l111_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬଛ") in CONFIG and str(CONFIG[bstack11l111_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ଜ")]).lower() != bstack11l111_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩଝ"):
                bstack1l1l1l1ll_opy_ = bstack11l1l11ll1_opy_()
                bstack111lll111_opy_ = bstack11l111_opy_ (u"ࠫࠬ࠭ࠊ࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱ࠍࡧࡴࡴࡳࡵࠢࡥࡷࡹࡧࡣ࡬ࡡࡳࡥࡹ࡮ࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࡜ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮࡭ࡧࡱ࡫ࡹ࡮ࠠ࠮ࠢ࠶ࡡࡀࠐࡣࡰࡰࡶࡸࠥࡨࡳࡵࡣࡦ࡯ࡤࡩࡡࡱࡵࠣࡁࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࡟ࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࠱ࡰࡪࡴࡧࡵࡪࠣ࠱ࠥ࠷࡝࠼ࠌࡦࡳࡳࡹࡴࠡࡲࡢ࡭ࡳࡪࡥࡹࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࡞ࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠷ࡣ࠻ࠋࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࠯ࡵ࡯࡭ࡨ࡫ࠨ࠱࠮ࠣࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠸࠯࠻ࠋࡥࡲࡲࡸࡺࠠࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯ࠥࡃࠠࡳࡧࡴࡹ࡮ࡸࡥࠩࠤࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨࠩ࠼ࠌ࡬ࡱࡵࡵࡲࡵࡡࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠺࡟ࡣࡵࡷࡥࡨࡱ࠮ࡤࡪࡵࡳࡲ࡯ࡵ࡮࠰࡯ࡥࡺࡴࡣࡩࠢࡀࠤࡦࡹࡹ࡯ࡥࠣࠬࡱࡧࡵ࡯ࡥ࡫ࡓࡵࡺࡩࡰࡰࡶ࠭ࠥࡃ࠾ࠡࡽࡾࠎࠥࠦ࡬ࡦࡶࠣࡧࡦࡶࡳ࠼ࠌࠣࠤࡹࡸࡹࠡࡽࡾࠎࠥࠦࠠࠡࡥࡤࡴࡸࠦ࠽ࠡࡌࡖࡓࡓ࠴ࡰࡢࡴࡶࡩ࠭ࡨࡳࡵࡣࡦ࡯ࡤࡩࡡࡱࡵࠬ࠿ࠏࠦࠠࡾࡿࠣࡧࡦࡺࡣࡩࠢࠫࡩࡽ࠯ࠠࡼࡽࠍࠤࠥࠦࠠࡤࡱࡱࡷࡴࡲࡥ࠯ࡧࡵࡶࡴࡸࠨࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵࡧࡲࡴࡧࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴ࠼ࠥ࠰ࠥ࡫ࡸࠪ࠽ࠍࠤࠥࢃࡽࠋࠢࠣࡶࡪࡺࡵࡳࡰࠣࡥࡼࡧࡩࡵࠢ࡬ࡱࡵࡵࡲࡵࡡࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠺࡟ࡣࡵࡷࡥࡨࡱ࠮ࡤࡪࡵࡳࡲ࡯ࡵ࡮࠰ࡦࡳࡳࡴࡥࡤࡶࠫࡿࢀࠐࠠࠡࠢࠣࡻࡸࡋ࡮ࡥࡲࡲ࡭ࡳࡺ࠺ࠡࠩࡾࡧࡩࡶࡕࡳ࡮ࢀࠫࠥ࠱ࠠࡦࡰࡦࡳࡩ࡫ࡕࡓࡋࡆࡳࡲࡶ࡯࡯ࡧࡱࡸ࠭ࡐࡓࡐࡐ࠱ࡷࡹࡸࡩ࡯ࡩ࡬ࡪࡾ࠮ࡣࡢࡲࡶ࠭࠮࠲ࠊࠡࠢࠣࠤ࠳࠴࠮࡭ࡣࡸࡲࡨ࡮ࡏࡱࡶ࡬ࡳࡳࡹࠊࠡࠢࢀࢁ࠮ࡁࠊࡾࡿ࠾ࠎ࠴࠰ࠠ࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࠤ࠯࠵ࠊࠨࠩࠪଞ").format(bstack1l1l1l1ll_opy_=bstack1l1l1l1ll_opy_)
            lines.insert(1, bstack111lll111_opy_)
            f.seek(0)
            with open(os.path.join(os.path.dirname(args[1]), bstack11l111_opy_ (u"ࠧ࡯࡮ࡥࡧࡻࡣࡧࡹࡴࡢࡥ࡮࠲࡯ࡹࠢଟ")), bstack11l111_opy_ (u"࠭ࡷࠨଠ")) as bstack1llll1ll_opy_:
              bstack1llll1ll_opy_.writelines(lines)
        CONFIG[bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩଡ")] = str(bstack1ll1111l_opy_) + str(__version__)
        bstack11ll11111_opy_ = os.environ[bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ଢ")]
        bstack11l11lll1l_opy_ = bstack11ll11lll_opy_.bstack11ll1l111_opy_(CONFIG, bstack1ll1111l_opy_)
        CONFIG[bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺࡨࡶࡤࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬଣ")] = bstack11ll11111_opy_
        CONFIG[bstack11l111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡒࡵࡳࡩࡻࡣࡵࡏࡤࡴࠬତ")] = bstack11l11lll1l_opy_
        bstack1l111ll1ll_opy_ = 0 if bstack1l11l111l1_opy_ < 0 else bstack1l11l111l1_opy_
        try:
          if bstack1ll1ll1ll_opy_ is True:
            bstack1l111ll1ll_opy_ = int(multiprocessing.current_process().name)
          elif bstack1lll111l1l_opy_ is True:
            bstack1l111ll1ll_opy_ = int(threading.current_thread().name)
        except:
          bstack1l111ll1ll_opy_ = 0
        CONFIG[bstack11l111_opy_ (u"ࠦࡺࡹࡥࡘ࠵ࡆࠦଥ")] = False
        CONFIG[bstack11l111_opy_ (u"ࠧ࡯ࡳࡑ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦଦ")] = True
        bstack11ll1llll1_opy_ = bstack1ll1111ll1_opy_(CONFIG, bstack1l111ll1ll_opy_)
        logger.debug(bstack1ll11l11_opy_.format(str(bstack11ll1llll1_opy_)))
        if CONFIG.get(bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪଧ")):
          bstack1ll111llll_opy_(bstack11ll1llll1_opy_)
        if bstack11l111_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪନ") in CONFIG and bstack11l111_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭଩") in CONFIG[bstack11l111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬପ")][bstack1l111ll1ll_opy_]:
          bstack1ll1l111l1_opy_ = CONFIG[bstack11l111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଫ")][bstack1l111ll1ll_opy_][bstack11l111_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩବ")]
        args.append(os.path.join(os.path.expanduser(bstack11l111_opy_ (u"ࠬࢄࠧଭ")), bstack11l111_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ମ"), bstack11l111_opy_ (u"ࠧ࠯ࡵࡨࡷࡸ࡯࡯࡯࡫ࡧࡷ࠳ࡺࡸࡵࠩଯ")))
        args.append(str(threading.get_ident()))
        args.append(json.dumps(bstack11ll1llll1_opy_))
        args[1] = os.path.join(os.path.dirname(args[1]), bstack11l111_opy_ (u"ࠣ࡫ࡱࡨࡪࡾ࡟ࡣࡵࡷࡥࡨࡱ࠮࡫ࡵࠥର"))
      bstack1l11lll1ll_opy_ = True
      return bstack1111l111_opy_(self, args, bufsize=bufsize, executable=executable,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    preexec_fn=preexec_fn, close_fds=close_fds,
                    shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines,
                    startupinfo=startupinfo, creationflags=creationflags,
                    restore_signals=restore_signals, start_new_session=start_new_session,
                    pass_fds=pass_fds, user=user, group=group, extra_groups=extra_groups,
                    encoding=encoding, errors=errors, text=text, umask=umask, pipesize=pipesize)
  except Exception as e:
    pass
  import playwright._impl._api_structures
  import playwright._impl._helper
  def bstack11lll1l11l_opy_(self,
        executablePath = None,
        channel = None,
        args = None,
        ignoreDefaultArgs = None,
        handleSIGINT = None,
        handleSIGTERM = None,
        handleSIGHUP = None,
        timeout = None,
        env = None,
        headless = None,
        devtools = None,
        proxy = None,
        downloadsPath = None,
        slowMo = None,
        tracesDir = None,
        chromiumSandbox = None,
        firefoxUserPrefs = None
        ):
    global CONFIG
    global bstack1l11l111l1_opy_
    global bstack1ll1l111l1_opy_
    global bstack1ll1ll1ll_opy_
    global bstack1lll111l1l_opy_
    global bstack1ll1111l_opy_
    CONFIG[bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫ଱")] = str(bstack1ll1111l_opy_) + str(__version__)
    bstack11ll11111_opy_ = os.environ[bstack11l111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨଲ")]
    bstack11l11lll1l_opy_ = bstack11ll11lll_opy_.bstack11ll1l111_opy_(CONFIG, bstack1ll1111l_opy_)
    CONFIG[bstack11l111_opy_ (u"ࠫࡹ࡫ࡳࡵࡪࡸࡦࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧଳ")] = bstack11ll11111_opy_
    CONFIG[bstack11l111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡔࡷࡵࡤࡶࡥࡷࡑࡦࡶࠧ଴")] = bstack11l11lll1l_opy_
    bstack1l111ll1ll_opy_ = 0 if bstack1l11l111l1_opy_ < 0 else bstack1l11l111l1_opy_
    try:
      if bstack1ll1ll1ll_opy_ is True:
        bstack1l111ll1ll_opy_ = int(multiprocessing.current_process().name)
      elif bstack1lll111l1l_opy_ is True:
        bstack1l111ll1ll_opy_ = int(threading.current_thread().name)
    except:
      bstack1l111ll1ll_opy_ = 0
    CONFIG[bstack11l111_opy_ (u"ࠨࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠧଵ")] = True
    bstack11ll1llll1_opy_ = bstack1ll1111ll1_opy_(CONFIG, bstack1l111ll1ll_opy_)
    logger.debug(bstack1ll11l11_opy_.format(str(bstack11ll1llll1_opy_)))
    if CONFIG.get(bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫଶ")):
      bstack1ll111llll_opy_(bstack11ll1llll1_opy_)
    if bstack11l111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫଷ") in CONFIG and bstack11l111_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧସ") in CONFIG[bstack11l111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ହ")][bstack1l111ll1ll_opy_]:
      bstack1ll1l111l1_opy_ = CONFIG[bstack11l111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ଺")][bstack1l111ll1ll_opy_][bstack11l111_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ଻")]
    import urllib
    import json
    if bstack11l111_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧ଼ࠪ") in CONFIG and str(CONFIG[bstack11l111_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫଽ")]).lower() != bstack11l111_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧା"):
        bstack1lllll1l11_opy_ = bstack11l1l11ll1_opy_()
        bstack1l1l1l1ll_opy_ = bstack1lllll1l11_opy_ + urllib.parse.quote(json.dumps(bstack11ll1llll1_opy_))
    else:
        bstack1l1l1l1ll_opy_ = bstack11l111_opy_ (u"ࠩࡺࡷࡸࡀ࠯࠰ࡥࡧࡴ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࡄࡩࡡࡱࡵࡀࠫି") + urllib.parse.quote(json.dumps(bstack11ll1llll1_opy_))
    browser = self.connect(bstack1l1l1l1ll_opy_)
    return browser
except Exception as e:
    pass
def bstack1l11l11lll_opy_():
    global bstack1l11lll1ll_opy_
    global bstack1ll1111l_opy_
    global CONFIG
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack1ll111ll1l_opy_
        global bstack11l11ll1l_opy_
        if not bstack111111l11_opy_:
          global bstack111llll11_opy_
          if not bstack111llll11_opy_:
            from bstack_utils.helper import bstack1l111l1l_opy_, bstack11ll111ll1_opy_, bstack1ll111l11_opy_
            bstack111llll11_opy_ = bstack1l111l1l_opy_()
            bstack11ll111ll1_opy_(bstack1ll1111l_opy_)
            bstack11l11lll1l_opy_ = bstack11ll11lll_opy_.bstack11ll1l111_opy_(CONFIG, bstack1ll1111l_opy_)
            bstack11l11ll1l_opy_.bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"ࠥࡔࡑࡇ࡙ࡘࡔࡌࡋࡍ࡚࡟ࡑࡔࡒࡈ࡚ࡉࡔࡠࡏࡄࡔࠧୀ"), bstack11l11lll1l_opy_)
          BrowserType.connect = bstack1ll111ll1l_opy_
          return
        BrowserType.launch = bstack11lll1l11l_opy_
        bstack1l11lll1ll_opy_ = True
    except Exception as e:
        pass
    try:
      import Browser
      from subprocess import Popen
      Popen.__init__ = bstack1l1l1l111l_opy_
      bstack1l11lll1ll_opy_ = True
    except Exception as e:
      pass
def bstack1l1l11l11_opy_(context, bstack1ll111l1l_opy_):
  try:
    context.page.evaluate(bstack11l111_opy_ (u"ࠦࡤࠦ࠽࠿ࠢࡾࢁࠧୁ"), bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠩୂ")+ json.dumps(bstack1ll111l1l_opy_) + bstack11l111_opy_ (u"ࠨࡽࡾࠤୃ"))
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠢࡦࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠢࡾࢁ࠿ࠦࡻࡾࠤୄ").format(str(e), traceback.format_exc()))
def bstack1lll1111_opy_(context, message, level):
  try:
    context.page.evaluate(bstack11l111_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤ୅"), bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡥࡣࡷࡥࠧࡀࠧ୆") + json.dumps(message) + bstack11l111_opy_ (u"ࠪ࠰ࠧࡲࡥࡷࡧ࡯ࠦ࠿࠭େ") + json.dumps(level) + bstack11l111_opy_ (u"ࠫࢂࢃࠧୈ"))
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠧ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠡࡣࡱࡲࡴࡺࡡࡵ࡫ࡲࡲࠥࢁࡽ࠻ࠢࡾࢁࠧ୉").format(str(e), traceback.format_exc()))
@measure(event_name=EVENTS.bstack11111l111_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack1l1ll111_opy_(self, url):
  global bstack1l1111llll_opy_
  try:
    bstack1llll11ll1_opy_(url)
  except Exception as err:
    logger.debug(bstack11ll1l1lll_opy_.format(str(err)))
  try:
    bstack1l1111llll_opy_(self, url)
  except Exception as e:
    try:
      bstack111llll1l1_opy_ = str(e)
      if any(err_msg in bstack111llll1l1_opy_ for err_msg in bstack1l1lllll1l_opy_):
        bstack1llll11ll1_opy_(url, True)
    except Exception as err:
      logger.debug(bstack11ll1l1lll_opy_.format(str(err)))
    raise e
def bstack1l1llll11l_opy_(self):
  global bstack11llllll_opy_
  bstack11llllll_opy_ = self
  return
def bstack11111l1ll_opy_(self):
  global bstack1lll1l1111_opy_
  bstack1lll1l1111_opy_ = self
  return
def bstack11llll11l_opy_(test_name, bstack1ll1lll1_opy_):
  global CONFIG
  if percy.bstack1l1l1ll111_opy_() == bstack11l111_opy_ (u"ࠨࡴࡳࡷࡨࠦ୊"):
    bstack11ll1111_opy_ = os.path.relpath(bstack1ll1lll1_opy_, start=os.getcwd())
    suite_name, _ = os.path.splitext(bstack11ll1111_opy_)
    bstack1ll111l111_opy_ = suite_name + bstack11l111_opy_ (u"ࠢ࠮ࠤୋ") + test_name
    threading.current_thread().percySessionName = bstack1ll111l111_opy_
def bstack111l1ll11_opy_(self, test, *args, **kwargs):
  global bstack111l1ll1l_opy_
  test_name = None
  bstack1ll1lll1_opy_ = None
  if test:
    test_name = str(test.name)
    bstack1ll1lll1_opy_ = str(test.source)
  bstack11llll11l_opy_(test_name, bstack1ll1lll1_opy_)
  bstack111l1ll1l_opy_(self, test, *args, **kwargs)
@measure(event_name=EVENTS.bstack11lll1ll11_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack11llll111l_opy_(driver, bstack1ll111l111_opy_):
  if not bstack1l11l111l_opy_ and bstack1ll111l111_opy_:
      bstack1l111111l1_opy_ = {
          bstack11l111_opy_ (u"ࠨࡣࡦࡸ࡮ࡵ࡮ࠨୌ"): bstack11l111_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧ୍ࠪ"),
          bstack11l111_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭୎"): {
              bstack11l111_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ୏"): bstack1ll111l111_opy_
          }
      }
      bstack11ll11ll1_opy_ = bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪ୐").format(json.dumps(bstack1l111111l1_opy_))
      driver.execute_script(bstack11ll11ll1_opy_)
  if bstack1l1111ll11_opy_:
      bstack1l1l1l1ll1_opy_ = {
          bstack11l111_opy_ (u"࠭ࡡࡤࡶ࡬ࡳࡳ࠭୑"): bstack11l111_opy_ (u"ࠧࡢࡰࡱࡳࡹࡧࡴࡦࠩ୒"),
          bstack11l111_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫ୓"): {
              bstack11l111_opy_ (u"ࠩࡧࡥࡹࡧࠧ୔"): bstack1ll111l111_opy_ + bstack11l111_opy_ (u"ࠪࠤࡵࡧࡳࡴࡧࡧࠥࠬ୕"),
              bstack11l111_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪୖ"): bstack11l111_opy_ (u"ࠬ࡯࡮ࡧࡱࠪୗ")
          }
      }
      if bstack1l1111ll11_opy_.status == bstack11l111_opy_ (u"࠭ࡐࡂࡕࡖࠫ୘"):
          bstack1ll1111111_opy_ = bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠬ୙").format(json.dumps(bstack1l1l1l1ll1_opy_))
          driver.execute_script(bstack1ll1111111_opy_)
          bstack1ll11l1ll1_opy_(driver, bstack11l111_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨ୚"))
      elif bstack1l1111ll11_opy_.status == bstack11l111_opy_ (u"ࠩࡉࡅࡎࡒࠧ୛"):
          reason = bstack11l111_opy_ (u"ࠥࠦଡ଼")
          bstack11llll1l1_opy_ = bstack1ll111l111_opy_ + bstack11l111_opy_ (u"ࠫࠥ࡬ࡡࡪ࡮ࡨࡨࠬଢ଼")
          if bstack1l1111ll11_opy_.message:
              reason = str(bstack1l1111ll11_opy_.message)
              bstack11llll1l1_opy_ = bstack11llll1l1_opy_ + bstack11l111_opy_ (u"ࠬࠦࡷࡪࡶ࡫ࠤࡪࡸࡲࡰࡴ࠽ࠤࠬ୞") + reason
          bstack1l1l1l1ll1_opy_[bstack11l111_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩୟ")] = {
              bstack11l111_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ୠ"): bstack11l111_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧୡ"),
              bstack11l111_opy_ (u"ࠩࡧࡥࡹࡧࠧୢ"): bstack11llll1l1_opy_
          }
          bstack1ll1111111_opy_ = bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠨୣ").format(json.dumps(bstack1l1l1l1ll1_opy_))
          driver.execute_script(bstack1ll1111111_opy_)
          bstack1ll11l1ll1_opy_(driver, bstack11l111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ୤"), reason)
          bstack11ll11ll1l_opy_(reason, str(bstack1l1111ll11_opy_), str(bstack1l11l111l1_opy_), logger)
@measure(event_name=EVENTS.bstack1l111lll11_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack1l111l1lll_opy_(driver, test):
  if percy.bstack1l1l1ll111_opy_() == bstack11l111_opy_ (u"ࠧࡺࡲࡶࡧࠥ୥") and percy.bstack1llll1llll_opy_() == bstack11l111_opy_ (u"ࠨࡴࡦࡵࡷࡧࡦࡹࡥࠣ୦"):
      bstack1111111l_opy_ = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠧࡱࡧࡵࡧࡾ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ୧"), None)
      bstack1111l11ll_opy_(driver, bstack1111111l_opy_, test)
  if (bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠨ࡫ࡶࡅ࠶࠷ࡹࡕࡧࡶࡸࠬ୨"), None) and
      bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ୩"), None)) or (
      bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠪ࡭ࡸࡇࡰࡱࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ୪"), None) and
      bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠫࡦࡶࡰࡂ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭୫"), None)):
      logger.info(bstack11l111_opy_ (u"ࠧࡇࡵࡵࡱࡰࡥࡹ࡫ࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣࡩࡽ࡫ࡣࡶࡶ࡬ࡳࡳࠦࡨࡢࡵࠣࡩࡳࡪࡥࡥ࠰ࠣࡔࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡧࡱࡵࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡹ࡫ࡳࡵ࡫ࡱ࡫ࠥ࡯ࡳࠡࡷࡱࡨࡪࡸࡷࡢࡻ࠱ࠤࠧ୬"))
      bstack1lllll11l_opy_.bstack1l1ll11ll1_opy_(driver, name=test.name, path=test.source)
def bstack11l1lllll_opy_(test, bstack1ll111l111_opy_):
    try:
      bstack11l1l11l1l_opy_ = datetime.datetime.now()
      data = {}
      if test:
        data[bstack11l111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ୭")] = bstack1ll111l111_opy_
      if bstack1l1111ll11_opy_:
        if bstack1l1111ll11_opy_.status == bstack11l111_opy_ (u"ࠧࡑࡃࡖࡗࠬ୮"):
          data[bstack11l111_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ୯")] = bstack11l111_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩ୰")
        elif bstack1l1111ll11_opy_.status == bstack11l111_opy_ (u"ࠪࡊࡆࡏࡌࠨୱ"):
          data[bstack11l111_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ୲")] = bstack11l111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ୳")
          if bstack1l1111ll11_opy_.message:
            data[bstack11l111_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭୴")] = str(bstack1l1111ll11_opy_.message)
      user = CONFIG[bstack11l111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ୵")]
      key = CONFIG[bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ୶")]
      host = bstack111111ll_opy_(cli.config, [bstack11l111_opy_ (u"ࠤࡤࡴ࡮ࡹࠢ୷"), bstack11l111_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷࡩࠧ୸"), bstack11l111_opy_ (u"ࠦࡦࡶࡩࠣ୹")], bstack11l111_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡡࡱ࡫࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲࠨ୺"))
      url = bstack11l111_opy_ (u"࠭ࡻࡾ࠱ࡤࡹࡹࡵ࡭ࡢࡶࡨ࠳ࡸ࡫ࡳࡴ࡫ࡲࡲࡸ࠵ࡻࡾ࠰࡭ࡷࡴࡴࠧ୻").format(host, bstack1l1l11ll_opy_)
      headers = {
        bstack11l111_opy_ (u"ࠧࡄࡱࡱࡸࡪࡴࡴ࠮ࡶࡼࡴࡪ࠭୼"): bstack11l111_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠫ୽"),
      }
      if bool(data):
        requests.put(url, json=data, headers=headers, auth=(user, key))
        cli.bstack1l11lllll_opy_(bstack11l111_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺ࡶࡲࡧࡥࡹ࡫࡟ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡳࡵࡣࡷࡹࡸࠨ୾"), datetime.datetime.now() - bstack11l1l11l1l_opy_)
    except Exception as e:
      logger.error(bstack1ll111ll_opy_.format(str(e)))
def bstack1l1111l1ll_opy_(test, bstack1ll111l111_opy_):
  global CONFIG
  global bstack1lll1l1111_opy_
  global bstack11llllll_opy_
  global bstack1l1l11ll_opy_
  global bstack1l1111ll11_opy_
  global bstack1ll1l111l1_opy_
  global bstack1ll11lll_opy_
  global bstack1l11lll111_opy_
  global bstack11ll11ll11_opy_
  global bstack1111ll1l1_opy_
  global bstack1l1ll111l1_opy_
  global bstack11l11l111_opy_
  global bstack1l11ll11ll_opy_
  try:
    if not bstack1l1l11ll_opy_:
      with bstack1l11ll11ll_opy_:
        bstack1l1lll1ll_opy_ = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"ࠪࢂࠬ୿")), bstack11l111_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ஀"), bstack11l111_opy_ (u"ࠬ࠴ࡳࡦࡵࡶ࡭ࡴࡴࡩࡥࡵ࠱ࡸࡽࡺࠧ஁"))
        if os.path.exists(bstack1l1lll1ll_opy_):
          with open(bstack1l1lll1ll_opy_, bstack11l111_opy_ (u"࠭ࡲࠨஂ")) as f:
            content = f.read().strip()
            if content:
              bstack11l1llll_opy_ = json.loads(bstack11l111_opy_ (u"ࠢࡼࠤஃ") + content + bstack11l111_opy_ (u"ࠨࠤࡻࠦ࠿ࠦࠢࡺࠤࠪ஄") + bstack11l111_opy_ (u"ࠤࢀࠦஅ"))
              bstack1l1l11ll_opy_ = bstack11l1llll_opy_.get(str(threading.get_ident()))
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢࡵࡩࡦࡪࡩ࡯ࡩࠣࡷࡪࡹࡳࡪࡱࡱࠤࡎࡊࡳࠡࡨ࡬ࡰࡪࡀࠠࠨஆ") + str(e))
  if bstack1l1ll111l1_opy_:
    with bstack11l11l11l_opy_:
      bstack1llllllll1_opy_ = bstack1l1ll111l1_opy_.copy()
    for driver in bstack1llllllll1_opy_:
      if bstack1l1l11ll_opy_ == driver.session_id:
        if test:
          bstack1l111l1lll_opy_(driver, test)
        bstack11llll111l_opy_(driver, bstack1ll111l111_opy_)
  elif bstack1l1l11ll_opy_:
    bstack11l1lllll_opy_(test, bstack1ll111l111_opy_)
  if bstack1lll1l1111_opy_:
    bstack1l11lll111_opy_(bstack1lll1l1111_opy_)
  if bstack11llllll_opy_:
    bstack11ll11ll11_opy_(bstack11llllll_opy_)
  if bstack11l1l11ll_opy_:
    bstack1111ll1l1_opy_()
def bstack111ll1l1_opy_(self, test, *args, **kwargs):
  bstack1ll111l111_opy_ = None
  if test:
    bstack1ll111l111_opy_ = str(test.name)
  bstack1l1111l1ll_opy_(test, bstack1ll111l111_opy_)
  bstack1ll11lll_opy_(self, test, *args, **kwargs)
def bstack1ll1l1lll_opy_(self, parent, test, skip_on_failure=None, rpa=False):
  global bstack1l11ll1111_opy_
  global CONFIG
  global bstack1l1ll111l1_opy_
  global bstack1l1l11ll_opy_
  global bstack1l11ll11ll_opy_
  bstack11l1llll1_opy_ = None
  try:
    if bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠫࡦ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪஇ"), None) or bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠬࡧࡰࡱࡃ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧஈ"), None):
      try:
        if not bstack1l1l11ll_opy_:
          bstack1l1lll1ll_opy_ = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"࠭ࡾࠨஉ")), bstack11l111_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧஊ"), bstack11l111_opy_ (u"ࠨ࠰ࡶࡩࡸࡹࡩࡰࡰ࡬ࡨࡸ࠴ࡴࡹࡶࠪ஋"))
          with bstack1l11ll11ll_opy_:
            if os.path.exists(bstack1l1lll1ll_opy_):
              with open(bstack1l1lll1ll_opy_, bstack11l111_opy_ (u"ࠩࡵࠫ஌")) as f:
                content = f.read().strip()
                if content:
                  bstack11l1llll_opy_ = json.loads(bstack11l111_opy_ (u"ࠥࡿࠧ஍") + content + bstack11l111_opy_ (u"ࠫࠧࡾࠢ࠻ࠢࠥࡽࠧ࠭எ") + bstack11l111_opy_ (u"ࠧࢃࠢஏ"))
                  bstack1l1l11ll_opy_ = bstack11l1llll_opy_.get(str(threading.get_ident()))
      except Exception as e:
        logger.debug(bstack11l111_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥࡸࡥࡢࡦ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡊࡆࡶࠤ࡫࡯࡬ࡦࠢ࡬ࡲࠥࡺࡥࡴࡶࠣࡷࡹࡧࡴࡶࡵ࠽ࠤࠬஐ") + str(e))
      if bstack1l1ll111l1_opy_:
        with bstack11l11l11l_opy_:
          bstack1llllllll1_opy_ = bstack1l1ll111l1_opy_.copy()
        for driver in bstack1llllllll1_opy_:
          if bstack1l1l11ll_opy_ == driver.session_id:
            bstack11l1llll1_opy_ = driver
    bstack11ll1l1l1_opy_ = bstack1lllll11l_opy_.bstack11l1ll1l1_opy_(test.tags)
    if bstack11l1llll1_opy_:
      threading.current_thread().isA11yTest = bstack1lllll11l_opy_.bstack1lll11l111_opy_(bstack11l1llll1_opy_, bstack11ll1l1l1_opy_)
      threading.current_thread().isAppA11yTest = bstack1lllll11l_opy_.bstack1lll11l111_opy_(bstack11l1llll1_opy_, bstack11ll1l1l1_opy_)
    else:
      threading.current_thread().isA11yTest = bstack11ll1l1l1_opy_
      threading.current_thread().isAppA11yTest = bstack11ll1l1l1_opy_
  except:
    pass
  bstack1l11ll1111_opy_(self, parent, test, skip_on_failure=skip_on_failure, rpa=rpa)
  global bstack1l1111ll11_opy_
  try:
    bstack1l1111ll11_opy_ = self._test
  except:
    bstack1l1111ll11_opy_ = self.test
def bstack1l1l1l1l11_opy_():
  global bstack1111llll_opy_
  try:
    if os.path.exists(bstack1111llll_opy_):
      os.remove(bstack1111llll_opy_)
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡧࡩࡱ࡫ࡴࡪࡰࡪࠤࡷࡵࡢࡰࡶࠣࡶࡪࡶ࡯ࡳࡶࠣࡪ࡮ࡲࡥ࠻ࠢࠪ஑") + str(e))
def bstack1l1l1lll1_opy_():
  global bstack1111llll_opy_
  bstack111l1l1l1_opy_ = {}
  lock_file = bstack1111llll_opy_ + bstack11l111_opy_ (u"ࠨ࠰࡯ࡳࡨࡱࠧஒ")
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11l111_opy_ (u"ࠩࡩ࡭ࡱ࡫࡬ࡰࡥ࡮ࠤࡳࡵࡴࠡࡣࡹࡥ࡮ࡲࡡࡣ࡮ࡨ࠰ࠥࡻࡳࡪࡰࡪࠤࡧࡧࡳࡪࡥࠣࡪ࡮ࡲࡥࠡࡱࡳࡩࡷࡧࡴࡪࡱࡱࡷࠬஓ"))
    try:
      if not os.path.isfile(bstack1111llll_opy_):
        with open(bstack1111llll_opy_, bstack11l111_opy_ (u"ࠪࡻࠬஔ")) as f:
          json.dump({}, f)
      if os.path.exists(bstack1111llll_opy_):
        with open(bstack1111llll_opy_, bstack11l111_opy_ (u"ࠫࡷ࠭க")) as f:
          content = f.read().strip()
          if content:
            bstack111l1l1l1_opy_ = json.loads(content)
    except Exception as e:
      logger.debug(bstack11l111_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡳࡧࡤࡨ࡮ࡴࡧࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠠࡧ࡫࡯ࡩ࠿ࠦࠧ஖") + str(e))
    return bstack111l1l1l1_opy_
  try:
    os.makedirs(os.path.dirname(bstack1111llll_opy_), exist_ok=True)
    with FileLock(lock_file, timeout=10):
      if not os.path.isfile(bstack1111llll_opy_):
        with open(bstack1111llll_opy_, bstack11l111_opy_ (u"࠭ࡷࠨ஗")) as f:
          json.dump({}, f)
      if os.path.exists(bstack1111llll_opy_):
        with open(bstack1111llll_opy_, bstack11l111_opy_ (u"ࠧࡳࠩ஘")) as f:
          content = f.read().strip()
          if content:
            bstack111l1l1l1_opy_ = json.loads(content)
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡶࡪࡧࡤࡪࡰࡪࠤࡷࡵࡢࡰࡶࠣࡶࡪࡶ࡯ࡳࡶࠣࡪ࡮ࡲࡥ࠻ࠢࠪங") + str(e))
  finally:
    return bstack111l1l1l1_opy_
def bstack11llll11l1_opy_(platform_index, item_index):
  global bstack1111llll_opy_
  lock_file = bstack1111llll_opy_ + bstack11l111_opy_ (u"ࠩ࠱ࡰࡴࡩ࡫ࠨச")
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11l111_opy_ (u"ࠪࡪ࡮ࡲࡥ࡭ࡱࡦ࡯ࠥࡴ࡯ࡵࠢࡤࡺࡦ࡯࡬ࡢࡤ࡯ࡩ࠱ࠦࡵࡴ࡫ࡱ࡫ࠥࡨࡡࡴ࡫ࡦࠤ࡫࡯࡬ࡦࠢࡲࡴࡪࡸࡡࡵ࡫ࡲࡲࡸ࠭஛"))
    try:
      bstack111l1l1l1_opy_ = {}
      if os.path.exists(bstack1111llll_opy_):
        with open(bstack1111llll_opy_, bstack11l111_opy_ (u"ࠫࡷ࠭ஜ")) as f:
          content = f.read().strip()
          if content:
            bstack111l1l1l1_opy_ = json.loads(content)
      bstack111l1l1l1_opy_[item_index] = platform_index
      with open(bstack1111llll_opy_, bstack11l111_opy_ (u"ࠧࡽࠢ஝")) as outfile:
        json.dump(bstack111l1l1l1_opy_, outfile)
    except Exception as e:
      logger.debug(bstack11l111_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡹࡵ࡭ࡹ࡯࡮ࡨࠢࡷࡳࠥࡸ࡯ࡣࡱࡷࠤࡷ࡫ࡰࡰࡴࡷࠤ࡫࡯࡬ࡦ࠼ࠣࠫஞ") + str(e))
    return
  try:
    os.makedirs(os.path.dirname(bstack1111llll_opy_), exist_ok=True)
    with FileLock(lock_file, timeout=10):
      bstack111l1l1l1_opy_ = {}
      if os.path.exists(bstack1111llll_opy_):
        with open(bstack1111llll_opy_, bstack11l111_opy_ (u"ࠧࡳࠩட")) as f:
          content = f.read().strip()
          if content:
            bstack111l1l1l1_opy_ = json.loads(content)
      bstack111l1l1l1_opy_[item_index] = platform_index
      with open(bstack1111llll_opy_, bstack11l111_opy_ (u"ࠣࡹࠥ஠")) as outfile:
        json.dump(bstack111l1l1l1_opy_, outfile)
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡼࡸࡩࡵ࡫ࡱ࡫ࠥࡺ࡯ࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠠࡧ࡫࡯ࡩ࠿ࠦࠧ஡") + str(e))
def bstack11l11lll_opy_(bstack1l11lll1_opy_):
  global CONFIG
  bstack111l11111_opy_ = bstack11l111_opy_ (u"ࠪࠫ஢")
  if not bstack11l111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧண") in CONFIG:
    logger.info(bstack11l111_opy_ (u"ࠬࡔ࡯ࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠤࡵࡧࡳࡴࡧࡧࠤࡺࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡨࡧࡱࡩࡷࡧࡴࡦࠢࡵࡩࡵࡵࡲࡵࠢࡩࡳࡷࠦࡒࡰࡤࡲࡸࠥࡸࡵ࡯ࠩத"))
  try:
    platform = CONFIG[bstack11l111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ஥")][bstack1l11lll1_opy_]
    if bstack11l111_opy_ (u"ࠧࡰࡵࠪ஦") in platform:
      bstack111l11111_opy_ += str(platform[bstack11l111_opy_ (u"ࠨࡱࡶࠫ஧")]) + bstack11l111_opy_ (u"ࠩ࠯ࠤࠬந")
    if bstack11l111_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ன") in platform:
      bstack111l11111_opy_ += str(platform[bstack11l111_opy_ (u"ࠫࡴࡹࡖࡦࡴࡶ࡭ࡴࡴࠧப")]) + bstack11l111_opy_ (u"ࠬ࠲ࠠࠨ஫")
    if bstack11l111_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪ஬") in platform:
      bstack111l11111_opy_ += str(platform[bstack11l111_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫ஭")]) + bstack11l111_opy_ (u"ࠨ࠮ࠣࠫம")
    if bstack11l111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠫய") in platform:
      bstack111l11111_opy_ += str(platform[bstack11l111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬர")]) + bstack11l111_opy_ (u"ࠫ࠱ࠦࠧற")
    if bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪல") in platform:
      bstack111l11111_opy_ += str(platform[bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫள")]) + bstack11l111_opy_ (u"ࠧ࠭ࠢࠪழ")
    if bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩவ") in platform:
      bstack111l11111_opy_ += str(platform[bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪஶ")]) + bstack11l111_opy_ (u"ࠪ࠰ࠥ࠭ஷ")
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠫࡘࡵ࡭ࡦࠢࡨࡶࡷࡵࡲࠡ࡫ࡱࠤ࡬࡫࡮ࡦࡴࡤࡸ࡮ࡴࡧࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡷࡹࡸࡩ࡯ࡩࠣࡪࡴࡸࠠࡳࡧࡳࡳࡷࡺࠠࡨࡧࡱࡩࡷࡧࡴࡪࡱࡱࠫஸ") + str(e))
  finally:
    if bstack111l11111_opy_[len(bstack111l11111_opy_) - 2:] == bstack11l111_opy_ (u"ࠬ࠲ࠠࠨஹ"):
      bstack111l11111_opy_ = bstack111l11111_opy_[:-2]
    return bstack111l11111_opy_
def bstack11lllll11l_opy_(path, bstack111l11111_opy_):
  try:
    import xml.etree.ElementTree as ET
    bstack1llll1l1ll_opy_ = ET.parse(path)
    bstack1l1111ll1_opy_ = bstack1llll1l1ll_opy_.getroot()
    bstack1l1ll1l11_opy_ = None
    for suite in bstack1l1111ll1_opy_.iter(bstack11l111_opy_ (u"࠭ࡳࡶ࡫ࡷࡩࠬ஺")):
      if bstack11l111_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧ஻") in suite.attrib:
        suite.attrib[bstack11l111_opy_ (u"ࠨࡰࡤࡱࡪ࠭஼")] += bstack11l111_opy_ (u"ࠩࠣࠫ஽") + bstack111l11111_opy_
        bstack1l1ll1l11_opy_ = suite
    bstack1l1lll1lll_opy_ = None
    for robot in bstack1l1111ll1_opy_.iter(bstack11l111_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩா")):
      bstack1l1lll1lll_opy_ = robot
    bstack1l11ll11_opy_ = len(bstack1l1lll1lll_opy_.findall(bstack11l111_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪி")))
    if bstack1l11ll11_opy_ == 1:
      bstack1l1lll1lll_opy_.remove(bstack1l1lll1lll_opy_.findall(bstack11l111_opy_ (u"ࠬࡹࡵࡪࡶࡨࠫீ"))[0])
      bstack1l1lll11ll_opy_ = ET.Element(bstack11l111_opy_ (u"࠭ࡳࡶ࡫ࡷࡩࠬு"), attrib={bstack11l111_opy_ (u"ࠧ࡯ࡣࡰࡩࠬூ"): bstack11l111_opy_ (u"ࠨࡕࡸ࡭ࡹ࡫ࡳࠨ௃"), bstack11l111_opy_ (u"ࠩ࡬ࡨࠬ௄"): bstack11l111_opy_ (u"ࠪࡷ࠵࠭௅")})
      bstack1l1lll1lll_opy_.insert(1, bstack1l1lll11ll_opy_)
      bstack11ll1l111l_opy_ = None
      for suite in bstack1l1lll1lll_opy_.iter(bstack11l111_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪெ")):
        bstack11ll1l111l_opy_ = suite
      bstack11ll1l111l_opy_.append(bstack1l1ll1l11_opy_)
      bstack11l1l11l_opy_ = None
      for status in bstack1l1ll1l11_opy_.iter(bstack11l111_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬே")):
        bstack11l1l11l_opy_ = status
      bstack11ll1l111l_opy_.append(bstack11l1l11l_opy_)
    bstack1llll1l1ll_opy_.write(path)
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡲࡤࡶࡸ࡯࡮ࡨࠢࡺ࡬࡮ࡲࡥࠡࡩࡨࡲࡪࡸࡡࡵ࡫ࡱ࡫ࠥࡸ࡯ࡣࡱࡷࠤࡷ࡫ࡰࡰࡴࡷࠫை") + str(e))
def bstack1llll11l1_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name):
  global bstack1l1lll1l1l_opy_
  global CONFIG
  if bstack11l111_opy_ (u"ࠢࡱࡻࡷ࡬ࡴࡴࡰࡢࡶ࡫ࠦ௉") in options:
    del options[bstack11l111_opy_ (u"ࠣࡲࡼࡸ࡭ࡵ࡮ࡱࡣࡷ࡬ࠧொ")]
  bstack11llllllll_opy_ = bstack1l1l1lll1_opy_()
  for item_id in bstack11llllllll_opy_.keys():
    path = os.path.join(os.getcwd(), bstack11l111_opy_ (u"ࠩࡳࡥࡧࡵࡴࡠࡴࡨࡷࡺࡲࡴࡴࠩோ"), str(item_id), bstack11l111_opy_ (u"ࠪࡳࡺࡺࡰࡶࡶ࠱ࡼࡲࡲࠧௌ"))
    bstack11lllll11l_opy_(path, bstack11l11lll_opy_(bstack11llllllll_opy_[item_id]))
  bstack1l1l1l1l11_opy_()
  return bstack1l1lll1l1l_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name)
def bstack1llll1lll1_opy_(self, ff_profile_dir):
  global bstack11lll1l1ll_opy_
  if not ff_profile_dir:
    return None
  return bstack11lll1l1ll_opy_(self, ff_profile_dir)
def bstack1llll111ll_opy_(datasources, opts_for_run, outs_dir, pabot_args, suite_group):
  from pabot.pabot import QueueItem
  global CONFIG
  global bstack111lllllll_opy_
  bstack1lll11l1l_opy_ = []
  if bstack11l111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹ்ࠧ") in CONFIG:
    bstack1lll11l1l_opy_ = CONFIG[bstack11l111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ௎")]
  return [
    QueueItem(
      datasources,
      outs_dir,
      opts_for_run,
      suite,
      pabot_args[bstack11l111_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪࠢ௏")],
      pabot_args[bstack11l111_opy_ (u"ࠢࡷࡧࡵࡦࡴࡹࡥࠣௐ")],
      argfile,
      pabot_args.get(bstack11l111_opy_ (u"ࠣࡪ࡬ࡺࡪࠨ௑")),
      pabot_args[bstack11l111_opy_ (u"ࠤࡳࡶࡴࡩࡥࡴࡵࡨࡷࠧ௒")],
      platform[0],
      bstack111lllllll_opy_
    )
    for suite in suite_group
    for argfile in pabot_args[bstack11l111_opy_ (u"ࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸ࡫࡯࡬ࡦࡵࠥ௓")] or [(bstack11l111_opy_ (u"ࠦࠧ௔"), None)]
    for platform in enumerate(bstack1lll11l1l_opy_)
  ]
def bstack1llll1l111_opy_(self, datasources, outs_dir, options,
                        execution_item, command, verbose, argfile,
                        hive=None, processes=0, platform_index=0, bstack1111lll1l_opy_=bstack11l111_opy_ (u"ࠬ࠭௕")):
  global bstack1lll1lll1l_opy_
  self.platform_index = platform_index
  self.bstack1l1l111ll1_opy_ = bstack1111lll1l_opy_
  bstack1lll1lll1l_opy_(self, datasources, outs_dir, options,
                      execution_item, command, verbose, argfile, hive, processes)
def bstack1lll11111_opy_(caller_id, datasources, is_last, item, outs_dir):
  global bstack1l11111l_opy_
  global bstack11l1l1l111_opy_
  bstack111l1l1l_opy_ = copy.deepcopy(item)
  if not bstack11l111_opy_ (u"࠭ࡶࡢࡴ࡬ࡥࡧࡲࡥࠨ௖") in item.options:
    bstack111l1l1l_opy_.options[bstack11l111_opy_ (u"ࠧࡷࡣࡵ࡭ࡦࡨ࡬ࡦࠩௗ")] = []
  bstack11l11111_opy_ = bstack111l1l1l_opy_.options[bstack11l111_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ௘")].copy()
  for v in bstack111l1l1l_opy_.options[bstack11l111_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫ௙")]:
    if bstack11l111_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡓࡐࡆ࡚ࡆࡐࡔࡐࡍࡓࡊࡅ࡙ࠩ௚") in v:
      bstack11l11111_opy_.remove(v)
    if bstack11l111_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡇࡑࡏࡁࡓࡉࡖࠫ௛") in v:
      bstack11l11111_opy_.remove(v)
    if bstack11l111_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡉࡋࡆࡍࡑࡆࡅࡑࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩ௜") in v:
      bstack11l11111_opy_.remove(v)
  bstack11l11111_opy_.insert(0, bstack11l111_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡖࡌࡂࡖࡉࡓࡗࡓࡉࡏࡆࡈ࡜࠿ࢁࡽࠨ௝").format(bstack111l1l1l_opy_.platform_index))
  bstack11l11111_opy_.insert(0, bstack11l111_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡄࡆࡈࡏࡓࡈࡇࡌࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕ࠾ࢀࢃࠧ௞").format(bstack111l1l1l_opy_.bstack1l1l111ll1_opy_))
  bstack111l1l1l_opy_.options[bstack11l111_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ௟")] = bstack11l11111_opy_
  if bstack11l1l1l111_opy_:
    bstack111l1l1l_opy_.options[bstack11l111_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫ௠")].insert(0, bstack11l111_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡆࡐࡎࡇࡒࡈࡕ࠽ࡿࢂ࠭௡").format(bstack11l1l1l111_opy_))
  return bstack1l11111l_opy_(caller_id, datasources, is_last, bstack111l1l1l_opy_, outs_dir)
def bstack1l1111lll_opy_(command, item_index):
  try:
    if bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠬ௢")):
      os.environ[bstack11l111_opy_ (u"ࠬࡉࡕࡓࡔࡈࡒ࡙ࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡆࡄࡘࡆ࠭௣")] = json.dumps(CONFIG[bstack11l111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ௤")][item_index % bstack1l1ll1lll_opy_])
    global bstack11l1l1l111_opy_
    if bstack11l1l1l111_opy_:
      command[0] = command[0].replace(bstack11l111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭௥"), bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠭ࡴࡦ࡮ࠤࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠥ࠳࠭ࡣࡵࡷࡥࡨࡱ࡟ࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡ࡬ࡲࡩ࡫ࡸࠡࠩ௦") + str(item_index % bstack1l1ll1lll_opy_) + bstack11l111_opy_ (u"ࠩࠣ࠱࠲ࡨࡳࡵࡣࡦ࡯ࡤ࡯ࡴࡦ࡯ࡢ࡭ࡳࡪࡥࡹࠢࠪ௧") + str(
        item_index) + bstack11l111_opy_ (u"ࠪࠤࠬ௨") + bstack11l1l1l111_opy_, 1)
    else:
      command[0] = command[0].replace(bstack11l111_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪ௩"),
                                      bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠱ࡸࡪ࡫ࠡࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠢ࠰࠱ࡧࡹࡴࡢࡥ࡮ࡣࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࠥ࠭௪") +  str(item_index % bstack1l1ll1lll_opy_) + bstack11l111_opy_ (u"࠭ࠠ࠮࠯ࡥࡷࡹࡧࡣ࡬ࡡ࡬ࡸࡪࡳ࡟ࡪࡰࡧࡩࡽࠦࠧ௫") + str(item_index), 1)
  except Exception as e:
    logger.error(bstack11l111_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦ࡭ࡰࡦ࡬ࡪࡾ࡯࡮ࡨࠢࡦࡳࡲࡳࡡ࡯ࡦࠣࡪࡴࡸࠠࡱࡣࡥࡳࡹࠦࡲࡶࡰ࠽ࠤࢀࢃࠧ௬").format(str(e)))
def bstack1l1l1ll11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index):
  global bstack1ll11ll1l1_opy_
  try:
    bstack1l1111lll_opy_(command, item_index)
    return bstack1ll11ll1l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
  except Exception as e:
    logger.error(bstack11l111_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡴࡦࡨ࡯ࡵࠢࡵࡹࡳࡀࠠࡼࡿࠪ௭").format(str(e)))
    raise e
def bstack111ll1ll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir):
  global bstack1ll11ll1l1_opy_
  try:
    bstack1l1111lll_opy_(command, item_index)
    return bstack1ll11ll1l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
  except Exception as e:
    logger.error(bstack11l111_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡵࡧࡢࡰࡶࠣࡶࡺࡴࠠ࠳࠰࠴࠷࠿ࠦࡻࡾࠩ௮").format(str(e)))
    try:
      return bstack1ll11ll1l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
    except Exception as e2:
      logger.error(bstack11l111_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡡࡣࡱࡷࠤ࠷࠴࠱࠴ࠢࡩࡥࡱࡲࡢࡢࡥ࡮࠾ࠥࢁࡽࠨ௯").format(str(e2)))
      raise e
def bstack1l1llll1ll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout):
  global bstack1ll11ll1l1_opy_
  try:
    bstack1l1111lll_opy_(command, item_index)
    if process_timeout is None:
      process_timeout = 3600
    return bstack1ll11ll1l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
  except Exception as e:
    logger.error(bstack11l111_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡰࡢࡤࡲࡸࠥࡸࡵ࡯ࠢ࠵࠲࠶࠻࠺ࠡࡽࢀࠫ௰").format(str(e)))
    try:
      return bstack1ll11ll1l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
    except Exception as e2:
      logger.error(bstack11l111_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡱࡣࡥࡳࡹࠦ࠲࠯࠳࠸ࠤ࡫ࡧ࡬࡭ࡤࡤࡧࡰࡀࠠࡼࡿࠪ௱").format(str(e2)))
      raise e
def _111ll1l1l_opy_(bstack1l1lll1111_opy_, item_index, process_timeout, sleep_before_start, bstack111lll1l1_opy_):
  bstack1l1111lll_opy_(bstack1l1lll1111_opy_, item_index)
  if process_timeout is None:
    process_timeout = 3600
  if sleep_before_start and sleep_before_start > 0:
    time.sleep(min(sleep_before_start, 5))
  return process_timeout
def bstack1l1ll1ll11_opy_(command, bstack1ll111l11l_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start):
  global bstack1ll11ll1l1_opy_
  try:
    bstack1l1111lll_opy_(command, item_index)
    if process_timeout is None:
      process_timeout = 3600
    if sleep_before_start and sleep_before_start > 0:
      time.sleep(min(sleep_before_start, 5))
    return bstack1ll11ll1l1_opy_(command, bstack1ll111l11l_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start)
  except Exception as e:
    logger.error(bstack11l111_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡲࡤࡦࡴࡺࠠࡳࡷࡱࠤ࠺࠴࠰࠻ࠢࡾࢁࠬ௲").format(str(e)))
    try:
      return bstack1ll11ll1l1_opy_(command, bstack1ll111l11l_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
    except Exception as e2:
      logger.error(bstack11l111_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡳࡥࡧࡵࡴࠡࡨࡤࡰࡱࡨࡡࡤ࡭࠽ࠤࢀࢃࠧ௳").format(str(e2)))
      raise e
def bstack11lll1ll1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start):
  global bstack1ll11ll1l1_opy_
  try:
    process_timeout = _111ll1l1l_opy_(command, item_index, process_timeout, sleep_before_start, bstack11l111_opy_ (u"ࠨ࠶࠱࠶ࠬ௴"))
    return bstack1ll11ll1l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start)
  except Exception as e:
    logger.error(bstack11l111_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡵࡧࡢࡰࡶࠣࡶࡺࡴࠠ࠵࠰࠵࠾ࠥࢁࡽࠨ௵").format(str(e)))
    try:
      return bstack1ll11ll1l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
    except Exception as e2:
      logger.error(bstack11l111_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡡࡣࡱࡷࠤ࡫ࡧ࡬࡭ࡤࡤࡧࡰࡀࠠࡼࡿࠪ௶").format(str(e2)))
      raise e
def is_driver_active(driver):
  return True if driver and driver.session_id else False
def bstack1l111l1l1_opy_(self, runner, quiet=False, capture=True):
  global bstack1l111111l_opy_
  bstack1l11l1ll_opy_ = bstack1l111111l_opy_(self, runner, quiet=quiet, capture=capture)
  if self.exception:
    if not hasattr(runner, bstack11l111_opy_ (u"ࠫࡪࡾࡣࡦࡲࡷ࡭ࡴࡴ࡟ࡢࡴࡵࠫ௷")):
      runner.exception_arr = []
    if not hasattr(runner, bstack11l111_opy_ (u"ࠬ࡫ࡸࡤࡡࡷࡶࡦࡩࡥࡣࡣࡦ࡯ࡤࡧࡲࡳࠩ௸")):
      runner.exc_traceback_arr = []
    runner.exception = self.exception
    runner.exc_traceback = self.exc_traceback
    runner.exception_arr.append(self.exception)
    runner.exc_traceback_arr.append(self.exc_traceback)
  return bstack1l11l1ll_opy_
def bstack11l11ll1l1_opy_(runner, hook_name, context, element, bstack11ll11l1l_opy_, *args):
  try:
    if runner.hooks.get(hook_name):
      bstack1ll1l111l_opy_.bstack11ll111l11_opy_(hook_name, element)
    bstack11ll11l1l_opy_(runner, hook_name, context, *args)
    if runner.hooks.get(hook_name):
      bstack1ll1l111l_opy_.bstack1llll1l11_opy_(element)
      if hook_name not in [bstack11l111_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࠪ௹"), bstack11l111_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡡ࡭࡮ࠪ௺")] and args and hasattr(args[0], bstack11l111_opy_ (u"ࠨࡧࡵࡶࡴࡸ࡟࡮ࡧࡶࡷࡦ࡭ࡥࠨ௻")):
        args[0].error_message = bstack11l111_opy_ (u"ࠩࠪ௼")
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡨࡢࡰࡧࡰࡪࠦࡨࡰࡱ࡮ࡷࠥ࡯࡮ࠡࡤࡨ࡬ࡦࡼࡥ࠻ࠢࡾࢁࠬ௽").format(str(e)))
@measure(event_name=EVENTS.bstack11l1ll1ll1_opy_, stage=STAGE.bstack1l1l111l1_opy_, hook_type=bstack11l111_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡅࡱࡲࠢ௾"), bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack1lll1ll1l1_opy_(runner, name, context, bstack11ll11l1l_opy_, *args):
    if runner.hooks.get(bstack11l111_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡧ࡬࡭ࠤ௿")).__name__ != bstack11l111_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࡢࡨࡪ࡬ࡡࡶ࡮ࡷࡣ࡭ࡵ࡯࡬ࠤఀ"):
      bstack11l11ll1l1_opy_(runner, name, context, runner, bstack11ll11l1l_opy_, *args)
    try:
      threading.current_thread().bstackSessionDriver if bstack11l1111ll_opy_(bstack11l111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭ఁ")) else context.browser
      runner.driver_initialised = bstack11l111_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࠧం")
    except Exception as e:
      logger.debug(bstack11l111_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡥࡵࠢࡧࡶ࡮ࡼࡥࡳࠢ࡬ࡲ࡮ࡺࡩࡢ࡮࡬ࡷࡪࠦࡡࡵࡶࡵ࡭ࡧࡻࡴࡦ࠼ࠣࡿࢂ࠭ః").format(str(e)))
def bstack1l111ll1_opy_(runner, name, context, bstack11ll11l1l_opy_, *args):
    bstack11l11ll1l1_opy_(runner, name, context, context.feature, bstack11ll11l1l_opy_, *args)
    try:
      if not bstack1l11l111l_opy_:
        bstack11l1llll1_opy_ = threading.current_thread().bstackSessionDriver if bstack11l1111ll_opy_(bstack11l111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩఄ")) else context.browser
        if is_driver_active(bstack11l1llll1_opy_):
          if runner.driver_initialised is None: runner.driver_initialised = bstack11l111_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣ࡫࡫ࡡࡵࡷࡵࡩࠧఅ")
          bstack1ll111l1l_opy_ = str(runner.feature.name)
          bstack1l1l11l11_opy_(context, bstack1ll111l1l_opy_)
          bstack11l1llll1_opy_.execute_script(bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪఆ") + json.dumps(bstack1ll111l1l_opy_) + bstack11l111_opy_ (u"࠭ࡽࡾࠩఇ"))
    except Exception as e:
      logger.debug(bstack11l111_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠦࡩ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡩࡩࡦࡺࡵࡳࡧ࠽ࠤࢀࢃࠧఈ").format(str(e)))
def bstack1ll11111l1_opy_(runner, name, context, bstack11ll11l1l_opy_, *args):
    if hasattr(context, bstack11l111_opy_ (u"ࠨࡵࡦࡩࡳࡧࡲࡪࡱࠪఉ")):
        bstack1ll1l111l_opy_.start_test(context)
    target = context.scenario if hasattr(context, bstack11l111_opy_ (u"ࠩࡶࡧࡪࡴࡡࡳ࡫ࡲࠫఊ")) else context.feature
    bstack11l11ll1l1_opy_(runner, name, context, target, bstack11ll11l1l_opy_, *args)
@measure(event_name=EVENTS.bstack11l1l111l1_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack1l1l11l1ll_opy_(runner, name, context, bstack11ll11l1l_opy_, *args):
    if len(context.scenario.tags) == 0: bstack1ll1l111l_opy_.start_test(context)
    bstack11l11ll1l1_opy_(runner, name, context, context.scenario, bstack11ll11l1l_opy_, *args)
    threading.current_thread().a11y_stop = False
    bstack11ll1lllll_opy_.bstack11l1l1l1l_opy_(context, *args)
    try:
      bstack11l1llll1_opy_ = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩఋ"), context.browser)
      if is_driver_active(bstack11l1llll1_opy_):
        bstack11l11l1l_opy_.bstack11ll1lll11_opy_(bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪఌ"), {}))
        if runner.driver_initialised is None: runner.driver_initialised = bstack11l111_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡹࡣࡦࡰࡤࡶ࡮ࡵࠢ఍")
        if (not bstack1l11l111l_opy_):
          scenario_name = args[0].name
          feature_name = bstack1ll111l1l_opy_ = str(runner.feature.name)
          bstack1ll111l1l_opy_ = feature_name + bstack11l111_opy_ (u"࠭ࠠ࠮ࠢࠪఎ") + scenario_name
          if runner.driver_initialised == bstack11l111_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠤఏ"):
            bstack1l1l11l11_opy_(context, bstack1ll111l1l_opy_)
            bstack11l1llll1_opy_.execute_script(bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠥ࠭ఐ") + json.dumps(bstack1ll111l1l_opy_) + bstack11l111_opy_ (u"ࠩࢀࢁࠬ఑"))
    except Exception as e:
      logger.debug(bstack11l111_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠢ࡬ࡲࠥࡨࡥࡧࡱࡵࡩࠥࡹࡣࡦࡰࡤࡶ࡮ࡵ࠺ࠡࡽࢀࠫఒ").format(str(e)))
@measure(event_name=EVENTS.bstack11l1ll1ll1_opy_, stage=STAGE.bstack1l1l111l1_opy_, hook_type=bstack11l111_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡗࡹ࡫ࡰࠣఓ"), bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack1l111lll_opy_(runner, name, context, bstack11ll11l1l_opy_, *args):
    bstack11l11ll1l1_opy_(runner, name, context, args[0], bstack11ll11l1l_opy_, *args)
    try:
      bstack11l1llll1_opy_ = threading.current_thread().bstackSessionDriver if bstack11l1111ll_opy_(bstack11l111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫఔ")) else context.browser
      if is_driver_active(bstack11l1llll1_opy_):
        if runner.driver_initialised is None: runner.driver_initialised = bstack11l111_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡵࡧࡳࠦక")
        bstack1ll1l111l_opy_.bstack1lll1111l1_opy_(args[0])
        if runner.driver_initialised == bstack11l111_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡶࡨࡴࠧఖ"):
          feature_name = bstack1ll111l1l_opy_ = str(runner.feature.name)
          bstack1ll111l1l_opy_ = feature_name + bstack11l111_opy_ (u"ࠨࠢ࠰ࠤࠬగ") + context.scenario.name
          bstack11l1llll1_opy_.execute_script(bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨ࡮ࡢ࡯ࡨࠦ࠿ࠦࠧఘ") + json.dumps(bstack1ll111l1l_opy_) + bstack11l111_opy_ (u"ࠪࢁࢂ࠭ఙ"))
    except Exception as e:
      logger.debug(bstack11l111_opy_ (u"ࠫࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡧࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠣ࡭ࡳࠦࡢࡦࡨࡲࡶࡪࠦࡳࡵࡧࡳ࠾ࠥࢁࡽࠨచ").format(str(e)))
@measure(event_name=EVENTS.bstack11l1ll1ll1_opy_, stage=STAGE.bstack1l1l111l1_opy_, hook_type=bstack11l111_opy_ (u"ࠧࡧࡦࡵࡧࡵࡗࡹ࡫ࡰࠣఛ"), bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack1l1ll11l_opy_(runner, name, context, bstack11ll11l1l_opy_, *args):
  bstack1ll1l111l_opy_.bstack1l1lll11l_opy_(args[0])
  try:
    step_status = args[0].status.name
    bstack11l1llll1_opy_ = threading.current_thread().bstackSessionDriver if bstack11l111_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬజ") in threading.current_thread().__dict__.keys() else context.browser
    if is_driver_active(bstack11l1llll1_opy_):
      if runner.driver_initialised is None:
        runner.driver_initialised  = bstack11l111_opy_ (u"ࠧࡪࡰࡶࡸࡪࡶࠧఝ")
        feature_name = bstack1ll111l1l_opy_ = str(runner.feature.name)
        bstack1ll111l1l_opy_ = feature_name + bstack11l111_opy_ (u"ࠨࠢ࠰ࠤࠬఞ") + context.scenario.name
        bstack11l1llll1_opy_.execute_script(bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨ࡮ࡢ࡯ࡨࠦ࠿ࠦࠧట") + json.dumps(bstack1ll111l1l_opy_) + bstack11l111_opy_ (u"ࠪࢁࢂ࠭ఠ"))
    if str(step_status).lower() == bstack11l111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫడ"):
      bstack111llll1l_opy_ = bstack11l111_opy_ (u"ࠬ࠭ఢ")
      bstack1ll1111l1l_opy_ = bstack11l111_opy_ (u"࠭ࠧణ")
      bstack1l11l1l1ll_opy_ = bstack11l111_opy_ (u"ࠧࠨత")
      try:
        import traceback
        bstack111llll1l_opy_ = runner.exception.__class__.__name__
        bstack11l1ll1lll_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack1ll1111l1l_opy_ = bstack11l111_opy_ (u"ࠨࠢࠪథ").join(bstack11l1ll1lll_opy_)
        bstack1l11l1l1ll_opy_ = bstack11l1ll1lll_opy_[-1]
      except Exception as e:
        logger.debug(bstack1lll1l11ll_opy_.format(str(e)))
      bstack111llll1l_opy_ += bstack1l11l1l1ll_opy_
      bstack1lll1111_opy_(context, json.dumps(str(args[0].name) + bstack11l111_opy_ (u"ࠤࠣ࠱ࠥࡌࡡࡪ࡮ࡨࡨࠦࡢ࡮ࠣద") + str(bstack1ll1111l1l_opy_)),
                          bstack11l111_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤధ"))
      if runner.driver_initialised == bstack11l111_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡺࡥࡱࠤన"):
        bstack11lll111_opy_(getattr(context, bstack11l111_opy_ (u"ࠬࡶࡡࡨࡧࠪ఩"), None), bstack11l111_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨప"), bstack111llll1l_opy_)
        bstack11l1llll1_opy_.execute_script(bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡪࡡࡵࡣࠥ࠾ࠬఫ") + json.dumps(str(args[0].name) + bstack11l111_opy_ (u"ࠣࠢ࠰ࠤࡋࡧࡩ࡭ࡧࡧࠥࡡࡴࠢబ") + str(bstack1ll1111l1l_opy_)) + bstack11l111_opy_ (u"ࠩ࠯ࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡦࡴࡵࡳࡷࠨࡽࡾࠩభ"))
      if runner.driver_initialised == bstack11l111_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡹ࡫ࡰࠣమ"):
        bstack1ll11l1ll1_opy_(bstack11l1llll1_opy_, bstack11l111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫయ"), bstack11l111_opy_ (u"࡙ࠧࡣࡦࡰࡤࡶ࡮ࡵࠠࡧࡣ࡬ࡰࡪࡪࠠࡸ࡫ࡷ࡬࠿ࠦ࡜࡯ࠤర") + str(bstack111llll1l_opy_))
    else:
      bstack1lll1111_opy_(context, bstack11l111_opy_ (u"ࠨࡐࡢࡵࡶࡩࡩࠧࠢఱ"), bstack11l111_opy_ (u"ࠢࡪࡰࡩࡳࠧల"))
      if runner.driver_initialised == bstack11l111_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡵࡷࡩࡵࠨళ"):
        bstack11lll111_opy_(getattr(context, bstack11l111_opy_ (u"ࠩࡳࡥ࡬࡫ࠧఴ"), None), bstack11l111_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠥవ"))
      bstack11l1llll1_opy_.execute_script(bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩశ") + json.dumps(str(args[0].name) + bstack11l111_opy_ (u"ࠧࠦ࠭ࠡࡒࡤࡷࡸ࡫ࡤࠢࠤష")) + bstack11l111_opy_ (u"࠭ࠬࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦ࡮ࡴࡦࡰࠤࢀࢁࠬస"))
      if runner.driver_initialised == bstack11l111_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡶࡨࡴࠧహ"):
        bstack1ll11l1ll1_opy_(bstack11l1llll1_opy_, bstack11l111_opy_ (u"ࠣࡲࡤࡷࡸ࡫ࡤࠣ఺"))
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡳࡡࡳ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠤࡸࡺࡡࡵࡷࡶࠤ࡮ࡴࠠࡢࡨࡷࡩࡷࠦࡳࡵࡧࡳ࠾ࠥࢁࡽࠨ఻").format(str(e)))
  bstack11l11ll1l1_opy_(runner, name, context, args[0], bstack11ll11l1l_opy_, *args)
@measure(event_name=EVENTS.bstack11l11111l1_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack1ll1l11lll_opy_(runner, name, context, bstack11ll11l1l_opy_, *args):
  bstack1ll1l111l_opy_.end_test(args[0])
  try:
    bstack1l11l11111_opy_ = args[0].status.name
    bstack11l1llll1_opy_ = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳ఼ࠩ"), context.browser)
    bstack11ll1lllll_opy_.bstack1l1l1lll1l_opy_(bstack11l1llll1_opy_)
    if str(bstack1l11l11111_opy_).lower() == bstack11l111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫఽ"):
      bstack111llll1l_opy_ = bstack11l111_opy_ (u"ࠬ࠭ా")
      bstack1ll1111l1l_opy_ = bstack11l111_opy_ (u"࠭ࠧి")
      bstack1l11l1l1ll_opy_ = bstack11l111_opy_ (u"ࠧࠨీ")
      try:
        import traceback
        bstack111llll1l_opy_ = runner.exception.__class__.__name__
        bstack11l1ll1lll_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack1ll1111l1l_opy_ = bstack11l111_opy_ (u"ࠨࠢࠪు").join(bstack11l1ll1lll_opy_)
        bstack1l11l1l1ll_opy_ = bstack11l1ll1lll_opy_[-1]
      except Exception as e:
        logger.debug(bstack1lll1l11ll_opy_.format(str(e)))
      bstack111llll1l_opy_ += bstack1l11l1l1ll_opy_
      bstack1lll1111_opy_(context, json.dumps(str(args[0].name) + bstack11l111_opy_ (u"ࠤࠣ࠱ࠥࡌࡡࡪ࡮ࡨࡨࠦࡢ࡮ࠣూ") + str(bstack1ll1111l1l_opy_)),
                          bstack11l111_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤృ"))
      if runner.driver_initialised == bstack11l111_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴࠨౄ") or runner.driver_initialised == bstack11l111_opy_ (u"ࠬ࡯࡮ࡴࡶࡨࡴࠬ౅"):
        bstack11lll111_opy_(getattr(context, bstack11l111_opy_ (u"࠭ࡰࡢࡩࡨࠫె"), None), bstack11l111_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢే"), bstack111llll1l_opy_)
        bstack11l1llll1_opy_.execute_script(bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿࠭ై") + json.dumps(str(args[0].name) + bstack11l111_opy_ (u"ࠤࠣ࠱ࠥࡌࡡࡪ࡮ࡨࡨࠦࡢ࡮ࠣ౉") + str(bstack1ll1111l1l_opy_)) + bstack11l111_opy_ (u"ࠪ࠰ࠥࠨ࡬ࡦࡸࡨࡰࠧࡀࠠࠣࡧࡵࡶࡴࡸࠢࡾࡿࠪొ"))
      if runner.driver_initialised == bstack11l111_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴࠨో") or runner.driver_initialised == bstack11l111_opy_ (u"ࠬ࡯࡮ࡴࡶࡨࡴࠬౌ"):
        bstack1ll11l1ll1_opy_(bstack11l1llll1_opy_, bstack11l111_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ్࠭"), bstack11l111_opy_ (u"ࠢࡔࡥࡨࡲࡦࡸࡩࡰࠢࡩࡥ࡮ࡲࡥࡥࠢࡺ࡭ࡹ࡮࠺ࠡ࡞ࡱࠦ౎") + str(bstack111llll1l_opy_))
    else:
      bstack1lll1111_opy_(context, bstack11l111_opy_ (u"ࠣࡒࡤࡷࡸ࡫ࡤࠢࠤ౏"), bstack11l111_opy_ (u"ࠤ࡬ࡲ࡫ࡵࠢ౐"))
      if runner.driver_initialised == bstack11l111_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠧ౑") or runner.driver_initialised == bstack11l111_opy_ (u"ࠫ࡮ࡴࡳࡵࡧࡳࠫ౒"):
        bstack11lll111_opy_(getattr(context, bstack11l111_opy_ (u"ࠬࡶࡡࡨࡧࠪ౓"), None), bstack11l111_opy_ (u"ࠨࡰࡢࡵࡶࡩࡩࠨ౔"))
      bstack11l1llll1_opy_.execute_script(bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡪࡡࡵࡣࠥ࠾ౕࠬ") + json.dumps(str(args[0].name) + bstack11l111_opy_ (u"ࠣࠢ࠰ࠤࡕࡧࡳࡴࡧࡧౖࠥࠧ")) + bstack11l111_opy_ (u"ࠩ࠯ࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡪࡰࡩࡳࠧࢃࡽࠨ౗"))
      if runner.driver_initialised == bstack11l111_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠧౘ") or runner.driver_initialised == bstack11l111_opy_ (u"ࠫ࡮ࡴࡳࡵࡧࡳࠫౙ"):
        bstack1ll11l1ll1_opy_(bstack11l1llll1_opy_, bstack11l111_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧౚ"))
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡰࡥࡷࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡵࡷࡥࡹࡻࡳࠡ࡫ࡱࠤࡦ࡬ࡴࡦࡴࠣࡪࡪࡧࡴࡶࡴࡨ࠾ࠥࢁࡽࠨ౛").format(str(e)))
  bstack11l11ll1l1_opy_(runner, name, context, context.scenario, bstack11ll11l1l_opy_, *args)
  if len(context.scenario.tags) == 0: threading.current_thread().current_test_uuid = None
def bstack1lll1l1l1_opy_(runner, name, context, bstack11ll11l1l_opy_, *args):
    target = context.scenario if hasattr(context, bstack11l111_opy_ (u"ࠧࡴࡥࡨࡲࡦࡸࡩࡰࠩ౜")) else context.feature
    bstack11l11ll1l1_opy_(runner, name, context, target, bstack11ll11l1l_opy_, *args)
    threading.current_thread().current_test_uuid = None
def bstack11l1111l_opy_(runner, name, context, bstack11ll11l1l_opy_, *args):
    try:
      bstack11l1llll1_opy_ = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧౝ"), context.browser)
      bstack11l1111l1l_opy_ = bstack11l111_opy_ (u"ࠩࠪ౞")
      if context.failed is True:
        bstack111111ll1_opy_ = []
        bstack1l1l11l1l_opy_ = []
        bstack11ll1l11l1_opy_ = []
        try:
          import traceback
          for exc in runner.exception_arr:
            bstack111111ll1_opy_.append(exc.__class__.__name__)
          for exc_tb in runner.exc_traceback_arr:
            bstack11l1ll1lll_opy_ = traceback.format_tb(exc_tb)
            bstack1l1l11l1l1_opy_ = bstack11l111_opy_ (u"ࠪࠤࠬ౟").join(bstack11l1ll1lll_opy_)
            bstack1l1l11l1l_opy_.append(bstack1l1l11l1l1_opy_)
            bstack11ll1l11l1_opy_.append(bstack11l1ll1lll_opy_[-1])
        except Exception as e:
          logger.debug(bstack1lll1l11ll_opy_.format(str(e)))
        bstack111llll1l_opy_ = bstack11l111_opy_ (u"ࠫࠬౠ")
        for i in range(len(bstack111111ll1_opy_)):
          bstack111llll1l_opy_ += bstack111111ll1_opy_[i] + bstack11ll1l11l1_opy_[i] + bstack11l111_opy_ (u"ࠬࡢ࡮ࠨౡ")
        bstack11l1111l1l_opy_ = bstack11l111_opy_ (u"࠭ࠠࠨౢ").join(bstack1l1l11l1l_opy_)
        if runner.driver_initialised in [bstack11l111_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡧࡧࡤࡸࡺࡸࡥࠣౣ"), bstack11l111_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࠧ౤")]:
          bstack1lll1111_opy_(context, bstack11l1111l1l_opy_, bstack11l111_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣ౥"))
          bstack11lll111_opy_(getattr(context, bstack11l111_opy_ (u"ࠪࡴࡦ࡭ࡥࠨ౦"), None), bstack11l111_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦ౧"), bstack111llll1l_opy_)
          bstack11l1llll1_opy_.execute_script(bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡨࡦࡺࡡࠣ࠼ࠪ౨") + json.dumps(bstack11l1111l1l_opy_) + bstack11l111_opy_ (u"࠭ࠬࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦࡪࡸࡲࡰࡴࠥࢁࢂ࠭౩"))
          bstack1ll11l1ll1_opy_(bstack11l1llll1_opy_, bstack11l111_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢ౪"), bstack11l111_opy_ (u"ࠣࡕࡲࡱࡪࠦࡳࡤࡧࡱࡥࡷ࡯࡯ࡴࠢࡩࡥ࡮ࡲࡥࡥ࠼ࠣࡠࡳࠨ౫") + str(bstack111llll1l_opy_))
          bstack1ll11l11ll_opy_ = bstack1ll11l1l_opy_(bstack11l1111l1l_opy_, runner.feature.name, logger)
          if (bstack1ll11l11ll_opy_ != None):
            bstack1l11llll1_opy_.append(bstack1ll11l11ll_opy_)
      else:
        if runner.driver_initialised in [bstack11l111_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡩࡩࡦࡺࡵࡳࡧࠥ౬"), bstack11l111_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡥࡱࡲࠢ౭")]:
          bstack1lll1111_opy_(context, bstack11l111_opy_ (u"ࠦࡋ࡫ࡡࡵࡷࡵࡩ࠿ࠦࠢ౮") + str(runner.feature.name) + bstack11l111_opy_ (u"ࠧࠦࡰࡢࡵࡶࡩࡩࠧࠢ౯"), bstack11l111_opy_ (u"ࠨࡩ࡯ࡨࡲࠦ౰"))
          bstack11lll111_opy_(getattr(context, bstack11l111_opy_ (u"ࠧࡱࡣࡪࡩࠬ౱"), None), bstack11l111_opy_ (u"ࠣࡲࡤࡷࡸ࡫ࡤࠣ౲"))
          bstack11l1llll1_opy_.execute_script(bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡥࡣࡷࡥࠧࡀࠧ౳") + json.dumps(bstack11l111_opy_ (u"ࠥࡊࡪࡧࡴࡶࡴࡨ࠾ࠥࠨ౴") + str(runner.feature.name) + bstack11l111_opy_ (u"ࠦࠥࡶࡡࡴࡵࡨࡨࠦࠨ౵")) + bstack11l111_opy_ (u"ࠬ࠲ࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥ࡭ࡳ࡬࡯ࠣࡿࢀࠫ౶"))
          bstack1ll11l1ll1_opy_(bstack11l1llll1_opy_, bstack11l111_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭౷"))
          bstack1ll11l11ll_opy_ = bstack1ll11l1l_opy_(bstack11l1111l1l_opy_, runner.feature.name, logger)
          if (bstack1ll11l11ll_opy_ != None):
            bstack1l11llll1_opy_.append(bstack1ll11l11ll_opy_)
    except Exception as e:
      logger.debug(bstack11l111_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡱࡦࡸ࡫ࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡶࡸࡦࡺࡵࡴࠢ࡬ࡲࠥࡧࡦࡵࡧࡵࠤ࡫࡫ࡡࡵࡷࡵࡩ࠿ࠦࡻࡾࠩ౸").format(str(e)))
    bstack11l11ll1l1_opy_(runner, name, context, context.feature, bstack11ll11l1l_opy_, *args)
@measure(event_name=EVENTS.bstack11l1ll1ll1_opy_, stage=STAGE.bstack1l1l111l1_opy_, hook_type=bstack11l111_opy_ (u"ࠣࡣࡩࡸࡪࡸࡁ࡭࡮ࠥ౹"), bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack1l111llll1_opy_(runner, name, context, bstack11ll11l1l_opy_, *args):
    bstack11l11ll1l1_opy_(runner, name, context, runner, bstack11ll11l1l_opy_, *args)
def bstack1l1ll1l1ll_opy_(self, name, context, *args):
  try:
    if bstack111111l11_opy_:
      platform_index = int(threading.current_thread()._name) % bstack1l1ll1lll_opy_
      bstack1l1l1111ll_opy_ = CONFIG[bstack11l111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ౺")][platform_index]
      os.environ[bstack11l111_opy_ (u"ࠪࡇ࡚ࡘࡒࡆࡐࡗࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡄࡂࡖࡄࠫ౻")] = json.dumps(bstack1l1l1111ll_opy_)
    global bstack11ll11l1l_opy_
    if not hasattr(self, bstack11l111_opy_ (u"ࠫࡩࡸࡩࡷࡧࡵࡣ࡮ࡴࡩࡵ࡫ࡤࡰ࡮ࡹࡥࡥࠩ౼")):
      self.driver_initialised = None
    bstack1l11ll11l1_opy_ = {
        bstack11l111_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࡤࡧ࡬࡭ࠩ౽"): bstack1lll1ll1l1_opy_,
        bstack11l111_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪࡥࡦࡦࡣࡷࡹࡷ࡫ࠧ౾"): bstack1l111ll1_opy_,
        bstack11l111_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫࡟ࡵࡣࡪࠫ౿"): bstack1ll11111l1_opy_,
        bstack11l111_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡵࡦࡩࡳࡧࡲࡪࡱࠪಀ"): bstack1l1l11l1ll_opy_,
        bstack11l111_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡶࡸࡪࡶࠧಁ"): bstack1l111lll_opy_,
        bstack11l111_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡶࡸࡪࡶࠧಂ"): bstack1l1ll11l_opy_,
        bstack11l111_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠬಃ"): bstack1ll1l11lll_opy_,
        bstack11l111_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣࡹࡧࡧࠨ಄"): bstack1lll1l1l1_opy_,
        bstack11l111_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤ࡬ࡥࡢࡶࡸࡶࡪ࠭ಅ"): bstack11l1111l_opy_,
        bstack11l111_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡡ࡭࡮ࠪಆ"): bstack1l111llll1_opy_
    }
    handler = bstack1l11ll11l1_opy_.get(name, bstack11ll11l1l_opy_)
    try:
      handler(self, name, context, bstack11ll11l1l_opy_, *args)
    except Exception as e:
      logger.debug(bstack11l111_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡦࡪ࡮ࡡࡷࡧࠣ࡬ࡴࡵ࡫ࠡࡪࡤࡲࡩࡲࡥࡳࠢࡾࢁ࠿ࠦࡻࡾࠩಇ").format(name, str(e)))
    if name in [bstack11l111_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡨࡨࡥࡹࡻࡲࡦࠩಈ"), bstack11l111_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠫಉ"), bstack11l111_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡥࡱࡲࠧಊ")]:
      try:
        bstack11l1llll1_opy_ = threading.current_thread().bstackSessionDriver if bstack11l1111ll_opy_(bstack11l111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫಋ")) else context.browser
        bstack11lllll1l_opy_ = (
          (name == bstack11l111_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡧ࡬࡭ࠩಌ") and self.driver_initialised == bstack11l111_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡢ࡮࡯ࠦ಍")) or
          (name == bstack11l111_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡧࡧࡤࡸࡺࡸࡥࠨಎ") and self.driver_initialised == bstack11l111_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡩࡩࡦࡺࡵࡳࡧࠥಏ")) or
          (name == bstack11l111_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠫಐ") and self.driver_initialised in [bstack11l111_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴࠨ಑"), bstack11l111_opy_ (u"ࠧ࡯࡮ࡴࡶࡨࡴࠧಒ")]) or
          (name == bstack11l111_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡹࡴࡦࡲࠪಓ") and self.driver_initialised == bstack11l111_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡶࡨࡴࠧಔ"))
        )
        if bstack11lllll1l_opy_:
          self.driver_initialised = None
          if bstack11l1llll1_opy_ and hasattr(bstack11l1llll1_opy_, bstack11l111_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠬಕ")):
            try:
              bstack11l1llll1_opy_.quit()
            except Exception as e:
              logger.debug(bstack11l111_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡࡳࡸ࡭ࡹࡺࡩ࡯ࡩࠣࡨࡷ࡯ࡶࡦࡴࠣ࡭ࡳࠦࡢࡦࡪࡤࡺࡪࠦࡨࡰࡱ࡮࠾ࠥࢁࡽࠨಖ").format(str(e)))
      except Exception as e:
        logger.debug(bstack11l111_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡧࡦࡵࡧࡵࠤ࡭ࡵ࡯࡬ࠢࡦࡰࡪࡧ࡮ࡶࡲࠣࡪࡴࡸࠠࡼࡿ࠽ࠤࢀࢃࠧಗ").format(name, str(e)))
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠫࡈࡸࡩࡵ࡫ࡦࡥࡱࠦࡥࡳࡴࡲࡶࠥ࡯࡮ࠡࡤࡨ࡬ࡦࡼࡥࠡࡴࡸࡲࠥ࡮࡯ࡰ࡭ࠣࡿࢂࡀࠠࡼࡿࠪಘ").format(name, str(e)))
    try:
      bstack11ll11l1l_opy_(self, name, context, *args)
    except Exception as e2:
      logger.debug(bstack11l111_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡧࡣ࡯ࡰࡧࡧࡣ࡬ࠢࡲࡶ࡮࡭ࡩ࡯ࡣ࡯ࠤࡧ࡫ࡨࡢࡸࡨࠤ࡭ࡵ࡯࡬ࠢࡾࢁ࠿ࠦࡻࡾࠩಙ").format(name, str(e2)))
def bstack1lll11lll1_opy_(config, startdir):
  return bstack11l111_opy_ (u"ࠨࡤࡳ࡫ࡹࡩࡷࡀࠠࡼ࠲ࢀࠦಚ").format(bstack11l111_opy_ (u"ࠢࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠨಛ"))
notset = Notset()
def bstack111ll11l1_opy_(self, name: str, default=notset, skip: bool = False):
  global bstack1lll111ll_opy_
  if str(name).lower() == bstack11l111_opy_ (u"ࠨࡦࡵ࡭ࡻ࡫ࡲࠨಜ"):
    return bstack11l111_opy_ (u"ࠤࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠣಝ")
  else:
    return bstack1lll111ll_opy_(self, name, default, skip)
def bstack1lllllllll_opy_(item, when):
  global bstack1lll11l1ll_opy_
  try:
    bstack1lll11l1ll_opy_(item, when)
  except Exception as e:
    pass
def bstack1l1ll11lll_opy_():
  return
def bstack1l11111l1_opy_(type, name, status, reason, bstack1l1lllll1_opy_, bstack1ll111l1ll_opy_):
  bstack1l111111l1_opy_ = {
    bstack11l111_opy_ (u"ࠪࡥࡨࡺࡩࡰࡰࠪಞ"): type,
    bstack11l111_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧಟ"): {}
  }
  if type == bstack11l111_opy_ (u"ࠬࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠧಠ"):
    bstack1l111111l1_opy_[bstack11l111_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩಡ")][bstack11l111_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ಢ")] = bstack1l1lllll1_opy_
    bstack1l111111l1_opy_[bstack11l111_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫಣ")][bstack11l111_opy_ (u"ࠩࡧࡥࡹࡧࠧತ")] = json.dumps(str(bstack1ll111l1ll_opy_))
  if type == bstack11l111_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫಥ"):
    bstack1l111111l1_opy_[bstack11l111_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧದ")][bstack11l111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪಧ")] = name
  if type == bstack11l111_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩನ"):
    bstack1l111111l1_opy_[bstack11l111_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪ಩")][bstack11l111_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨಪ")] = status
    if status == bstack11l111_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩಫ"):
      bstack1l111111l1_opy_[bstack11l111_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ಬ")][bstack11l111_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫಭ")] = json.dumps(str(reason))
  bstack11ll11ll1_opy_ = bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪಮ").format(json.dumps(bstack1l111111l1_opy_))
  return bstack11ll11ll1_opy_
def bstack11l1lllll1_opy_(driver_command, response):
    if driver_command == bstack11l111_opy_ (u"࠭ࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࠪಯ"):
        bstack11l11l1l_opy_.bstack11l11111ll_opy_({
            bstack11l111_opy_ (u"ࠧࡪ࡯ࡤ࡫ࡪ࠭ರ"): response[bstack11l111_opy_ (u"ࠨࡸࡤࡰࡺ࡫ࠧಱ")],
            bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩಲ"): bstack11l11l1l_opy_.current_test_uuid()
        })
def bstack1llll1ll1_opy_(item, call, rep):
  global bstack11ll11l11_opy_
  global bstack1l1ll111l1_opy_
  global bstack1l11l111l_opy_
  name = bstack11l111_opy_ (u"ࠪࠫಳ")
  try:
    if rep.when == bstack11l111_opy_ (u"ࠫࡨࡧ࡬࡭ࠩ಴"):
      bstack1l1l11ll_opy_ = threading.current_thread().bstackSessionId
      try:
        if not bstack1l11l111l_opy_:
          name = str(rep.nodeid)
          bstack1l1lll1ll1_opy_ = bstack1l11111l1_opy_(bstack11l111_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ವ"), name, bstack11l111_opy_ (u"࠭ࠧಶ"), bstack11l111_opy_ (u"ࠧࠨಷ"), bstack11l111_opy_ (u"ࠨࠩಸ"), bstack11l111_opy_ (u"ࠩࠪಹ"))
          threading.current_thread().bstack1l11l1l111_opy_ = name
          for driver in bstack1l1ll111l1_opy_:
            if bstack1l1l11ll_opy_ == driver.session_id:
              driver.execute_script(bstack1l1lll1ll1_opy_)
      except Exception as e:
        logger.debug(bstack11l111_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡹࡥࡵࡶ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠤ࡫ࡵࡲࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡹࡥࡴࡵ࡬ࡳࡳࡀࠠࡼࡿࠪ಺").format(str(e)))
      try:
        bstack1ll1l1l111_opy_(rep.outcome.lower())
        if rep.outcome.lower() != bstack11l111_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ಻"):
          status = bstack11l111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨ಼ࠬ") if rep.outcome.lower() == bstack11l111_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ಽ") else bstack11l111_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧಾ")
          reason = bstack11l111_opy_ (u"ࠨࠩಿ")
          if status == bstack11l111_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩೀ"):
            reason = rep.longrepr.reprcrash.message
            if (not threading.current_thread().bstackTestErrorMessages):
              threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(reason)
          level = bstack11l111_opy_ (u"ࠪ࡭ࡳ࡬࡯ࠨು") if status == bstack11l111_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫೂ") else bstack11l111_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫೃ")
          data = name + bstack11l111_opy_ (u"࠭ࠠࡱࡣࡶࡷࡪࡪࠡࠨೄ") if status == bstack11l111_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ೅") else name + bstack11l111_opy_ (u"ࠨࠢࡩࡥ࡮ࡲࡥࡥࠣࠣࠫೆ") + reason
          bstack11l11l1111_opy_ = bstack1l11111l1_opy_(bstack11l111_opy_ (u"ࠩࡤࡲࡳࡵࡴࡢࡶࡨࠫೇ"), bstack11l111_opy_ (u"ࠪࠫೈ"), bstack11l111_opy_ (u"ࠫࠬ೉"), bstack11l111_opy_ (u"ࠬ࠭ೊ"), level, data)
          for driver in bstack1l1ll111l1_opy_:
            if bstack1l1l11ll_opy_ == driver.session_id:
              driver.execute_script(bstack11l11l1111_opy_)
      except Exception as e:
        logger.debug(bstack11l111_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࠣࡧࡴࡴࡴࡦࡺࡷࠤ࡫ࡵࡲࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡹࡥࡴࡵ࡬ࡳࡳࡀࠠࡼࡿࠪೋ").format(str(e)))
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡪࡩࡹࡺࡩ࡯ࡩࠣࡷࡹࡧࡴࡦࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡷࡩࡸࡺࠠࡴࡶࡤࡸࡺࡹ࠺ࠡࡽࢀࠫೌ").format(str(e)))
  bstack11ll11l11_opy_(item, call, rep)
def bstack1111l11ll_opy_(driver, bstack11ll1l1l11_opy_, test=None):
  global bstack1l11l111l1_opy_
  if test != None:
    bstack1l1111l111_opy_ = getattr(test, bstack11l111_opy_ (u"ࠨࡰࡤࡱࡪ್࠭"), None)
    bstack111l11ll_opy_ = getattr(test, bstack11l111_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ೎"), None)
    PercySDK.screenshot(driver, bstack11ll1l1l11_opy_, bstack1l1111l111_opy_=bstack1l1111l111_opy_, bstack111l11ll_opy_=bstack111l11ll_opy_, bstack11llll1l1l_opy_=bstack1l11l111l1_opy_)
  else:
    PercySDK.screenshot(driver, bstack11ll1l1l11_opy_)
@measure(event_name=EVENTS.bstack1l1ll1111l_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack11111ll1l_opy_(driver):
  if bstack111111111_opy_.bstack11ll1111l1_opy_() is True or bstack111111111_opy_.capturing() is True:
    return
  bstack111111111_opy_.bstack1lll111l11_opy_()
  while not bstack111111111_opy_.bstack11ll1111l1_opy_():
    bstack1llll11lll_opy_ = bstack111111111_opy_.bstack1lll1l11l_opy_()
    bstack1111l11ll_opy_(driver, bstack1llll11lll_opy_)
  bstack111111111_opy_.bstack1l1l11ll1_opy_()
def bstack1ll1lll1l1_opy_(sequence, driver_command, response = None, bstack1l1l1ll1l_opy_ = None, args = None):
    try:
      if sequence != bstack11l111_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࠪ೏"):
        return
      if percy.bstack1l1l1ll111_opy_() == bstack11l111_opy_ (u"ࠦ࡫ࡧ࡬ࡴࡧࠥ೐"):
        return
      bstack1llll11lll_opy_ = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠬࡶࡥࡳࡥࡼࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ೑"), None)
      for command in bstack1llllll1ll_opy_:
        if command == driver_command:
          with bstack11l11l11l_opy_:
            bstack1llllllll1_opy_ = bstack1l1ll111l1_opy_.copy()
          for driver in bstack1llllllll1_opy_:
            bstack11111ll1l_opy_(driver)
      bstack1lll11lll_opy_ = percy.bstack1llll1llll_opy_()
      if driver_command in bstack11l11l111l_opy_[bstack1lll11lll_opy_]:
        bstack111111111_opy_.bstack111l11l1l_opy_(bstack1llll11lll_opy_, driver_command)
    except Exception as e:
      pass
def bstack1llllll111_opy_(framework_name):
  if bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥ࡭ࡰࡦࡢࡧࡦࡲ࡬ࡦࡦࠪ೒")):
      return
  bstack11l11ll1l_opy_.bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟࡮ࡱࡧࡣࡨࡧ࡬࡭ࡧࡧࠫ೓"), True)
  global bstack1ll1111l_opy_
  global bstack1l11lll1ll_opy_
  global bstack1l11ll1lll_opy_
  bstack1ll1111l_opy_ = framework_name
  logger.info(bstack1l1llll1l_opy_.format(bstack1ll1111l_opy_.split(bstack11l111_opy_ (u"ࠨ࠯ࠪ೔"))[0]))
  bstack1lll11l1_opy_()
  try:
    from selenium import webdriver
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
    if bstack111111l11_opy_:
      Service.start = bstack11111l1l_opy_
      Service.stop = bstack1111111ll_opy_
      webdriver.Remote.get = bstack1l1ll111_opy_
      WebDriver.quit = bstack1ll11l1l1l_opy_
      webdriver.Remote.__init__ = bstack1111ll111_opy_
    if not bstack111111l11_opy_:
        webdriver.Remote.__init__ = bstack1ll1ll11_opy_
    WebDriver.getAccessibilityResults = getAccessibilityResults
    WebDriver.get_accessibility_results = getAccessibilityResults
    WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
    WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
    WebDriver.performScan = perform_scan
    WebDriver.perform_scan = perform_scan
    WebDriver.execute = bstack1l1ll1llll_opy_
    bstack1l11lll1ll_opy_ = True
  except Exception as e:
    pass
  try:
    if bstack111111l11_opy_:
      from QWeb.keywords import browser
      browser.close_browser = bstack11l11llll_opy_
  except Exception as e:
    pass
  bstack1l11l11lll_opy_()
  if not bstack1l11lll1ll_opy_:
    bstack11l1lll11l_opy_(bstack11l111_opy_ (u"ࠤࡓࡥࡨࡱࡡࡨࡧࡶࠤࡳࡵࡴࠡ࡫ࡱࡷࡹࡧ࡬࡭ࡧࡧࠦೕ"), bstack1ll11ll111_opy_)
  if bstack1lllll11_opy_():
    try:
      from selenium.webdriver.remote.remote_connection import RemoteConnection
      if hasattr(RemoteConnection, bstack11l111_opy_ (u"ࠪࡣ࡬࡫ࡴࡠࡲࡵࡳࡽࡿ࡟ࡶࡴ࡯ࠫೖ")) and callable(getattr(RemoteConnection, bstack11l111_opy_ (u"ࠫࡤ࡭ࡥࡵࡡࡳࡶࡴࡾࡹࡠࡷࡵࡰࠬ೗"))):
        RemoteConnection._get_proxy_url = bstack1ll1ll111_opy_
      else:
        from selenium.webdriver.remote.client_config import ClientConfig
        ClientConfig.get_proxy_url = bstack1ll1ll111_opy_
    except Exception as e:
      logger.error(bstack1lll1l111l_opy_.format(str(e)))
  if bstack11l1lll1l_opy_():
    bstack11llll111_opy_(CONFIG, logger)
  if (bstack11l111_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫ೘") in str(framework_name).lower()):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        if percy.bstack1l1l1ll111_opy_() == bstack11l111_opy_ (u"ࠨࡴࡳࡷࡨࠦ೙"):
          bstack1l111111_opy_(bstack1ll1lll1l1_opy_)
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack1llll1lll1_opy_
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCache.close = bstack11111l1ll_opy_
      except Exception as e:
        logger.warn(bstack1lll111l1_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        ApplicationCache.close = bstack1l1llll11l_opy_
      except Exception as e:
        logger.debug(bstack11l1l111ll_opy_ + str(e))
    except Exception as e:
      bstack11l1lll11l_opy_(e, bstack1lll111l1_opy_)
    Output.start_test = bstack111l1ll11_opy_
    Output.end_test = bstack111ll1l1_opy_
    TestStatus.__init__ = bstack1ll1l1lll_opy_
    QueueItem.__init__ = bstack1llll1l111_opy_
    pabot._create_items = bstack1llll111ll_opy_
    try:
      from pabot import __version__ as bstack1ll1l11ll1_opy_
      if version.parse(bstack1ll1l11ll1_opy_) >= version.parse(bstack11l111_opy_ (u"ࠧ࠶࠰࠳࠲࠵࠭೚")):
        pabot._run = bstack1l1ll1ll11_opy_
      elif version.parse(bstack1ll1l11ll1_opy_) >= version.parse(bstack11l111_opy_ (u"ࠨ࠶࠱࠶࠳࠶ࠧ೛")):
        pabot._run = bstack11lll1ll1_opy_
      elif version.parse(bstack1ll1l11ll1_opy_) >= version.parse(bstack11l111_opy_ (u"ࠩ࠵࠲࠶࠻࠮࠱ࠩ೜")):
        pabot._run = bstack1l1llll1ll_opy_
      elif version.parse(bstack1ll1l11ll1_opy_) >= version.parse(bstack11l111_opy_ (u"ࠪ࠶࠳࠷࠳࠯࠲ࠪೝ")):
        pabot._run = bstack111ll1ll_opy_
      else:
        pabot._run = bstack1l1l1ll11_opy_
    except Exception as e:
      pabot._run = bstack1l1l1ll11_opy_
    pabot._create_command_for_execution = bstack1lll11111_opy_
    pabot._report_results = bstack1llll11l1_opy_
  if bstack11l111_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫೞ") in str(framework_name).lower():
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack11l1lll11l_opy_(e, bstack111lll1ll_opy_)
    Runner.run_hook = bstack1l1ll1l1ll_opy_
    Step.run = bstack1l111l1l1_opy_
  if bstack11l111_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ೟") in str(framework_name).lower():
    if not bstack111111l11_opy_:
      return
    try:
      from pytest_selenium import pytest_selenium
      from _pytest.config import Config
      pytest_selenium.pytest_report_header = bstack1lll11lll1_opy_
      from pytest_selenium.drivers import browserstack
      browserstack.pytest_selenium_runtest_makereport = bstack1l1ll11lll_opy_
      Config.getoption = bstack111ll11l1_opy_
    except Exception as e:
      pass
    try:
      from pytest_bdd import reporting
      reporting.runtest_makereport = bstack1llll1ll1_opy_
    except Exception as e:
      pass
def bstack1l111l111l_opy_():
  global CONFIG
  if bstack11l111_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭ೠ") in CONFIG and int(CONFIG[bstack11l111_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧೡ")]) > 1:
    logger.warn(bstack11l111l11_opy_)
def bstack11l11l11ll_opy_(arg, bstack11lll1111_opy_, bstack1ll1l1llll_opy_=None):
  global CONFIG
  global bstack1l1l11lll1_opy_
  global bstack1l1l1l11_opy_
  global bstack111111l11_opy_
  global bstack11l11ll1l_opy_
  bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨೢ")
  if bstack11lll1111_opy_ and isinstance(bstack11lll1111_opy_, str):
    bstack11lll1111_opy_ = eval(bstack11lll1111_opy_)
  CONFIG = bstack11lll1111_opy_[bstack11l111_opy_ (u"ࠩࡆࡓࡓࡌࡉࡈࠩೣ")]
  bstack1l1l11lll1_opy_ = bstack11lll1111_opy_[bstack11l111_opy_ (u"ࠪࡌ࡚ࡈ࡟ࡖࡔࡏࠫ೤")]
  bstack1l1l1l11_opy_ = bstack11lll1111_opy_[bstack11l111_opy_ (u"ࠫࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭೥")]
  bstack111111l11_opy_ = bstack11lll1111_opy_[bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆ࡛ࡔࡐࡏࡄࡘࡎࡕࡎࠨ೦")]
  bstack11l11ll1l_opy_.bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡳࡦࡵࡶ࡭ࡴࡴࠧ೧"), bstack111111l11_opy_)
  os.environ[bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠩ೨")] = bstack1l1ll111l_opy_
  os.environ[bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍࠧ೩")] = json.dumps(CONFIG)
  os.environ[bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡊࡘࡆࡤ࡛ࡒࡍࠩ೪")] = bstack1l1l11lll1_opy_
  os.environ[bstack11l111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡌࡗࡤࡇࡐࡑࡡࡄ࡙࡙ࡕࡍࡂࡖࡈࠫ೫")] = str(bstack1l1l1l11_opy_)
  os.environ[bstack11l111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔ࡞࡚ࡅࡔࡖࡢࡔࡑ࡛ࡇࡊࡐࠪ೬")] = str(True)
  if bstack11llll1l_opy_(arg, [bstack11l111_opy_ (u"ࠬ࠳࡮ࠨ೭"), bstack11l111_opy_ (u"࠭࠭࠮ࡰࡸࡱࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠧ೮")]) != -1:
    os.environ[bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐ࡚ࡖࡈࡗ࡙ࡥࡐࡂࡔࡄࡐࡑࡋࡌࠨ೯")] = str(True)
  if len(sys.argv) <= 1:
    logger.critical(bstack11l11lll1_opy_)
    return
  bstack1l1ll1lll1_opy_()
  global bstack1l111l1ll1_opy_
  global bstack1l11l111l1_opy_
  global bstack111lllllll_opy_
  global bstack11l1l1l111_opy_
  global bstack1l1ll1ll_opy_
  global bstack1l11ll1lll_opy_
  global bstack1ll1ll1ll_opy_
  arg.append(bstack11l111_opy_ (u"ࠣ࠯࡚ࠦ೰"))
  arg.append(bstack11l111_opy_ (u"ࠤ࡬࡫ࡳࡵࡲࡦ࠼ࡐࡳࡩࡻ࡬ࡦࠢࡤࡰࡷ࡫ࡡࡥࡻࠣ࡭ࡲࡶ࡯ࡳࡶࡨࡨ࠿ࡶࡹࡵࡧࡶࡸ࠳ࡖࡹࡵࡧࡶࡸ࡜ࡧࡲ࡯࡫ࡱ࡫ࠧೱ"))
  arg.append(bstack11l111_opy_ (u"ࠥ࠱࡜ࠨೲ"))
  arg.append(bstack11l111_opy_ (u"ࠦ࡮࡭࡮ࡰࡴࡨ࠾࡙࡮ࡥࠡࡪࡲࡳࡰ࡯࡭ࡱ࡮ࠥೳ"))
  global bstack1l1l1l1l_opy_
  global bstack11lll1l1_opy_
  global bstack1l11ll1ll1_opy_
  global bstack1l11ll1111_opy_
  global bstack11lll1l1ll_opy_
  global bstack1lll1lll1l_opy_
  global bstack1l11111l_opy_
  global bstack11ll111lll_opy_
  global bstack1l1111llll_opy_
  global bstack1ll1lll11_opy_
  global bstack1lll111ll_opy_
  global bstack1lll11l1ll_opy_
  global bstack11ll11l11_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack1l1l1l1l_opy_ = webdriver.Remote.__init__
    bstack11lll1l1_opy_ = WebDriver.quit
    bstack11ll111lll_opy_ = WebDriver.close
    bstack1l1111llll_opy_ = WebDriver.get
    bstack1l11ll1ll1_opy_ = WebDriver.execute
  except Exception as e:
    pass
  if bstack11lll1ll_opy_(CONFIG) and bstack1l1lll1l1_opy_():
    if bstack1lllll1l1_opy_() < version.parse(bstack1lll1l1l1l_opy_):
      logger.error(bstack1ll1l1l1_opy_.format(bstack1lllll1l1_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        if hasattr(RemoteConnection, bstack11l111_opy_ (u"ࠬࡥࡧࡦࡶࡢࡴࡷࡵࡸࡺࡡࡸࡶࡱ࠭೴")) and callable(getattr(RemoteConnection, bstack11l111_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧ೵"))):
          bstack1ll1lll11_opy_ = RemoteConnection._get_proxy_url
        else:
          from selenium.webdriver.remote.client_config import ClientConfig
          bstack1ll1lll11_opy_ = ClientConfig.get_proxy_url
      except Exception as e:
        logger.error(bstack1lll1l111l_opy_.format(str(e)))
  try:
    from _pytest.config import Config
    bstack1lll111ll_opy_ = Config.getoption
    from _pytest import runner
    bstack1lll11l1ll_opy_ = runner._update_current_test_var
  except Exception as e:
    logger.warn(e, bstack111l1l111_opy_)
  try:
    from pytest_bdd import reporting
    bstack11ll11l11_opy_ = reporting.runtest_makereport
  except Exception as e:
    logger.debug(bstack11l111_opy_ (u"ࠧࡑ࡮ࡨࡥࡸ࡫ࠠࡪࡰࡶࡸࡦࡲ࡬ࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡺ࡯ࠡࡴࡸࡲࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡷࡩࡸࡺࡳࠨ೶"))
  bstack111lllllll_opy_ = CONFIG.get(bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ೷"), {}).get(bstack11l111_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ೸"))
  bstack1ll1ll1ll_opy_ = True
  if cli.is_enabled(CONFIG):
    if cli.bstack11llll11_opy_():
      bstack11111l1l1_opy_.invoke(bstack1llllll11l_opy_.CONNECT, bstack11ll11l11l_opy_())
    platform_index = int(os.environ.get(bstack11l111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪ೹"), bstack11l111_opy_ (u"ࠫ࠵࠭೺")))
  else:
    bstack1llllll111_opy_(bstack1111111l1_opy_)
  os.environ[bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡚࡙ࡅࡓࡐࡄࡑࡊ࠭೻")] = CONFIG[bstack11l111_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨ೼")]
  os.environ[bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡄࡅࡈࡗࡘࡥࡋࡆ࡛ࠪ೽")] = CONFIG[bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ೾")]
  os.environ[bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡘࡘࡔࡓࡁࡕࡋࡒࡒࠬ೿")] = bstack111111l11_opy_.__str__()
  from _pytest.config import main as bstack1l1ll1ll1_opy_
  bstack1l1l11l11l_opy_ = []
  try:
    exit_code = bstack1l1ll1ll1_opy_(arg)
    if cli.is_enabled(CONFIG):
      cli.bstack111l11ll1_opy_()
    if bstack11l111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺࠧഀ") in multiprocessing.current_process().__dict__.keys():
      for bstack111lll11ll_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack1l1l11l11l_opy_.append(bstack111lll11ll_opy_)
    try:
      bstack1ll1l1l11l_opy_ = (bstack1l1l11l11l_opy_, int(exit_code))
      bstack1ll1l1llll_opy_.append(bstack1ll1l1l11l_opy_)
    except:
      bstack1ll1l1llll_opy_.append((bstack1l1l11l11l_opy_, exit_code))
  except Exception as e:
    logger.error(traceback.format_exc())
    bstack1l1l11l11l_opy_.append({bstack11l111_opy_ (u"ࠫࡳࡧ࡭ࡦࠩഁ"): bstack11l111_opy_ (u"ࠬࡖࡲࡰࡥࡨࡷࡸࠦࠧം") + os.environ.get(bstack11l111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ഃ")), bstack11l111_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ഄ"): traceback.format_exc(), bstack11l111_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧഅ"): int(os.environ.get(bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩആ")))})
    bstack1ll1l1llll_opy_.append((bstack1l1l11l11l_opy_, 1))
def mod_behave_main(args, retries):
  try:
    from behave.configuration import Configuration
    from behave.__main__ import run_behave
    from browserstack_sdk.bstack_behave_runner import BehaveRunner
    config = Configuration(args)
    config.update_userdata({bstack11l111_opy_ (u"ࠥࡶࡪࡺࡲࡪࡧࡶࠦഇ"): str(retries)})
    return run_behave(config, runner_class=BehaveRunner)
  except Exception as e:
    bstack1lllll1ll1_opy_ = e.__class__.__name__
    print(bstack11l111_opy_ (u"ࠦࠪࡹ࠺ࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡳࡷࡱࡲ࡮ࡴࡧࠡࡤࡨ࡬ࡦࡼࡥࠡࡶࡨࡷࡹࠦࠥࡴࠤഈ") % (bstack1lllll1ll1_opy_, e))
    return 1
def bstack11ll1l1ll_opy_(arg):
  global bstack11l1ll111l_opy_
  bstack1llllll111_opy_(bstack11lllll111_opy_)
  os.environ[bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭ഉ")] = str(bstack1l1l1l11_opy_)
  retries = bstack1l1ll1ll1l_opy_.bstack111lll11l_opy_(CONFIG)
  status_code = 0
  if bstack1l1ll1ll1l_opy_.bstack1l1llll1_opy_(CONFIG):
    status_code = mod_behave_main(arg, retries)
  else:
    from behave.__main__ import main as bstack111llllll1_opy_
    status_code = bstack111llllll1_opy_(arg)
  if status_code != 0:
    bstack11l1ll111l_opy_ = status_code
def bstack1l1lllll_opy_():
  logger.info(bstack1ll11111l_opy_)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(bstack11l111_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬഊ"), help=bstack11l111_opy_ (u"ࠧࡈࡧࡱࡩࡷࡧࡴࡦࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡥࡲࡲ࡫࡯ࡧࠨഋ"))
  parser.add_argument(bstack11l111_opy_ (u"ࠨ࠯ࡸࠫഌ"), bstack11l111_opy_ (u"ࠩ࠰࠱ࡺࡹࡥࡳࡰࡤࡱࡪ࠭഍"), help=bstack11l111_opy_ (u"ࠪ࡝ࡴࡻࡲࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡶࡵࡨࡶࡳࡧ࡭ࡦࠩഎ"))
  parser.add_argument(bstack11l111_opy_ (u"ࠫ࠲ࡱࠧഏ"), bstack11l111_opy_ (u"ࠬ࠳࠭࡬ࡧࡼࠫഐ"), help=bstack11l111_opy_ (u"࡙࠭ࡰࡷࡵࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡥࡨࡩࡥࡴࡵࠣ࡯ࡪࡿࠧ഑"))
  parser.add_argument(bstack11l111_opy_ (u"ࠧ࠮ࡨࠪഒ"), bstack11l111_opy_ (u"ࠨ࠯࠰ࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ഓ"), help=bstack11l111_opy_ (u"ࠩ࡜ࡳࡺࡸࠠࡵࡧࡶࡸࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨഔ"))
  bstack1l1llll111_opy_ = parser.parse_args()
  try:
    bstack1111l1l1_opy_ = bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡪࡩࡳ࡫ࡲࡪࡥ࠱ࡽࡲࡲ࠮ࡴࡣࡰࡴࡱ࡫ࠧക")
    if bstack1l1llll111_opy_.framework and bstack1l1llll111_opy_.framework not in (bstack11l111_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫഖ"), bstack11l111_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲ࠸࠭ഗ")):
      bstack1111l1l1_opy_ = bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠯ࡻࡰࡰ࠳ࡹࡡ࡮ࡲ࡯ࡩࠬഘ")
    bstack11ll111ll_opy_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1111l1l1_opy_)
    bstack11ll11l1_opy_ = open(bstack11ll111ll_opy_, bstack11l111_opy_ (u"ࠧࡳࠩങ"))
    bstack11l11ll11_opy_ = bstack11ll11l1_opy_.read()
    bstack11ll11l1_opy_.close()
    if bstack1l1llll111_opy_.username:
      bstack11l11ll11_opy_ = bstack11l11ll11_opy_.replace(bstack11l111_opy_ (u"ࠨ࡛ࡒ࡙ࡗࡥࡕࡔࡇࡕࡒࡆࡓࡅࠨച"), bstack1l1llll111_opy_.username)
    if bstack1l1llll111_opy_.key:
      bstack11l11ll11_opy_ = bstack11l11ll11_opy_.replace(bstack11l111_opy_ (u"ࠩ࡜ࡓ࡚ࡘ࡟ࡂࡅࡆࡉࡘ࡙࡟ࡌࡇ࡜ࠫഛ"), bstack1l1llll111_opy_.key)
    if bstack1l1llll111_opy_.framework:
      bstack11l11ll11_opy_ = bstack11l11ll11_opy_.replace(bstack11l111_opy_ (u"ࠪ࡝ࡔ࡛ࡒࡠࡈࡕࡅࡒࡋࡗࡐࡔࡎࠫജ"), bstack1l1llll111_opy_.framework)
    file_name = bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡽࡲࡲࠧഝ")
    file_path = os.path.abspath(file_name)
    bstack1ll1l1l11_opy_ = open(file_path, bstack11l111_opy_ (u"ࠬࡽࠧഞ"))
    bstack1ll1l1l11_opy_.write(bstack11l11ll11_opy_)
    bstack1ll1l1l11_opy_.close()
    logger.info(bstack1lll1l1l11_opy_)
    try:
      os.environ[bstack11l111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࠨട")] = bstack1l1llll111_opy_.framework if bstack1l1llll111_opy_.framework != None else bstack11l111_opy_ (u"ࠢࠣഠ")
      config = yaml.safe_load(bstack11l11ll11_opy_)
      config[bstack11l111_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨഡ")] = bstack11l111_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯࠯ࡶࡩࡹࡻࡰࠨഢ")
      bstack1l11llll_opy_(bstack11l111lll1_opy_, config)
    except Exception as e:
      logger.debug(bstack111111l1l_opy_.format(str(e)))
  except Exception as e:
    logger.error(bstack111l11lll_opy_.format(str(e)))
def bstack1l11llll_opy_(bstack1l111llll_opy_, config, bstack1ll111111_opy_={}):
  global bstack111111l11_opy_
  global bstack11ll1l11ll_opy_
  global bstack11l11ll1l_opy_
  if not config:
    return
  bstack111l111l_opy_ = bstack11llll1ll1_opy_ if not bstack111111l11_opy_ else (
    bstack11l1l1111l_opy_ if bstack11l111_opy_ (u"ࠪࡥࡵࡶࠧണ") in config else (
        bstack1l11ll1l11_opy_ if config.get(bstack11l111_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨത")) else bstack111lll1lll_opy_
    )
)
  bstack1l11llll11_opy_ = False
  bstack1ll1ll11l_opy_ = False
  if bstack111111l11_opy_ is True:
      if bstack11l111_opy_ (u"ࠬࡧࡰࡱࠩഥ") in config:
          bstack1l11llll11_opy_ = True
      else:
          bstack1ll1ll11l_opy_ = True
  bstack11l11lll1l_opy_ = bstack11ll11lll_opy_.bstack11ll1l111_opy_(config, bstack11ll1l11ll_opy_)
  bstack1lllll111l_opy_ = bstack1l1l1lll11_opy_()
  data = {
    bstack11l111_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨദ"): config[bstack11l111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩധ")],
    bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫന"): config[bstack11l111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬഩ")],
    bstack11l111_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧപ"): bstack1l111llll_opy_,
    bstack11l111_opy_ (u"ࠫࡩ࡫ࡴࡦࡥࡷࡩࡩࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨഫ"): os.environ.get(bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧബ"), bstack11ll1l11ll_opy_),
    bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨഭ"): bstack1l1ll11ll_opy_,
    bstack11l111_opy_ (u"ࠧࡰࡲࡷ࡭ࡲࡧ࡬ࡠࡪࡸࡦࡤࡻࡲ࡭ࠩമ"): bstack1ll1l1111_opy_(),
    bstack11l111_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡱࡴࡲࡴࡪࡸࡴࡪࡧࡶࠫയ"): {
      bstack11l111_opy_ (u"ࠩ࡯ࡥࡳ࡭ࡵࡢࡩࡨࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧര"): str(config[bstack11l111_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪറ")]) if bstack11l111_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫല") in config else bstack11l111_opy_ (u"ࠧࡻ࡮࡬ࡰࡲࡻࡳࠨള"),
      bstack11l111_opy_ (u"࠭࡬ࡢࡰࡪࡹࡦ࡭ࡥࡗࡧࡵࡷ࡮ࡵ࡮ࠨഴ"): sys.version,
      bstack11l111_opy_ (u"ࠧࡳࡧࡩࡩࡷࡸࡥࡳࠩവ"): bstack111ll11l_opy_(os.environ.get(bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࠪശ"), bstack11ll1l11ll_opy_)),
      bstack11l111_opy_ (u"ࠩ࡯ࡥࡳ࡭ࡵࡢࡩࡨࠫഷ"): bstack11l111_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪസ"),
      bstack11l111_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸࠬഹ"): bstack111l111l_opy_,
      bstack11l111_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹࡥ࡭ࡢࡲࠪഺ"): bstack11l11lll1l_opy_,
      bstack11l111_opy_ (u"࠭ࡴࡦࡵࡷ࡬ࡺࡨ࡟ࡶࡷ࡬ࡨ഻ࠬ"): os.environ[bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈ഼ࠬ")],
      bstack11l111_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫഽ"): os.environ.get(bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡈࡕࡅࡒࡋࡗࡐࡔࡎࠫാ"), bstack11ll1l11ll_opy_),
      bstack11l111_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ി"): bstack11l1111l11_opy_(os.environ.get(bstack11l111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐ࠭ീ"), bstack11ll1l11ll_opy_)),
      bstack11l111_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡈࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫു"): bstack1lllll111l_opy_.get(bstack11l111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫൂ")),
      bstack11l111_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ൃ"): bstack1lllll111l_opy_.get(bstack11l111_opy_ (u"ࠨࡸࡨࡶࡸ࡯࡯࡯ࠩൄ")),
      bstack11l111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ൅"): config[bstack11l111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭െ")] if config[bstack11l111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧേ")] else bstack11l111_opy_ (u"ࠧࡻ࡮࡬ࡰࡲࡻࡳࠨൈ"),
      bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ൉"): str(config[bstack11l111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩൊ")]) if bstack11l111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪോ") in config else bstack11l111_opy_ (u"ࠤࡸࡲࡰࡴ࡯ࡸࡰࠥൌ"),
      bstack11l111_opy_ (u"ࠪࡳࡸ്࠭"): sys.platform,
      bstack11l111_opy_ (u"ࠫ࡭ࡵࡳࡵࡰࡤࡱࡪ࠭ൎ"): socket.gethostname(),
      bstack11l111_opy_ (u"ࠬࡹࡤ࡬ࡔࡸࡲࡎࡪࠧ൏"): bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"࠭ࡳࡥ࡭ࡕࡹࡳࡏࡤࠨ൐"))
    }
  }
  if not bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠧࡴࡦ࡮ࡏ࡮ࡲ࡬ࡔ࡫ࡪࡲࡦࡲࠧ൑")) is None:
    data[bstack11l111_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡱࡴࡲࡴࡪࡸࡴࡪࡧࡶࠫ൒")][bstack11l111_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡑࡪࡺࡡࡥࡣࡷࡥࠬ൓")] = {
      bstack11l111_opy_ (u"ࠪࡶࡪࡧࡳࡰࡰࠪൔ"): bstack11l111_opy_ (u"ࠫࡺࡹࡥࡳࡡ࡮࡭ࡱࡲࡥࡥࠩൕ"),
      bstack11l111_opy_ (u"ࠬࡹࡩࡨࡰࡤࡰࠬൖ"): bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"࠭ࡳࡥ࡭ࡎ࡭ࡱࡲࡓࡪࡩࡱࡥࡱ࠭ൗ")),
      bstack11l111_opy_ (u"ࠧࡴ࡫ࡪࡲࡦࡲࡎࡶ࡯ࡥࡩࡷ࠭൘"): bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠨࡵࡧ࡯ࡐ࡯࡬࡭ࡐࡲࠫ൙"))
    }
  if bstack1l111llll_opy_ == bstack1ll1l11l1l_opy_:
    data[bstack11l111_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡲࡵࡳࡵ࡫ࡲࡵ࡫ࡨࡷࠬ൚")][bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡅࡲࡲ࡫࡯ࡧࠨ൛")] = bstack1l11lll11l_opy_(config)
    data[bstack11l111_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧ൜")][bstack11l111_opy_ (u"ࠬ࡯ࡳࡑࡧࡵࡧࡾࡇࡵࡵࡱࡈࡲࡦࡨ࡬ࡦࡦࠪ൝")] = percy.bstack1l1ll11l1l_opy_
    data[bstack11l111_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡶࡲࡰࡲࡨࡶࡹ࡯ࡥࡴࠩ൞")][bstack11l111_opy_ (u"ࠧࡱࡧࡵࡧࡾࡈࡵࡪ࡮ࡧࡍࡩ࠭ൟ")] = percy.percy_build_id
  if not bstack1l1ll1ll1l_opy_.bstack1l1l1l11ll_opy_(CONFIG):
    data[bstack11l111_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡱࡴࡲࡴࡪࡸࡴࡪࡧࡶࠫൠ")][bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࠭ൡ")] = bstack1l1ll1ll1l_opy_.bstack1l1l1l11ll_opy_(CONFIG)
  bstack1lll1ll11_opy_ = bstack1ll1l11l11_opy_.bstack111llll1_opy_(CONFIG, logger)
  bstack1llll11ll_opy_ = bstack1l1ll1ll1l_opy_.bstack111llll1_opy_(config=CONFIG)
  if bstack1lll1ll11_opy_ is not None and bstack1llll11ll_opy_ is not None and bstack1llll11ll_opy_.bstack1l11111l11_opy_():
    data[bstack11l111_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡳࡶࡴࡶࡥࡳࡶ࡬ࡩࡸ࠭ൢ")][bstack1llll11ll_opy_.bstack1l11111ll_opy_()] = bstack1lll1ll11_opy_.bstack1ll1l11l1_opy_()
  update(data[bstack11l111_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧൣ")], bstack1ll111111_opy_)
  try:
    response = bstack111lllll1l_opy_(bstack11l111_opy_ (u"ࠬࡖࡏࡔࡖࠪ൤"), bstack1l1l1111l1_opy_(bstack11lll111l1_opy_), data, {
      bstack11l111_opy_ (u"࠭ࡡࡶࡶ࡫ࠫ൥"): (config[bstack11l111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ൦")], config[bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ൧")])
    })
    if response:
      logger.debug(bstack1l11l1l1_opy_.format(bstack1l111llll_opy_, str(response.json())))
  except Exception as e:
    logger.debug(bstack11l1l1ll1_opy_.format(str(e)))
def bstack111ll11l_opy_(framework):
  return bstack11l111_opy_ (u"ࠤࡾࢁ࠲ࡶࡹࡵࡪࡲࡲࡦ࡭ࡥ࡯ࡶ࠲ࡿࢂࠨ൨").format(str(framework), __version__) if framework else bstack11l111_opy_ (u"ࠥࡴࡾࡺࡨࡰࡰࡤ࡫ࡪࡴࡴ࠰ࡽࢀࠦ൩").format(
    __version__)
def bstack1l1ll1lll1_opy_():
  global CONFIG
  global bstack1l1ll1l111_opy_
  if bool(CONFIG):
    return
  try:
    bstack1l1111111l_opy_()
    logger.debug(bstack11l1l11lll_opy_.format(str(CONFIG)))
    bstack1l1ll1l111_opy_ = bstack11l111111l_opy_.configure_logger(CONFIG, bstack1l1ll1l111_opy_)
    bstack1lll11l1_opy_()
  except Exception as e:
    logger.error(bstack11l111_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡧࡷࡹࡵ࠲ࠠࡦࡴࡵࡳࡷࡀࠠࠣ൪") + str(e))
    sys.exit(1)
  sys.excepthook = bstack1ll11l1111_opy_
  atexit.register(bstack1ll11ll1ll_opy_)
  signal.signal(signal.SIGINT, bstack111l1ll1_opy_)
  signal.signal(signal.SIGTERM, bstack111l1ll1_opy_)
def bstack1ll11l1111_opy_(exctype, value, traceback):
  global bstack1l1ll111l1_opy_
  try:
    for driver in bstack1l1ll111l1_opy_:
      bstack1ll11l1ll1_opy_(driver, bstack11l111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ൫"), bstack11l111_opy_ (u"ࠨࡓࡦࡵࡶ࡭ࡴࡴࠠࡧࡣ࡬ࡰࡪࡪࠠࡸ࡫ࡷ࡬࠿ࠦ࡜࡯ࠤ൬") + str(value))
  except Exception:
    pass
  logger.info(bstack1lll1111l_opy_)
  bstack111l1111l_opy_(value, True)
  sys.__excepthook__(exctype, value, traceback)
  sys.exit(1)
def bstack111l1111l_opy_(message=bstack11l111_opy_ (u"ࠧࠨ൭"), bstack11lllllll_opy_ = False):
  global CONFIG
  bstack1lll11ll1l_opy_ = bstack11l111_opy_ (u"ࠨࡩ࡯ࡳࡧࡧ࡬ࡆࡺࡦࡩࡵࡺࡩࡰࡰࠪ൮") if bstack11lllllll_opy_ else bstack11l111_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨ൯")
  try:
    if message:
      bstack1ll111111_opy_ = {
        bstack1lll11ll1l_opy_ : str(message)
      }
      bstack1l11llll_opy_(bstack1ll1l11l1l_opy_, CONFIG, bstack1ll111111_opy_)
    else:
      bstack1l11llll_opy_(bstack1ll1l11l1l_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack1ll11111ll_opy_.format(str(e)))
def bstack1l11l1ll11_opy_(bstack1lllll1lll_opy_, size):
  bstack1l1lll11l1_opy_ = []
  while len(bstack1lllll1lll_opy_) > size:
    bstack1lll1lllll_opy_ = bstack1lllll1lll_opy_[:size]
    bstack1l1lll11l1_opy_.append(bstack1lll1lllll_opy_)
    bstack1lllll1lll_opy_ = bstack1lllll1lll_opy_[size:]
  bstack1l1lll11l1_opy_.append(bstack1lllll1lll_opy_)
  return bstack1l1lll11l1_opy_
def bstack11l1111l1_opy_(args):
  if bstack11l111_opy_ (u"ࠪ࠱ࡲ࠭൰") in args and bstack11l111_opy_ (u"ࠫࡵࡪࡢࠨ൱") in args:
    return True
  return False
@measure(event_name=EVENTS.bstack1ll1111lll_opy_, stage=STAGE.bstack1llll1l1l1_opy_)
def run_on_browserstack(bstack11l111l1ll_opy_=None, bstack1ll1l1llll_opy_=None, bstack11l11l11l1_opy_=False):
  global CONFIG
  global bstack1l1l11lll1_opy_
  global bstack1l1l1l11_opy_
  global bstack11ll1l11ll_opy_
  global bstack11l11ll1l_opy_
  bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"ࠬ࠭൲")
  bstack11l11lll11_opy_(bstack1l11lll1l_opy_, logger)
  if bstack11l111l1ll_opy_ and isinstance(bstack11l111l1ll_opy_, str):
    bstack11l111l1ll_opy_ = eval(bstack11l111l1ll_opy_)
  if bstack11l111l1ll_opy_:
    CONFIG = bstack11l111l1ll_opy_[bstack11l111_opy_ (u"࠭ࡃࡐࡐࡉࡍࡌ࠭൳")]
    bstack1l1l11lll1_opy_ = bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠧࡉࡗࡅࡣ࡚ࡘࡌࠨ൴")]
    bstack1l1l1l11_opy_ = bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠨࡋࡖࡣࡆࡖࡐࡠࡃࡘࡘࡔࡓࡁࡕࡇࠪ൵")]
    bstack11l11ll1l_opy_.bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"ࠩࡌࡗࡤࡇࡐࡑࡡࡄ࡙࡙ࡕࡍࡂࡖࡈࠫ൶"), bstack1l1l1l11_opy_)
    bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪ൷")
  bstack11l11ll1l_opy_.bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"ࠫࡸࡪ࡫ࡓࡷࡱࡍࡩ࠭൸"), uuid4().__str__())
  logger.info(bstack11l111_opy_ (u"࡙ࠬࡄࡌࠢࡵࡹࡳࠦࡳࡵࡣࡵࡸࡪࡪࠠࡸ࡫ࡷ࡬ࠥ࡯ࡤ࠻ࠢࠪ൹") + bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"࠭ࡳࡥ࡭ࡕࡹࡳࡏࡤࠨൺ")));
  logger.debug(bstack11l111_opy_ (u"ࠧࡴࡦ࡮ࡖࡺࡴࡉࡥ࠿ࠪൻ") + bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠨࡵࡧ࡯ࡗࡻ࡮ࡊࡦࠪർ")))
  if not bstack11l11l11l1_opy_:
    if len(sys.argv) <= 1:
      logger.critical(bstack11l11lll1_opy_)
      return
    if sys.argv[1] == bstack11l111_opy_ (u"ࠩ࠰࠱ࡻ࡫ࡲࡴ࡫ࡲࡲࠬൽ") or sys.argv[1] == bstack11l111_opy_ (u"ࠪ࠱ࡻ࠭ൾ"):
      logger.info(bstack11l111_opy_ (u"ࠫࡇࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡔࡾࡺࡨࡰࡰࠣࡗࡉࡑࠠࡷࡽࢀࠫൿ").format(__version__))
      return
    if sys.argv[1] == bstack11l111_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫ඀"):
      bstack1l1lllll_opy_()
      return
  args = sys.argv
  bstack1l1ll1lll1_opy_()
  global bstack1l111l1ll1_opy_
  global bstack1l1ll1lll_opy_
  global bstack1ll1ll1ll_opy_
  global bstack1lll111l1l_opy_
  global bstack1l11l111l1_opy_
  global bstack111lllllll_opy_
  global bstack11l1l1l111_opy_
  global bstack1l1111l1l1_opy_
  global bstack1l1ll1ll_opy_
  global bstack1l11ll1lll_opy_
  global bstack11lll1111l_opy_
  bstack1l1ll1lll_opy_ = len(CONFIG.get(bstack11l111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩඁ"), []))
  if not bstack1l1ll111l_opy_:
    if args[1] == bstack11l111_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧං") or args[1] == bstack11l111_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮࠴ࠩඃ"):
      bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩ඄")
      args = args[2:]
    elif args[1] == bstack11l111_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩඅ"):
      bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪආ")
      args = args[2:]
    elif args[1] == bstack11l111_opy_ (u"ࠬࡶࡡࡣࡱࡷࠫඇ"):
      bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬඈ")
      args = args[2:]
    elif args[1] == bstack11l111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠳ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠨඉ"):
      bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩඊ")
      args = args[2:]
    elif args[1] == bstack11l111_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩඋ"):
      bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪඌ")
      args = args[2:]
    elif args[1] == bstack11l111_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫඍ"):
      bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬඎ")
      args = args[2:]
    else:
      if not bstack11l111_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩඏ") in CONFIG or str(CONFIG[bstack11l111_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪඐ")]).lower() in [bstack11l111_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨඑ"), bstack11l111_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯࠵ࠪඒ")]:
        bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪඓ")
        args = args[1:]
      elif str(CONFIG[bstack11l111_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧඔ")]).lower() == bstack11l111_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫඕ"):
        bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬඖ")
        args = args[1:]
      elif str(CONFIG[bstack11l111_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪ඗")]).lower() == bstack11l111_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧ඘"):
        bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨ඙")
        args = args[1:]
      elif str(CONFIG[bstack11l111_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ක")]).lower() == bstack11l111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫඛ"):
        bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬග")
        args = args[1:]
      elif str(CONFIG[bstack11l111_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩඝ")]).lower() == bstack11l111_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧඞ"):
        bstack1l1ll111l_opy_ = bstack11l111_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨඟ")
        args = args[1:]
      else:
        os.environ[bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡈࡕࡅࡒࡋࡗࡐࡔࡎࠫච")] = bstack1l1ll111l_opy_
        bstack1l1l1lll_opy_(bstack1ll1llll1_opy_)
  os.environ[bstack11l111_opy_ (u"ࠪࡊࡗࡇࡍࡆ࡙ࡒࡖࡐࡥࡕࡔࡇࡇࠫඡ")] = bstack1l1ll111l_opy_
  bstack11ll1l11ll_opy_ = bstack1l1ll111l_opy_
  if cli.is_enabled(CONFIG):
    try:
      bstack1l1lll1l11_opy_ = bstack1l1l1l1l1_opy_[bstack11l111_opy_ (u"ࠫࡕ࡟ࡔࡆࡕࡗ࠱ࡇࡊࡄࠨජ")] if bstack1l1ll111l_opy_ == bstack11l111_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬඣ") and bstack1lll1ll111_opy_() else bstack1l1ll111l_opy_
      bstack11111l1l1_opy_.invoke(bstack1llllll11l_opy_.bstack11ll11111l_opy_, bstack11lll11ll1_opy_(
        sdk_version=__version__,
        path_config=bstack1llll11l11_opy_(),
        path_project=os.getcwd(),
        test_framework=bstack1l1lll1l11_opy_,
        frameworks=[bstack1l1lll1l11_opy_],
        framework_versions={
          bstack1l1lll1l11_opy_: bstack11l1111l11_opy_(bstack11l111_opy_ (u"࠭ࡒࡰࡤࡲࡸࠬඤ") if bstack1l1ll111l_opy_ in [bstack11l111_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭ඥ"), bstack11l111_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧඦ"), bstack11l111_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪට")] else bstack1l1ll111l_opy_)
        },
        bs_config=CONFIG
      ))
      if cli.config.get(bstack11l111_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠧඨ"), None):
        CONFIG[bstack11l111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷࠨඩ")] = cli.config.get(bstack11l111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠢඪ"), None)
    except Exception as e:
      bstack11111l1l1_opy_.invoke(bstack1llllll11l_opy_.bstack111l1l11l_opy_, e.__traceback__, 1)
    if bstack1l1l1l11_opy_:
      CONFIG[bstack11l111_opy_ (u"ࠨࡡࡱࡲࠥණ")] = cli.config[bstack11l111_opy_ (u"ࠢࡢࡲࡳࠦඬ")]
      logger.info(bstack111l11l1_opy_.format(CONFIG[bstack11l111_opy_ (u"ࠨࡣࡳࡴࠬත")]))
  else:
    bstack11111l1l1_opy_.clear()
  global bstack1111l111_opy_
  global bstack111llll11_opy_
  if bstack11l111l1ll_opy_:
    try:
      bstack11l1l11l1l_opy_ = datetime.datetime.now()
      os.environ[bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡈࡕࡅࡒࡋࡗࡐࡔࡎࠫථ")] = bstack1l1ll111l_opy_
      bstack1l11llll_opy_(bstack11l111l1l_opy_, CONFIG)
      cli.bstack1l11lllll_opy_(bstack11l111_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻ࡵࡧ࡯ࡤࡺࡥࡴࡶࡢࡥࡹࡺࡥ࡮ࡲࡷࡩࡩࠨද"), datetime.datetime.now() - bstack11l1l11l1l_opy_)
    except Exception as e:
      logger.debug(bstack11llll11ll_opy_.format(str(e)))
  global bstack1l1l1l1l_opy_
  global bstack11lll1l1_opy_
  global bstack111l1ll1l_opy_
  global bstack1ll11lll_opy_
  global bstack11ll11ll11_opy_
  global bstack1l11lll111_opy_
  global bstack1l11ll1111_opy_
  global bstack11lll1l1ll_opy_
  global bstack1ll11ll1l1_opy_
  global bstack1lll1lll1l_opy_
  global bstack1l11111l_opy_
  global bstack11ll111lll_opy_
  global bstack11ll11l1l_opy_
  global bstack1l111111l_opy_
  global bstack1l1111llll_opy_
  global bstack1ll1lll11_opy_
  global bstack1lll111ll_opy_
  global bstack1lll11l1ll_opy_
  global bstack1l1lll1l1l_opy_
  global bstack11ll11l11_opy_
  global bstack1l11ll1ll1_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack1l1l1l1l_opy_ = webdriver.Remote.__init__
    bstack11lll1l1_opy_ = WebDriver.quit
    bstack11ll111lll_opy_ = WebDriver.close
    bstack1l1111llll_opy_ = WebDriver.get
    bstack1l11ll1ll1_opy_ = WebDriver.execute
  except Exception as e:
    pass
  try:
    import Browser
    from subprocess import Popen
    bstack1111l111_opy_ = Popen.__init__
  except Exception as e:
    pass
  try:
    from bstack_utils.helper import bstack1l111l1l_opy_
    bstack111llll11_opy_ = bstack1l111l1l_opy_()
  except Exception as e:
    pass
  try:
    global bstack1111ll1l1_opy_
    from QWeb.keywords import browser
    bstack1111ll1l1_opy_ = browser.close_browser
  except Exception as e:
    pass
  if bstack11lll1ll_opy_(CONFIG) and bstack1l1lll1l1_opy_():
    if bstack1lllll1l1_opy_() < version.parse(bstack1lll1l1l1l_opy_):
      logger.error(bstack1ll1l1l1_opy_.format(bstack1lllll1l1_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        if hasattr(RemoteConnection, bstack11l111_opy_ (u"ࠫࡤ࡭ࡥࡵࡡࡳࡶࡴࡾࡹࡠࡷࡵࡰࠬධ")) and callable(getattr(RemoteConnection, bstack11l111_opy_ (u"ࠬࡥࡧࡦࡶࡢࡴࡷࡵࡸࡺࡡࡸࡶࡱ࠭න"))):
          RemoteConnection._get_proxy_url = bstack1ll1ll111_opy_
        else:
          from selenium.webdriver.remote.client_config import ClientConfig
          ClientConfig.get_proxy_url = bstack1ll1ll111_opy_
      except Exception as e:
        logger.error(bstack1lll1l111l_opy_.format(str(e)))
  if not CONFIG.get(bstack11l111_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡁࡶࡶࡲࡇࡦࡶࡴࡶࡴࡨࡐࡴ࡭ࡳࠨ඲"), False) and not bstack11l111l1ll_opy_:
    logger.info(bstack11l11l1lll_opy_)
  if not cli.is_enabled(CONFIG):
    if bstack11l111_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫඳ") in CONFIG and str(CONFIG[bstack11l111_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬප")]).lower() != bstack11l111_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨඵ"):
      bstack11l1lll1_opy_()
    elif bstack1l1ll111l_opy_ != bstack11l111_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪබ") or (bstack1l1ll111l_opy_ == bstack11l111_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫභ") and not bstack11l111l1ll_opy_):
      bstack1l1l11111l_opy_()
  if (bstack1l1ll111l_opy_ in [bstack11l111_opy_ (u"ࠬࡶࡡࡣࡱࡷࠫම"), bstack11l111_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬඹ"), bstack11l111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠳ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠨය")]):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCreator._get_ff_profile = bstack1llll1lll1_opy_
        bstack1l11lll111_opy_ = WebDriverCache.close
      except Exception as e:
        logger.warn(bstack1lll111l1_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        bstack11ll11ll11_opy_ = ApplicationCache.close
      except Exception as e:
        logger.debug(bstack11l1l111ll_opy_ + str(e))
    except Exception as e:
      bstack11l1lll11l_opy_(e, bstack1lll111l1_opy_)
    if bstack1l1ll111l_opy_ != bstack11l111_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩර"):
      bstack1l1l1l1l11_opy_()
    bstack111l1ll1l_opy_ = Output.start_test
    bstack1ll11lll_opy_ = Output.end_test
    bstack1l11ll1111_opy_ = TestStatus.__init__
    bstack1ll11ll1l1_opy_ = pabot._run
    bstack1lll1lll1l_opy_ = QueueItem.__init__
    bstack1l11111l_opy_ = pabot._create_command_for_execution
    bstack1l1lll1l1l_opy_ = pabot._report_results
  if bstack1l1ll111l_opy_ == bstack11l111_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩ඼"):
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack11l1lll11l_opy_(e, bstack111lll1ll_opy_)
    bstack11ll11l1l_opy_ = Runner.run_hook
    bstack1l111111l_opy_ = Step.run
  if bstack1l1ll111l_opy_ == bstack11l111_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪල"):
    try:
      from _pytest.config import Config
      bstack1lll111ll_opy_ = Config.getoption
      from _pytest import runner
      bstack1lll11l1ll_opy_ = runner._update_current_test_var
    except Exception as e:
      logger.warn(e, bstack111l1l111_opy_)
    try:
      from pytest_bdd import reporting
      bstack11ll11l11_opy_ = reporting.runtest_makereport
    except Exception as e:
      logger.debug(bstack11l111_opy_ (u"ࠫࡕࡲࡥࡢࡵࡨࠤ࡮ࡴࡳࡵࡣ࡯ࡰࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡷࡳࠥࡸࡵ࡯ࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡴࡦࡵࡷࡷࠬ඾"))
  try:
    framework_name = bstack11l111_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫ඿") if bstack1l1ll111l_opy_ in [bstack11l111_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬව"), bstack11l111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ශ"), bstack11l111_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩෂ")] else bstack1l1l1llll1_opy_(bstack1l1ll111l_opy_)
    bstack1ll1lllll_opy_ = {
      bstack11l111_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࠪස"): bstack11l111_opy_ (u"ࠪࡔࡾࡺࡥࡴࡶ࠰ࡧࡺࡩࡵ࡮ࡤࡨࡶࠬහ") if bstack1l1ll111l_opy_ == bstack11l111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫළ") and bstack1lll1ll111_opy_() else framework_name,
      bstack11l111_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡸࡨࡶࡸ࡯࡯࡯ࠩෆ"): bstack11l1111l11_opy_(framework_name),
      bstack11l111_opy_ (u"࠭ࡳࡥ࡭ࡢࡺࡪࡸࡳࡪࡱࡱࠫ෇"): __version__,
      bstack11l111_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡹࡸ࡫ࡤࠨ෈"): bstack1l1ll111l_opy_
    }
    if bstack1l1ll111l_opy_ in bstack11llllll11_opy_ + bstack1111ll1l_opy_:
      if bstack1lllll11l_opy_.bstack1lll1111ll_opy_(CONFIG):
        if bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨ෉") in CONFIG:
          os.environ[bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎ්ࠪ")] = os.getenv(bstack11l111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚࡟ࡂࡅࡆࡉࡘ࡙ࡉࡃࡋࡏࡍ࡙࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟࡚ࡏࡏࠫ෋"), json.dumps(CONFIG[bstack11l111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫ෌")]))
          CONFIG[bstack11l111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬ෍")].pop(bstack11l111_opy_ (u"࠭ࡩ࡯ࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫ෎"), None)
          CONFIG[bstack11l111_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧා")].pop(bstack11l111_opy_ (u"ࠨࡧࡻࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ැ"), None)
        bstack1ll1lllll_opy_[bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࠩෑ")] = {
          bstack11l111_opy_ (u"ࠪࡲࡦࡳࡥࠨි"): bstack11l111_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠭ී"),
          bstack11l111_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳ࠭ු"): str(bstack1lllll1l1_opy_())
        }
    if bstack1l1ll111l_opy_ not in [bstack11l111_opy_ (u"࠭ࡲࡰࡤࡲࡸ࠲࡯࡮ࡵࡧࡵࡲࡦࡲࠧ෕")] and not cli.is_running():
      bstack1l111ll111_opy_, bstack1l11l11l_opy_ = bstack11l11l1l_opy_.launch(CONFIG, bstack1ll1lllll_opy_)
      if bstack1l11l11l_opy_.get(bstack11l111_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧූ")) is not None and bstack1lllll11l_opy_.bstack111lllll11_opy_(CONFIG) is None:
        value = bstack1l11l11l_opy_[bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ෗")].get(bstack11l111_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪෘ"))
        if value is not None:
            CONFIG[bstack11l111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪෙ")] = value
        else:
          logger.debug(bstack11l111_opy_ (u"ࠦࡓࡵࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡥࡣࡷࡥࠥ࡬࡯ࡶࡰࡧࠤ࡮ࡴࠠࡳࡧࡶࡴࡴࡴࡳࡦࠤේ"))
  except Exception as e:
    logger.debug(bstack11l1llllll_opy_.format(bstack11l111_opy_ (u"࡚ࠬࡥࡴࡶࡋࡹࡧ࠭ෛ"), str(e)))
  if bstack1l1ll111l_opy_ == bstack11l111_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ො"):
    bstack1ll1ll1ll_opy_ = True
    if bstack11l111l1ll_opy_ and bstack11l11l11l1_opy_:
      bstack111lllllll_opy_ = CONFIG.get(bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫෝ"), {}).get(bstack11l111_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪෞ"))
      bstack1llllll111_opy_(bstack11lll11l1l_opy_)
    elif bstack11l111l1ll_opy_:
      bstack111lllllll_opy_ = CONFIG.get(bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ෟ"), {}).get(bstack11l111_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ෠"))
      global bstack1l1ll111l1_opy_
      try:
        if bstack11l1111l1_opy_(bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ෡")]) and multiprocessing.current_process().name == bstack11l111_opy_ (u"ࠬ࠶ࠧ෢"):
          bstack11l111l1ll_opy_[bstack11l111_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ෣")].remove(bstack11l111_opy_ (u"ࠧ࠮࡯ࠪ෤"))
          bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫ෥")].remove(bstack11l111_opy_ (u"ࠩࡳࡨࡧ࠭෦"))
          bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭෧")] = bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ෨")][0]
          with open(bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ෩")], bstack11l111_opy_ (u"࠭ࡲࠨ෪")) as f:
            bstack11ll11l1l1_opy_ = f.read()
          bstack11ll11l111_opy_ = bstack11l111_opy_ (u"ࠢࠣࠤࡩࡶࡴࡳࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡳࡥ࡭ࠣ࡭ࡲࡶ࡯ࡳࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡ࡬ࡲ࡮ࡺࡩࡢ࡮࡬ࡾࡪࡁࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡩ࡯࡫ࡷ࡭ࡦࡲࡩࡻࡧࠫࡿࢂ࠯࠻ࠡࡨࡵࡳࡲࠦࡰࡥࡤࠣ࡭ࡲࡶ࡯ࡳࡶࠣࡔࡩࡨ࠻ࠡࡱࡪࡣࡩࡨࠠ࠾ࠢࡓࡨࡧ࠴ࡤࡰࡡࡥࡶࡪࡧ࡫࠼ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡪࡥࡧࠢࡰࡳࡩࡥࡢࡳࡧࡤ࡯࠭ࡹࡥ࡭ࡨ࠯ࠤࡦࡸࡧ࠭ࠢࡷࡩࡲࡶ࡯ࡳࡣࡵࡽࠥࡃࠠ࠱ࠫ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡷࡶࡾࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡢࡴࡪࠤࡂࠦࡳࡵࡴࠫ࡭ࡳࡺࠨࡢࡴࡪ࠭࠰࠷࠰ࠪࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡦࡺࡦࡩࡵࡺࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡥࡸࠦࡥ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡳࡥࡸࡹࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡵࡧࡠࡦࡥࠬࡸ࡫࡬ࡧ࠮ࡤࡶ࡬࠲ࡴࡦ࡯ࡳࡳࡷࡧࡲࡺࠫࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡐࡥࡤ࠱ࡨࡴࡥࡢࠡ࠿ࠣࡱࡴࡪ࡟ࡣࡴࡨࡥࡰࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡓࡨࡧ࠴ࡤࡰࡡࡥࡶࡪࡧ࡫ࠡ࠿ࠣࡱࡴࡪ࡟ࡣࡴࡨࡥࡰࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡓࡨࡧ࠮ࠩ࠯ࡵࡨࡸࡤࡺࡲࡢࡥࡨࠬ࠮ࡢ࡮ࠣࠤࠥ෫").format(str(bstack11l111l1ll_opy_))
          bstack1llll1l11l_opy_ = bstack11ll11l111_opy_ + bstack11ll11l1l1_opy_
          bstack1ll1l1l1l1_opy_ = bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫ෬")] + bstack11l111_opy_ (u"ࠩࡢࡦࡸࡺࡡࡤ࡭ࡢࡸࡪࡳࡰ࠯ࡲࡼࠫ෭")
          with open(bstack1ll1l1l1l1_opy_, bstack11l111_opy_ (u"ࠪࡻࠬ෮")):
            pass
          with open(bstack1ll1l1l1l1_opy_, bstack11l111_opy_ (u"ࠦࡼ࠱ࠢ෯")) as f:
            f.write(bstack1llll1l11l_opy_)
          import subprocess
          bstack11111111l_opy_ = subprocess.run([bstack11l111_opy_ (u"ࠧࡶࡹࡵࡪࡲࡲࠧ෰"), bstack1ll1l1l1l1_opy_])
          if os.path.exists(bstack1ll1l1l1l1_opy_):
            os.unlink(bstack1ll1l1l1l1_opy_)
          os._exit(bstack11111111l_opy_.returncode)
        else:
          if bstack11l1111l1_opy_(bstack11l111l1ll_opy_[bstack11l111_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ෱")]):
            bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪෲ")].remove(bstack11l111_opy_ (u"ࠨ࠯ࡰࠫෳ"))
            bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ෴")].remove(bstack11l111_opy_ (u"ࠪࡴࡩࡨࠧ෵"))
            bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ෶")] = bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ෷")][0]
          bstack1llllll111_opy_(bstack11lll11l1l_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(bstack11l111l1ll_opy_[bstack11l111_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ෸")])))
          sys.argv = sys.argv[2:]
          mod_globals = globals()
          mod_globals[bstack11l111_opy_ (u"ࠧࡠࡡࡱࡥࡲ࡫࡟ࡠࠩ෹")] = bstack11l111_opy_ (u"ࠨࡡࡢࡱࡦ࡯࡮ࡠࡡࠪ෺")
          mod_globals[bstack11l111_opy_ (u"ࠩࡢࡣ࡫࡯࡬ࡦࡡࡢࠫ෻")] = os.path.abspath(bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭෼")])
          exec(open(bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ෽")]).read(), mod_globals)
      except BaseException as e:
        try:
          traceback.print_exc()
          logger.error(bstack11l111_opy_ (u"ࠬࡉࡡࡶࡩ࡫ࡸࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮࠻ࠢࡾࢁࠬ෾").format(str(e)))
          for driver in bstack1l1ll111l1_opy_:
            bstack1ll1l1llll_opy_.append({
              bstack11l111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ෿"): bstack11l111l1ll_opy_[bstack11l111_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ฀")],
              bstack11l111_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧก"): str(e),
              bstack11l111_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨข"): multiprocessing.current_process().name
            })
            bstack1ll11l1ll1_opy_(driver, bstack11l111_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪฃ"), bstack11l111_opy_ (u"ࠦࡘ࡫ࡳࡴ࡫ࡲࡲࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡽࡩࡵࡪ࠽ࠤࡡࡴࠢค") + str(e))
        except Exception:
          pass
      finally:
        try:
          for driver in bstack1l1ll111l1_opy_:
            driver.quit()
        except Exception as e:
          pass
    else:
      percy.init(bstack1l1l1l11_opy_, CONFIG, logger)
      bstack11ll1l11l_opy_()
      bstack1l111l111l_opy_()
      percy.bstack1l1l1lllll_opy_()
      bstack11lll1111_opy_ = {
        bstack11l111_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨฅ"): args[0],
        bstack11l111_opy_ (u"࠭ࡃࡐࡐࡉࡍࡌ࠭ฆ"): CONFIG,
        bstack11l111_opy_ (u"ࠧࡉࡗࡅࡣ࡚ࡘࡌࠨง"): bstack1l1l11lll1_opy_,
        bstack11l111_opy_ (u"ࠨࡋࡖࡣࡆࡖࡐࡠࡃࡘࡘࡔࡓࡁࡕࡇࠪจ"): bstack1l1l1l11_opy_
      }
      if bstack11l111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬฉ") in CONFIG:
        bstack11l1l1l1_opy_ = bstack1l1l1l11l_opy_(args, logger, CONFIG, bstack111111l11_opy_, bstack1l1ll1lll_opy_)
        bstack1l1111l1l1_opy_ = bstack11l1l1l1_opy_.bstack111lll1ll1_opy_(run_on_browserstack, bstack11lll1111_opy_, bstack11l1111l1_opy_(args))
      else:
        if bstack11l1111l1_opy_(args):
          bstack11lll1111_opy_[bstack11l111_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ช")] = args
          test = multiprocessing.Process(name=str(0),
                                         target=run_on_browserstack, args=(bstack11lll1111_opy_,))
          test.start()
          test.join()
        else:
          bstack1llllll111_opy_(bstack11lll11l1l_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(args[0])))
          mod_globals = globals()
          mod_globals[bstack11l111_opy_ (u"ࠫࡤࡥ࡮ࡢ࡯ࡨࡣࡤ࠭ซ")] = bstack11l111_opy_ (u"ࠬࡥ࡟࡮ࡣ࡬ࡲࡤࡥࠧฌ")
          mod_globals[bstack11l111_opy_ (u"࠭࡟ࡠࡨ࡬ࡰࡪࡥ࡟ࠨญ")] = os.path.abspath(args[0])
          sys.argv = sys.argv[2:]
          exec(open(args[0]).read(), mod_globals)
  elif bstack1l1ll111l_opy_ == bstack11l111_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭ฎ") or bstack1l1ll111l_opy_ == bstack11l111_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧฏ"):
    percy.init(bstack1l1l1l11_opy_, CONFIG, logger)
    percy.bstack1l1l1lllll_opy_()
    try:
      from pabot import pabot
    except Exception as e:
      bstack11l1lll11l_opy_(e, bstack1lll111l1_opy_)
    bstack11ll1l11l_opy_()
    bstack1llllll111_opy_(bstack1l11ll111l_opy_)
    if bstack111111l11_opy_:
      bstack11ll1lll_opy_(bstack1l11ll111l_opy_, args)
      if bstack11l111_opy_ (u"ࠩ࠰࠱ࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠧฐ") in args:
        i = args.index(bstack11l111_opy_ (u"ࠪ࠱࠲ࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠨฑ"))
        args.pop(i)
        args.pop(i)
      if bstack11l111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧฒ") not in CONFIG:
        CONFIG[bstack11l111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨณ")] = [{}]
        bstack1l1ll1lll_opy_ = 1
      if bstack1l111l1ll1_opy_ == 0:
        bstack1l111l1ll1_opy_ = 1
      args.insert(0, str(bstack1l111l1ll1_opy_))
      args.insert(0, str(bstack11l111_opy_ (u"࠭࠭࠮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫด")))
    if bstack11l11l1l_opy_.on():
      try:
        from robot.run import USAGE
        from robot.utils import ArgumentParser
        from pabot.arguments import _parse_pabot_args
        bstack111ll1111_opy_, pabot_args = _parse_pabot_args(args)
        opts, bstack11111lll1_opy_ = ArgumentParser(
            USAGE,
            auto_pythonpath=False,
            auto_argumentfile=True,
            env_options=bstack11l111_opy_ (u"ࠢࡓࡑࡅࡓ࡙ࡥࡏࡑࡖࡌࡓࡓ࡙ࠢต"),
        ).parse_args(bstack111ll1111_opy_)
        bstack1l1lll1l_opy_ = args.index(bstack111ll1111_opy_[0]) if len(bstack111ll1111_opy_) > 0 else len(args)
        args.insert(bstack1l1lll1l_opy_, str(bstack11l111_opy_ (u"ࠨ࠯࠰ࡰ࡮ࡹࡴࡦࡰࡨࡶࠬถ")))
        args.insert(bstack1l1lll1l_opy_ + 1, str(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack11l111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡵࡳࡧࡵࡴࡠ࡮࡬ࡷࡹ࡫࡮ࡦࡴ࠱ࡴࡾ࠭ท"))))
        if bstack1l1ll1ll1l_opy_.bstack1l1llll1_opy_(CONFIG):
          args.insert(bstack1l1lll1l_opy_, str(bstack11l111_opy_ (u"ࠪ࠱࠲ࡲࡩࡴࡶࡨࡲࡪࡸࠧธ")))
          args.insert(bstack1l1lll1l_opy_ + 1, str(bstack11l111_opy_ (u"ࠫࡗ࡫ࡴࡳࡻࡉࡥ࡮ࡲࡥࡥ࠼ࡾࢁࠬน").format(bstack1l1ll1ll1l_opy_.bstack111lll11l_opy_(CONFIG))))
        if bstack111ll1lll_opy_(os.environ.get(bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡗࡋࡒࡖࡐࠪบ"))) and str(os.environ.get(bstack11l111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡘࡅࡓࡗࡑࡣ࡙ࡋࡓࡕࡕࠪป"), bstack11l111_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬผ"))) != bstack11l111_opy_ (u"ࠨࡰࡸࡰࡱ࠭ฝ"):
          for bstack1l111ll11l_opy_ in bstack11111lll1_opy_:
            args.remove(bstack1l111ll11l_opy_)
          test_files = os.environ.get(bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡔࡈࡖ࡚ࡔ࡟ࡕࡇࡖࡘࡘ࠭พ")).split(bstack11l111_opy_ (u"ࠪ࠰ࠬฟ"))
          for bstack1llll1l1l_opy_ in test_files:
            args.append(bstack1llll1l1l_opy_)
      except Exception as e:
        logger.error(bstack11l111_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡤࡸࡹࡧࡣࡩ࡫ࡱ࡫ࠥࡲࡩࡴࡶࡨࡲࡪࡸࠠࡧࡱࡵࠤࢀࢃ࠮ࠡࡇࡵࡶࡴࡸࠠ࠮ࠢࡾࢁࠧภ").format(bstack11l11ll1ll_opy_, e))
    pabot.main(args)
  elif bstack1l1ll111l_opy_ == bstack11l111_opy_ (u"ࠬࡸ࡯ࡣࡱࡷ࠱࡮ࡴࡴࡦࡴࡱࡥࡱ࠭ม"):
    try:
      from robot import run_cli
    except Exception as e:
      bstack11l1lll11l_opy_(e, bstack1lll111l1_opy_)
    for a in args:
      if bstack11l111_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡖࡌࡂࡖࡉࡓࡗࡓࡉࡏࡆࡈ࡜ࠬย") in a:
        bstack1l11l111l1_opy_ = int(a.split(bstack11l111_opy_ (u"ࠧ࠻ࠩร"))[1])
      if bstack11l111_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡅࡇࡉࡐࡔࡉࡁࡍࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖࠬฤ") in a:
        bstack111lllllll_opy_ = str(a.split(bstack11l111_opy_ (u"ࠩ࠽ࠫล"))[1])
      if bstack11l111_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡆࡐࡎࡇࡒࡈࡕࠪฦ") in a:
        bstack11l1l1l111_opy_ = str(a.split(bstack11l111_opy_ (u"ࠫ࠿࠭ว"))[1])
    bstack1ll1l11l_opy_ = None
    bstack1ll11ll11l_opy_ = None
    if bstack11l111_opy_ (u"ࠬ࠳࠭ࡣࡵࡷࡥࡨࡱ࡟ࡪࡶࡨࡱࡤ࡯࡮ࡥࡧࡻࠫศ") in args:
      i = args.index(bstack11l111_opy_ (u"࠭࠭࠮ࡤࡶࡸࡦࡩ࡫ࡠ࡫ࡷࡩࡲࡥࡩ࡯ࡦࡨࡼࠬษ"))
      args.pop(i)
      bstack1ll1l11l_opy_ = args.pop(i)
    if bstack11l111_opy_ (u"ࠧ࠮࠯ࡥࡷࡹࡧࡣ࡬ࡡࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࠪส") in args:
      i = args.index(bstack11l111_opy_ (u"ࠨ࠯࠰ࡦࡸࡺࡡࡤ࡭ࡢࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࠫห"))
      args.pop(i)
      bstack1ll11ll11l_opy_ = args.pop(i)
    if bstack1ll1l11l_opy_ is not None:
      global bstack1l111l1l1l_opy_
      bstack1l111l1l1l_opy_ = bstack1ll1l11l_opy_
    if bstack1ll11ll11l_opy_ is not None and int(bstack1l11l111l1_opy_) < 0:
      bstack1l11l111l1_opy_ = int(bstack1ll11ll11l_opy_)
    bstack1llllll111_opy_(bstack1l11ll111l_opy_)
    run_cli(args)
    if bstack11l111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠭ฬ") in multiprocessing.current_process().__dict__.keys():
      for bstack111lll11ll_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack1ll1l1llll_opy_.append(bstack111lll11ll_opy_)
  elif bstack1l1ll111l_opy_ == bstack11l111_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪอ"):
    bstack1lllll1111_opy_ = bstack1l1ll11111_opy_(args, logger, CONFIG, bstack111111l11_opy_)
    bstack1lllll1111_opy_.bstack111l1111_opy_()
    bstack11ll1l11l_opy_()
    bstack1lll111l1l_opy_ = True
    bstack1l11ll1lll_opy_ = bstack1lllll1111_opy_.bstack1lll111l_opy_()
    bstack1lllll1111_opy_.bstack11lll1111_opy_(bstack1l11l111l_opy_)
    bstack1lllll1111_opy_.bstack11l111ll11_opy_()
    bstack11ll1llll_opy_(bstack1l1ll111l_opy_, CONFIG, bstack1lllll1111_opy_.bstack1l11l1ll1_opy_())
    bstack1lll1ll1ll_opy_ = bstack1lllll1111_opy_.bstack111lll1ll1_opy_(bstack11l11l11ll_opy_, {
      bstack11l111_opy_ (u"ࠫࡍ࡛ࡂࡠࡗࡕࡐࠬฮ"): bstack1l1l11lll1_opy_,
      bstack11l111_opy_ (u"ࠬࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋࠧฯ"): bstack1l1l1l11_opy_,
      bstack11l111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡕࡕࡑࡐࡅ࡙ࡏࡏࡏࠩะ"): bstack111111l11_opy_
    })
    try:
      bstack1l1l11l11l_opy_, bstack1lllll11ll_opy_ = map(list, zip(*bstack1lll1ll1ll_opy_))
      bstack1l1ll1ll_opy_ = bstack1l1l11l11l_opy_[0]
      for status_code in bstack1lllll11ll_opy_:
        if status_code != 0:
          bstack11lll1111l_opy_ = status_code
          break
    except Exception as e:
      logger.debug(bstack11l111_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡦࡼࡥࠡࡧࡵࡶࡴࡸࡳࠡࡣࡱࡨࠥࡹࡴࡢࡶࡸࡷࠥࡩ࡯ࡥࡧ࠱ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠ࠻ࠢࡾࢁࠧั").format(str(e)))
  elif bstack1l1ll111l_opy_ == bstack11l111_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨา"):
    try:
      from behave.__main__ import main as bstack111llllll1_opy_
      from behave.configuration import Configuration
    except Exception as e:
      bstack11l1lll11l_opy_(e, bstack111lll1ll_opy_)
    bstack11ll1l11l_opy_()
    bstack1lll111l1l_opy_ = True
    bstack1111l111l_opy_ = 1
    if bstack11l111_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩำ") in CONFIG:
      bstack1111l111l_opy_ = CONFIG[bstack11l111_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪิ")]
    if bstack11l111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧี") in CONFIG:
      bstack1l111ll11_opy_ = int(bstack1111l111l_opy_) * int(len(CONFIG[bstack11l111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨึ")]))
    else:
      bstack1l111ll11_opy_ = int(bstack1111l111l_opy_)
    config = Configuration(args)
    bstack11ll11lll1_opy_ = config.paths
    if len(bstack11ll11lll1_opy_) == 0:
      import glob
      pattern = bstack11l111_opy_ (u"࠭ࠪࠫ࠱࠭࠲࡫࡫ࡡࡵࡷࡵࡩࠬื")
      bstack1llll11111_opy_ = glob.glob(pattern, recursive=True)
      args.extend(bstack1llll11111_opy_)
      config = Configuration(args)
      bstack11ll11lll1_opy_ = config.paths
    bstack11ll1ll1_opy_ = [os.path.normpath(item) for item in bstack11ll11lll1_opy_]
    bstack1ll111l1_opy_ = [os.path.normpath(item) for item in args]
    bstack11l111111_opy_ = [item for item in bstack1ll111l1_opy_ if item not in bstack11ll1ll1_opy_]
    import platform as pf
    if pf.system().lower() == bstack11l111_opy_ (u"ࠧࡸ࡫ࡱࡨࡴࡽࡳࠨุ"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack11ll1ll1_opy_ = [str(PurePosixPath(PureWindowsPath(bstack1ll1l1l1ll_opy_)))
                    for bstack1ll1l1l1ll_opy_ in bstack11ll1ll1_opy_]
    bstack1l1l11ll1l_opy_ = []
    for spec in bstack11ll1ll1_opy_:
      bstack1lll1l111_opy_ = []
      bstack1lll1l111_opy_ += bstack11l111111_opy_
      bstack1lll1l111_opy_.append(spec)
      bstack1l1l11ll1l_opy_.append(bstack1lll1l111_opy_)
    execution_items = []
    for bstack1lll1l111_opy_ in bstack1l1l11ll1l_opy_:
      if bstack11l111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶูࠫ") in CONFIG:
        for index, _ in enumerate(CONFIG[bstack11l111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷฺࠬ")]):
          item = {}
          item[bstack11l111_opy_ (u"ࠪࡥࡷ࡭ࠧ฻")] = bstack11l111_opy_ (u"ࠫࠥ࠭฼").join(bstack1lll1l111_opy_)
          item[bstack11l111_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫ฽")] = index
          execution_items.append(item)
      else:
        item = {}
        item[bstack11l111_opy_ (u"࠭ࡡࡳࡩࠪ฾")] = bstack11l111_opy_ (u"ࠧࠡࠩ฿").join(bstack1lll1l111_opy_)
        item[bstack11l111_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧเ")] = 0
        execution_items.append(item)
    bstack1ll111lll1_opy_ = bstack1l11l1ll11_opy_(execution_items, bstack1l111ll11_opy_)
    for execution_item in bstack1ll111lll1_opy_:
      bstack1l11ll1ll_opy_ = []
      for item in execution_item:
        bstack1l11ll1ll_opy_.append(bstack1l11llll1l_opy_(name=str(item[bstack11l111_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨแ")]),
                                             target=bstack11ll1l1ll_opy_,
                                             args=(item[bstack11l111_opy_ (u"ࠪࡥࡷ࡭ࠧโ")],)))
      for t in bstack1l11ll1ll_opy_:
        t.start()
      for t in bstack1l11ll1ll_opy_:
        t.join()
  else:
    bstack1l1l1lll_opy_(bstack1ll1llll1_opy_)
  if not bstack11l111l1ll_opy_:
    bstack1l1l1ll1l1_opy_()
    if(bstack1l1ll111l_opy_ in [bstack11l111_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫใ"), bstack11l111_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬไ")]):
      bstack1l1ll11l1_opy_()
  bstack11l111111l_opy_.bstack11ll1ll11l_opy_()
def browserstack_initialize(bstack11111l11_opy_=None):
  logger.info(bstack11l111_opy_ (u"࠭ࡒࡶࡰࡱ࡭ࡳ࡭ࠠࡔࡆࡎࠤࡼ࡯ࡴࡩࠢࡤࡶ࡬ࡹ࠺ࠡࠩๅ") + str(bstack11111l11_opy_))
  run_on_browserstack(bstack11111l11_opy_, None, True)
@measure(event_name=EVENTS.bstack1111lllll_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack1l1l1ll1l1_opy_():
  global CONFIG
  global bstack11ll1l11ll_opy_
  global bstack11lll1111l_opy_
  global bstack11l1ll111l_opy_
  global bstack11l11ll1l_opy_
  bstack1l111l111_opy_.bstack1l11l1lll1_opy_()
  if cli.is_running():
    bstack11111l1l1_opy_.invoke(bstack1llllll11l_opy_.bstack11l1lll11_opy_)
  else:
    bstack1llll11ll_opy_ = bstack1l1ll1ll1l_opy_.bstack111llll1_opy_(config=CONFIG)
    bstack1llll11ll_opy_.bstack11ll1ll111_opy_(CONFIG)
  if bstack11ll1l11ll_opy_ == bstack11l111_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧๆ"):
    if not cli.is_enabled(CONFIG):
      bstack11l11l1l_opy_.stop()
  else:
    bstack11l11l1l_opy_.stop()
  if not cli.is_enabled(CONFIG):
    bstack1l11lllll1_opy_.bstack1l11111l1l_opy_()
  if bstack11l111_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬ็") in CONFIG and str(CONFIG[bstack11l111_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ่࠭")]).lower() != bstack11l111_opy_ (u"ࠪࡪࡦࡲࡳࡦ้ࠩ"):
    hashed_id, bstack1llll111l_opy_ = bstack111111lll_opy_()
  else:
    hashed_id, bstack1llll111l_opy_ = get_build_link()
  bstack1lll11l11_opy_(hashed_id)
  logger.info(bstack11l111_opy_ (u"ࠫࡘࡊࡋࠡࡴࡸࡲࠥ࡫࡮ࡥࡧࡧࠤ࡫ࡵࡲࠡ࡫ࡧ࠾๊ࠬ") + bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠬࡹࡤ࡬ࡔࡸࡲࡎࡪ๋ࠧ"), bstack11l111_opy_ (u"࠭ࠧ์")) + bstack11l111_opy_ (u"ࠧ࠭ࠢࡷࡩࡸࡺࡨࡶࡤࠣ࡭ࡩࡀࠠࠨํ") + os.getenv(bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭๎"), bstack11l111_opy_ (u"ࠩࠪ๏")))
  if hashed_id is not None and bstack1lll1lll1_opy_() != -1:
    sessions = bstack1l1l1ll1_opy_(hashed_id)
    bstack11lll111ll_opy_(sessions, bstack1llll111l_opy_)
  if bstack11ll1l11ll_opy_ == bstack11l111_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ๐") and bstack11lll1111l_opy_ != 0:
    sys.exit(bstack11lll1111l_opy_)
  if bstack11ll1l11ll_opy_ == bstack11l111_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫ๑") and bstack11l1ll111l_opy_ != 0:
    sys.exit(bstack11l1ll111l_opy_)
def bstack1lll11l11_opy_(new_id):
    global bstack1l1ll11ll_opy_
    bstack1l1ll11ll_opy_ = new_id
def bstack1l1l1llll1_opy_(bstack1l1lll111l_opy_):
  if bstack1l1lll111l_opy_:
    return bstack1l1lll111l_opy_.capitalize()
  else:
    return bstack11l111_opy_ (u"ࠬ࠭๒")
@measure(event_name=EVENTS.bstack1lll11111l_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack11llll1ll_opy_(bstack11l11l1ll1_opy_):
  if bstack11l111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ๓") in bstack11l11l1ll1_opy_ and bstack11l11l1ll1_opy_[bstack11l111_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ๔")] != bstack11l111_opy_ (u"ࠨࠩ๕"):
    return bstack11l11l1ll1_opy_[bstack11l111_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ๖")]
  else:
    bstack1ll111l111_opy_ = bstack11l111_opy_ (u"ࠥࠦ๗")
    if bstack11l111_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࠫ๘") in bstack11l11l1ll1_opy_ and bstack11l11l1ll1_opy_[bstack11l111_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬ๙")] != None:
      bstack1ll111l111_opy_ += bstack11l11l1ll1_opy_[bstack11l111_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪ࠭๚")] + bstack11l111_opy_ (u"ࠢ࠭ࠢࠥ๛")
      if bstack11l11l1ll1_opy_[bstack11l111_opy_ (u"ࠨࡱࡶࠫ๜")] == bstack11l111_opy_ (u"ࠤ࡬ࡳࡸࠨ๝"):
        bstack1ll111l111_opy_ += bstack11l111_opy_ (u"ࠥ࡭ࡔ࡙ࠠࠣ๞")
      bstack1ll111l111_opy_ += (bstack11l11l1ll1_opy_[bstack11l111_opy_ (u"ࠫࡴࡹ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ๟")] or bstack11l111_opy_ (u"ࠬ࠭๠"))
      return bstack1ll111l111_opy_
    else:
      bstack1ll111l111_opy_ += bstack1l1l1llll1_opy_(bstack11l11l1ll1_opy_[bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧ๡")]) + bstack11l111_opy_ (u"ࠢࠡࠤ๢") + (
              bstack11l11l1ll1_opy_[bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠪ๣")] or bstack11l111_opy_ (u"ࠩࠪ๤")) + bstack11l111_opy_ (u"ࠥ࠰ࠥࠨ๥")
      if bstack11l11l1ll1_opy_[bstack11l111_opy_ (u"ࠫࡴࡹࠧ๦")] == bstack11l111_opy_ (u"ࠧ࡝ࡩ࡯ࡦࡲࡻࡸࠨ๧"):
        bstack1ll111l111_opy_ += bstack11l111_opy_ (u"ࠨࡗࡪࡰࠣࠦ๨")
      bstack1ll111l111_opy_ += bstack11l11l1ll1_opy_[bstack11l111_opy_ (u"ࠧࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠫ๩")] or bstack11l111_opy_ (u"ࠨࠩ๪")
      return bstack1ll111l111_opy_
@measure(event_name=EVENTS.bstack1lll1ll1_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack1ll11ll11_opy_(bstack1lll1ll11l_opy_):
  if bstack1lll1ll11l_opy_ == bstack11l111_opy_ (u"ࠤࡧࡳࡳ࡫ࠢ๫"):
    return bstack11l111_opy_ (u"ࠪࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࠦࡳࡵࡻ࡯ࡩࡂࠨࡣࡰ࡮ࡲࡶ࠿࡭ࡲࡦࡧࡱ࠿ࠧࡄ࠼ࡧࡱࡱࡸࠥࡩ࡯࡭ࡱࡵࡁࠧ࡭ࡲࡦࡧࡱࠦࡃࡉ࡯࡮ࡲ࡯ࡩࡹ࡫ࡤ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭๬")
  elif bstack1lll1ll11l_opy_ == bstack11l111_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦ๭"):
    return bstack11l111_opy_ (u"ࠬࡂࡴࡥࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢࠡࡵࡷࡽࡱ࡫࠽ࠣࡥࡲࡰࡴࡸ࠺ࡳࡧࡧ࠿ࠧࡄ࠼ࡧࡱࡱࡸࠥࡩ࡯࡭ࡱࡵࡁࠧࡸࡥࡥࠤࡁࡊࡦ࡯࡬ࡦࡦ࠿࠳࡫ࡵ࡮ࡵࡀ࠿࠳ࡹࡪ࠾ࠨ๮")
  elif bstack1lll1ll11l_opy_ == bstack11l111_opy_ (u"ࠨࡰࡢࡵࡶࡩࡩࠨ๯"):
    return bstack11l111_opy_ (u"ࠧ࠽ࡶࡧࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࠣࡷࡹࡿ࡬ࡦ࠿ࠥࡧࡴࡲ࡯ࡳ࠼ࡪࡶࡪ࡫࡮࠼ࠤࡁࡀ࡫ࡵ࡮ࡵࠢࡦࡳࡱࡵࡲ࠾ࠤࡪࡶࡪ࡫࡮ࠣࡀࡓࡥࡸࡹࡥࡥ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧ๰")
  elif bstack1lll1ll11l_opy_ == bstack11l111_opy_ (u"ࠣࡧࡵࡶࡴࡸࠢ๱"):
    return bstack11l111_opy_ (u"ࠩ࠿ࡸࡩࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࠥࡹࡴࡺ࡮ࡨࡁࠧࡩ࡯࡭ࡱࡵ࠾ࡷ࡫ࡤ࠼ࠤࡁࡀ࡫ࡵ࡮ࡵࠢࡦࡳࡱࡵࡲ࠾ࠤࡵࡩࡩࠨ࠾ࡆࡴࡵࡳࡷࡂ࠯ࡧࡱࡱࡸࡃࡂ࠯ࡵࡦࡁࠫ๲")
  elif bstack1lll1ll11l_opy_ == bstack11l111_opy_ (u"ࠥࡸ࡮ࡳࡥࡰࡷࡷࠦ๳"):
    return bstack11l111_opy_ (u"ࠫࡁࡺࡤࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨࠠࡴࡶࡼࡰࡪࡃࠢࡤࡱ࡯ࡳࡷࡀࠣࡦࡧࡤ࠷࠷࠼࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࠥࡨࡩࡦ࠹࠲࠷ࠤࡁࡘ࡮ࡳࡥࡰࡷࡷࡀ࠴࡬࡯࡯ࡶࡁࡀ࠴ࡺࡤ࠿ࠩ๴")
  elif bstack1lll1ll11l_opy_ == bstack11l111_opy_ (u"ࠧࡸࡵ࡯ࡰ࡬ࡲ࡬ࠨ๵"):
    return bstack11l111_opy_ (u"࠭࠼ࡵࡦࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࠢࡶࡸࡾࡲࡥ࠾ࠤࡦࡳࡱࡵࡲ࠻ࡤ࡯ࡥࡨࡱ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡤ࡯ࡥࡨࡱࠢ࠿ࡔࡸࡲࡳ࡯࡮ࡨ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧ๶")
  else:
    return bstack11l111_opy_ (u"ࠧ࠽ࡶࡧࠤࡦࡲࡩࡨࡰࡀࠦࡨ࡫࡮ࡵࡧࡵࠦࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࠤࡸࡺࡹ࡭ࡧࡀࠦࡨࡵ࡬ࡰࡴ࠽ࡦࡱࡧࡣ࡬࠽ࠥࡂࡁ࡬࡯࡯ࡶࠣࡧࡴࡲ࡯ࡳ࠿ࠥࡦࡱࡧࡣ࡬ࠤࡁࠫ๷") + bstack1l1l1llll1_opy_(
      bstack1lll1ll11l_opy_) + bstack11l111_opy_ (u"ࠨ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧ๸")
def bstack1l11l111ll_opy_(session):
  return bstack11l111_opy_ (u"ࠩ࠿ࡸࡷࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡲࡰࡹࠥࡂࡁࡺࡤࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠦࡳࡦࡵࡶ࡭ࡴࡴ࠭࡯ࡣࡰࡩࠧࡄ࠼ࡢࠢ࡫ࡶࡪ࡬࠽ࠣࡽࢀࠦࠥࡺࡡࡳࡩࡨࡸࡂࠨ࡟ࡣ࡮ࡤࡲࡰࠨ࠾ࡼࡿ࠿࠳ࡦࡄ࠼࠰ࡶࡧࡂࢀࢃࡻࡾ࠾ࡷࡨࠥࡧ࡬ࡪࡩࡱࡁࠧࡩࡥ࡯ࡶࡨࡶࠧࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࡃࢁࡽ࠽࠱ࡷࡨࡃࡂࡴࡥࠢࡤࡰ࡮࡭࡮࠾ࠤࡦࡩࡳࡺࡥࡳࠤࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࡀࡾࢁࡁ࠵ࡴࡥࡀ࠿ࡸࡩࠦࡡ࡭࡫ࡪࡲࡂࠨࡣࡦࡰࡷࡩࡷࠨࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࡄࡻࡾ࠾࠲ࡸࡩࡄ࠼ࡵࡦࠣࡥࡱ࡯ࡧ࡯࠿ࠥࡧࡪࡴࡴࡦࡴࠥࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࡁࡿࢂࡂ࠯ࡵࡦࡁࡀ࠴ࡺࡲ࠿ࠩ๹").format(
    session[bstack11l111_opy_ (u"ࠪࡴࡺࡨ࡬ࡪࡥࡢࡹࡷࡲࠧ๺")], bstack11llll1ll_opy_(session), bstack1ll11ll11_opy_(session[bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡷࡹࡧࡴࡶࡵࠪ๻")]),
    bstack1ll11ll11_opy_(session[bstack11l111_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ๼")]),
    bstack1l1l1llll1_opy_(session[bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧ๽")] or session[bstack11l111_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࠧ๾")] or bstack11l111_opy_ (u"ࠨࠩ๿")) + bstack11l111_opy_ (u"ࠤࠣࠦ຀") + (session[bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬກ")] or bstack11l111_opy_ (u"ࠫࠬຂ")),
    session[bstack11l111_opy_ (u"ࠬࡵࡳࠨ຃")] + bstack11l111_opy_ (u"ࠨࠠࠣຄ") + session[bstack11l111_opy_ (u"ࠧࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠫ຅")], session[bstack11l111_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࠪຆ")] or bstack11l111_opy_ (u"ࠩࠪງ"),
    session[bstack11l111_opy_ (u"ࠪࡧࡷ࡫ࡡࡵࡧࡧࡣࡦࡺࠧຈ")] if session[bstack11l111_opy_ (u"ࠫࡨࡸࡥࡢࡶࡨࡨࡤࡧࡴࠨຉ")] else bstack11l111_opy_ (u"ࠬ࠭ຊ"))
@measure(event_name=EVENTS.bstack1l11l11l11_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def bstack11lll111ll_opy_(sessions, bstack1llll111l_opy_):
  try:
    bstack11lll1l11_opy_ = bstack11l111_opy_ (u"ࠨࠢ຋")
    if not os.path.exists(bstack11111111_opy_):
      os.mkdir(bstack11111111_opy_)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack11l111_opy_ (u"ࠧࡢࡵࡶࡩࡹࡹ࠯ࡳࡧࡳࡳࡷࡺ࠮ࡩࡶࡰࡰࠬຌ")), bstack11l111_opy_ (u"ࠨࡴࠪຍ")) as f:
      bstack11lll1l11_opy_ = f.read()
    bstack11lll1l11_opy_ = bstack11lll1l11_opy_.replace(bstack11l111_opy_ (u"ࠩࡾࠩࡗࡋࡓࡖࡎࡗࡗࡤࡉࡏࡖࡐࡗࠩࢂ࠭ຎ"), str(len(sessions)))
    bstack11lll1l11_opy_ = bstack11lll1l11_opy_.replace(bstack11l111_opy_ (u"ࠪࡿࠪࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠦࡿࠪຏ"), bstack1llll111l_opy_)
    bstack11lll1l11_opy_ = bstack11lll1l11_opy_.replace(bstack11l111_opy_ (u"ࠫࢀࠫࡂࡖࡋࡏࡈࡤࡔࡁࡎࡇࠨࢁࠬຐ"),
                                              sessions[0].get(bstack11l111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣࡳࡧ࡭ࡦࠩຑ")) if sessions[0] else bstack11l111_opy_ (u"࠭ࠧຒ"))
    with open(os.path.join(bstack11111111_opy_, bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠳ࡲࡦࡲࡲࡶࡹ࠴ࡨࡵ࡯࡯ࠫຓ")), bstack11l111_opy_ (u"ࠨࡹࠪດ")) as stream:
      stream.write(bstack11lll1l11_opy_.split(bstack11l111_opy_ (u"ࠩࡾࠩࡘࡋࡓࡔࡋࡒࡒࡘࡥࡄࡂࡖࡄࠩࢂ࠭ຕ"))[0])
      for session in sessions:
        stream.write(bstack1l11l111ll_opy_(session))
      stream.write(bstack11lll1l11_opy_.split(bstack11l111_opy_ (u"ࠪࡿ࡙ࠪࡅࡔࡕࡌࡓࡓ࡙࡟ࡅࡃࡗࡅࠪࢃࠧຖ"))[1])
    logger.info(bstack11l111_opy_ (u"ࠫࡌ࡫࡮ࡦࡴࡤࡸࡪࡪࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡢࡶ࡫࡯ࡨࠥࡧࡲࡵ࡫ࡩࡥࡨࡺࡳࠡࡣࡷࠤࢀࢃࠧທ").format(bstack11111111_opy_));
  except Exception as e:
    logger.debug(bstack1l11l111_opy_.format(str(e)))
def bstack1l1l1ll1_opy_(hashed_id):
  global CONFIG
  try:
    bstack11l1l11l1l_opy_ = datetime.datetime.now()
    host = bstack11l111_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡡࡱ࡫࠰ࡧࡱࡵࡵࡥ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱࠬຘ") if bstack11l111_opy_ (u"࠭ࡡࡱࡲࠪນ") in CONFIG else bstack11l111_opy_ (u"ࠧࡩࡶࡷࡴࡸࡀ࠯࠰ࡣࡳ࡭࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭ࠨບ")
    user = CONFIG[bstack11l111_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪປ")]
    key = CONFIG[bstack11l111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬຜ")]
    bstack1ll111ll11_opy_ = bstack11l111_opy_ (u"ࠪࡥࡵࡶ࠭ࡢࡷࡷࡳࡲࡧࡴࡦࠩຝ") if bstack11l111_opy_ (u"ࠫࡦࡶࡰࠨພ") in CONFIG else (bstack11l111_opy_ (u"ࠬࡺࡵࡳࡤࡲࡷࡨࡧ࡬ࡦࠩຟ") if CONFIG.get(bstack11l111_opy_ (u"࠭ࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧࠪຠ")) else bstack11l111_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡦࠩມ"))
    host = bstack111111ll_opy_(cli.config, [bstack11l111_opy_ (u"ࠣࡣࡳ࡭ࡸࠨຢ"), bstack11l111_opy_ (u"ࠤࡤࡴࡵࡇࡵࡵࡱࡰࡥࡹ࡫ࠢຣ"), bstack11l111_opy_ (u"ࠥࡥࡵ࡯ࠢ຤")], host) if bstack11l111_opy_ (u"ࠫࡦࡶࡰࠨລ") in CONFIG else bstack111111ll_opy_(cli.config, [bstack11l111_opy_ (u"ࠧࡧࡰࡪࡵࠥ຦"), bstack11l111_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡥࠣວ"), bstack11l111_opy_ (u"ࠢࡢࡲ࡬ࠦຨ")], host)
    url = bstack11l111_opy_ (u"ࠨࡽࢀ࠳ࢀࢃ࠯ࡣࡷ࡬ࡰࡩࡹ࠯ࡼࡿ࠲ࡷࡪࡹࡳࡪࡱࡱࡷ࠳ࡰࡳࡰࡰࠪຩ").format(host, bstack1ll111ll11_opy_, hashed_id)
    headers = {
      bstack11l111_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨສ"): bstack11l111_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ຫ"),
    }
    proxies = bstack11111llll_opy_(CONFIG, url)
    response = requests.get(url, headers=headers, proxies=proxies, auth=(user, key))
    if response.json():
      cli.bstack1l11lllll_opy_(bstack11l111_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼ࡪࡩࡹࡥࡳࡦࡵࡶ࡭ࡴࡴࡳࡠ࡮࡬ࡷࡹࠨຬ"), datetime.datetime.now() - bstack11l1l11l1l_opy_)
      return list(map(lambda session: session[bstack11l111_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡶࡩࡸࡹࡩࡰࡰࠪອ")], response.json()))
  except Exception as e:
    logger.debug(bstack11l1l1l11l_opy_.format(str(e)))
@measure(event_name=EVENTS.bstack1l1l1ll11l_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def get_build_link():
  global CONFIG
  global bstack1l1ll11ll_opy_
  try:
    if bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩຮ") in CONFIG:
      bstack11l1l11l1l_opy_ = datetime.datetime.now()
      host = bstack11l111_opy_ (u"ࠧࡢࡲ࡬࠱ࡨࡲ࡯ࡶࡦࠪຯ") if bstack11l111_opy_ (u"ࠨࡣࡳࡴࠬະ") in CONFIG else bstack11l111_opy_ (u"ࠩࡤࡴ࡮࠭ັ")
      user = CONFIG[bstack11l111_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬາ")]
      key = CONFIG[bstack11l111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧຳ")]
      bstack1ll111ll11_opy_ = bstack11l111_opy_ (u"ࠬࡧࡰࡱ࠯ࡤࡹࡹࡵ࡭ࡢࡶࡨࠫິ") if bstack11l111_opy_ (u"࠭ࡡࡱࡲࠪີ") in CONFIG else bstack11l111_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡦࠩຶ")
      url = bstack11l111_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࡾࢁ࠿ࢁࡽࡁࡽࢀ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡼࡿ࠲ࡦࡺ࡯࡬ࡥࡵ࠱࡮ࡸࡵ࡮ࠨື").format(user, key, host, bstack1ll111ll11_opy_)
      if cli.is_enabled(CONFIG):
        bstack1llll111l_opy_, hashed_id = cli.bstack11l1l1lll1_opy_()
        logger.info(bstack11lll1ll1l_opy_.format(bstack1llll111l_opy_))
        return [hashed_id, bstack1llll111l_opy_]
      else:
        headers = {
          bstack11l111_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨຸ"): bstack11l111_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳູ࠭"),
        }
        if bstack11l111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ຺࠭") in CONFIG:
          params = {bstack11l111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪົ"): CONFIG[bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩຼ")], bstack11l111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡩࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪຽ"): CONFIG[bstack11l111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ຾")]}
        else:
          params = {bstack11l111_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ຿"): CONFIG[bstack11l111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ເ")]}
        proxies = bstack11111llll_opy_(CONFIG, url)
        response = requests.get(url, params=params, headers=headers, proxies=proxies)
        if response.json():
          bstack1l1111l11_opy_ = response.json()[0][bstack11l111_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡤࡸ࡭ࡱࡪࠧແ")]
          if bstack1l1111l11_opy_:
            bstack1llll111l_opy_ = bstack1l1111l11_opy_[bstack11l111_opy_ (u"ࠬࡶࡵࡣ࡮࡬ࡧࡤࡻࡲ࡭ࠩໂ")].split(bstack11l111_opy_ (u"࠭ࡰࡶࡤ࡯࡭ࡨ࠳ࡢࡶ࡫࡯ࡨࠬໃ"))[0] + bstack11l111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡹ࠯ࠨໄ") + bstack1l1111l11_opy_[
              bstack11l111_opy_ (u"ࠨࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫ໅")]
            logger.info(bstack11lll1ll1l_opy_.format(bstack1llll111l_opy_))
            bstack1l1ll11ll_opy_ = bstack1l1111l11_opy_[bstack11l111_opy_ (u"ࠩ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬໆ")]
            bstack1111ll11l_opy_ = CONFIG[bstack11l111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭໇")]
            if bstack11l111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ່࠭") in CONFIG:
              bstack1111ll11l_opy_ += bstack11l111_opy_ (u"້ࠬࠦࠧ") + CONFIG[bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ໊")]
            if bstack1111ll11l_opy_ != bstack1l1111l11_opy_[bstack11l111_opy_ (u"ࠧ࡯ࡣࡰࡩ໋ࠬ")]:
              logger.debug(bstack1ll1llll11_opy_.format(bstack1l1111l11_opy_[bstack11l111_opy_ (u"ࠨࡰࡤࡱࡪ࠭໌")], bstack1111ll11l_opy_))
            cli.bstack1l11lllll_opy_(bstack11l111_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺ࡨࡧࡷࡣࡧࡻࡩ࡭ࡦࡢࡰ࡮ࡴ࡫ࠣໍ"), datetime.datetime.now() - bstack11l1l11l1l_opy_)
            return [bstack1l1111l11_opy_[bstack11l111_opy_ (u"ࠪ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭໎")], bstack1llll111l_opy_]
    else:
      logger.warn(bstack1l1ll11l11_opy_)
  except Exception as e:
    logger.debug(bstack1ll1lll111_opy_.format(str(e)))
  return [None, None]
def bstack1llll11ll1_opy_(url, bstack1lll11l1l1_opy_=False):
  global CONFIG
  global bstack1l1l111ll_opy_
  if not bstack1l1l111ll_opy_:
    hostname = bstack1l1ll1l1_opy_(url)
    is_private = bstack11l11l1l1_opy_(hostname)
    if (bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨ໏") in CONFIG and not bstack111ll1lll_opy_(CONFIG[bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ໐")])) and (is_private or bstack1lll11l1l1_opy_):
      bstack1l1l111ll_opy_ = hostname
def bstack1l1ll1l1_opy_(url):
  return urlparse(url).hostname
def bstack11l11l1l1_opy_(hostname):
  for bstack111llllll_opy_ in bstack1l111ll1l_opy_:
    regex = re.compile(bstack111llllll_opy_)
    if regex.match(hostname):
      return True
  return False
def bstack11l1111ll_opy_(bstack11l1l111_opy_):
  return True if bstack11l1l111_opy_ in threading.current_thread().__dict__.keys() else False
@measure(event_name=EVENTS.bstack1llll11l1l_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def getAccessibilityResults(driver):
  global CONFIG
  global bstack1l11l111l1_opy_
  bstack1ll1llll_opy_ = not (bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"࠭ࡩࡴࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ໑"), None) and bstack1l11lll1l1_opy_(
          threading.current_thread(), bstack11l111_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭໒"), None))
  bstack1ll11l1l1_opy_ = getattr(driver, bstack11l111_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨ໓"), None) != True
  bstack111ll111l_opy_ = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠩ࡬ࡷࡆࡶࡰࡂ࠳࠴ࡽ࡙࡫ࡳࡵࠩ໔"), None) and bstack1l11lll1l1_opy_(
          threading.current_thread(), bstack11l111_opy_ (u"ࠪࡥࡵࡶࡁ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ໕"), None)
  if bstack111ll111l_opy_:
    if not bstack1ll1l1ll1l_opy_():
      logger.warning(bstack11l111_opy_ (u"ࠦࡓࡵࡴࠡࡣࡱࠤࡆࡶࡰࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡹࡥࡴࡵ࡬ࡳࡳ࠲ࠠࡤࡣࡱࡲࡴࡺࠠࡳࡧࡷࡶ࡮࡫ࡶࡦࠢࡄࡴࡵࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡲࡦࡵࡸࡰࡹࡹ࠮ࠣ໖"))
      return {}
    logger.debug(bstack11l111_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡴࡨࡷࡺࡲࡴࡴࠩ໗"))
    logger.debug(perform_scan(driver, driver_command=bstack11l111_opy_ (u"࠭ࡥࡹࡧࡦࡹࡹ࡫ࡓࡤࡴ࡬ࡴࡹ࠭໘")))
    results = bstack1l1ll111ll_opy_(bstack11l111_opy_ (u"ࠢࡳࡧࡶࡹࡱࡺࡳࠣ໙"))
    if results is not None and results.get(bstack11l111_opy_ (u"ࠣ࡫ࡶࡷࡺ࡫ࡳࠣ໚")) is not None:
        return results[bstack11l111_opy_ (u"ࠤ࡬ࡷࡸࡻࡥࡴࠤ໛")]
    logger.error(bstack11l111_opy_ (u"ࠥࡒࡴࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡒࡦࡵࡸࡰࡹࡹࠠࡸࡧࡵࡩࠥ࡬࡯ࡶࡰࡧ࠲ࠧໜ"))
    return []
  if not bstack1lllll11l_opy_.bstack11l1l11l11_opy_(CONFIG, bstack1l11l111l1_opy_) or (bstack1ll11l1l1_opy_ and bstack1ll1llll_opy_):
    logger.warning(bstack11l111_opy_ (u"ࠦࡓࡵࡴࠡࡣࡱࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡵࡨࡷࡸ࡯࡯࡯࠮ࠣࡧࡦࡴ࡮ࡰࡶࠣࡶࡪࡺࡲࡪࡧࡹࡩࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡸࡥࡴࡷ࡯ࡸࡸ࠴ࠢໝ"))
    return {}
  try:
    logger.debug(bstack11l111_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡴࡨࡷࡺࡲࡴࡴࠩໞ"))
    logger.debug(perform_scan(driver))
    results = driver.execute_async_script(bstack1ll11l1lll_opy_.bstack1l111l1111_opy_)
    return results
  except Exception:
    logger.error(bstack11l111_opy_ (u"ࠨࡎࡰࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡵࡩࡸࡻ࡬ࡵࡵࠣࡻࡪࡸࡥࠡࡨࡲࡹࡳࡪ࠮ࠣໟ"))
    return {}
@measure(event_name=EVENTS.bstack11lllll1l1_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def getAccessibilityResultsSummary(driver):
  global CONFIG
  global bstack1l11l111l1_opy_
  bstack1ll1llll_opy_ = not (bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠧࡪࡵࡄ࠵࠶ࡿࡔࡦࡵࡷࠫ໠"), None) and bstack1l11lll1l1_opy_(
          threading.current_thread(), bstack11l111_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ໡"), None))
  bstack1ll11l1l1_opy_ = getattr(driver, bstack11l111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩ໢"), None) != True
  bstack111ll111l_opy_ = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠪ࡭ࡸࡇࡰࡱࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ໣"), None) and bstack1l11lll1l1_opy_(
          threading.current_thread(), bstack11l111_opy_ (u"ࠫࡦࡶࡰࡂ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭໤"), None)
  if bstack111ll111l_opy_:
    if not bstack1ll1l1ll1l_opy_():
      logger.warning(bstack11l111_opy_ (u"ࠧࡔ࡯ࡵࠢࡤࡲࠥࡇࡰࡱࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡳࡦࡵࡶ࡭ࡴࡴࠬࠡࡥࡤࡲࡳࡵࡴࠡࡴࡨࡸࡷ࡯ࡥࡷࡧࠣࡅࡵࡶࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡳࡧࡶࡹࡱࡺࡳࠡࡵࡸࡱࡲࡧࡲࡺ࠰ࠥ໥"))
      return {}
    logger.debug(bstack11l111_opy_ (u"࠭ࡐࡦࡴࡩࡳࡷࡳࡩ࡯ࡩࠣࡷࡨࡧ࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡵࡩࡸࡻ࡬ࡵࡵࠣࡷࡺࡳ࡭ࡢࡴࡼࠫ໦"))
    logger.debug(perform_scan(driver, driver_command=bstack11l111_opy_ (u"ࠧࡦࡺࡨࡧࡺࡺࡥࡔࡥࡵ࡭ࡵࡺࠧ໧")))
    results = bstack1l1ll111ll_opy_(bstack11l111_opy_ (u"ࠣࡴࡨࡷࡺࡲࡴࡔࡷࡰࡱࡦࡸࡹࠣ໨"))
    if results is not None and results.get(bstack11l111_opy_ (u"ࠤࡶࡹࡲࡳࡡࡳࡻࠥ໩")) is not None:
        return results[bstack11l111_opy_ (u"ࠥࡷࡺࡳ࡭ࡢࡴࡼࠦ໪")]
    logger.error(bstack11l111_opy_ (u"ࠦࡓࡵࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡓࡧࡶࡹࡱࡺࡳࠡࡕࡸࡱࡲࡧࡲࡺࠢࡺࡥࡸࠦࡦࡰࡷࡱࡨ࠳ࠨ໫"))
    return {}
  if not bstack1lllll11l_opy_.bstack11l1l11l11_opy_(CONFIG, bstack1l11l111l1_opy_) or (bstack1ll11l1l1_opy_ and bstack1ll1llll_opy_):
    logger.warning(bstack11l111_opy_ (u"ࠧࡔ࡯ࡵࠢࡤࡲࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡶࡩࡸࡹࡩࡰࡰ࠯ࠤࡨࡧ࡮࡯ࡱࡷࠤࡷ࡫ࡴࡳ࡫ࡨࡺࡪࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡲࡦࡵࡸࡰࡹࡹࠠࡴࡷࡰࡱࡦࡸࡹ࠯ࠤ໬"))
    return {}
  try:
    logger.debug(bstack11l111_opy_ (u"࠭ࡐࡦࡴࡩࡳࡷࡳࡩ࡯ࡩࠣࡷࡨࡧ࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡵࡩࡸࡻ࡬ࡵࡵࠣࡷࡺࡳ࡭ࡢࡴࡼࠫ໭"))
    logger.debug(perform_scan(driver))
    bstack1l11l11ll1_opy_ = driver.execute_async_script(bstack1ll11l1lll_opy_.bstack1l1llll1l1_opy_)
    return bstack1l11l11ll1_opy_
  except Exception:
    logger.error(bstack11l111_opy_ (u"ࠢࡏࡱࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡷࡺࡳ࡭ࡢࡴࡼࠤࡼࡧࡳࠡࡨࡲࡹࡳࡪ࠮ࠣ໮"))
    return {}
def bstack1ll1l1ll1l_opy_():
  global CONFIG
  global bstack1l11l111l1_opy_
  bstack111llll1ll_opy_ = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠨ࡫ࡶࡅࡵࡶࡁ࠲࠳ࡼࡘࡪࡹࡴࠨ໯"), None) and bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠩࡤࡴࡵࡇ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ໰"), None)
  if not bstack1lllll11l_opy_.bstack11l1l11l11_opy_(CONFIG, bstack1l11l111l1_opy_) or not bstack111llll1ll_opy_:
        logger.warning(bstack11l111_opy_ (u"ࠥࡒࡴࡺࠠࡢࡰࠣࡅࡵࡶࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠱ࠦࡣࡢࡰࡱࡳࡹࠦࡲࡦࡶࡵ࡭ࡪࡼࡥࠡࡴࡨࡷࡺࡲࡴࡴ࠰ࠥ໱"))
        return False
  return True
def bstack1l1ll111ll_opy_(bstack1lll1l11l1_opy_):
    bstack11ll1l11_opy_ = bstack11l11l1l_opy_.current_test_uuid() if bstack11l11l1l_opy_.current_test_uuid() else bstack1l11lllll1_opy_.current_hook_uuid()
    with ThreadPoolExecutor() as executor:
        future = executor.submit(bstack111l1l1ll_opy_(bstack11ll1l11_opy_, bstack1lll1l11l1_opy_))
        try:
            return future.result(timeout=bstack1lll1llll_opy_)
        except TimeoutError:
            logger.error(bstack11l111_opy_ (u"࡙ࠦ࡯࡭ࡦࡱࡸࡸࠥࡧࡦࡵࡧࡵࠤࢀࢃࡳࠡࡹ࡫࡭ࡱ࡫ࠠࡧࡧࡷࡧ࡭࡯࡮ࡨࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡕࡩࡸࡻ࡬ࡵࡵࠥ໲").format(bstack1lll1llll_opy_))
        except Exception as ex:
            logger.debug(bstack11l111_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡷ࡫ࡴࡳ࡫ࡨࡺ࡮ࡴࡧࠡࡃࡳࡴࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡾࢁ࠳ࠦࡅࡳࡴࡲࡶࠥ࠳ࠠࡼࡿࠥ໳").format(bstack1lll1l11l1_opy_, str(ex)))
    return {}
@measure(event_name=EVENTS.bstack1lll11ll1_opy_, stage=STAGE.bstack1l1l111l1_opy_, bstack1ll111l111_opy_=bstack1ll1l111l1_opy_)
def perform_scan(driver, *args, **kwargs):
  global CONFIG
  global bstack1l11l111l1_opy_
  bstack1ll1llll_opy_ = not (bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"࠭ࡩࡴࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ໴"), None) and bstack1l11lll1l1_opy_(
          threading.current_thread(), bstack11l111_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭໵"), None))
  bstack1lll11ll11_opy_ = not (bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠨ࡫ࡶࡅࡵࡶࡁ࠲࠳ࡼࡘࡪࡹࡴࠨ໶"), None) and bstack1l11lll1l1_opy_(
          threading.current_thread(), bstack11l111_opy_ (u"ࠩࡤࡴࡵࡇ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ໷"), None))
  bstack1ll11l1l1_opy_ = getattr(driver, bstack11l111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡄ࠵࠶ࡿࡓࡩࡱࡸࡰࡩ࡙ࡣࡢࡰࠪ໸"), None) != True
  if not bstack1lllll11l_opy_.bstack11l1l11l11_opy_(CONFIG, bstack1l11l111l1_opy_) or (bstack1ll11l1l1_opy_ and bstack1ll1llll_opy_ and bstack1lll11ll11_opy_):
    logger.warning(bstack11l111_opy_ (u"ࠦࡓࡵࡴࠡࡣࡱࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡵࡨࡷࡸ࡯࡯࡯࠮ࠣࡧࡦࡴ࡮ࡰࡶࠣࡶࡺࡴࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡴࡥࡤࡲ࠳ࠨ໹"))
    return {}
  try:
    bstack1ll111ll1_opy_ = bstack11l111_opy_ (u"ࠬࡧࡰࡱࠩ໺") in CONFIG and CONFIG.get(bstack11l111_opy_ (u"࠭ࡡࡱࡲࠪ໻"), bstack11l111_opy_ (u"ࠧࠨ໼"))
    session_id = getattr(driver, bstack11l111_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠬ໽"), None)
    if not session_id:
      logger.warning(bstack11l111_opy_ (u"ࠤࡑࡳࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡉࡅࠢࡩࡳࡺࡴࡤࠡࡨࡲࡶࠥࡪࡲࡪࡸࡨࡶࠧ໾"))
      return {bstack11l111_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤ໿"): bstack11l111_opy_ (u"ࠦࡓࡵࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡋࡇࠤ࡫ࡵࡵ࡯ࡦࠥༀ")}
    if bstack1ll111ll1_opy_:
      try:
        bstack111l1lll1_opy_ = {
              bstack11l111_opy_ (u"ࠬࡺࡨࡋࡹࡷࡘࡴࡱࡥ࡯ࠩ༁"): os.environ.get(bstack11l111_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫ༂"), os.environ.get(bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ༃"), bstack11l111_opy_ (u"ࠨࠩ༄"))),
              bstack11l111_opy_ (u"ࠩࡷ࡬࡙࡫ࡳࡵࡔࡸࡲ࡚ࡻࡩࡥࠩ༅"): bstack11l11l1l_opy_.current_test_uuid() if bstack11l11l1l_opy_.current_test_uuid() else bstack1l11lllll1_opy_.current_hook_uuid(),
              bstack11l111_opy_ (u"ࠪࡥࡺࡺࡨࡉࡧࡤࡨࡪࡸࠧ༆"): os.environ.get(bstack11l111_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩ༇")),
              bstack11l111_opy_ (u"ࠬࡹࡣࡢࡰࡗ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬ༈"): str(int(datetime.datetime.now().timestamp() * 1000)),
              bstack11l111_opy_ (u"࠭ࡴࡩࡄࡸ࡭ࡱࡪࡕࡶ࡫ࡧࠫ༉"): os.environ.get(bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬ༊"), bstack11l111_opy_ (u"ࠨࠩ་")),
              bstack11l111_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࠩ༌"): kwargs.get(bstack11l111_opy_ (u"ࠪࡨࡷ࡯ࡶࡦࡴࡢࡧࡴࡳ࡭ࡢࡰࡧࠫ།"), None) or bstack11l111_opy_ (u"ࠫࠬ༎")
          }
        if not hasattr(thread_local, bstack11l111_opy_ (u"ࠬࡨࡡࡴࡧࡢࡥࡵࡶ࡟ࡢ࠳࠴ࡽࡤࡹࡣࡳ࡫ࡳࡸࠬ༏")):
            scripts = {bstack11l111_opy_ (u"࠭ࡳࡤࡣࡱࠫ༐"): bstack1ll11l1lll_opy_.perform_scan}
            thread_local.base_app_a11y_script = scripts
        bstack1ll1ll11l1_opy_ = copy.deepcopy(thread_local.base_app_a11y_script)
        bstack1ll1ll11l1_opy_[bstack11l111_opy_ (u"ࠧࡴࡥࡤࡲࠬ༑")] = bstack1ll1ll11l1_opy_[bstack11l111_opy_ (u"ࠨࡵࡦࡥࡳ࠭༒")] % json.dumps(bstack111l1lll1_opy_)
        bstack1ll11l1lll_opy_.bstack111lllll1_opy_(bstack1ll1ll11l1_opy_)
        bstack1ll11l1lll_opy_.store()
        bstack111llll11l_opy_ = driver.execute_script(bstack1ll11l1lll_opy_.perform_scan)
      except Exception as bstack11ll1lll1_opy_:
        logger.info(bstack11l111_opy_ (u"ࠤࡄࡴࡵ࡯ࡵ࡮ࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡶࡧࡦࡴࠠࡧࡣ࡬ࡰࡪࡪ࠺ࠡࠤ༓") + str(bstack11ll1lll1_opy_))
        bstack111llll11l_opy_ = {bstack11l111_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤ༔"): str(bstack11ll1lll1_opy_)}
    else:
      bstack111llll11l_opy_ = driver.execute_async_script(bstack1ll11l1lll_opy_.perform_scan, {bstack11l111_opy_ (u"ࠫࡲ࡫ࡴࡩࡱࡧࠫ༕"): kwargs.get(bstack11l111_opy_ (u"ࠬࡪࡲࡪࡸࡨࡶࡤࡩ࡯࡮࡯ࡤࡲࡩ࠭༖"), None) or bstack11l111_opy_ (u"࠭ࠧ༗")})
    return bstack111llll11l_opy_
  except Exception as err:
    logger.error(bstack11l111_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡶࡺࡴࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡴࡥࡤࡲ࠳ࠦࡻࡾࠤ༘").format(str(err)))
    return {}