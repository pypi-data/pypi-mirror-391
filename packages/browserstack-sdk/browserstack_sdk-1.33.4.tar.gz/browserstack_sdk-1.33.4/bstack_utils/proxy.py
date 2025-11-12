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
from urllib.parse import urlparse
from bstack_utils.config import Config
from bstack_utils.messages import bstack111l111lll1_opy_
bstack11l11ll1l_opy_ = Config.bstack111llll1_opy_()
def bstack1llllll1111l_opy_(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
def bstack1llllll11l1l_opy_(bstack1llllll11111_opy_, bstack1llllll11ll1_opy_):
    from pypac import get_pac
    from pypac import PACSession
    from pypac.parser import PACFile
    import socket
    if os.path.isfile(bstack1llllll11111_opy_):
        with open(bstack1llllll11111_opy_) as f:
            pac = PACFile(f.read())
    elif bstack1llllll1111l_opy_(bstack1llllll11111_opy_):
        pac = get_pac(url=bstack1llllll11111_opy_)
    else:
        raise Exception(bstack11l111_opy_ (u"ࠧࡑࡣࡦࠤ࡫࡯࡬ࡦࠢࡧࡳࡪࡹࠠ࡯ࡱࡷࠤࡪࡾࡩࡴࡶ࠽ࠤࢀࢃࠧΊ").format(bstack1llllll11111_opy_))
    session = PACSession(pac)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((bstack11l111_opy_ (u"ࠣ࠺࠱࠼࠳࠾࠮࠹ࠤ῜"), 80))
        bstack1llllll111l1_opy_ = s.getsockname()[0]
        s.close()
    except:
        bstack1llllll111l1_opy_ = bstack11l111_opy_ (u"ࠩ࠳࠲࠵࠴࠰࠯࠲ࠪ῝")
    proxy_url = session.get_pac().find_proxy_for_url(bstack1llllll11ll1_opy_, bstack1llllll111l1_opy_)
    return proxy_url
def bstack11lll1ll_opy_(config):
    return bstack11l111_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ࠭῞") in config or bstack11l111_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨ῟") in config
def bstack1lll111lll_opy_(config):
    if not bstack11lll1ll_opy_(config):
        return
    if config.get(bstack11l111_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨῠ")):
        return config.get(bstack11l111_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩῡ"))
    if config.get(bstack11l111_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫῢ")):
        return config.get(bstack11l111_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬΰ"))
def bstack11111llll_opy_(config, bstack1llllll11ll1_opy_):
    proxy = bstack1lll111lll_opy_(config)
    proxies = {}
    if config.get(bstack11l111_opy_ (u"ࠩ࡫ࡸࡹࡶࡐࡳࡱࡻࡽࠬῤ")) or config.get(bstack11l111_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧῥ")):
        if proxy.endswith(bstack11l111_opy_ (u"ࠫ࠳ࡶࡡࡤࠩῦ")):
            proxies = bstack1lllll1ll_opy_(proxy, bstack1llllll11ll1_opy_)
        else:
            proxies = {
                bstack11l111_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࠫῧ"): proxy
            }
    bstack11l11ll1l_opy_.bstack11l1l1ll11_opy_(bstack11l111_opy_ (u"࠭ࡰࡳࡱࡻࡽࡘ࡫ࡴࡵ࡫ࡱ࡫ࡸ࠭Ῠ"), proxies)
    return proxies
def bstack1lllll1ll_opy_(bstack1llllll11111_opy_, bstack1llllll11ll1_opy_):
    proxies = {}
    global bstack1llllll111ll_opy_
    if bstack11l111_opy_ (u"ࠧࡑࡃࡆࡣࡕࡘࡏ࡙࡛ࠪῩ") in globals():
        return bstack1llllll111ll_opy_
    try:
        proxy = bstack1llllll11l1l_opy_(bstack1llllll11111_opy_, bstack1llllll11ll1_opy_)
        if bstack11l111_opy_ (u"ࠣࡆࡌࡖࡊࡉࡔࠣῪ") in proxy:
            proxies = {}
        elif bstack11l111_opy_ (u"ࠤࡋࡘ࡙ࡖࠢΎ") in proxy or bstack11l111_opy_ (u"ࠥࡌ࡙࡚ࡐࡔࠤῬ") in proxy or bstack11l111_opy_ (u"ࠦࡘࡕࡃࡌࡕࠥ῭") in proxy:
            bstack1llllll11l11_opy_ = proxy.split(bstack11l111_opy_ (u"ࠧࠦࠢ΅"))
            if bstack11l111_opy_ (u"ࠨ࠺࠰࠱ࠥ`") in bstack11l111_opy_ (u"ࠢࠣ῰").join(bstack1llllll11l11_opy_[1:]):
                proxies = {
                    bstack11l111_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧ῱"): bstack11l111_opy_ (u"ࠤࠥῲ").join(bstack1llllll11l11_opy_[1:])
                }
            else:
                proxies = {
                    bstack11l111_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩῳ"): str(bstack1llllll11l11_opy_[0]).lower() + bstack11l111_opy_ (u"ࠦ࠿࠵࠯ࠣῴ") + bstack11l111_opy_ (u"ࠧࠨ῵").join(bstack1llllll11l11_opy_[1:])
                }
        elif bstack11l111_opy_ (u"ࠨࡐࡓࡑ࡛࡝ࠧῶ") in proxy:
            bstack1llllll11l11_opy_ = proxy.split(bstack11l111_opy_ (u"ࠢࠡࠤῷ"))
            if bstack11l111_opy_ (u"ࠣ࠼࠲࠳ࠧῸ") in bstack11l111_opy_ (u"ࠤࠥΌ").join(bstack1llllll11l11_opy_[1:]):
                proxies = {
                    bstack11l111_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩῺ"): bstack11l111_opy_ (u"ࠦࠧΏ").join(bstack1llllll11l11_opy_[1:])
                }
            else:
                proxies = {
                    bstack11l111_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࠫῼ"): bstack11l111_opy_ (u"ࠨࡨࡵࡶࡳ࠾࠴࠵ࠢ´") + bstack11l111_opy_ (u"ࠢࠣ῾").join(bstack1llllll11l11_opy_[1:])
                }
        else:
            proxies = {
                bstack11l111_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧ῿"): proxy
            }
    except Exception as e:
        print(bstack11l111_opy_ (u"ࠤࡶࡳࡲ࡫ࠠࡦࡴࡵࡳࡷࠨ "), bstack111l111lll1_opy_.format(bstack1llllll11111_opy_, str(e)))
    bstack1llllll111ll_opy_ = proxies
    return proxies