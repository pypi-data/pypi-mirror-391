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
from filelock import FileLock
import json
import os
import time
import uuid
import logging
from typing import Dict, List, Optional
from bstack_utils.bstack11l111111l_opy_ import get_logger
logger = get_logger(__name__)
bstack1llllll1l11l_opy_: Dict[str, float] = {}
bstack1llllll1ll1l_opy_: List = []
bstack1llllll1l111_opy_ = 5
bstack11l1l1ll1l_opy_ = os.path.join(os.getcwd(), bstack11l111_opy_ (u"ࠪࡰࡴ࡭ࠧῂ"), bstack11l111_opy_ (u"ࠫࡰ࡫ࡹ࠮࡯ࡨࡸࡷ࡯ࡣࡴ࠰࡭ࡷࡴࡴࠧῃ"))
logging.getLogger(bstack11l111_opy_ (u"ࠬ࡬ࡩ࡭ࡧ࡯ࡳࡨࡱࠧῄ")).setLevel(logging.WARNING)
lock = FileLock(bstack11l1l1ll1l_opy_+bstack11l111_opy_ (u"ࠨ࠮࡭ࡱࡦ࡯ࠧ῅"))
class bstack1llllll11lll_opy_:
    duration: float
    name: str
    startTime: float
    worker: int
    status: bool
    failure: str
    details: Optional[str]
    entryType: str
    platform: Optional[int]
    command: Optional[str]
    hookType: Optional[str]
    cli: Optional[bool]
    def __init__(self, duration: float, name: str, start_time: float, bstack1llllll1lll1_opy_: int, status: bool, failure: str, details: Optional[str] = None, platform: Optional[int] = None, command: Optional[str] = None, test_name: Optional[str] = None, hook_type: Optional[str] = None, cli: Optional[bool] = False) -> None:
        self.duration = duration
        self.name = name
        self.startTime = start_time
        self.worker = bstack1llllll1lll1_opy_
        self.status = status
        self.failure = failure
        self.details = details
        self.entryType = bstack11l111_opy_ (u"ࠢ࡮ࡧࡤࡷࡺࡸࡥࠣῆ")
        self.platform = platform
        self.command = command
        self.testName = test_name
        self.hookType = hook_type
        self.cli = cli
