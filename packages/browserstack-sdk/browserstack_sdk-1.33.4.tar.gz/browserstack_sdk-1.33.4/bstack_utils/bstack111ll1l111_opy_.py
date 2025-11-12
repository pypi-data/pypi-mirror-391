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
from uuid import uuid4
from bstack_utils.helper import bstack1l11ll11l_opy_, bstack111l1ll1lll_opy_
from bstack_utils.bstack1ll1l1ll1_opy_ import bstack1lllll1l1lll_opy_
class bstack1111l1l11l_opy_:
    def __init__(self, name=None, code=None, uuid=None, file_path=None, started_at=None, framework=None, tags=[], scope=[], bstack1llll1ll11l1_opy_=None, bstack1llll1l1llll_opy_=True, bstack11llll1l111_opy_=None, bstack1l111llll_opy_=None, result=None, duration=None, bstack111l1l11l1_opy_=None, meta={}):
        self.bstack111l1l11l1_opy_ = bstack111l1l11l1_opy_
        self.name = name
        self.code = code
        self.file_path = file_path
        self.uuid = uuid
        if not self.uuid and bstack1llll1l1llll_opy_:
            self.uuid = uuid4().__str__()
        self.started_at = started_at
        self.framework = framework
        self.tags = tags
        self.scope = scope
        self.bstack1llll1ll11l1_opy_ = bstack1llll1ll11l1_opy_
        self.bstack11llll1l111_opy_ = bstack11llll1l111_opy_
        self.bstack1l111llll_opy_ = bstack1l111llll_opy_
        self.result = result
        self.duration = duration
        self.meta = meta
        self.hooks = []
    def bstack111l11l11l_opy_(self):
        if self.uuid:
            return self.uuid
        self.uuid = uuid4().__str__()
        return self.uuid
    def bstack111l1lll11_opy_(self, meta):
        self.meta = meta
    def bstack111l1ll1ll_opy_(self, hooks):
        self.hooks = hooks
    def bstack1llll1l11lll_opy_(self):
        bstack1llll1l1l111_opy_ = os.path.relpath(self.file_path, start=os.getcwd())
        return {
            bstack11l111_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ₺"): bstack1llll1l1l111_opy_,
            bstack11l111_opy_ (u"ࠧ࡭ࡱࡦࡥࡹ࡯࡯࡯ࠩ₻"): bstack1llll1l1l111_opy_,
            bstack11l111_opy_ (u"ࠨࡸࡦࡣ࡫࡯࡬ࡦࡲࡤࡸ࡭࠭₼"): bstack1llll1l1l111_opy_
        }
    def set(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(bstack11l111_opy_ (u"ࠤࡘࡲࡪࡾࡰࡦࡥࡷࡩࡩࠦࡡࡳࡩࡸࡱࡪࡴࡴ࠻ࠢࠥ₽") + key)
            setattr(self, key, val)
    def bstack1llll1l11ll1_opy_(self):
        return {
            bstack11l111_opy_ (u"ࠪࡲࡦࡳࡥࠨ₾"): self.name,
            bstack11l111_opy_ (u"ࠫࡧࡵࡤࡺࠩ₿"): {
                bstack11l111_opy_ (u"ࠬࡲࡡ࡯ࡩࠪ⃀"): bstack11l111_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭⃁"),
                bstack11l111_opy_ (u"ࠧࡤࡱࡧࡩࠬ⃂"): self.code
            },
            bstack11l111_opy_ (u"ࠨࡵࡦࡳࡵ࡫ࡳࠨ⃃"): self.scope,
            bstack11l111_opy_ (u"ࠩࡷࡥ࡬ࡹࠧ⃄"): self.tags,
            bstack11l111_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭⃅"): self.framework,
            bstack11l111_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ⃆"): self.started_at
        }
    def bstack1llll1ll11ll_opy_(self):
        return {
         bstack11l111_opy_ (u"ࠬࡳࡥࡵࡣࠪ⃇"): self.meta
        }
    def bstack1llll1l11l1l_opy_(self):
        return {
            bstack11l111_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡘࡥࡳࡷࡱࡔࡦࡸࡡ࡮ࠩ⃈"): {
                bstack11l111_opy_ (u"ࠧࡳࡧࡵࡹࡳࡥ࡮ࡢ࡯ࡨࠫ⃉"): self.bstack1llll1ll11l1_opy_
            }
        }
    def bstack1llll1l1l11l_opy_(self, bstack1llll1ll1111_opy_, details):
        step = next(filter(lambda st: st[bstack11l111_opy_ (u"ࠨ࡫ࡧࠫ⃊")] == bstack1llll1ll1111_opy_, self.meta[bstack11l111_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨ⃋")]), None)
        step.update(details)
    def bstack1lll1111l1_opy_(self, bstack1llll1ll1111_opy_):
        step = next(filter(lambda st: st[bstack11l111_opy_ (u"ࠪ࡭ࡩ࠭⃌")] == bstack1llll1ll1111_opy_, self.meta[bstack11l111_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪ⃍")]), None)
        step.update({
            bstack11l111_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⃎"): bstack1l11ll11l_opy_()
        })
    def bstack111ll11ll1_opy_(self, bstack1llll1ll1111_opy_, result, duration=None):
        bstack11llll1l111_opy_ = bstack1l11ll11l_opy_()
        if bstack1llll1ll1111_opy_ is not None and self.meta.get(bstack11l111_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬ⃏")):
            step = next(filter(lambda st: st[bstack11l111_opy_ (u"ࠧࡪࡦࠪ⃐")] == bstack1llll1ll1111_opy_, self.meta[bstack11l111_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧ⃑")]), None)
            step.update({
                bstack11l111_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺ⃒ࠧ"): bstack11llll1l111_opy_,
                bstack11l111_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲ⃓ࠬ"): duration if duration else bstack111l1ll1lll_opy_(step[bstack11l111_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ⃔")], bstack11llll1l111_opy_),
                bstack11l111_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ⃕"): result.result,
                bstack11l111_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫ࠧ⃖"): str(result.exception) if result.exception else None
            })
    def add_step(self, bstack1llll1l1ll11_opy_):
        if self.meta.get(bstack11l111_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭⃗")):
            self.meta[bstack11l111_opy_ (u"ࠨࡵࡷࡩࡵࡹ⃘ࠧ")].append(bstack1llll1l1ll11_opy_)
        else:
            self.meta[bstack11l111_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨ⃙")] = [ bstack1llll1l1ll11_opy_ ]
    def bstack1llll1l1lll1_opy_(self):
        return {
            bstack11l111_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ⃚"): self.bstack111l11l11l_opy_(),
            **self.bstack1llll1l11ll1_opy_(),
            **self.bstack1llll1l11lll_opy_(),
            **self.bstack1llll1ll11ll_opy_()
        }
    def bstack1llll1l1l1ll_opy_(self):
        if not self.result:
            return {}
        data = {
            bstack11l111_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⃛"): self.bstack11llll1l111_opy_,
            bstack11l111_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴ࡟ࡪࡰࡢࡱࡸ࠭⃜"): self.duration,
            bstack11l111_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭⃝"): self.result.result
        }
        if data[bstack11l111_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ⃞")] == bstack11l111_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ⃟"):
            data[bstack11l111_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࡢࡸࡾࡶࡥࠨ⃠")] = self.result.bstack1llllll1lll_opy_()
            data[bstack11l111_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࠫ⃡")] = [{bstack11l111_opy_ (u"ࠫࡧࡧࡣ࡬ࡶࡵࡥࡨ࡫ࠧ⃢"): self.result.bstack111ll1l11l1_opy_()}]
        return data
    def bstack1llll1l11l11_opy_(self):
        return {
            bstack11l111_opy_ (u"ࠬࡻࡵࡪࡦࠪ⃣"): self.bstack111l11l11l_opy_(),
            **self.bstack1llll1l11ll1_opy_(),
            **self.bstack1llll1l11lll_opy_(),
            **self.bstack1llll1l1l1ll_opy_(),
            **self.bstack1llll1ll11ll_opy_()
        }
    def bstack111l1l1ll1_opy_(self, event, result=None):
        if result:
            self.result = result
        if bstack11l111_opy_ (u"࠭ࡓࡵࡣࡵࡸࡪࡪࠧ⃤") in event:
            return self.bstack1llll1l1lll1_opy_()
        elif bstack11l111_opy_ (u"ࠧࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥ⃥ࠩ") in event:
            return self.bstack1llll1l11l11_opy_()
    def bstack111l11111l_opy_(self):
        pass
    def stop(self, time=None, duration=None, result=None):
        self.bstack11llll1l111_opy_ = time if time else bstack1l11ll11l_opy_()
        self.duration = duration if duration else bstack111l1ll1lll_opy_(self.started_at, self.bstack11llll1l111_opy_)
        if result:
            self.result = result
class bstack111ll1l11l_opy_(bstack1111l1l11l_opy_):
    def __init__(self, hooks=[], bstack111ll1lll1_opy_={}, *args, **kwargs):
        self.hooks = hooks
        self.bstack111ll1lll1_opy_ = bstack111ll1lll1_opy_
        super().__init__(*args, **kwargs, bstack1l111llll_opy_=bstack11l111_opy_ (u"ࠨࡶࡨࡷࡹ⃦࠭"))
    @classmethod
    def bstack1llll1l1ll1l_opy_(cls, scenario, feature, test, **kwargs):
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack11l111_opy_ (u"ࠩ࡬ࡨࠬ⃧"): id(step),
                bstack11l111_opy_ (u"ࠪࡸࡪࡾࡴࠨ⃨"): step.name,
                bstack11l111_opy_ (u"ࠫࡰ࡫ࡹࡸࡱࡵࡨࠬ⃩"): step.keyword,
            })
        return bstack111ll1l11l_opy_(
            **kwargs,
            meta={
                bstack11l111_opy_ (u"ࠬ࡬ࡥࡢࡶࡸࡶࡪ⃪࠭"): {
                    bstack11l111_opy_ (u"࠭࡮ࡢ࡯ࡨ⃫ࠫ"): feature.name,
                    bstack11l111_opy_ (u"ࠧࡱࡣࡷ࡬⃬ࠬ"): feature.filename,
                    bstack11l111_opy_ (u"ࠨࡦࡨࡷࡨࡸࡩࡱࡶ࡬ࡳࡳ⃭࠭"): feature.description
                },
                bstack11l111_opy_ (u"ࠩࡶࡧࡪࡴࡡࡳ࡫ࡲ⃮ࠫ"): {
                    bstack11l111_opy_ (u"ࠪࡲࡦࡳࡥࠨ⃯"): scenario.name
                },
                bstack11l111_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪ⃰"): steps,
                bstack11l111_opy_ (u"ࠬ࡫ࡸࡢ࡯ࡳࡰࡪࡹࠧ⃱"): bstack1lllll1l1lll_opy_(test)
            }
        )
    def bstack1llll1ll1l11_opy_(self):
        return {
            bstack11l111_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⃲"): self.hooks
        }
    def bstack1llll1ll111l_opy_(self):
        if self.bstack111ll1lll1_opy_:
            return {
                bstack11l111_opy_ (u"ࠧࡪࡰࡷࡩ࡬ࡸࡡࡵ࡫ࡲࡲࡸ࠭⃳"): self.bstack111ll1lll1_opy_
            }
        return {}
    def bstack1llll1l11l11_opy_(self):
        return {
            **super().bstack1llll1l11l11_opy_(),
            **self.bstack1llll1ll1l11_opy_()
        }
    def bstack1llll1l1lll1_opy_(self):
        return {
            **super().bstack1llll1l1lll1_opy_(),
            **self.bstack1llll1ll111l_opy_()
        }
    def bstack111l11111l_opy_(self):
        return bstack11l111_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࠪ⃴")
class bstack111l1ll1l1_opy_(bstack1111l1l11l_opy_):
    def __init__(self, hook_type, *args,bstack111ll1lll1_opy_={}, **kwargs):
        self.hook_type = hook_type
        self.bstack1ll11l1llll_opy_ = None
        self.bstack111ll1lll1_opy_ = bstack111ll1lll1_opy_
        super().__init__(*args, **kwargs, bstack1l111llll_opy_=bstack11l111_opy_ (u"ࠩ࡫ࡳࡴࡱࠧ⃵"))
    def bstack1111l1l1ll_opy_(self):
        return self.hook_type
    def bstack1llll1l1l1l1_opy_(self):
        return {
            bstack11l111_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡶࡼࡴࡪ࠭⃶"): self.hook_type
        }
    def bstack1llll1l11l11_opy_(self):
        return {
            **super().bstack1llll1l11l11_opy_(),
            **self.bstack1llll1l1l1l1_opy_()
        }
    def bstack1llll1l1lll1_opy_(self):
        return {
            **super().bstack1llll1l1lll1_opy_(),
            bstack11l111_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡩࡥࠩ⃷"): self.bstack1ll11l1llll_opy_,
            **self.bstack1llll1l1l1l1_opy_()
        }
    def bstack111l11111l_opy_(self):
        return bstack11l111_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴࠧ⃸")
    def bstack111ll1ll1l_opy_(self, bstack1ll11l1llll_opy_):
        self.bstack1ll11l1llll_opy_ = bstack1ll11l1llll_opy_