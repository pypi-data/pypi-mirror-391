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
import threading
from uuid import uuid4
from itertools import zip_longest
from collections import OrderedDict
from robot.libraries.BuiltIn import BuiltIn
from browserstack_sdk.bstack1111lll111_opy_ import RobotHandler
from bstack_utils.capture import bstack111ll1llll_opy_
from bstack_utils.bstack111ll1l111_opy_ import bstack1111l1l11l_opy_, bstack111l1ll1l1_opy_, bstack111ll1l11l_opy_
from bstack_utils.bstack111ll1l1l1_opy_ import bstack1l11lllll1_opy_
from bstack_utils.bstack111ll1111l_opy_ import bstack11l11l1l_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack1l11lll1l1_opy_, bstack1l11ll11l_opy_, Result, \
    error_handler, bstack111l11ll1l_opy_
class bstack_robot_listener:
    ROBOT_LISTENER_API_VERSION = 2
    _lock = threading.Lock()
    store = {
        bstack11l111_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩྍ"): [],
        bstack11l111_opy_ (u"࠭ࡧ࡭ࡱࡥࡥࡱࡥࡨࡰࡱ࡮ࡷࠬྎ"): [],
        bstack11l111_opy_ (u"ࠧࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࠫྏ"): []
    }
    bstack111l1l11ll_opy_ = []
    bstack111l1111ll_opy_ = []
    @staticmethod
    def bstack111ll1ll11_opy_(log):
        if not ((isinstance(log[bstack11l111_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩྐ")], list) or (isinstance(log[bstack11l111_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪྑ")], dict)) and len(log[bstack11l111_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫྒ")])>0) or (isinstance(log[bstack11l111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬྒྷ")], str) and log[bstack11l111_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ྔ")].strip())):
            return
        active = bstack1l11lllll1_opy_.bstack111lll1111_opy_()
        log = {
            bstack11l111_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬྕ"): log[bstack11l111_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ྖ")],
            bstack11l111_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫྗ"): bstack111l11ll1l_opy_().isoformat() + bstack11l111_opy_ (u"ࠩ࡝ࠫ྘"),
            bstack11l111_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫྙ"): log[bstack11l111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬྚ")],
        }
        if active:
            if active[bstack11l111_opy_ (u"ࠬࡺࡹࡱࡧࠪྛ")] == bstack11l111_opy_ (u"࠭ࡨࡰࡱ࡮ࠫྜ"):
                log[bstack11l111_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧྜྷ")] = active[bstack11l111_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨྞ")]
            elif active[bstack11l111_opy_ (u"ࠩࡷࡽࡵ࡫ࠧྟ")] == bstack11l111_opy_ (u"ࠪࡸࡪࡹࡴࠨྠ"):
                log[bstack11l111_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫྡ")] = active[bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬྡྷ")]
        bstack11l11l1l_opy_.bstack1l111lll1_opy_([log])
    def __init__(self):
        self.messages = bstack111l1l1lll_opy_()
        self._111l11ll11_opy_ = None
        self._1111l1ll1l_opy_ = None
        self._1111lll11l_opy_ = OrderedDict()
        self.bstack111ll11111_opy_ = bstack111ll1llll_opy_(self.bstack111ll1ll11_opy_)
    @error_handler(class_method=True)
    def start_suite(self, name, attrs):
        self.messages.bstack1111ll1ll1_opy_()
        if not self._1111lll11l_opy_.get(attrs.get(bstack11l111_opy_ (u"࠭ࡩࡥࠩྣ")), None):
            self._1111lll11l_opy_[attrs.get(bstack11l111_opy_ (u"ࠧࡪࡦࠪྤ"))] = {}
        bstack111l11lll1_opy_ = bstack111ll1l11l_opy_(
                bstack111l1l11l1_opy_=attrs.get(bstack11l111_opy_ (u"ࠨ࡫ࡧࠫྥ")),
                name=name,
                started_at=bstack1l11ll11l_opy_(),
                file_path=os.path.relpath(attrs[bstack11l111_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩྦ")], start=os.getcwd()) if attrs.get(bstack11l111_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪྦྷ")) != bstack11l111_opy_ (u"ࠫࠬྨ") else bstack11l111_opy_ (u"ࠬ࠭ྩ"),
                framework=bstack11l111_opy_ (u"࠭ࡒࡰࡤࡲࡸࠬྪ")
            )
        threading.current_thread().current_suite_id = attrs.get(bstack11l111_opy_ (u"ࠧࡪࡦࠪྫ"), None)
        self._1111lll11l_opy_[attrs.get(bstack11l111_opy_ (u"ࠨ࡫ࡧࠫྫྷ"))][bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬྭ")] = bstack111l11lll1_opy_
    @error_handler(class_method=True)
    def end_suite(self, name, attrs):
        messages = self.messages.bstack111l1l1l1l_opy_()
        self._111l11l1ll_opy_(messages)
        with self._lock:
            for bstack1111ll1lll_opy_ in self.bstack111l1l11ll_opy_:
                bstack1111ll1lll_opy_[bstack11l111_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࠬྮ")][bstack11l111_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪྯ")].extend(self.store[bstack11l111_opy_ (u"ࠬ࡭࡬ࡰࡤࡤࡰࡤ࡮࡯ࡰ࡭ࡶࠫྰ")])
                bstack11l11l1l_opy_.bstack1llll11l_opy_(bstack1111ll1lll_opy_)
            self.bstack111l1l11ll_opy_ = []
            self.store[bstack11l111_opy_ (u"࠭ࡧ࡭ࡱࡥࡥࡱࡥࡨࡰࡱ࡮ࡷࠬྱ")] = []
    @error_handler(class_method=True)
    def start_test(self, name, attrs):
        self.bstack111ll11111_opy_.start()
        if not self._1111lll11l_opy_.get(attrs.get(bstack11l111_opy_ (u"ࠧࡪࡦࠪྲ")), None):
            self._1111lll11l_opy_[attrs.get(bstack11l111_opy_ (u"ࠨ࡫ࡧࠫླ"))] = {}
        driver = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨྴ"), None)
        bstack111ll1l111_opy_ = bstack111ll1l11l_opy_(
            bstack111l1l11l1_opy_=attrs.get(bstack11l111_opy_ (u"ࠪ࡭ࡩ࠭ྵ")),
            name=name,
            started_at=bstack1l11ll11l_opy_(),
            file_path=os.path.relpath(attrs[bstack11l111_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫྶ")], start=os.getcwd()),
            scope=RobotHandler.bstack1111llll11_opy_(attrs.get(bstack11l111_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬྷ"), None)),
            framework=bstack11l111_opy_ (u"࠭ࡒࡰࡤࡲࡸࠬྸ"),
            tags=attrs[bstack11l111_opy_ (u"ࠧࡵࡣࡪࡷࠬྐྵ")],
            hooks=self.store[bstack11l111_opy_ (u"ࠨࡩ࡯ࡳࡧࡧ࡬ࡠࡪࡲࡳࡰࡹࠧྺ")],
            bstack111ll1lll1_opy_=bstack11l11l1l_opy_.bstack111l1ll11l_opy_(driver) if driver and driver.session_id else {},
            meta={},
            code=bstack11l111_opy_ (u"ࠤࡾࢁࠥࡢ࡮ࠡࡽࢀࠦྻ").format(bstack11l111_opy_ (u"ࠥࠤࠧྼ").join(attrs[bstack11l111_opy_ (u"ࠫࡹࡧࡧࡴࠩ྽")]), name) if attrs[bstack11l111_opy_ (u"ࠬࡺࡡࡨࡵࠪ྾")] else name
        )
        self._1111lll11l_opy_[attrs.get(bstack11l111_opy_ (u"࠭ࡩࡥࠩ྿"))][bstack11l111_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ࿀")] = bstack111ll1l111_opy_
        threading.current_thread().current_test_uuid = bstack111ll1l111_opy_.bstack111l11l11l_opy_()
        threading.current_thread().current_test_id = attrs.get(bstack11l111_opy_ (u"ࠨ࡫ࡧࠫ࿁"), None)
        self.bstack111ll11lll_opy_(bstack11l111_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖࡸࡦࡸࡴࡦࡦࠪ࿂"), bstack111ll1l111_opy_)
    @error_handler(class_method=True)
    def end_test(self, name, attrs):
        self.bstack111ll11111_opy_.reset()
        bstack111l11l111_opy_ = bstack1111llllll_opy_.get(attrs.get(bstack11l111_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ࿃")), bstack11l111_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ࿄"))
        self._1111lll11l_opy_[attrs.get(bstack11l111_opy_ (u"ࠬ࡯ࡤࠨ࿅"))][bstack11l111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢ࿆ࠩ")].stop(time=bstack1l11ll11l_opy_(), duration=int(attrs.get(bstack11l111_opy_ (u"ࠧࡦ࡮ࡤࡴࡸ࡫ࡤࡵ࡫ࡰࡩࠬ࿇"), bstack11l111_opy_ (u"ࠨ࠲ࠪ࿈"))), result=Result(result=bstack111l11l111_opy_, exception=attrs.get(bstack11l111_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ࿉")), bstack111l1ll111_opy_=[attrs.get(bstack11l111_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ࿊"))]))
        self.bstack111ll11lll_opy_(bstack11l111_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭࿋"), self._1111lll11l_opy_[attrs.get(bstack11l111_opy_ (u"ࠬ࡯ࡤࠨ࿌"))][bstack11l111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ࿍")], True)
        with self._lock:
            self.store[bstack11l111_opy_ (u"ࠧࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࠫ࿎")] = []
        threading.current_thread().current_test_uuid = None
        threading.current_thread().current_test_id = None
    @error_handler(class_method=True)
    def start_keyword(self, name, attrs):
        self.messages.bstack1111ll1ll1_opy_()
        current_test_id = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡪࡦࠪ࿏"), None)
        bstack111l1l1111_opy_ = current_test_id if bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡧࠫ࿐"), None) else bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡸࡻࡩࡵࡧࡢ࡭ࡩ࠭࿑"), None)
        if attrs.get(bstack11l111_opy_ (u"ࠫࡹࡿࡰࡦࠩ࿒"), bstack11l111_opy_ (u"ࠬ࠭࿓")).lower() in [bstack11l111_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬ࿔"), bstack11l111_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࠩ࿕")]:
            hook_type = bstack111l11l1l1_opy_(attrs.get(bstack11l111_opy_ (u"ࠨࡶࡼࡴࡪ࠭࿖")), bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭࿗"), None))
            hook_name = bstack11l111_opy_ (u"ࠪࡿࢂ࠭࿘").format(attrs.get(bstack11l111_opy_ (u"ࠫࡰࡽ࡮ࡢ࡯ࡨࠫ࿙"), bstack11l111_opy_ (u"ࠬ࠭࿚")))
            if hook_type in [bstack11l111_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡁࡍࡎࠪ࿛"), bstack11l111_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡁࡍࡎࠪ࿜")]:
                hook_name = bstack11l111_opy_ (u"ࠨ࡝ࡾࢁࡢࠦࡻࡾࠩ࿝").format(bstack1111llll1l_opy_.get(hook_type), attrs.get(bstack11l111_opy_ (u"ࠩ࡮ࡻࡳࡧ࡭ࡦࠩ࿞"), bstack11l111_opy_ (u"ࠪࠫ࿟")))
            bstack111l1l111l_opy_ = bstack111l1ll1l1_opy_(
                bstack111l1l11l1_opy_=bstack111l1l1111_opy_ + bstack11l111_opy_ (u"ࠫ࠲࠭࿠") + attrs.get(bstack11l111_opy_ (u"ࠬࡺࡹࡱࡧࠪ࿡"), bstack11l111_opy_ (u"࠭ࠧ࿢")).lower(),
                name=hook_name,
                started_at=bstack1l11ll11l_opy_(),
                file_path=os.path.relpath(attrs.get(bstack11l111_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧ࿣")), start=os.getcwd()),
                framework=bstack11l111_opy_ (u"ࠨࡔࡲࡦࡴࡺࠧ࿤"),
                tags=attrs[bstack11l111_opy_ (u"ࠩࡷࡥ࡬ࡹࠧ࿥")],
                scope=RobotHandler.bstack1111llll11_opy_(attrs.get(bstack11l111_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪ࿦"), None)),
                hook_type=hook_type,
                meta={}
            )
            threading.current_thread().current_hook_uuid = bstack111l1l111l_opy_.bstack111l11l11l_opy_()
            threading.current_thread().current_hook_id = bstack111l1l1111_opy_ + bstack11l111_opy_ (u"ࠫ࠲࠭࿧") + attrs.get(bstack11l111_opy_ (u"ࠬࡺࡹࡱࡧࠪ࿨"), bstack11l111_opy_ (u"࠭ࠧ࿩")).lower()
            with self._lock:
                self.store[bstack11l111_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫ࿪")] = [bstack111l1l111l_opy_.bstack111l11l11l_opy_()]
                if bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬ࿫"), None):
                    self.store[bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡸ࠭࿬")].append(bstack111l1l111l_opy_.bstack111l11l11l_opy_())
                else:
                    self.store[bstack11l111_opy_ (u"ࠪ࡫ࡱࡵࡢࡢ࡮ࡢ࡬ࡴࡵ࡫ࡴࠩ࿭")].append(bstack111l1l111l_opy_.bstack111l11l11l_opy_())
            if bstack111l1l1111_opy_:
                self._1111lll11l_opy_[bstack111l1l1111_opy_ + bstack11l111_opy_ (u"ࠫ࠲࠭࿮") + attrs.get(bstack11l111_opy_ (u"ࠬࡺࡹࡱࡧࠪ࿯"), bstack11l111_opy_ (u"࠭ࠧ࿰")).lower()] = { bstack11l111_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ࿱"): bstack111l1l111l_opy_ }
            bstack11l11l1l_opy_.bstack111ll11lll_opy_(bstack11l111_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ࿲"), bstack111l1l111l_opy_)
        else:
            bstack111l1lllll_opy_ = {
                bstack11l111_opy_ (u"ࠩ࡬ࡨࠬ࿳"): uuid4().__str__(),
                bstack11l111_opy_ (u"ࠪࡸࡪࡾࡴࠨ࿴"): bstack11l111_opy_ (u"ࠫࢀࢃࠠࡼࡿࠪ࿵").format(attrs.get(bstack11l111_opy_ (u"ࠬࡱࡷ࡯ࡣࡰࡩࠬ࿶")), attrs.get(bstack11l111_opy_ (u"࠭ࡡࡳࡩࡶࠫ࿷"), bstack11l111_opy_ (u"ࠧࠨ࿸"))) if attrs.get(bstack11l111_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭࿹"), []) else attrs.get(bstack11l111_opy_ (u"ࠩ࡮ࡻࡳࡧ࡭ࡦࠩ࿺")),
                bstack11l111_opy_ (u"ࠪࡷࡹ࡫ࡰࡠࡣࡵ࡫ࡺࡳࡥ࡯ࡶࠪ࿻"): attrs.get(bstack11l111_opy_ (u"ࠫࡦࡸࡧࡴࠩ࿼"), []),
                bstack11l111_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ࿽"): bstack1l11ll11l_opy_(),
                bstack11l111_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭࿾"): bstack11l111_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨ࿿"),
                bstack11l111_opy_ (u"ࠨࡦࡨࡷࡨࡸࡩࡱࡶ࡬ࡳࡳ࠭က"): attrs.get(bstack11l111_opy_ (u"ࠩࡧࡳࡨ࠭ခ"), bstack11l111_opy_ (u"ࠪࠫဂ"))
            }
            if attrs.get(bstack11l111_opy_ (u"ࠫࡱ࡯ࡢ࡯ࡣࡰࡩࠬဃ"), bstack11l111_opy_ (u"ࠬ࠭င")) != bstack11l111_opy_ (u"࠭ࠧစ"):
                bstack111l1lllll_opy_[bstack11l111_opy_ (u"ࠧ࡬ࡧࡼࡻࡴࡸࡤࠨဆ")] = attrs.get(bstack11l111_opy_ (u"ࠨ࡮࡬ࡦࡳࡧ࡭ࡦࠩဇ"))
            if not self.bstack111l1111ll_opy_:
                self._1111lll11l_opy_[self._1111ll111l_opy_()][bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬဈ")].add_step(bstack111l1lllll_opy_)
                threading.current_thread().current_step_uuid = bstack111l1lllll_opy_[bstack11l111_opy_ (u"ࠪ࡭ࡩ࠭ဉ")]
            self.bstack111l1111ll_opy_.append(bstack111l1lllll_opy_)
    @error_handler(class_method=True)
    def end_keyword(self, name, attrs):
        messages = self.messages.bstack111l1l1l1l_opy_()
        self._111l11l1ll_opy_(messages)
        current_test_id = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢ࡭ࡩ࠭ည"), None)
        bstack111l1l1111_opy_ = current_test_id if current_test_id else bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡳࡶ࡫ࡷࡩࡤ࡯ࡤࠨဋ"), None)
        bstack1111ll1l1l_opy_ = bstack1111llllll_opy_.get(attrs.get(bstack11l111_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭ဌ")), bstack11l111_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨဍ"))
        bstack111l1111l1_opy_ = attrs.get(bstack11l111_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩဎ"))
        if bstack1111ll1l1l_opy_ != bstack11l111_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪဏ") and not attrs.get(bstack11l111_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫတ")) and self._111l11ll11_opy_:
            bstack111l1111l1_opy_ = self._111l11ll11_opy_
        bstack111ll11l11_opy_ = Result(result=bstack1111ll1l1l_opy_, exception=bstack111l1111l1_opy_, bstack111l1ll111_opy_=[bstack111l1111l1_opy_])
        if attrs.get(bstack11l111_opy_ (u"ࠫࡹࡿࡰࡦࠩထ"), bstack11l111_opy_ (u"ࠬ࠭ဒ")).lower() in [bstack11l111_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬဓ"), bstack11l111_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࠩန")]:
            bstack111l1l1111_opy_ = current_test_id if current_test_id else bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡶࡹ࡮ࡺࡥࡠ࡫ࡧࠫပ"), None)
            if bstack111l1l1111_opy_:
                bstack111ll111l1_opy_ = bstack111l1l1111_opy_ + bstack11l111_opy_ (u"ࠤ࠰ࠦဖ") + attrs.get(bstack11l111_opy_ (u"ࠪࡸࡾࡶࡥࠨဗ"), bstack11l111_opy_ (u"ࠫࠬဘ")).lower()
                self._1111lll11l_opy_[bstack111ll111l1_opy_][bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨမ")].stop(time=bstack1l11ll11l_opy_(), duration=int(attrs.get(bstack11l111_opy_ (u"࠭ࡥ࡭ࡣࡳࡷࡪࡪࡴࡪ࡯ࡨࠫယ"), bstack11l111_opy_ (u"ࠧ࠱ࠩရ"))), result=bstack111ll11l11_opy_)
                bstack11l11l1l_opy_.bstack111ll11lll_opy_(bstack11l111_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡈ࡬ࡲ࡮ࡹࡨࡦࡦࠪလ"), self._1111lll11l_opy_[bstack111ll111l1_opy_][bstack11l111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬဝ")])
        else:
            bstack111l1l1111_opy_ = current_test_id if current_test_id else bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡ࡬ࡨࠬသ"), None)
            if bstack111l1l1111_opy_ and len(self.bstack111l1111ll_opy_) == 1:
                current_step_uuid = bstack1l11lll1l1_opy_(threading.current_thread(), bstack11l111_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡹࡴࡦࡲࡢࡹࡺ࡯ࡤࠨဟ"), None)
                self._1111lll11l_opy_[bstack111l1l1111_opy_][bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨဠ")].bstack111ll11ll1_opy_(current_step_uuid, duration=int(attrs.get(bstack11l111_opy_ (u"࠭ࡥ࡭ࡣࡳࡷࡪࡪࡴࡪ࡯ࡨࠫအ"), bstack11l111_opy_ (u"ࠧ࠱ࠩဢ"))), result=bstack111ll11l11_opy_)
            else:
                self.bstack1111l1lll1_opy_(attrs)
            self.bstack111l1111ll_opy_.pop()
    def log_message(self, message):
        try:
            if message.get(bstack11l111_opy_ (u"ࠨࡪࡷࡱࡱ࠭ဣ"), bstack11l111_opy_ (u"ࠩࡱࡳࠬဤ")) == bstack11l111_opy_ (u"ࠪࡽࡪࡹࠧဥ"):
                return
            self.messages.push(message)
            logs = []
            if bstack1l11lllll1_opy_.bstack111lll1111_opy_():
                logs.append({
                    bstack11l111_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧဦ"): bstack1l11ll11l_opy_(),
                    bstack11l111_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ဧ"): message.get(bstack11l111_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧဨ")),
                    bstack11l111_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ဩ"): message.get(bstack11l111_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧဪ")),
                    **bstack1l11lllll1_opy_.bstack111lll1111_opy_()
                })
                if len(logs) > 0:
                    bstack11l11l1l_opy_.bstack1l111lll1_opy_(logs)
        except Exception as err:
            pass
    def close(self):
        bstack11l11l1l_opy_.bstack1111lll1ll_opy_()
    def bstack1111l1lll1_opy_(self, bstack1111lll1l1_opy_):
        if not bstack1l11lllll1_opy_.bstack111lll1111_opy_():
            return
        kwname = bstack11l111_opy_ (u"ࠩࡾࢁࠥࢁࡽࠨါ").format(bstack1111lll1l1_opy_.get(bstack11l111_opy_ (u"ࠪ࡯ࡼࡴࡡ࡮ࡧࠪာ")), bstack1111lll1l1_opy_.get(bstack11l111_opy_ (u"ࠫࡦࡸࡧࡴࠩိ"), bstack11l111_opy_ (u"ࠬ࠭ီ"))) if bstack1111lll1l1_opy_.get(bstack11l111_opy_ (u"࠭ࡡࡳࡩࡶࠫု"), []) else bstack1111lll1l1_opy_.get(bstack11l111_opy_ (u"ࠧ࡬ࡹࡱࡥࡲ࡫ࠧူ"))
        error_message = bstack11l111_opy_ (u"ࠣ࡭ࡺࡲࡦࡳࡥ࠻ࠢ࡟ࠦࢀ࠶ࡽ࡝ࠤࠣࢀࠥࡹࡴࡢࡶࡸࡷ࠿ࠦ࡜ࠣࡽ࠴ࢁࡡࠨࠠࡽࠢࡨࡼࡨ࡫ࡰࡵ࡫ࡲࡲ࠿ࠦ࡜ࠣࡽ࠵ࢁࡡࠨࠢေ").format(kwname, bstack1111lll1l1_opy_.get(bstack11l111_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩဲ")), str(bstack1111lll1l1_opy_.get(bstack11l111_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫဳ"))))
        bstack1111ll1l11_opy_ = bstack11l111_opy_ (u"ࠦࡰࡽ࡮ࡢ࡯ࡨ࠾ࠥࡢࠢࡼ࠲ࢀࡠࠧࠦࡼࠡࡵࡷࡥࡹࡻࡳ࠻ࠢ࡟ࠦࢀ࠷ࡽ࡝ࠤࠥဴ").format(kwname, bstack1111lll1l1_opy_.get(bstack11l111_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬဵ")))
        bstack1111l1llll_opy_ = error_message if bstack1111lll1l1_opy_.get(bstack11l111_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧံ")) else bstack1111ll1l11_opy_
        bstack111l111lll_opy_ = {
            bstack11l111_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲ့ࠪ"): self.bstack111l1111ll_opy_[-1].get(bstack11l111_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬး"), bstack1l11ll11l_opy_()),
            bstack11l111_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧ္ࠪ"): bstack1111l1llll_opy_,
            bstack11l111_opy_ (u"ࠪࡰࡪࡼࡥ࡭်ࠩ"): bstack11l111_opy_ (u"ࠫࡊࡘࡒࡐࡔࠪျ") if bstack1111lll1l1_opy_.get(bstack11l111_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬြ")) == bstack11l111_opy_ (u"࠭ࡆࡂࡋࡏࠫွ") else bstack11l111_opy_ (u"ࠧࡊࡐࡉࡓࠬှ"),
            **bstack1l11lllll1_opy_.bstack111lll1111_opy_()
        }
        bstack11l11l1l_opy_.bstack1l111lll1_opy_([bstack111l111lll_opy_])
    def _1111ll111l_opy_(self):
        for bstack111l1l11l1_opy_ in reversed(self._1111lll11l_opy_):
            bstack111l1l1l11_opy_ = bstack111l1l11l1_opy_
            data = self._1111lll11l_opy_[bstack111l1l11l1_opy_][bstack11l111_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫဿ")]
            if isinstance(data, bstack111l1ll1l1_opy_):
                if not bstack11l111_opy_ (u"ࠩࡈࡅࡈࡎࠧ၀") in data.bstack1111l1l1ll_opy_():
                    return bstack111l1l1l11_opy_
            else:
                return bstack111l1l1l11_opy_
    def _111l11l1ll_opy_(self, messages):
        try:
            bstack1111lllll1_opy_ = BuiltIn().get_variable_value(bstack11l111_opy_ (u"ࠥࠨࢀࡒࡏࡈࠢࡏࡉ࡛ࡋࡌࡾࠤ၁")) in (bstack1111l1ll11_opy_.DEBUG, bstack1111l1ll11_opy_.TRACE)
            for message, bstack111l11llll_opy_ in zip_longest(messages, messages[1:]):
                name = message.get(bstack11l111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ၂"))
                level = message.get(bstack11l111_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫ၃"))
                if level == bstack1111l1ll11_opy_.FAIL:
                    self._111l11ll11_opy_ = name or self._111l11ll11_opy_
                    self._1111l1ll1l_opy_ = bstack111l11llll_opy_.get(bstack11l111_opy_ (u"ࠨ࡭ࡦࡵࡶࡥ࡬࡫ࠢ၄")) if bstack1111lllll1_opy_ and bstack111l11llll_opy_ else self._1111l1ll1l_opy_
        except:
            pass
    @classmethod
    def bstack111ll11lll_opy_(self, event: str, bstack1111ll11ll_opy_: bstack1111l1l11l_opy_, bstack111l111l1l_opy_=False):
        if event == bstack11l111_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ၅"):
            bstack1111ll11ll_opy_.set(hooks=self.store[bstack11l111_opy_ (u"ࠨࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࠬ၆")])
        if event == bstack11l111_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖ࡯࡮ࡶࡰࡦࡦࠪ၇"):
            event = bstack11l111_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ၈")
        if bstack111l111l1l_opy_:
            bstack111l111ll1_opy_ = {
                bstack11l111_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ၉"): event,
                bstack1111ll11ll_opy_.bstack111l11111l_opy_(): bstack1111ll11ll_opy_.bstack111l1l1ll1_opy_(event)
            }
            with self._lock:
                self.bstack111l1l11ll_opy_.append(bstack111l111ll1_opy_)
        else:
            bstack11l11l1l_opy_.bstack111ll11lll_opy_(event, bstack1111ll11ll_opy_)
class bstack111l1l1lll_opy_:
    def __init__(self):
        self._111l111111_opy_ = []
    def bstack1111ll1ll1_opy_(self):
        self._111l111111_opy_.append([])
    def bstack111l1l1l1l_opy_(self):
        return self._111l111111_opy_.pop() if self._111l111111_opy_ else list()
    def push(self, message):
        self._111l111111_opy_[-1].append(message) if self._111l111111_opy_ else self._111l111111_opy_.append([message])
class bstack1111l1ll11_opy_:
    FAIL = bstack11l111_opy_ (u"ࠬࡌࡁࡊࡎࠪ၊")
    ERROR = bstack11l111_opy_ (u"࠭ࡅࡓࡔࡒࡖࠬ။")
    WARNING = bstack11l111_opy_ (u"ࠧࡘࡃࡕࡒࠬ၌")
    bstack1111l1l1l1_opy_ = bstack11l111_opy_ (u"ࠨࡋࡑࡊࡔ࠭၍")
    DEBUG = bstack11l111_opy_ (u"ࠩࡇࡉࡇ࡛ࡇࠨ၎")
    TRACE = bstack11l111_opy_ (u"ࠪࡘࡗࡇࡃࡆࠩ၏")
    bstack1111ll11l1_opy_ = [FAIL, ERROR]
def bstack111l111l11_opy_(bstack1111ll1111_opy_):
    if not bstack1111ll1111_opy_:
        return None
    if bstack1111ll1111_opy_.get(bstack11l111_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧၐ"), None):
        return getattr(bstack1111ll1111_opy_[bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨၑ")], bstack11l111_opy_ (u"࠭ࡵࡶ࡫ࡧࠫၒ"), None)
    return bstack1111ll1111_opy_.get(bstack11l111_opy_ (u"ࠧࡶࡷ࡬ࡨࠬၓ"), None)
def bstack111l11l1l1_opy_(hook_type, current_test_uuid):
    if hook_type.lower() not in [bstack11l111_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧၔ"), bstack11l111_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࠫၕ")]:
        return
    if hook_type.lower() == bstack11l111_opy_ (u"ࠪࡷࡪࡺࡵࡱࠩၖ"):
        if current_test_uuid is None:
            return bstack11l111_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡆࡒࡌࠨၗ")
        else:
            return bstack11l111_opy_ (u"ࠬࡈࡅࡇࡑࡕࡉࡤࡋࡁࡄࡊࠪၘ")
    elif hook_type.lower() == bstack11l111_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࠨၙ"):
        if current_test_uuid is None:
            return bstack11l111_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡁࡍࡎࠪၚ")
        else:
            return bstack11l111_opy_ (u"ࠨࡃࡉࡘࡊࡘ࡟ࡆࡃࡆࡌࠬၛ")