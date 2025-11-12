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
import grpc
import copy
import asyncio
import threading
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1lll1l11ll1_opy_ import bstack1lll1ll1l11_opy_
from browserstack_sdk.sdk_cli.bstack1lllll11lll_opy_ import (
    bstack1llll11111l_opy_,
    bstack1llll1l11l1_opy_,
    bstack1lllll1lll1_opy_,
)
from bstack_utils.constants import *
from typing import Any, List, Union, Dict
from pathlib import Path
from browserstack_sdk.sdk_cli.bstack1ll1l111ll1_opy_ import bstack1ll1l11111l_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack1llllll1l1_opy_
from bstack_utils.helper import bstack1l1l1l1l1ll_opy_
import threading
import os
import urllib.parse
class bstack1lll1llll11_opy_(bstack1lll1ll1l11_opy_):
    def __init__(self, bstack1ll1l1lll11_opy_):
        super().__init__()
        bstack1ll1l11111l_opy_.bstack1ll111111ll_opy_((bstack1llll11111l_opy_.bstack1llll111l1l_opy_, bstack1llll1l11l1_opy_.PRE), self.bstack1l11lll11l1_opy_)
        bstack1ll1l11111l_opy_.bstack1ll111111ll_opy_((bstack1llll11111l_opy_.bstack1llll111l1l_opy_, bstack1llll1l11l1_opy_.PRE), self.bstack1l11lll1l11_opy_)
        bstack1ll1l11111l_opy_.bstack1ll111111ll_opy_((bstack1llll11111l_opy_.bstack1llll1llll1_opy_, bstack1llll1l11l1_opy_.PRE), self.bstack1l11lll1ll1_opy_)
        bstack1ll1l11111l_opy_.bstack1ll111111ll_opy_((bstack1llll11111l_opy_.bstack1llll111lll_opy_, bstack1llll1l11l1_opy_.PRE), self.bstack1l11llll1ll_opy_)
        bstack1ll1l11111l_opy_.bstack1ll111111ll_opy_((bstack1llll11111l_opy_.bstack1llll111l1l_opy_, bstack1llll1l11l1_opy_.PRE), self.bstack1l1l11111ll_opy_)
        bstack1ll1l11111l_opy_.bstack1ll111111ll_opy_((bstack1llll11111l_opy_.QUIT, bstack1llll1l11l1_opy_.PRE), self.on_close)
        self.bstack1ll1l1lll11_opy_ = bstack1ll1l1lll11_opy_
    def is_enabled(self) -> bool:
        return True
    def bstack1l11lll11l1_opy_(
        self,
        f: bstack1ll1l11111l_opy_,
        bstack1l11lll111l_opy_: object,
        exec: Tuple[bstack1lllll1lll1_opy_, str],
        bstack1llll11llll_opy_: Tuple[bstack1llll11111l_opy_, bstack1llll1l11l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l111_opy_ (u"ࠣ࡮ࡤࡹࡳࡩࡨࠣፏ"):
            return
        if not bstack1l1l1l1l1ll_opy_():
            self.logger.debug(bstack11l111_opy_ (u"ࠤࡕࡩࡹࡻࡲ࡯࡫ࡱ࡫ࠥ࡯࡮ࠡ࡮ࡤࡹࡳࡩࡨࠡ࡯ࡨࡸ࡭ࡵࡤ࠭ࠢࡱࡳࡹࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳࠨፐ"))
            return
        def wrapped(bstack1l11lll111l_opy_, launch, *args, **kwargs):
            response = self.bstack1l11lllll1l_opy_(f.platform_index, instance.ref(), json.dumps({bstack11l111_opy_ (u"ࠪ࡭ࡸࡖ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩፑ"): True}).encode(bstack11l111_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥፒ")))
            if response is not None and response.capabilities:
                if not bstack1l1l1l1l1ll_opy_():
                    browser = launch(bstack1l11lll111l_opy_)
                    return browser
                bstack1l1l11111l1_opy_ = json.loads(response.capabilities.decode(bstack11l111_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦፓ")))
                if not bstack1l1l11111l1_opy_: # empty caps bstack1l11llll11l_opy_ bstack1l1l1111111_opy_ bstack1l11llll1l1_opy_ bstack1ll1l11llll_opy_ or error in processing
                    return
                bstack1l11lll1lll_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l1l11111l1_opy_))
                f.bstack1llll1l1111_opy_(instance, bstack1ll1l11111l_opy_.bstack1l11lllll11_opy_, bstack1l11lll1lll_opy_)
                f.bstack1llll1l1111_opy_(instance, bstack1ll1l11111l_opy_.bstack1l11lllllll_opy_, bstack1l1l11111l1_opy_)
                browser = bstack1l11lll111l_opy_.connect(bstack1l11lll1lll_opy_)
                return browser
        return wrapped
    def bstack1l11lll1ll1_opy_(
        self,
        f: bstack1ll1l11111l_opy_,
        Connection: object,
        exec: Tuple[bstack1lllll1lll1_opy_, str],
        bstack1llll11llll_opy_: Tuple[bstack1llll11111l_opy_, bstack1llll1l11l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l111_opy_ (u"ࠨࡤࡪࡵࡳࡥࡹࡩࡨࠣፔ"):
            self.logger.debug(bstack11l111_opy_ (u"ࠢࡓࡧࡷࡹࡷࡴࡩ࡯ࡩࠣ࡭ࡳࠦࡤࡪࡵࡳࡥࡹࡩࡨࠡ࡯ࡨࡸ࡭ࡵࡤ࠭ࠢࡱࡳࡹࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳࠨፕ"))
            return
        if not bstack1l1l1l1l1ll_opy_():
            return
        def wrapped(Connection, dispatch, *args, **kwargs):
            data = args[0]
            try:
                if args and args[0].get(bstack11l111_opy_ (u"ࠨࡲࡤࡶࡦࡳࡳࠨፖ"), {}).get(bstack11l111_opy_ (u"ࠩࡥࡷࡕࡧࡲࡢ࡯ࡶࠫፗ")):
                    bstack1l1l111111l_opy_ = args[0][bstack11l111_opy_ (u"ࠥࡴࡦࡸࡡ࡮ࡵࠥፘ")][bstack11l111_opy_ (u"ࠦࡧࡹࡐࡢࡴࡤࡱࡸࠨፙ")]
                    session_id = bstack1l1l111111l_opy_.get(bstack11l111_opy_ (u"ࠧࡹࡥࡴࡵ࡬ࡳࡳࡏࡤࠣፚ"))
                    f.bstack1llll1l1111_opy_(instance, bstack1ll1l11111l_opy_.bstack1l11llll111_opy_, session_id)
            except Exception as e:
                self.logger.debug(bstack11l111_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡪࡩࡴࡲࡤࡸࡨ࡮ࠠ࡮ࡧࡷ࡬ࡴࡪ࠺ࠡࠤ፛"), e)
            dispatch(Connection, *args)
        return wrapped
    def bstack1l1l11111ll_opy_(
        self,
        f: bstack1ll1l11111l_opy_,
        bstack1l11lll111l_opy_: object,
        exec: Tuple[bstack1lllll1lll1_opy_, str],
        bstack1llll11llll_opy_: Tuple[bstack1llll11111l_opy_, bstack1llll1l11l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l111_opy_ (u"ࠢࡤࡱࡱࡲࡪࡩࡴࠣ፜"):
            return
        if not bstack1l1l1l1l1ll_opy_():
            self.logger.debug(bstack11l111_opy_ (u"ࠣࡔࡨࡸࡺࡸ࡮ࡪࡰࡪࠤ࡮ࡴࠠࡤࡱࡱࡲࡪࡩࡴࠡ࡯ࡨࡸ࡭ࡵࡤ࠭ࠢࡱࡳࡹࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳࠨ፝"))
            return
        def wrapped(bstack1l11lll111l_opy_, connect, *args, **kwargs):
            response = self.bstack1l11lllll1l_opy_(f.platform_index, instance.ref(), json.dumps({bstack11l111_opy_ (u"ࠩ࡬ࡷࡕࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨ፞"): True}).encode(bstack11l111_opy_ (u"ࠥࡹࡹ࡬࠭࠹ࠤ፟")))
            if response is not None and response.capabilities:
                bstack1l1l11111l1_opy_ = json.loads(response.capabilities.decode(bstack11l111_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥ፠")))
                if not bstack1l1l11111l1_opy_:
                    return
                bstack1l11lll1lll_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l1l11111l1_opy_))
                if bstack1l1l11111l1_opy_.get(bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ፡")):
                    browser = bstack1l11lll111l_opy_.bstack1l11lll1l1l_opy_(bstack1l11lll1lll_opy_)
                    return browser
                else:
                    args = list(args)
                    args[0] = bstack1l11lll1lll_opy_
                    return connect(bstack1l11lll111l_opy_, *args, **kwargs)
        return wrapped
    def bstack1l11lll1l11_opy_(
        self,
        f: bstack1ll1l11111l_opy_,
        bstack1l1lll1111l_opy_: object,
        exec: Tuple[bstack1lllll1lll1_opy_, str],
        bstack1llll11llll_opy_: Tuple[bstack1llll11111l_opy_, bstack1llll1l11l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l111_opy_ (u"ࠨ࡮ࡦࡹࡢࡴࡦ࡭ࡥࠣ።"):
            return
        if not bstack1l1l1l1l1ll_opy_():
            self.logger.debug(bstack11l111_opy_ (u"ࠢࡓࡧࡷࡹࡷࡴࡩ࡯ࡩࠣ࡭ࡳࠦ࡮ࡦࡹࡢࡴࡦ࡭ࡥࠡ࡯ࡨࡸ࡭ࡵࡤ࠭ࠢࡱࡳࡹࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳࠨ፣"))
            return
        def wrapped(bstack1l1lll1111l_opy_, bstack1l11llllll1_opy_, *args, **kwargs):
            contexts = bstack1l1lll1111l_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                            if bstack11l111_opy_ (u"ࠣࡣࡥࡳࡺࡺ࠺ࡣ࡮ࡤࡲࡰࠨ፤") in page.url:
                                return page
                            else:
                                return bstack1l11llllll1_opy_(bstack1l1lll1111l_opy_)
                    else:
                        return bstack1l11llllll1_opy_(bstack1l1lll1111l_opy_)
        return wrapped
    def bstack1l11lllll1l_opy_(self, platform_index: int, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        self.logger.debug(bstack11l111_opy_ (u"ࠤࡵࡩ࡬࡯ࡳࡵࡧࡵࡣࡼ࡫ࡢࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰ࡬ࡸ࠿ࠦࠢ፥") + str(req) + bstack11l111_opy_ (u"ࠥࠦ፦"))
        try:
            r = self.bstack1lll111llll_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack11l111_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࡹࡵࡤࡥࡨࡷࡸࡃࠢ፧") + str(r.success) + bstack11l111_opy_ (u"ࠧࠨ፨"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack11l111_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦ፩") + str(e) + bstack11l111_opy_ (u"ࠢࠣ፪"))
            traceback.print_exc()
            raise e
    def bstack1l11llll1ll_opy_(
        self,
        f: bstack1ll1l11111l_opy_,
        Connection: object,
        exec: Tuple[bstack1lllll1lll1_opy_, str],
        bstack1llll11llll_opy_: Tuple[bstack1llll11111l_opy_, bstack1llll1l11l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l111_opy_ (u"ࠣࡡࡶࡩࡳࡪ࡟࡮ࡧࡶࡷࡦ࡭ࡥࡠࡶࡲࡣࡸ࡫ࡲࡷࡧࡵࠦ፫"):
            return
        if not bstack1l1l1l1l1ll_opy_():
            return
        def wrapped(Connection, bstack1l11lll11ll_opy_, *args, **kwargs):
            return bstack1l11lll11ll_opy_(Connection, *args, **kwargs)
        return wrapped
    def on_close(
        self,
        f: bstack1ll1l11111l_opy_,
        bstack1l11lll111l_opy_: object,
        exec: Tuple[bstack1lllll1lll1_opy_, str],
        bstack1llll11llll_opy_: Tuple[bstack1llll11111l_opy_, bstack1llll1l11l1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack11l111_opy_ (u"ࠤࡦࡰࡴࡹࡥࠣ፬"):
            return
        if not bstack1l1l1l1l1ll_opy_():
            self.logger.debug(bstack11l111_opy_ (u"ࠥࡖࡪࡺࡵࡳࡰ࡬ࡲ࡬ࠦࡩ࡯ࠢࡦࡰࡴࡹࡥࠡ࡯ࡨࡸ࡭ࡵࡤ࠭ࠢࡱࡳࡹࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳࠨ፭"))
            return
        def wrapped(Connection, close, *args, **kwargs):
            return close(Connection)
        return wrapped