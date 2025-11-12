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
from _pytest import fixtures
from _pytest.python import _call_with_optional_argument
from pytest import Module, Class
from bstack_utils.helper import Result, bstack11l111l11ll_opy_
from browserstack_sdk.bstack11l11llll1_opy_ import bstack1l1ll11111_opy_
def _111l1l11lll_opy_(method, this, arg):
    arg_count = method.__code__.co_argcount
    if arg_count > 1:
        method(this, arg)
    else:
        method(this)
class bstack111l1l1ll1l_opy_:
    def __init__(self, handler):
        self._111l1ll11l1_opy_ = {}
        self._111l1l1llll_opy_ = {}
        self.handler = handler
        self.patch()
        pass
    def patch(self):
        pytest_version = bstack1l1ll11111_opy_.version()
        if bstack11l111l11ll_opy_(pytest_version, bstack11l111_opy_ (u"ࠨ࠸࠯࠳࠱࠵ࠧᷩ")) >= 0:
            self._111l1ll11l1_opy_[bstack11l111_opy_ (u"ࠧࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᷪ")] = Module._register_setup_function_fixture
            self._111l1ll11l1_opy_[bstack11l111_opy_ (u"ࠨ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᷫ")] = Module._register_setup_module_fixture
            self._111l1ll11l1_opy_[bstack11l111_opy_ (u"ࠩࡦࡰࡦࡹࡳࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᷬ")] = Class._register_setup_class_fixture
            self._111l1ll11l1_opy_[bstack11l111_opy_ (u"ࠪࡱࡪࡺࡨࡰࡦࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᷭ")] = Class._register_setup_method_fixture
            Module._register_setup_function_fixture = self.bstack111l1l1l11l_opy_(bstack11l111_opy_ (u"ࠫ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᷮ"))
            Module._register_setup_module_fixture = self.bstack111l1l1l11l_opy_(bstack11l111_opy_ (u"ࠬࡳ࡯ࡥࡷ࡯ࡩࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᷯ"))
            Class._register_setup_class_fixture = self.bstack111l1l1l11l_opy_(bstack11l111_opy_ (u"࠭ࡣ࡭ࡣࡶࡷࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᷰ"))
            Class._register_setup_method_fixture = self.bstack111l1l1l11l_opy_(bstack11l111_opy_ (u"ࠧ࡮ࡧࡷ࡬ࡴࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᷱ"))
        else:
            self._111l1ll11l1_opy_[bstack11l111_opy_ (u"ࠨࡨࡸࡲࡨࡺࡩࡰࡰࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᷲ")] = Module._inject_setup_function_fixture
            self._111l1ll11l1_opy_[bstack11l111_opy_ (u"ࠩࡰࡳࡩࡻ࡬ࡦࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᷳ")] = Module._inject_setup_module_fixture
            self._111l1ll11l1_opy_[bstack11l111_opy_ (u"ࠪࡧࡱࡧࡳࡴࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᷴ")] = Class._inject_setup_class_fixture
            self._111l1ll11l1_opy_[bstack11l111_opy_ (u"ࠫࡲ࡫ࡴࡩࡱࡧࡣ࡫࡯ࡸࡵࡷࡵࡩࠬ᷵")] = Class._inject_setup_method_fixture
            Module._inject_setup_function_fixture = self.bstack111l1l1l11l_opy_(bstack11l111_opy_ (u"ࠬ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨ᷶"))
            Module._inject_setup_module_fixture = self.bstack111l1l1l11l_opy_(bstack11l111_opy_ (u"࠭࡭ࡰࡦࡸࡰࡪࡥࡦࡪࡺࡷࡹࡷ࡫᷷ࠧ"))
            Class._inject_setup_class_fixture = self.bstack111l1l1l11l_opy_(bstack11l111_opy_ (u"ࠧࡤ࡮ࡤࡷࡸࡥࡦࡪࡺࡷࡹࡷ࡫᷸ࠧ"))
            Class._inject_setup_method_fixture = self.bstack111l1l1l11l_opy_(bstack11l111_opy_ (u"ࠨ࡯ࡨࡸ࡭ࡵࡤࡠࡨ࡬ࡼࡹࡻࡲࡦ᷹ࠩ"))
    def bstack111l1l1l1ll_opy_(self, bstack111l1ll1ll1_opy_, hook_type):
        bstack111l1ll1l11_opy_ = id(bstack111l1ll1ll1_opy_.__class__)
        if (bstack111l1ll1l11_opy_, hook_type) in self._111l1l1llll_opy_:
            return
        meth = getattr(bstack111l1ll1ll1_opy_, hook_type, None)
        if meth is not None and fixtures.getfixturemarker(meth) is None:
            self._111l1l1llll_opy_[(bstack111l1ll1l11_opy_, hook_type)] = meth
            setattr(bstack111l1ll1ll1_opy_, hook_type, self.bstack111l1l1l111_opy_(hook_type, bstack111l1ll1l11_opy_))
    def bstack111l1l1l1l1_opy_(self, instance, bstack111l1ll1l1l_opy_):
        if bstack111l1ll1l1l_opy_ == bstack11l111_opy_ (u"ࠤࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩ᷺ࠧ"):
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack11l111_opy_ (u"ࠥࡷࡪࡺࡵࡱࡡࡩࡹࡳࡩࡴࡪࡱࡱࠦ᷻"))
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack11l111_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࡥࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠣ᷼"))
        if bstack111l1ll1l1l_opy_ == bstack11l111_opy_ (u"ࠧࡳ࡯ࡥࡷ࡯ࡩࡤ࡬ࡩࡹࡶࡸࡶࡪࠨ᷽"):
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack11l111_opy_ (u"ࠨࡳࡦࡶࡸࡴࡤࡳ࡯ࡥࡷ࡯ࡩࠧ᷾"))
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack11l111_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡳࡩࡻ࡬ࡦࠤ᷿"))
        if bstack111l1ll1l1l_opy_ == bstack11l111_opy_ (u"ࠣࡥ࡯ࡥࡸࡹ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠣḀ"):
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack11l111_opy_ (u"ࠤࡶࡩࡹࡻࡰࡠࡥ࡯ࡥࡸࡹࠢḁ"))
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack11l111_opy_ (u"ࠥࡸࡪࡧࡲࡥࡱࡺࡲࡤࡩ࡬ࡢࡵࡶࠦḂ"))
        if bstack111l1ll1l1l_opy_ == bstack11l111_opy_ (u"ࠦࡲ࡫ࡴࡩࡱࡧࡣ࡫࡯ࡸࡵࡷࡵࡩࠧḃ"):
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack11l111_opy_ (u"ࠧࡹࡥࡵࡷࡳࡣࡲ࡫ࡴࡩࡱࡧࠦḄ"))
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack11l111_opy_ (u"ࠨࡴࡦࡣࡵࡨࡴࡽ࡮ࡠ࡯ࡨࡸ࡭ࡵࡤࠣḅ"))
    @staticmethod
    def bstack111l1ll111l_opy_(hook_type, func, args):
        if hook_type in [bstack11l111_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩ࠭Ḇ"), bstack11l111_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠪḇ")]:
            _111l1l11lll_opy_(func, args[0], args[1])
            return
        _call_with_optional_argument(func, args[0])
    def bstack111l1l1l111_opy_(self, hook_type, bstack111l1ll1l11_opy_):
        def bstack111l1l1ll11_opy_(arg=None):
            self.handler(hook_type, bstack11l111_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࠩḈ"))
            result = None
            try:
                bstack1llll1l1l11_opy_ = self._111l1l1llll_opy_[(bstack111l1ll1l11_opy_, hook_type)]
                self.bstack111l1ll111l_opy_(hook_type, bstack1llll1l1l11_opy_, (arg,))
                result = Result(result=bstack11l111_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪḉ"))
            except Exception as e:
                result = Result(result=bstack11l111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫḊ"), exception=e)
                self.handler(hook_type, bstack11l111_opy_ (u"ࠬࡧࡦࡵࡧࡵࠫḋ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack11l111_opy_ (u"࠭ࡡࡧࡶࡨࡶࠬḌ"), result)
        def bstack111l1ll1111_opy_(this, arg=None):
            self.handler(hook_type, bstack11l111_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫ࠧḍ"))
            result = None
            exception = None
            try:
                self.bstack111l1ll111l_opy_(hook_type, self._111l1l1llll_opy_[hook_type], (this, arg))
                result = Result(result=bstack11l111_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨḎ"))
            except Exception as e:
                result = Result(result=bstack11l111_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩḏ"), exception=e)
                self.handler(hook_type, bstack11l111_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࠩḐ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack11l111_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࠪḑ"), result)
        if hook_type in [bstack11l111_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡲ࡫ࡴࡩࡱࡧࠫḒ"), bstack11l111_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠ࡯ࡨࡸ࡭ࡵࡤࠨḓ")]:
            return bstack111l1ll1111_opy_
        return bstack111l1l1ll11_opy_
    def bstack111l1l1l11l_opy_(self, bstack111l1ll1l1l_opy_):
        def bstack111l1l1lll1_opy_(this, *args, **kwargs):
            self.bstack111l1l1l1l1_opy_(this, bstack111l1ll1l1l_opy_)
            self._111l1ll11l1_opy_[bstack111l1ll1l1l_opy_](this, *args, **kwargs)
        return bstack111l1l1lll1_opy_