class bstack1ll1l11ll1l_opy_:
    global bstack1llllll1l11l_opy_
    @staticmethod
    def bstack1l1lllllll1_opy_(key: str):
        bstack1l1llll11ll_opy_ = bstack1ll1l11ll1l_opy_.bstack11ll111ll1l_opy_(key)
        bstack1ll1l11ll1l_opy_.mark(bstack1l1llll11ll_opy_+bstack11l111_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣῇ"))
        return bstack1l1llll11ll_opy_
    @staticmethod
    def mark(key: str) -> None:
        try:
            bstack1llllll1l11l_opy_[key] = time.time_ns() / 1000000
        except Exception as e:
            logger.debug(bstack11l111_opy_ (u"ࠤࡈࡶࡷࡵࡲ࠻ࠢࡾࢁࠧῈ").format(e))
    @staticmethod
    def end(label: str, start: str, end: str, status: bool, failure: Optional[str] = None, hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            bstack1ll1l11ll1l_opy_.mark(end)
            bstack1ll1l11ll1l_opy_.measure(label, start, end, status, failure, hook_type, details, command, test_name)
        except Exception as e:
            logger.debug(bstack11l111_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡱࡥࡺࠢࡰࡩࡹࡸࡩࡤࡵ࠽ࠤࢀࢃࠢΈ").format(e))
    @staticmethod
    def measure(label: str, start: str, end: str, status: bool, failure: Optional[str], hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            if start not in bstack1llllll1l11l_opy_ or end not in bstack1llllll1l11l_opy_:
                logger.debug(bstack11l111_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡳࡵࡣࡵࡸࠥࡱࡥࡺࠢࡺ࡭ࡹ࡮ࠠࡷࡣ࡯ࡹࡪࠦࡻࡾࠢࡲࡶࠥ࡫࡮ࡥࠢ࡮ࡩࡾࠦࡷࡪࡶ࡫ࠤࡻࡧ࡬ࡶࡧࠣࡿࢂࠨῊ").format(start,end))
                return
            duration: float = bstack1llllll1l11l_opy_[end] - bstack1llllll1l11l_opy_[start]
            bstack1llllll1l1ll_opy_ = os.environ.get(bstack11l111_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇࡏࡎࡂࡔ࡜ࡣࡎ࡙࡟ࡓࡗࡑࡒࡎࡔࡇࠣΉ"), bstack11l111_opy_ (u"ࠨࡦࡢ࡮ࡶࡩࠧῌ")).lower() == bstack11l111_opy_ (u"ࠢࡵࡴࡸࡩࠧ῍")
            bstack1llllll1llll_opy_: bstack1llllll11lll_opy_ = bstack1llllll11lll_opy_(duration, label, bstack1llllll1l11l_opy_[start], os.getpid(), status, failure, details, os.environ.get(bstack11l111_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠣ῎"), 0), command, test_name, hook_type, bstack1llllll1l1ll_opy_)
            del bstack1llllll1l11l_opy_[start]
            del bstack1llllll1l11l_opy_[end]
            bstack1ll1l11ll1l_opy_.bstack1llllll1ll11_opy_(bstack1llllll1llll_opy_)
        except Exception as e:
            logger.debug(bstack11l111_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠ࡮ࡧࡤࡷࡺࡸࡩ࡯ࡩࠣ࡯ࡪࡿࠠ࡮ࡧࡷࡶ࡮ࡩࡳ࠻ࠢࡾࢁࠧ῏").format(e))
    @staticmethod
    def bstack1llllll1ll11_opy_(bstack1llllll1llll_opy_):
        os.makedirs(os.path.dirname(bstack11l1l1ll1l_opy_)) if not os.path.exists(os.path.dirname(bstack11l1l1ll1l_opy_)) else None
        bstack1ll1l11ll1l_opy_.bstack1llllll1l1l1_opy_()
        try:
            with lock:
                with open(bstack11l1l1ll1l_opy_, bstack11l111_opy_ (u"ࠥࡶ࠰ࠨῐ"), encoding=bstack11l111_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥῑ")) as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = []
                    data.append(bstack1llllll1llll_opy_.__dict__)
                    file.seek(0)
                    file.truncate()
                    json.dump(data, file, indent=4)
        except FileNotFoundError as bstack1lllllll1111_opy_:
            logger.debug(bstack11l111_opy_ (u"ࠧࡌࡩ࡭ࡧࠣࡲࡴࡺࠠࡧࡱࡸࡲࡩࠦࡻࡾࠤῒ").format(bstack1lllllll1111_opy_))
            with lock:
                with open(bstack11l1l1ll1l_opy_, bstack11l111_opy_ (u"ࠨࡷࠣΐ"), encoding=bstack11l111_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨ῔")) as file:
                    data = [bstack1llllll1llll_opy_.__dict__]
                    json.dump(data, file, indent=4)
        except Exception as e:
            logger.debug(bstack11l111_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣ࡯ࡪࡿࠠ࡮ࡧࡷࡶ࡮ࡩࡳࠡࡣࡳࡴࡪࡴࡤࠡࡽࢀࠦ῕").format(str(e)))
        finally:
            if os.path.exists(bstack11l1l1ll1l_opy_+bstack11l111_opy_ (u"ࠤ࠱ࡰࡴࡩ࡫ࠣῖ")):
                os.remove(bstack11l1l1ll1l_opy_+bstack11l111_opy_ (u"ࠥ࠲ࡱࡵࡣ࡬ࠤῗ"))
    @staticmethod
    def bstack1llllll1l1l1_opy_():
        attempt = 0
        while (attempt < bstack1llllll1l111_opy_):
            attempt += 1
            if os.path.exists(bstack11l1l1ll1l_opy_+bstack11l111_opy_ (u"ࠦ࠳ࡲ࡯ࡤ࡭ࠥῘ")):
                time.sleep(0.5)
            else:
                break
    @staticmethod
    def bstack11ll111ll1l_opy_(label: str) -> str:
        try:
            return bstack11l111_opy_ (u"ࠧࢁࡽ࠻ࡽࢀࠦῙ").format(label,str(uuid.uuid4().hex)[:6])
        except Exception as e:
            logger.debug(bstack11l111_opy_ (u"ࠨࡅࡳࡴࡲࡶ࠿ࠦࡻࡾࠤῚ").format(e))