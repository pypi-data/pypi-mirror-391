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
import collections
import datetime
import json
import os
import platform
import re
import subprocess
import traceback
import tempfile
import multiprocessing
import threading
import sys
import logging
from math import ceil
from unittest import result
import urllib
from urllib.parse import urlparse
import copy
import zipfile
import git
import requests
from packaging import version
from bstack_utils.config import Config
from bstack_utils.constants import (bstack1l111ll1l_opy_, bstack1ll1l1ll11_opy_, bstack1l111l11l_opy_,
                                    bstack11l1l11ll1l_opy_, bstack11l1l1ll1l1_opy_, bstack11l1l11l1l1_opy_, bstack11l1ll11111_opy_)
from bstack_utils.measure import measure
from bstack_utils.messages import bstack11lll11l_opy_, bstack1lll1l111l_opy_
from bstack_utils.proxy import bstack11111llll_opy_, bstack1lll111lll_opy_
from bstack_utils.constants import *
from bstack_utils import bstack11l111111l_opy_
from bstack_utils.bstack1ll1lllll1_opy_ import bstack1l1l1111l1_opy_
from browserstack_sdk._version import __version__
bstack11l11ll1l_opy_ = Config.bstack111llll1_opy_()
logger = bstack11l111111l_opy_.get_logger(__name__, bstack11l111111l_opy_.bstack1lll1lll111_opy_())
def bstack11ll11l1l11_opy_(config):
    return config[bstack11l111_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ᭰")]
def bstack11ll1l1l1ll_opy_(config):
    return config[bstack11l111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ᭱")]
def bstack11l1111lll_opy_():
    try:
        import playwright
        return True
    except ImportError:
        return False
def bstack111ll1l1l1l_opy_(obj):
    values = []
    bstack111l1lll11l_opy_ = re.compile(bstack11l111_opy_ (u"ࡷࠨ࡞ࡄࡗࡖࡘࡔࡓ࡟ࡕࡃࡊࡣࡡࡪࠫࠥࠤ᭲"), re.I)
    for key in obj.keys():
        if bstack111l1lll11l_opy_.match(key):
            values.append(obj[key])
    return values
def bstack111lll111l1_opy_(config):
    tags = []
    tags.extend(bstack111ll1l1l1l_opy_(os.environ))
    tags.extend(bstack111ll1l1l1l_opy_(config))
    return tags
def bstack111l1llll11_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack111ll11l1ll_opy_(bstack111ll1lll11_opy_):
    if not bstack111ll1lll11_opy_:
        return bstack11l111_opy_ (u"࠭ࠧ᭳")
    return bstack11l111_opy_ (u"ࠢࡼࡿࠣࠬࢀࢃࠩࠣ᭴").format(bstack111ll1lll11_opy_.name, bstack111ll1lll11_opy_.email)
def bstack11ll11l11l1_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack111ll11llll_opy_ = repo.common_dir
        info = {
            bstack11l111_opy_ (u"ࠣࡵ࡫ࡥࠧ᭵"): repo.head.commit.hexsha,
            bstack11l111_opy_ (u"ࠤࡶ࡬ࡴࡸࡴࡠࡵ࡫ࡥࠧ᭶"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack11l111_opy_ (u"ࠥࡦࡷࡧ࡮ࡤࡪࠥ᭷"): repo.active_branch.name,
            bstack11l111_opy_ (u"ࠦࡹࡧࡧࠣ᭸"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack11l111_opy_ (u"ࠧࡩ࡯࡮࡯࡬ࡸࡹ࡫ࡲࠣ᭹"): bstack111ll11l1ll_opy_(repo.head.commit.committer),
            bstack11l111_opy_ (u"ࠨࡣࡰ࡯ࡰ࡭ࡹࡺࡥࡳࡡࡧࡥࡹ࡫ࠢ᭺"): repo.head.commit.committed_datetime.isoformat(),
            bstack11l111_opy_ (u"ࠢࡢࡷࡷ࡬ࡴࡸࠢ᭻"): bstack111ll11l1ll_opy_(repo.head.commit.author),
            bstack11l111_opy_ (u"ࠣࡣࡸࡸ࡭ࡵࡲࡠࡦࡤࡸࡪࠨ᭼"): repo.head.commit.authored_datetime.isoformat(),
            bstack11l111_opy_ (u"ࠤࡦࡳࡲࡳࡩࡵࡡࡰࡩࡸࡹࡡࡨࡧࠥ᭽"): repo.head.commit.message,
            bstack11l111_opy_ (u"ࠥࡶࡴࡵࡴࠣ᭾"): repo.git.rev_parse(bstack11l111_opy_ (u"ࠦ࠲࠳ࡳࡩࡱࡺ࠱ࡹࡵࡰ࡭ࡧࡹࡩࡱࠨ᭿")),
            bstack11l111_opy_ (u"ࠧࡩ࡯࡮࡯ࡲࡲࡤ࡭ࡩࡵࡡࡧ࡭ࡷࠨᮀ"): bstack111ll11llll_opy_,
            bstack11l111_opy_ (u"ࠨࡷࡰࡴ࡮ࡸࡷ࡫ࡥࡠࡩ࡬ࡸࡤࡪࡩࡳࠤᮁ"): subprocess.check_output([bstack11l111_opy_ (u"ࠢࡨ࡫ࡷࠦᮂ"), bstack11l111_opy_ (u"ࠣࡴࡨࡺ࠲ࡶࡡࡳࡵࡨࠦᮃ"), bstack11l111_opy_ (u"ࠤ࠰࠱࡬࡯ࡴ࠮ࡥࡲࡱࡲࡵ࡮࠮ࡦ࡬ࡶࠧᮄ")]).strip().decode(
                bstack11l111_opy_ (u"ࠪࡹࡹ࡬࠭࠹ࠩᮅ")),
            bstack11l111_opy_ (u"ࠦࡱࡧࡳࡵࡡࡷࡥ࡬ࠨᮆ"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack11l111_opy_ (u"ࠧࡩ࡯࡮࡯࡬ࡸࡸࡥࡳࡪࡰࡦࡩࡤࡲࡡࡴࡶࡢࡸࡦ࡭ࠢᮇ"): repo.git.rev_list(
                bstack11l111_opy_ (u"ࠨࡻࡾ࠰࠱ࡿࢂࠨᮈ").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack111ll111111_opy_ = []
        for remote in remotes:
            bstack111llll1l1l_opy_ = {
                bstack11l111_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᮉ"): remote.name,
                bstack11l111_opy_ (u"ࠣࡷࡵࡰࠧᮊ"): remote.url,
            }
            bstack111ll111111_opy_.append(bstack111llll1l1l_opy_)
        bstack111ll1111ll_opy_ = {
            bstack11l111_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᮋ"): bstack11l111_opy_ (u"ࠥ࡫࡮ࡺࠢᮌ"),
            **info,
            bstack11l111_opy_ (u"ࠦࡷ࡫࡭ࡰࡶࡨࡷࠧᮍ"): bstack111ll111111_opy_
        }
        bstack111ll1111ll_opy_ = bstack111lll11111_opy_(bstack111ll1111ll_opy_)
        return bstack111ll1111ll_opy_
    except git.InvalidGitRepositoryError:
        return {}
    except Exception as err:
        print(bstack11l111_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡵࡰࡶ࡮ࡤࡸ࡮ࡴࡧࠡࡉ࡬ࡸࠥࡳࡥࡵࡣࡧࡥࡹࡧࠠࡸ࡫ࡷ࡬ࠥ࡫ࡲࡳࡱࡵ࠾ࠥࢁࡽࠣᮎ").format(err))
        return {}
def bstack111ll1111l1_opy_(bstack111ll1ll1l1_opy_=None):
    bstack11l111_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡇࡦࡶࠣ࡫࡮ࡺࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡶࡴࡪࡩࡩࡧ࡫ࡦࡥࡱࡲࡹࠡࡨࡲࡶࡲࡧࡴࡵࡧࡧࠤ࡫ࡵࡲࠡࡃࡌࠤࡸ࡫࡬ࡦࡥࡷ࡭ࡴࡴࠠࡶࡵࡨࠤࡨࡧࡳࡦࡵࠣࡪࡴࡸࠠࡦࡣࡦ࡬ࠥ࡬࡯࡭ࡦࡨࡶࠥ࡯࡮ࠡࡶ࡫ࡩࠥࡲࡩࡴࡶ࠱ࠎࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࡨࡲࡰࡩ࡫ࡲࡴࠢࠫࡰ࡮ࡹࡴ࠭ࠢࡲࡴࡹ࡯࡯࡯ࡣ࡯࠭࠿ࠦࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡏࡱࡱࡩ࠿ࠦࡍࡰࡰࡲ࠱ࡷ࡫ࡰࡰࠢࡤࡴࡵࡸ࡯ࡢࡥ࡫࠰ࠥࡻࡳࡦࡵࠣࡧࡺࡸࡲࡦࡰࡷࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿࠠ࡜ࡱࡶ࠲࡬࡫ࡴࡤࡹࡧࠬ࠮ࡣࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡆ࡯ࡳࡸࡾࠦ࡬ࡪࡵࡷࠤࡠࡣ࠺ࠡࡏࡸࡰࡹ࡯࠭ࡳࡧࡳࡳࠥࡧࡰࡱࡴࡲࡥࡨ࡮ࠠࡸ࡫ࡷ࡬ࠥࡴ࡯ࠡࡵࡲࡹࡷࡩࡥࡴࠢࡦࡳࡳ࡬ࡩࡨࡷࡵࡩࡩ࠲ࠠࡳࡧࡷࡹࡷࡴࡳࠡ࡝ࡠࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡑ࡯ࡳࡵࠢࡲࡪࠥࡶࡡࡵࡪࡶ࠾ࠥࡓࡵ࡭ࡶ࡬࠱ࡷ࡫ࡰࡰࠢࡤࡴࡵࡸ࡯ࡢࡥ࡫ࠤࡼ࡯ࡴࡩࠢࡶࡴࡪࡩࡩࡧ࡫ࡦࠤ࡫ࡵ࡬ࡥࡧࡵࡷࠥࡺ࡯ࠡࡣࡱࡥࡱࡿࡺࡦࠌࠣࠤࠥࠦࡒࡦࡶࡸࡶࡳࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢ࡯࡭ࡸࡺ࠺ࠡࡎ࡬ࡷࡹࠦ࡯ࡧࠢࡧ࡭ࡨࡺࡳ࠭ࠢࡨࡥࡨ࡮ࠠࡤࡱࡱࡸࡦ࡯࡮ࡪࡰࡪࠤ࡬࡯ࡴࠡ࡯ࡨࡸࡦࡪࡡࡵࡣࠣࡪࡴࡸࠠࡢࠢࡩࡳࡱࡪࡥࡳ࠰ࠍࠤࠥࠦࠠࠣࠤࠥᮏ")
    if bstack111ll1ll1l1_opy_ is None:
        bstack111ll1ll1l1_opy_ = [os.getcwd()]
    elif isinstance(bstack111ll1ll1l1_opy_, list) and len(bstack111ll1ll1l1_opy_) == 0:
        return []
    results = []
    for folder in bstack111ll1ll1l1_opy_:
        try:
            if not os.path.exists(folder):
                raise Exception(bstack11l111_opy_ (u"ࠢࡇࡱ࡯ࡨࡪࡸࠠࡥࡱࡨࡷࠥࡴ࡯ࡵࠢࡨࡼ࡮ࡹࡴ࠻ࠢࡾࢁࠧᮐ").format(folder))
            repo = git.Repo(folder, search_parent_directories=True)
            result = {
                bstack11l111_opy_ (u"ࠣࡲࡵࡍࡩࠨᮑ"): bstack11l111_opy_ (u"ࠤࠥᮒ"),
                bstack11l111_opy_ (u"ࠥࡪ࡮ࡲࡥࡴࡅ࡫ࡥࡳ࡭ࡥࡥࠤᮓ"): [],
                bstack11l111_opy_ (u"ࠦࡦࡻࡴࡩࡱࡵࡷࠧᮔ"): [],
                bstack11l111_opy_ (u"ࠧࡶࡲࡅࡣࡷࡩࠧᮕ"): bstack11l111_opy_ (u"ࠨࠢᮖ"),
                bstack11l111_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡍࡦࡵࡶࡥ࡬࡫ࡳࠣᮗ"): [],
                bstack11l111_opy_ (u"ࠣࡲࡵࡘ࡮ࡺ࡬ࡦࠤᮘ"): bstack11l111_opy_ (u"ࠤࠥᮙ"),
                bstack11l111_opy_ (u"ࠥࡴࡷࡊࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠥᮚ"): bstack11l111_opy_ (u"ࠦࠧᮛ"),
                bstack11l111_opy_ (u"ࠧࡶࡲࡓࡣࡺࡈ࡮࡬ࡦࠣᮜ"): bstack11l111_opy_ (u"ࠨࠢᮝ")
            }
            bstack11l111l1l1l_opy_ = repo.active_branch.name
            bstack11l111lll11_opy_ = repo.head.commit
            result[bstack11l111_opy_ (u"ࠢࡱࡴࡌࡨࠧᮞ")] = bstack11l111lll11_opy_.hexsha
            bstack111ll11l1l1_opy_ = _111lll11l1l_opy_(repo)
            logger.debug(bstack11l111_opy_ (u"ࠣࡄࡤࡷࡪࠦࡢࡳࡣࡱࡧ࡭ࠦࡦࡰࡴࠣࡧࡴࡳࡰࡢࡴ࡬ࡷࡴࡴ࠺ࠡࠤᮟ") + str(bstack111ll11l1l1_opy_) + bstack11l111_opy_ (u"ࠤࠥᮠ"))
            if bstack111ll11l1l1_opy_:
                try:
                    bstack111ll1l11ll_opy_ = repo.git.diff(bstack11l111_opy_ (u"ࠥ࠱࠲ࡴࡡ࡮ࡧ࠰ࡳࡳࡲࡹࠣᮡ"), bstack1lll111l111_opy_ (u"ࠦࢀࡨࡡࡴࡧࡢࡦࡷࡧ࡮ࡤࡪࢀ࠲࠳࠴ࡻࡤࡷࡵࡶࡪࡴࡴࡠࡤࡵࡥࡳࡩࡨࡾࠤᮢ")).split(bstack11l111_opy_ (u"ࠬࡢ࡮ࠨᮣ"))
                    logger.debug(bstack11l111_opy_ (u"ࠨࡃࡩࡣࡱ࡫ࡪࡪࠠࡧ࡫࡯ࡩࡸࠦࡢࡦࡶࡺࡩࡪࡴࠠࡼࡤࡤࡷࡪࡥࡢࡳࡣࡱࡧ࡭ࢃࠠࡢࡰࡧࠤࢀࡩࡵࡳࡴࡨࡲࡹࡥࡢࡳࡣࡱࡧ࡭ࢃ࠺ࠡࠤᮤ") + str(bstack111ll1l11ll_opy_) + bstack11l111_opy_ (u"ࠢࠣᮥ"))
                    result[bstack11l111_opy_ (u"ࠣࡨ࡬ࡰࡪࡹࡃࡩࡣࡱ࡫ࡪࡪࠢᮦ")] = [f.strip() for f in bstack111ll1l11ll_opy_ if f.strip()]
                    commits = list(repo.iter_commits(bstack1lll111l111_opy_ (u"ࠤࡾࡦࡦࡹࡥࡠࡤࡵࡥࡳࡩࡨࡾ࠰࠱ࡿࡨࡻࡲࡳࡧࡱࡸࡤࡨࡲࡢࡰࡦ࡬ࢂࠨᮧ")))
                except Exception:
                    logger.debug(bstack11l111_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡧࡦࡶࠣࡧ࡭ࡧ࡮ࡨࡧࡧࠤ࡫࡯࡬ࡦࡵࠣࡪࡷࡵ࡭ࠡࡤࡵࡥࡳࡩࡨࠡࡥࡲࡱࡵࡧࡲࡪࡵࡲࡲ࠳ࠦࡆࡢ࡮࡯࡭ࡳ࡭ࠠࡣࡣࡦ࡯ࠥࡺ࡯ࠡࡴࡨࡧࡪࡴࡴࠡࡥࡲࡱࡲ࡯ࡴࡴ࠰ࠥᮨ"))
                    commits = list(repo.iter_commits(max_count=10))
                    if commits:
                        result[bstack11l111_opy_ (u"ࠦ࡫࡯࡬ࡦࡵࡆ࡬ࡦࡴࡧࡦࡦࠥᮩ")] = _111ll1lll1l_opy_(commits[:5])
            else:
                commits = list(repo.iter_commits(max_count=10))
                if commits:
                    result[bstack11l111_opy_ (u"ࠧ࡬ࡩ࡭ࡧࡶࡇ࡭ࡧ࡮ࡨࡧࡧ᮪ࠦ")] = _111ll1lll1l_opy_(commits[:5])
            bstack11l11111111_opy_ = set()
            bstack111lll1ll11_opy_ = []
            for commit in commits:
                logger.debug(bstack11l111_opy_ (u"ࠨࡐࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡧࡴࡳ࡭ࡪࡶ࠽ࠤ᮫ࠧ") + str(commit.message) + bstack11l111_opy_ (u"ࠢࠣᮬ"))
                bstack11l11l11l11_opy_ = commit.author.name if commit.author else bstack11l111_opy_ (u"ࠣࡗࡱ࡯ࡳࡵࡷ࡯ࠤᮭ")
                bstack11l11111111_opy_.add(bstack11l11l11l11_opy_)
                bstack111lll1ll11_opy_.append({
                    bstack11l111_opy_ (u"ࠤࡰࡩࡸࡹࡡࡨࡧࠥᮮ"): commit.message.strip(),
                    bstack11l111_opy_ (u"ࠥࡹࡸ࡫ࡲࠣᮯ"): bstack11l11l11l11_opy_
                })
            result[bstack11l111_opy_ (u"ࠦࡦࡻࡴࡩࡱࡵࡷࠧ᮰")] = list(bstack11l11111111_opy_)
            result[bstack11l111_opy_ (u"ࠧࡩ࡯࡮࡯࡬ࡸࡒ࡫ࡳࡴࡣࡪࡩࡸࠨ᮱")] = bstack111lll1ll11_opy_
            result[bstack11l111_opy_ (u"ࠨࡰࡳࡆࡤࡸࡪࠨ᮲")] = bstack11l111lll11_opy_.committed_datetime.strftime(bstack11l111_opy_ (u"࡛ࠢࠦ࠰ࠩࡲ࠳ࠥࡥࠤ᮳"))
            if (not result[bstack11l111_opy_ (u"ࠣࡲࡵࡘ࡮ࡺ࡬ࡦࠤ᮴")] or result[bstack11l111_opy_ (u"ࠤࡳࡶ࡙࡯ࡴ࡭ࡧࠥ᮵")].strip() == bstack11l111_opy_ (u"ࠥࠦ᮶")) and bstack11l111lll11_opy_.message:
                bstack11l111l111l_opy_ = bstack11l111lll11_opy_.message.strip().splitlines()
                result[bstack11l111_opy_ (u"ࠦࡵࡸࡔࡪࡶ࡯ࡩࠧ᮷")] = bstack11l111l111l_opy_[0] if bstack11l111l111l_opy_ else bstack11l111_opy_ (u"ࠧࠨ᮸")
                if len(bstack11l111l111l_opy_) > 2:
                    result[bstack11l111_opy_ (u"ࠨࡰࡳࡆࡨࡷࡨࡸࡩࡱࡶ࡬ࡳࡳࠨ᮹")] = bstack11l111_opy_ (u"ࠧ࡝ࡰࠪᮺ").join(bstack11l111l111l_opy_[2:]).strip()
            results.append(result)
        except Exception as err:
            logger.error(bstack11l111_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡱࡳࡹࡱࡧࡴࡪࡰࡪࠤࡌ࡯ࡴࠡ࡯ࡨࡸࡦࡪࡡࡵࡣࠣࡪࡴࡸࠠࡂࡋࠣࡷࡪࡲࡥࡤࡶ࡬ࡳࡳࠦࠨࡧࡱ࡯ࡨࡪࡸ࠺ࠡࡽࢀ࠭࠿ࠦࡻࡾࠢ࠰ࠤࢀࢃࠢᮻ").format(
                folder,
                type(err).__name__,
                str(err)
            ))
    filtered_results = [
        result
        for result in results
        if _111l1lll1l1_opy_(result)
    ]
    return filtered_results
def _111l1lll1l1_opy_(result):
    bstack11l111_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡋࡩࡱࡶࡥࡳࠢࡷࡳࠥࡩࡨࡦࡥ࡮ࠤ࡮࡬ࠠࡢࠢࡪ࡭ࡹࠦ࡭ࡦࡶࡤࡨࡦࡺࡡࠡࡴࡨࡷࡺࡲࡴࠡ࡫ࡶࠤࡻࡧ࡬ࡪࡦࠣࠬࡳࡵ࡮࠮ࡧࡰࡴࡹࡿࠠࡧ࡫࡯ࡩࡸࡉࡨࡢࡰࡪࡩࡩࠦࡡ࡯ࡦࠣࡥࡺࡺࡨࡰࡴࡶ࠭࠳ࠐࠠࠡࠢࠣࠦࠧࠨᮼ")
    return (
        isinstance(result.get(bstack11l111_opy_ (u"ࠥࡪ࡮ࡲࡥࡴࡅ࡫ࡥࡳ࡭ࡥࡥࠤᮽ"), None), list)
        and len(result[bstack11l111_opy_ (u"ࠦ࡫࡯࡬ࡦࡵࡆ࡬ࡦࡴࡧࡦࡦࠥᮾ")]) > 0
        and isinstance(result.get(bstack11l111_opy_ (u"ࠧࡧࡵࡵࡪࡲࡶࡸࠨᮿ"), None), list)
        and len(result[bstack11l111_opy_ (u"ࠨࡡࡶࡶ࡫ࡳࡷࡹࠢᯀ")]) > 0
    )
def _111lll11l1l_opy_(repo):
    bstack11l111_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࡕࡴࡼࠤࡹࡵࠠࡥࡧࡷࡩࡷࡳࡩ࡯ࡧࠣࡸ࡭࡫ࠠࡣࡣࡶࡩࠥࡨࡲࡢࡰࡦ࡬ࠥ࡬࡯ࡳࠢࡷ࡬ࡪࠦࡧࡪࡸࡨࡲࠥࡸࡥࡱࡱࠣࡻ࡮ࡺࡨࡰࡷࡷࠤ࡭ࡧࡲࡥࡥࡲࡨࡪࡪࠠ࡯ࡣࡰࡩࡸࠦࡡ࡯ࡦࠣࡻࡴࡸ࡫ࠡࡹ࡬ࡸ࡭ࠦࡡ࡭࡮࡚ࠣࡈ࡙ࠠࡱࡴࡲࡺ࡮ࡪࡥࡳࡵ࠱ࠎࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴࠢࡷ࡬ࡪࠦࡤࡦࡨࡤࡹࡱࡺࠠࡣࡴࡤࡲࡨ࡮ࠠࡪࡨࠣࡴࡴࡹࡳࡪࡤ࡯ࡩ࠱ࠦࡥ࡭ࡵࡨࠤࡓࡵ࡮ࡦ࠰ࠍࠤࠥࠦࠠࠣࠤࠥᯁ")
    try:
        try:
            origin = repo.remotes.origin
            bstack11l111lllll_opy_ = origin.refs[bstack11l111_opy_ (u"ࠨࡊࡈࡅࡉ࠭ᯂ")]
            target = bstack11l111lllll_opy_.reference.name
            if target.startswith(bstack11l111_opy_ (u"ࠩࡲࡶ࡮࡭ࡩ࡯࠱ࠪᯃ")):
                return target
        except Exception:
            pass
        if repo.remotes and repo.remotes.origin.refs:
            for ref in repo.remotes.origin.refs:
                if ref.name.startswith(bstack11l111_opy_ (u"ࠪࡳࡷ࡯ࡧࡪࡰ࠲ࠫᯄ")):
                    return ref.name
        if repo.heads:
            return repo.heads[0].name
    except Exception:
        pass
    return None
def _111ll1lll1l_opy_(commits):
    bstack11l111_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࡌ࡫ࡴࠡ࡮࡬ࡷࡹࠦ࡯ࡧࠢࡦ࡬ࡦࡴࡧࡦࡦࠣࡪ࡮ࡲࡥࡴࠢࡩࡶࡴࡳࠠࡢࠢ࡯࡭ࡸࡺࠠࡰࡨࠣࡧࡴࡳ࡭ࡪࡶࡶ࠲ࠏࠦࠠࠡࠢࠥࠦࠧᯅ")
    bstack111ll1l11ll_opy_ = set()
    try:
        for commit in commits:
            if commit.parents:
                for parent in commit.parents:
                    diff = commit.diff(parent)
                    for bstack111ll11111l_opy_ in diff:
                        if bstack111ll11111l_opy_.a_path:
                            bstack111ll1l11ll_opy_.add(bstack111ll11111l_opy_.a_path)
                        if bstack111ll11111l_opy_.b_path:
                            bstack111ll1l11ll_opy_.add(bstack111ll11111l_opy_.b_path)
    except Exception:
        pass
    return list(bstack111ll1l11ll_opy_)
def bstack111lll11111_opy_(bstack111ll1111ll_opy_):
    bstack11l111l1ll1_opy_ = bstack111ll1l1lll_opy_(bstack111ll1111ll_opy_)
    if bstack11l111l1ll1_opy_ and bstack11l111l1ll1_opy_ > bstack11l1l11ll1l_opy_:
        bstack111lll1l111_opy_ = bstack11l111l1ll1_opy_ - bstack11l1l11ll1l_opy_
        bstack111ll111l1l_opy_ = bstack111llll11ll_opy_(bstack111ll1111ll_opy_[bstack11l111_opy_ (u"ࠧࡩ࡯࡮࡯࡬ࡸࡤࡳࡥࡴࡵࡤ࡫ࡪࠨᯆ")], bstack111lll1l111_opy_)
        bstack111ll1111ll_opy_[bstack11l111_opy_ (u"ࠨࡣࡰ࡯ࡰ࡭ࡹࡥ࡭ࡦࡵࡶࡥ࡬࡫ࠢᯇ")] = bstack111ll111l1l_opy_
        logger.info(bstack11l111_opy_ (u"ࠢࡕࡪࡨࠤࡨࡵ࡭࡮࡫ࡷࠤ࡭ࡧࡳࠡࡤࡨࡩࡳࠦࡴࡳࡷࡱࡧࡦࡺࡥࡥ࠰ࠣࡗ࡮ࢀࡥࠡࡱࡩࠤࡨࡵ࡭࡮࡫ࡷࠤࡦ࡬ࡴࡦࡴࠣࡸࡷࡻ࡮ࡤࡣࡷ࡭ࡴࡴࠠࡪࡵࠣࡿࢂࠦࡋࡃࠤᯈ")
                    .format(bstack111ll1l1lll_opy_(bstack111ll1111ll_opy_) / 1024))
    return bstack111ll1111ll_opy_
def bstack111ll1l1lll_opy_(bstack11llllllll_opy_):
    try:
        if bstack11llllllll_opy_:
            bstack11l111ll1l1_opy_ = json.dumps(bstack11llllllll_opy_)
            bstack11l11l11l1l_opy_ = sys.getsizeof(bstack11l111ll1l1_opy_)
            return bstack11l11l11l1l_opy_
    except Exception as e:
        logger.debug(bstack11l111_opy_ (u"ࠣࡕࡲࡱࡪࡺࡨࡪࡰࡪࠤࡼ࡫࡮ࡵࠢࡺࡶࡴࡴࡧࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡣ࡯ࡧࡺࡲࡡࡵ࡫ࡱ࡫ࠥࡹࡩࡻࡧࠣࡳ࡫ࠦࡊࡔࡑࡑࠤࡴࡨࡪࡦࡥࡷ࠾ࠥࢁࡽࠣᯉ").format(e))
    return -1
def bstack111llll11ll_opy_(field, bstack111ll1l111l_opy_):
    try:
        bstack11l111llll1_opy_ = len(bytes(bstack11l1l1ll1l1_opy_, bstack11l111_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨᯊ")))
        bstack11l1111l1l1_opy_ = bytes(field, bstack11l111_opy_ (u"ࠪࡹࡹ࡬࠭࠹ࠩᯋ"))
        bstack111lll11l11_opy_ = len(bstack11l1111l1l1_opy_)
        bstack11l11l1l111_opy_ = ceil(bstack111lll11l11_opy_ - bstack111ll1l111l_opy_ - bstack11l111llll1_opy_)
        if bstack11l11l1l111_opy_ > 0:
            bstack111l1llll1l_opy_ = bstack11l1111l1l1_opy_[:bstack11l11l1l111_opy_].decode(bstack11l111_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪᯌ"), errors=bstack11l111_opy_ (u"ࠬ࡯ࡧ࡯ࡱࡵࡩࠬᯍ")) + bstack11l1l1ll1l1_opy_
            return bstack111l1llll1l_opy_
    except Exception as e:
        logger.debug(bstack11l111_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤࡹࡸࡵ࡯ࡥࡤࡸ࡮ࡴࡧࠡࡨ࡬ࡩࡱࡪࠬࠡࡰࡲࡸ࡭࡯࡮ࡨࠢࡺࡥࡸࠦࡴࡳࡷࡱࡧࡦࡺࡥࡥࠢ࡫ࡩࡷ࡫࠺ࠡࡽࢀࠦᯎ").format(e))
    return field
def bstack1l1lllllll_opy_():
    env = os.environ
    if (bstack11l111_opy_ (u"ࠢࡋࡇࡑࡏࡎࡔࡓࡠࡗࡕࡐࠧᯏ") in env and len(env[bstack11l111_opy_ (u"ࠣࡌࡈࡒࡐࡏࡎࡔࡡࡘࡖࡑࠨᯐ")]) > 0) or (
            bstack11l111_opy_ (u"ࠤࡍࡉࡓࡑࡉࡏࡕࡢࡌࡔࡓࡅࠣᯑ") in env and len(env[bstack11l111_opy_ (u"ࠥࡎࡊࡔࡋࡊࡐࡖࡣࡍࡕࡍࡆࠤᯒ")]) > 0):
        return {
            bstack11l111_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᯓ"): bstack11l111_opy_ (u"ࠧࡐࡥ࡯࡭࡬ࡲࡸࠨᯔ"),
            bstack11l111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᯕ"): env.get(bstack11l111_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡕࡓࡎࠥᯖ")),
            bstack11l111_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᯗ"): env.get(bstack11l111_opy_ (u"ࠤࡍࡓࡇࡥࡎࡂࡏࡈࠦᯘ")),
            bstack11l111_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᯙ"): env.get(bstack11l111_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥᯚ"))
        }
    if env.get(bstack11l111_opy_ (u"ࠧࡉࡉࠣᯛ")) == bstack11l111_opy_ (u"ࠨࡴࡳࡷࡨࠦᯜ") and bstack111ll1lll_opy_(env.get(bstack11l111_opy_ (u"ࠢࡄࡋࡕࡇࡑࡋࡃࡊࠤᯝ"))):
        return {
            bstack11l111_opy_ (u"ࠣࡰࡤࡱࡪࠨᯞ"): bstack11l111_opy_ (u"ࠤࡆ࡭ࡷࡩ࡬ࡦࡅࡌࠦᯟ"),
            bstack11l111_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᯠ"): env.get(bstack11l111_opy_ (u"ࠦࡈࡏࡒࡄࡎࡈࡣࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒࠢᯡ")),
            bstack11l111_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᯢ"): env.get(bstack11l111_opy_ (u"ࠨࡃࡊࡔࡆࡐࡊࡥࡊࡐࡄࠥᯣ")),
            bstack11l111_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᯤ"): env.get(bstack11l111_opy_ (u"ࠣࡅࡌࡖࡈࡒࡅࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࠦᯥ"))
        }
    if env.get(bstack11l111_opy_ (u"ࠤࡆࡍ᯦ࠧ")) == bstack11l111_opy_ (u"ࠥࡸࡷࡻࡥࠣᯧ") and bstack111ll1lll_opy_(env.get(bstack11l111_opy_ (u"࡙ࠦࡘࡁࡗࡋࡖࠦᯨ"))):
        return {
            bstack11l111_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᯩ"): bstack11l111_opy_ (u"ࠨࡔࡳࡣࡹ࡭ࡸࠦࡃࡊࠤᯪ"),
            bstack11l111_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᯫ"): env.get(bstack11l111_opy_ (u"ࠣࡖࡕࡅ࡛ࡏࡓࡠࡄࡘࡍࡑࡊ࡟ࡘࡇࡅࡣ࡚ࡘࡌࠣᯬ")),
            bstack11l111_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᯭ"): env.get(bstack11l111_opy_ (u"ࠥࡘࡗࡇࡖࡊࡕࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧᯮ")),
            bstack11l111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᯯ"): env.get(bstack11l111_opy_ (u"࡚ࠧࡒࡂࡘࡌࡗࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᯰ"))
        }
    if env.get(bstack11l111_opy_ (u"ࠨࡃࡊࠤᯱ")) == bstack11l111_opy_ (u"ࠢࡵࡴࡸࡩ᯲ࠧ") and env.get(bstack11l111_opy_ (u"ࠣࡅࡌࡣࡓࡇࡍࡆࠤ᯳")) == bstack11l111_opy_ (u"ࠤࡦࡳࡩ࡫ࡳࡩ࡫ࡳࠦ᯴"):
        return {
            bstack11l111_opy_ (u"ࠥࡲࡦࡳࡥࠣ᯵"): bstack11l111_opy_ (u"ࠦࡈࡵࡤࡦࡵ࡫࡭ࡵࠨ᯶"),
            bstack11l111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᯷"): None,
            bstack11l111_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣ᯸"): None,
            bstack11l111_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᯹"): None
        }
    if env.get(bstack11l111_opy_ (u"ࠣࡄࡌࡘࡇ࡛ࡃࡌࡇࡗࡣࡇࡘࡁࡏࡅࡋࠦ᯺")) and env.get(bstack11l111_opy_ (u"ࠤࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡉࡏࡎࡏࡌࡘࠧ᯻")):
        return {
            bstack11l111_opy_ (u"ࠥࡲࡦࡳࡥࠣ᯼"): bstack11l111_opy_ (u"ࠦࡇ࡯ࡴࡣࡷࡦ࡯ࡪࡺࠢ᯽"),
            bstack11l111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᯾"): env.get(bstack11l111_opy_ (u"ࠨࡂࡊࡖࡅ࡙ࡈࡑࡅࡕࡡࡊࡍ࡙ࡥࡈࡕࡖࡓࡣࡔࡘࡉࡈࡋࡑࠦ᯿")),
            bstack11l111_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᰀ"): None,
            bstack11l111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᰁ"): env.get(bstack11l111_opy_ (u"ࠤࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᰂ"))
        }
    if env.get(bstack11l111_opy_ (u"ࠥࡇࡎࠨᰃ")) == bstack11l111_opy_ (u"ࠦࡹࡸࡵࡦࠤᰄ") and bstack111ll1lll_opy_(env.get(bstack11l111_opy_ (u"ࠧࡊࡒࡐࡐࡈࠦᰅ"))):
        return {
            bstack11l111_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᰆ"): bstack11l111_opy_ (u"ࠢࡅࡴࡲࡲࡪࠨᰇ"),
            bstack11l111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᰈ"): env.get(bstack11l111_opy_ (u"ࠤࡇࡖࡔࡔࡅࡠࡄࡘࡍࡑࡊ࡟ࡍࡋࡑࡏࠧᰉ")),
            bstack11l111_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᰊ"): None,
            bstack11l111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᰋ"): env.get(bstack11l111_opy_ (u"ࠧࡊࡒࡐࡐࡈࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥᰌ"))
        }
    if env.get(bstack11l111_opy_ (u"ࠨࡃࡊࠤᰍ")) == bstack11l111_opy_ (u"ࠢࡵࡴࡸࡩࠧᰎ") and bstack111ll1lll_opy_(env.get(bstack11l111_opy_ (u"ࠣࡕࡈࡑࡆࡖࡈࡐࡔࡈࠦᰏ"))):
        return {
            bstack11l111_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᰐ"): bstack11l111_opy_ (u"ࠥࡗࡪࡳࡡࡱࡪࡲࡶࡪࠨᰑ"),
            bstack11l111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᰒ"): env.get(bstack11l111_opy_ (u"࡙ࠧࡅࡎࡃࡓࡌࡔࡘࡅࡠࡑࡕࡋࡆࡔࡉ࡛ࡃࡗࡍࡔࡔ࡟ࡖࡔࡏࠦᰓ")),
            bstack11l111_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᰔ"): env.get(bstack11l111_opy_ (u"ࠢࡔࡇࡐࡅࡕࡎࡏࡓࡇࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧᰕ")),
            bstack11l111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᰖ"): env.get(bstack11l111_opy_ (u"ࠤࡖࡉࡒࡇࡐࡉࡑࡕࡉࡤࡐࡏࡃࡡࡌࡈࠧᰗ"))
        }
    if env.get(bstack11l111_opy_ (u"ࠥࡇࡎࠨᰘ")) == bstack11l111_opy_ (u"ࠦࡹࡸࡵࡦࠤᰙ") and bstack111ll1lll_opy_(env.get(bstack11l111_opy_ (u"ࠧࡍࡉࡕࡎࡄࡆࡤࡉࡉࠣᰚ"))):
        return {
            bstack11l111_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᰛ"): bstack11l111_opy_ (u"ࠢࡈ࡫ࡷࡐࡦࡨࠢᰜ"),
            bstack11l111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᰝ"): env.get(bstack11l111_opy_ (u"ࠤࡆࡍࡤࡐࡏࡃࡡࡘࡖࡑࠨᰞ")),
            bstack11l111_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᰟ"): env.get(bstack11l111_opy_ (u"ࠦࡈࡏ࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤᰠ")),
            bstack11l111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᰡ"): env.get(bstack11l111_opy_ (u"ࠨࡃࡊࡡࡍࡓࡇࡥࡉࡅࠤᰢ"))
        }
    if env.get(bstack11l111_opy_ (u"ࠢࡄࡋࠥᰣ")) == bstack11l111_opy_ (u"ࠣࡶࡵࡹࡪࠨᰤ") and bstack111ll1lll_opy_(env.get(bstack11l111_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࠧᰥ"))):
        return {
            bstack11l111_opy_ (u"ࠥࡲࡦࡳࡥࠣᰦ"): bstack11l111_opy_ (u"ࠦࡇࡻࡩ࡭ࡦ࡮࡭ࡹ࡫ࠢᰧ"),
            bstack11l111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᰨ"): env.get(bstack11l111_opy_ (u"ࠨࡂࡖࡋࡏࡈࡐࡏࡔࡆࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧᰩ")),
            bstack11l111_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᰪ"): env.get(bstack11l111_opy_ (u"ࠣࡄࡘࡍࡑࡊࡋࡊࡖࡈࡣࡑࡇࡂࡆࡎࠥᰫ")) or env.get(bstack11l111_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࡤࡖࡉࡑࡇࡏࡍࡓࡋ࡟ࡏࡃࡐࡉࠧᰬ")),
            bstack11l111_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᰭ"): env.get(bstack11l111_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡎࡍ࡙ࡋ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨᰮ"))
        }
    if bstack111ll1lll_opy_(env.get(bstack11l111_opy_ (u"࡚ࠧࡆࡠࡄࡘࡍࡑࡊࠢᰯ"))):
        return {
            bstack11l111_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᰰ"): bstack11l111_opy_ (u"ࠢࡗ࡫ࡶࡹࡦࡲࠠࡔࡶࡸࡨ࡮ࡵࠠࡕࡧࡤࡱ࡙ࠥࡥࡳࡸ࡬ࡧࡪࡹࠢᰱ"),
            bstack11l111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᰲ"): bstack11l111_opy_ (u"ࠤࡾࢁࢀࢃࠢᰳ").format(env.get(bstack11l111_opy_ (u"ࠪࡗ࡞࡙ࡔࡆࡏࡢࡘࡊࡇࡍࡇࡑࡘࡒࡉࡇࡔࡊࡑࡑࡗࡊࡘࡖࡆࡔࡘࡖࡎ࠭ᰴ")), env.get(bstack11l111_opy_ (u"ࠫࡘ࡟ࡓࡕࡇࡐࡣ࡙ࡋࡁࡎࡒࡕࡓࡏࡋࡃࡕࡋࡇࠫᰵ"))),
            bstack11l111_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᰶ"): env.get(bstack11l111_opy_ (u"ࠨࡓ࡚ࡕࡗࡉࡒࡥࡄࡆࡈࡌࡒࡎ࡚ࡉࡐࡐࡌࡈ᰷ࠧ")),
            bstack11l111_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᰸"): env.get(bstack11l111_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡏࡄࠣ᰹"))
        }
    if bstack111ll1lll_opy_(env.get(bstack11l111_opy_ (u"ࠤࡄࡔࡕ࡜ࡅ࡚ࡑࡕࠦ᰺"))):
        return {
            bstack11l111_opy_ (u"ࠥࡲࡦࡳࡥࠣ᰻"): bstack11l111_opy_ (u"ࠦࡆࡶࡰࡷࡧࡼࡳࡷࠨ᰼"),
            bstack11l111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᰽"): bstack11l111_opy_ (u"ࠨࡻࡾ࠱ࡳࡶࡴࡰࡥࡤࡶ࠲ࡿࢂ࠵ࡻࡾ࠱ࡥࡹ࡮ࡲࡤࡴ࠱ࡾࢁࠧ᰾").format(env.get(bstack11l111_opy_ (u"ࠧࡂࡒࡓ࡚ࡊ࡟ࡏࡓࡡࡘࡖࡑ࠭᰿")), env.get(bstack11l111_opy_ (u"ࠨࡃࡓࡔ࡛ࡋ࡙ࡐࡔࡢࡅࡈࡉࡏࡖࡐࡗࡣࡓࡇࡍࡆࠩ᱀")), env.get(bstack11l111_opy_ (u"ࠩࡄࡔࡕ࡜ࡅ࡚ࡑࡕࡣࡕࡘࡏࡋࡇࡆࡘࡤ࡙ࡌࡖࡉࠪ᱁")), env.get(bstack11l111_opy_ (u"ࠪࡅࡕࡖࡖࡆ࡛ࡒࡖࡤࡈࡕࡊࡎࡇࡣࡎࡊࠧ᱂"))),
            bstack11l111_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ᱃"): env.get(bstack11l111_opy_ (u"ࠧࡇࡐࡑࡘࡈ࡝ࡔࡘ࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤ᱄")),
            bstack11l111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧ᱅"): env.get(bstack11l111_opy_ (u"ࠢࡂࡒࡓ࡚ࡊ࡟ࡏࡓࡡࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࠣ᱆"))
        }
    if env.get(bstack11l111_opy_ (u"ࠣࡃ࡝࡙ࡗࡋ࡟ࡉࡖࡗࡔࡤ࡛ࡓࡆࡔࡢࡅࡌࡋࡎࡕࠤ᱇")) and env.get(bstack11l111_opy_ (u"ࠤࡗࡊࡤࡈࡕࡊࡎࡇࠦ᱈")):
        return {
            bstack11l111_opy_ (u"ࠥࡲࡦࡳࡥࠣ᱉"): bstack11l111_opy_ (u"ࠦࡆࢀࡵࡳࡧࠣࡇࡎࠨ᱊"),
            bstack11l111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᱋"): bstack11l111_opy_ (u"ࠨࡻࡾࡽࢀ࠳ࡤࡨࡵࡪ࡮ࡧ࠳ࡷ࡫ࡳࡶ࡮ࡷࡷࡄࡨࡵࡪ࡮ࡧࡍࡩࡃࡻࡾࠤ᱌").format(env.get(bstack11l111_opy_ (u"ࠧࡔ࡛ࡖࡘࡊࡓ࡟ࡕࡇࡄࡑࡋࡕࡕࡏࡆࡄࡘࡎࡕࡎࡔࡇࡕ࡚ࡊࡘࡕࡓࡋࠪᱍ")), env.get(bstack11l111_opy_ (u"ࠨࡕ࡜ࡗ࡙ࡋࡍࡠࡖࡈࡅࡒࡖࡒࡐࡌࡈࡇ࡙࠭ᱎ")), env.get(bstack11l111_opy_ (u"ࠩࡅ࡙ࡎࡒࡄࡠࡄࡘࡍࡑࡊࡉࡅࠩᱏ"))),
            bstack11l111_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧ᱐"): env.get(bstack11l111_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡆ࡚ࡏࡌࡅࡋࡇࠦ᱑")),
            bstack11l111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦ᱒"): env.get(bstack11l111_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤࡈࡕࡊࡎࡇࡍࡉࠨ᱓"))
        }
    if any([env.get(bstack11l111_opy_ (u"ࠢࡄࡑࡇࡉࡇ࡛ࡉࡍࡆࡢࡆ࡚ࡏࡌࡅࡡࡌࡈࠧ᱔")), env.get(bstack11l111_opy_ (u"ࠣࡅࡒࡈࡊࡈࡕࡊࡎࡇࡣࡗࡋࡓࡐࡎ࡙ࡉࡉࡥࡓࡐࡗࡕࡇࡊࡥࡖࡆࡔࡖࡍࡔࡔࠢ᱕")), env.get(bstack11l111_opy_ (u"ࠤࡆࡓࡉࡋࡂࡖࡋࡏࡈࡤ࡙ࡏࡖࡔࡆࡉࡤ࡜ࡅࡓࡕࡌࡓࡓࠨ᱖"))]):
        return {
            bstack11l111_opy_ (u"ࠥࡲࡦࡳࡥࠣ᱗"): bstack11l111_opy_ (u"ࠦࡆ࡝ࡓࠡࡅࡲࡨࡪࡈࡵࡪ࡮ࡧࠦ᱘"),
            bstack11l111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᱙"): env.get(bstack11l111_opy_ (u"ࠨࡃࡐࡆࡈࡆ࡚ࡏࡌࡅࡡࡓ࡙ࡇࡒࡉࡄࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧᱚ")),
            bstack11l111_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᱛ"): env.get(bstack11l111_opy_ (u"ࠣࡅࡒࡈࡊࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡢࡍࡉࠨᱜ")),
            bstack11l111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᱝ"): env.get(bstack11l111_opy_ (u"ࠥࡇࡔࡊࡅࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠣᱞ"))
        }
    if env.get(bstack11l111_opy_ (u"ࠦࡧࡧ࡭ࡣࡱࡲࡣࡧࡻࡩ࡭ࡦࡑࡹࡲࡨࡥࡳࠤᱟ")):
        return {
            bstack11l111_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᱠ"): bstack11l111_opy_ (u"ࠨࡂࡢ࡯ࡥࡳࡴࠨᱡ"),
            bstack11l111_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᱢ"): env.get(bstack11l111_opy_ (u"ࠣࡤࡤࡱࡧࡵ࡯ࡠࡤࡸ࡭ࡱࡪࡒࡦࡵࡸࡰࡹࡹࡕࡳ࡮ࠥᱣ")),
            bstack11l111_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᱤ"): env.get(bstack11l111_opy_ (u"ࠥࡦࡦࡳࡢࡰࡱࡢࡷ࡭ࡵࡲࡵࡌࡲࡦࡓࡧ࡭ࡦࠤᱥ")),
            bstack11l111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᱦ"): env.get(bstack11l111_opy_ (u"ࠧࡨࡡ࡮ࡤࡲࡳࡤࡨࡵࡪ࡮ࡧࡒࡺࡳࡢࡦࡴࠥᱧ"))
        }
    if env.get(bstack11l111_opy_ (u"ࠨࡗࡆࡔࡆࡏࡊࡘࠢᱨ")) or env.get(bstack11l111_opy_ (u"ࠢࡘࡇࡕࡇࡐࡋࡒࡠࡏࡄࡍࡓࡥࡐࡊࡒࡈࡐࡎࡔࡅࡠࡕࡗࡅࡗ࡚ࡅࡅࠤᱩ")):
        return {
            bstack11l111_opy_ (u"ࠣࡰࡤࡱࡪࠨᱪ"): bstack11l111_opy_ (u"ࠤ࡚ࡩࡷࡩ࡫ࡦࡴࠥᱫ"),
            bstack11l111_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᱬ"): env.get(bstack11l111_opy_ (u"ࠦ࡜ࡋࡒࡄࡍࡈࡖࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣᱭ")),
            bstack11l111_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᱮ"): bstack11l111_opy_ (u"ࠨࡍࡢ࡫ࡱࠤࡕ࡯ࡰࡦ࡮࡬ࡲࡪࠨᱯ") if env.get(bstack11l111_opy_ (u"ࠢࡘࡇࡕࡇࡐࡋࡒࡠࡏࡄࡍࡓࡥࡐࡊࡒࡈࡐࡎࡔࡅࡠࡕࡗࡅࡗ࡚ࡅࡅࠤᱰ")) else None,
            bstack11l111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᱱ"): env.get(bstack11l111_opy_ (u"ࠤ࡚ࡉࡗࡉࡋࡆࡔࡢࡋࡎ࡚࡟ࡄࡑࡐࡑࡎ࡚ࠢᱲ"))
        }
    if any([env.get(bstack11l111_opy_ (u"ࠥࡋࡈࡖ࡟ࡑࡔࡒࡎࡊࡉࡔࠣᱳ")), env.get(bstack11l111_opy_ (u"ࠦࡌࡉࡌࡐࡗࡇࡣࡕࡘࡏࡋࡇࡆࡘࠧᱴ")), env.get(bstack11l111_opy_ (u"ࠧࡍࡏࡐࡉࡏࡉࡤࡉࡌࡐࡗࡇࡣࡕࡘࡏࡋࡇࡆࡘࠧᱵ"))]):
        return {
            bstack11l111_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᱶ"): bstack11l111_opy_ (u"ࠢࡈࡱࡲ࡫ࡱ࡫ࠠࡄ࡮ࡲࡹࡩࠨᱷ"),
            bstack11l111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᱸ"): None,
            bstack11l111_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᱹ"): env.get(bstack11l111_opy_ (u"ࠥࡔࡗࡕࡊࡆࡅࡗࡣࡎࡊࠢᱺ")),
            bstack11l111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᱻ"): env.get(bstack11l111_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡎࡊࠢᱼ"))
        }
    if env.get(bstack11l111_opy_ (u"ࠨࡓࡉࡋࡓࡔࡆࡈࡌࡆࠤᱽ")):
        return {
            bstack11l111_opy_ (u"ࠢ࡯ࡣࡰࡩࠧ᱾"): bstack11l111_opy_ (u"ࠣࡕ࡫࡭ࡵࡶࡡࡣ࡮ࡨࠦ᱿"),
            bstack11l111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᲀ"): env.get(bstack11l111_opy_ (u"ࠥࡗࡍࡏࡐࡑࡃࡅࡐࡊࡥࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤᲁ")),
            bstack11l111_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᲂ"): bstack11l111_opy_ (u"ࠧࡐ࡯ࡣࠢࠦࡿࢂࠨᲃ").format(env.get(bstack11l111_opy_ (u"࠭ࡓࡉࡋࡓࡔࡆࡈࡌࡆࡡࡍࡓࡇࡥࡉࡅࠩᲄ"))) if env.get(bstack11l111_opy_ (u"ࠢࡔࡊࡌࡔࡕࡇࡂࡍࡇࡢࡎࡔࡈ࡟ࡊࡆࠥᲅ")) else None,
            bstack11l111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᲆ"): env.get(bstack11l111_opy_ (u"ࠤࡖࡌࡎࡖࡐࡂࡄࡏࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᲇ"))
        }
    if bstack111ll1lll_opy_(env.get(bstack11l111_opy_ (u"ࠥࡒࡊ࡚ࡌࡊࡈ࡜ࠦᲈ"))):
        return {
            bstack11l111_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᲉ"): bstack11l111_opy_ (u"ࠧࡔࡥࡵ࡮࡬ࡪࡾࠨᲊ"),
            bstack11l111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᲋"): env.get(bstack11l111_opy_ (u"ࠢࡅࡇࡓࡐࡔ࡟࡟ࡖࡔࡏࠦ᲌")),
            bstack11l111_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥ᲍"): env.get(bstack11l111_opy_ (u"ࠤࡖࡍ࡙ࡋ࡟ࡏࡃࡐࡉࠧ᲎")),
            bstack11l111_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤ᲏"): env.get(bstack11l111_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡍࡉࠨᲐ"))
        }
    if bstack111ll1lll_opy_(env.get(bstack11l111_opy_ (u"ࠧࡍࡉࡕࡊࡘࡆࡤࡇࡃࡕࡋࡒࡒࡘࠨᲑ"))):
        return {
            bstack11l111_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᲒ"): bstack11l111_opy_ (u"ࠢࡈ࡫ࡷࡌࡺࡨࠠࡂࡥࡷ࡭ࡴࡴࡳࠣᲓ"),
            bstack11l111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᲔ"): bstack11l111_opy_ (u"ࠤࡾࢁ࠴ࢁࡽ࠰ࡣࡦࡸ࡮ࡵ࡮ࡴ࠱ࡵࡹࡳࡹ࠯ࡼࡿࠥᲕ").format(env.get(bstack11l111_opy_ (u"ࠪࡋࡎ࡚ࡈࡖࡄࡢࡗࡊࡘࡖࡆࡔࡢ࡙ࡗࡒࠧᲖ")), env.get(bstack11l111_opy_ (u"ࠫࡌࡏࡔࡉࡗࡅࡣࡗࡋࡐࡐࡕࡌࡘࡔࡘ࡙ࠨᲗ")), env.get(bstack11l111_opy_ (u"ࠬࡍࡉࡕࡊࡘࡆࡤࡘࡕࡏࡡࡌࡈࠬᲘ"))),
            bstack11l111_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᲙ"): env.get(bstack11l111_opy_ (u"ࠢࡈࡋࡗࡌ࡚ࡈ࡟ࡘࡑࡕࡏࡋࡒࡏࡘࠤᲚ")),
            bstack11l111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᲛ"): env.get(bstack11l111_opy_ (u"ࠤࡊࡍ࡙ࡎࡕࡃࡡࡕ࡙ࡓࡥࡉࡅࠤᲜ"))
        }
    if env.get(bstack11l111_opy_ (u"ࠥࡇࡎࠨᲝ")) == bstack11l111_opy_ (u"ࠦࡹࡸࡵࡦࠤᲞ") and env.get(bstack11l111_opy_ (u"ࠧ࡜ࡅࡓࡅࡈࡐࠧᲟ")) == bstack11l111_opy_ (u"ࠨ࠱ࠣᲠ"):
        return {
            bstack11l111_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᲡ"): bstack11l111_opy_ (u"ࠣࡘࡨࡶࡨ࡫࡬ࠣᲢ"),
            bstack11l111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᲣ"): bstack11l111_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲ࡿࢂࠨᲤ").format(env.get(bstack11l111_opy_ (u"࡛ࠫࡋࡒࡄࡇࡏࡣ࡚ࡘࡌࠨᲥ"))),
            bstack11l111_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᲦ"): None,
            bstack11l111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᲧ"): None,
        }
    if env.get(bstack11l111_opy_ (u"ࠢࡕࡇࡄࡑࡈࡏࡔ࡚ࡡ࡙ࡉࡗ࡙ࡉࡐࡐࠥᲨ")):
        return {
            bstack11l111_opy_ (u"ࠣࡰࡤࡱࡪࠨᲩ"): bstack11l111_opy_ (u"ࠤࡗࡩࡦࡳࡣࡪࡶࡼࠦᲪ"),
            bstack11l111_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᲫ"): None,
            bstack11l111_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᲬ"): env.get(bstack11l111_opy_ (u"࡚ࠧࡅࡂࡏࡆࡍ࡙࡟࡟ࡑࡔࡒࡎࡊࡉࡔࡠࡐࡄࡑࡊࠨᲭ")),
            bstack11l111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᲮ"): env.get(bstack11l111_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨᲯ"))
        }
    if any([env.get(bstack11l111_opy_ (u"ࠣࡅࡒࡒࡈࡕࡕࡓࡕࡈࠦᲰ")), env.get(bstack11l111_opy_ (u"ࠤࡆࡓࡓࡉࡏࡖࡔࡖࡉࡤ࡛ࡒࡍࠤᲱ")), env.get(bstack11l111_opy_ (u"ࠥࡇࡔࡔࡃࡐࡗࡕࡗࡊࡥࡕࡔࡇࡕࡒࡆࡓࡅࠣᲲ")), env.get(bstack11l111_opy_ (u"ࠦࡈࡕࡎࡄࡑࡘࡖࡘࡋ࡟ࡕࡇࡄࡑࠧᲳ"))]):
        return {
            bstack11l111_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᲴ"): bstack11l111_opy_ (u"ࠨࡃࡰࡰࡦࡳࡺࡸࡳࡦࠤᲵ"),
            bstack11l111_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᲶ"): None,
            bstack11l111_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᲷ"): env.get(bstack11l111_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡌࡒࡆࡤࡔࡁࡎࡇࠥᲸ")) or None,
            bstack11l111_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᲹ"): env.get(bstack11l111_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡍࡉࠨᲺ"), 0)
        }
    if env.get(bstack11l111_opy_ (u"ࠧࡍࡏࡠࡌࡒࡆࡤࡔࡁࡎࡇࠥ᲻")):
        return {
            bstack11l111_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦ᲼"): bstack11l111_opy_ (u"ࠢࡈࡱࡆࡈࠧᲽ"),
            bstack11l111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᲾ"): None,
            bstack11l111_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᲿ"): env.get(bstack11l111_opy_ (u"ࠥࡋࡔࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣ᳀")),
            bstack11l111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥ᳁"): env.get(bstack11l111_opy_ (u"ࠧࡍࡏࡠࡒࡌࡔࡊࡒࡉࡏࡇࡢࡇࡔ࡛ࡎࡕࡇࡕࠦ᳂"))
        }
    if env.get(bstack11l111_opy_ (u"ࠨࡃࡇࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠦ᳃")):
        return {
            bstack11l111_opy_ (u"ࠢ࡯ࡣࡰࡩࠧ᳄"): bstack11l111_opy_ (u"ࠣࡅࡲࡨࡪࡌࡲࡦࡵ࡫ࠦ᳅"),
            bstack11l111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧ᳆"): env.get(bstack11l111_opy_ (u"ࠥࡇࡋࡥࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤ᳇")),
            bstack11l111_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ᳈"): env.get(bstack11l111_opy_ (u"ࠧࡉࡆࡠࡒࡌࡔࡊࡒࡉࡏࡇࡢࡒࡆࡓࡅࠣ᳉")),
            bstack11l111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧ᳊"): env.get(bstack11l111_opy_ (u"ࠢࡄࡈࡢࡆ࡚ࡏࡌࡅࡡࡌࡈࠧ᳋"))
        }
    return {bstack11l111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢ᳌"): None}
def get_host_info():
    return {
        bstack11l111_opy_ (u"ࠤ࡫ࡳࡸࡺ࡮ࡢ࡯ࡨࠦ᳍"): platform.node(),
        bstack11l111_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࠧ᳎"): platform.system(),
        bstack11l111_opy_ (u"ࠦࡹࡿࡰࡦࠤ᳏"): platform.machine(),
        bstack11l111_opy_ (u"ࠧࡼࡥࡳࡵ࡬ࡳࡳࠨ᳐"): platform.version(),
        bstack11l111_opy_ (u"ࠨࡡࡳࡥ࡫ࠦ᳑"): platform.architecture()[0]
    }
def bstack1l1lll1l1_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack111llll1111_opy_():
    if bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠨ᳒")):
        return bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ᳓")
    return bstack11l111_opy_ (u"ࠩࡸࡲࡰࡴ࡯ࡸࡰࡢ࡫ࡷ࡯ࡤࠨ᳔")
def bstack111ll111lll_opy_(driver):
    info = {
        bstack11l111_opy_ (u"ࠪࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴ᳕ࠩ"): driver.capabilities,
        bstack11l111_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡤ࡯ࡤࠨ᳖"): driver.session_id,
        bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ᳗࠭"): driver.capabilities.get(bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨ᳘ࠫ"), None),
        bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯᳙ࠩ"): driver.capabilities.get(bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩ᳚"), None),
        bstack11l111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࠫ᳛"): driver.capabilities.get(bstack11l111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦ᳜ࠩ"), None),
        bstack11l111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡥࡶࡦࡴࡶ࡭ࡴࡴ᳝ࠧ"):driver.capabilities.get(bstack11l111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴ᳞ࠧ"), None),
    }
    if bstack111llll1111_opy_() == bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯᳟ࠬ"):
        if bstack1l1l111lll_opy_():
            info[bstack11l111_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࠨ᳠")] = bstack11l111_opy_ (u"ࠨࡣࡳࡴ࠲ࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ᳡")
        elif driver.capabilities.get(bstack11l111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵ᳢ࠪ"), {}).get(bstack11l111_opy_ (u"ࠪࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫᳣ࠧ"), False):
            info[bstack11l111_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸ᳤ࠬ")] = bstack11l111_opy_ (u"ࠬࡺࡵࡳࡤࡲࡷࡨࡧ࡬ࡦ᳥ࠩ")
        else:
            info[bstack11l111_opy_ (u"࠭ࡰࡳࡱࡧࡹࡨࡺ᳦ࠧ")] = bstack11l111_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡦ᳧ࠩ")
    return info
def bstack1l1l111lll_opy_():
    if bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠨࡣࡳࡴࡤࡧࡵࡵࡱࡰࡥࡹ࡫᳨ࠧ")):
        return True
    if bstack111ll1lll_opy_(os.environ.get(bstack11l111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡋࡖࡣࡆࡖࡐࡠࡃࡘࡘࡔࡓࡁࡕࡇࠪᳩ"), None)):
        return True
    return False
def bstack111lllll1l_opy_(bstack111llll1lll_opy_, url, data, config):
    headers = config.get(bstack11l111_opy_ (u"ࠪ࡬ࡪࡧࡤࡦࡴࡶࠫᳪ"), None)
    proxies = bstack11111llll_opy_(config, url)
    auth = config.get(bstack11l111_opy_ (u"ࠫࡦࡻࡴࡩࠩᳫ"), None)
    response = requests.request(
            bstack111llll1lll_opy_,
            url=url,
            headers=headers,
            auth=auth,
            json=data,
            proxies=proxies
        )
    return response
def bstack1l11l1ll11_opy_(bstack1lllll1lll_opy_, size):
    bstack1l1lll11l1_opy_ = []
    while len(bstack1lllll1lll_opy_) > size:
        bstack1lll1lllll_opy_ = bstack1lllll1lll_opy_[:size]
        bstack1l1lll11l1_opy_.append(bstack1lll1lllll_opy_)
        bstack1lllll1lll_opy_ = bstack1lllll1lll_opy_[size:]
    bstack1l1lll11l1_opy_.append(bstack1lllll1lll_opy_)
    return bstack1l1lll11l1_opy_
def bstack11l111111ll_opy_(message, bstack111lllllll1_opy_=False):
    os.write(1, bytes(message, bstack11l111_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᳬ")))
    os.write(1, bytes(bstack11l111_opy_ (u"࠭࡜࡯᳭ࠩ"), bstack11l111_opy_ (u"ࠧࡶࡶࡩ࠱࠽࠭ᳮ")))
    if bstack111lllllll1_opy_:
        with open(bstack11l111_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠮ࡱ࠴࠵ࡾ࠳ࠧᳯ") + os.environ[bstack11l111_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡂࡖࡋࡏࡈࡤࡎࡁࡔࡊࡈࡈࡤࡏࡄࠨᳰ")] + bstack11l111_opy_ (u"ࠪ࠲ࡱࡵࡧࠨᳱ"), bstack11l111_opy_ (u"ࠫࡦ࠭ᳲ")) as f:
            f.write(message + bstack11l111_opy_ (u"ࠬࡢ࡮ࠨᳳ"))
def bstack1l1l1l1l1ll_opy_():
    return os.environ[bstack11l111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡕࡕࡑࡐࡅ࡙ࡏࡏࡏࠩ᳴")].lower() == bstack11l111_opy_ (u"ࠧࡵࡴࡸࡩࠬᳵ")
def bstack1l11ll11l_opy_():
    return bstack111l11ll1l_opy_().replace(tzinfo=None).isoformat() + bstack11l111_opy_ (u"ࠨ࡜ࠪᳶ")
def bstack111l1ll1lll_opy_(start, finish):
    return (datetime.datetime.fromisoformat(finish.rstrip(bstack11l111_opy_ (u"ࠩ࡝ࠫ᳷"))) - datetime.datetime.fromisoformat(start.rstrip(bstack11l111_opy_ (u"ࠪ࡞ࠬ᳸")))).total_seconds() * 1000
def bstack11l11l111ll_opy_(timestamp):
    return bstack11l1111l11l_opy_(timestamp).isoformat() + bstack11l111_opy_ (u"ࠫ࡟࠭᳹")
def bstack11l11l11111_opy_(bstack111lll11lll_opy_):
    date_format = bstack11l111_opy_ (u"࡙ࠬࠫࠦ࡯ࠨࡨࠥࠫࡈ࠻ࠧࡐ࠾࡙ࠪ࠮ࠦࡨࠪᳺ")
    bstack111l1llllll_opy_ = datetime.datetime.strptime(bstack111lll11lll_opy_, date_format)
    return bstack111l1llllll_opy_.isoformat() + bstack11l111_opy_ (u"࡚࠭ࠨ᳻")
def bstack11l11l11lll_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack11l111_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ᳼")
    else:
        return bstack11l111_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨ᳽")
def bstack111ll1lll_opy_(val):
    if val is None:
        return False
    return val.__str__().lower() == bstack11l111_opy_ (u"ࠩࡷࡶࡺ࡫ࠧ᳾")
def bstack11l11111l1l_opy_(val):
    return val.__str__().lower() == bstack11l111_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩ᳿")
def error_handler(bstack11l1111l111_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack11l1111l111_opy_ as e:
                print(bstack11l111_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡪࡺࡴࡣࡵ࡫ࡲࡲࠥࢁࡽࠡ࠯ࡁࠤࢀࢃ࠺ࠡࡽࢀࠦᴀ").format(func.__name__, bstack11l1111l111_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack111llllllll_opy_(bstack11l1111lll1_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack11l1111lll1_opy_(cls, *args, **kwargs)
            except bstack11l1111l111_opy_ as e:
                print(bstack11l111_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠦࡻࡾࠢ࠰ࡂࠥࢁࡽ࠻ࠢࡾࢁࠧᴁ").format(bstack11l1111lll1_opy_.__name__, bstack11l1111l111_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack111llllllll_opy_
    else:
        return decorator
def bstack11l11l1l1l_opy_(bstack11111l1ll1_opy_):
    if os.getenv(bstack11l111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡕࡕࡑࡐࡅ࡙ࡏࡏࡏࠩᴂ")) is not None:
        return bstack111ll1lll_opy_(os.getenv(bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࠪᴃ")))
    if bstack11l111_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᴄ") in bstack11111l1ll1_opy_ and bstack11l11111l1l_opy_(bstack11111l1ll1_opy_[bstack11l111_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᴅ")]):
        return False
    if bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᴆ") in bstack11111l1ll1_opy_ and bstack11l11111l1l_opy_(bstack11111l1ll1_opy_[bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᴇ")]):
        return False
    return True
def bstack1lll1ll111_opy_():
    try:
        from pytest_bdd import reporting
        bstack11l11l1l11l_opy_ = os.environ.get(bstack11l111_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡚࡙ࡅࡓࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠧᴈ"), None)
        return bstack11l11l1l11l_opy_ is None or bstack11l11l1l11l_opy_ == bstack11l111_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠥᴉ")
    except Exception as e:
        return False
def bstack1ll1ll1l1_opy_(hub_url, CONFIG):
    if bstack1lllll1l1_opy_() <= version.parse(bstack11l111_opy_ (u"ࠧ࠴࠰࠴࠷࠳࠶ࠧᴊ")):
        if hub_url:
            return bstack11l111_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤᴋ") + hub_url + bstack11l111_opy_ (u"ࠤ࠽࠼࠵࠵ࡷࡥ࠱࡫ࡹࡧࠨᴌ")
        return bstack1ll1l1ll11_opy_
    if hub_url:
        return bstack11l111_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳ࠧᴍ") + hub_url + bstack11l111_opy_ (u"ࠦ࠴ࡽࡤ࠰ࡪࡸࡦࠧᴎ")
    return bstack1l111l11l_opy_
def bstack11l111ll111_opy_():
    return isinstance(os.getenv(bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕ࡟ࡔࡆࡕࡗࡣࡕࡒࡕࡈࡋࡑࠫᴏ")), str)
def bstack1l1ll1l1_opy_(url):
    return urlparse(url).hostname
def bstack11l11l1l1_opy_(hostname):
    for bstack111llllll_opy_ in bstack1l111ll1l_opy_:
        regex = re.compile(bstack111llllll_opy_)
        if regex.match(hostname):
            return True
    return False
def bstack111lllll111_opy_(bstack111lll1ll1l_opy_, file_name, logger):
    bstack1ll11l1ll_opy_ = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"࠭ࡾࠨᴐ")), bstack111lll1ll1l_opy_)
    try:
        if not os.path.exists(bstack1ll11l1ll_opy_):
            os.makedirs(bstack1ll11l1ll_opy_)
        file_path = os.path.join(os.path.expanduser(bstack11l111_opy_ (u"ࠧࡿࠩᴑ")), bstack111lll1ll1l_opy_, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, bstack11l111_opy_ (u"ࠨࡹࠪᴒ")):
                pass
            with open(file_path, bstack11l111_opy_ (u"ࠤࡺ࠯ࠧᴓ")) as outfile:
                json.dump({}, outfile)
        return file_path
    except Exception as e:
        logger.debug(bstack11lll11l_opy_.format(str(e)))
def bstack111lll1llll_opy_(file_name, key, value, logger):
    file_path = bstack111lllll111_opy_(bstack11l111_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪᴔ"), file_name, logger)
    if file_path != None:
        if os.path.exists(file_path):
            bstack111l1l1l1_opy_ = json.load(open(file_path, bstack11l111_opy_ (u"ࠫࡷࡨࠧᴕ")))
        else:
            bstack111l1l1l1_opy_ = {}
        bstack111l1l1l1_opy_[key] = value
        with open(file_path, bstack11l111_opy_ (u"ࠧࡽࠫࠣᴖ")) as outfile:
            json.dump(bstack111l1l1l1_opy_, outfile)
def bstack1ll1lll11l_opy_(file_name, logger):
    file_path = bstack111lllll111_opy_(bstack11l111_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ᴗ"), file_name, logger)
    bstack111l1l1l1_opy_ = {}
    if file_path != None and os.path.exists(file_path):
        with open(file_path, bstack11l111_opy_ (u"ࠧࡳࠩᴘ")) as bstack11l1ll11ll_opy_:
            bstack111l1l1l1_opy_ = json.load(bstack11l1ll11ll_opy_)
    return bstack111l1l1l1_opy_
def bstack11l11lll11_opy_(file_path, logger):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.debug(bstack11l111_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡨࡪࡲࡥࡵ࡫ࡱ࡫ࠥ࡬ࡩ࡭ࡧ࠽ࠤࠬᴙ") + file_path + bstack11l111_opy_ (u"ࠩࠣࠫᴚ") + str(e))
def bstack1lllll1l1_opy_():
    from selenium import webdriver
    return version.parse(webdriver.__version__)
class Notset:
    def __repr__(self):
        return bstack11l111_opy_ (u"ࠥࡀࡓࡕࡔࡔࡇࡗࡂࠧᴛ")
def bstack11l1lll1ll_opy_(config):
    if bstack11l111_opy_ (u"ࠫ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪᴜ") in config:
        del (config[bstack11l111_opy_ (u"ࠬ࡯ࡳࡑ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠫᴝ")])
        return False
    if bstack1lllll1l1_opy_() < version.parse(bstack11l111_opy_ (u"࠭࠳࠯࠶࠱࠴ࠬᴞ")):
        return False
    if bstack1lllll1l1_opy_() >= version.parse(bstack11l111_opy_ (u"ࠧ࠵࠰࠴࠲࠺࠭ᴟ")):
        return True
    if bstack11l111_opy_ (u"ࠨࡷࡶࡩ࡜࠹ࡃࠨᴠ") in config and config[bstack11l111_opy_ (u"ࠩࡸࡷࡪ࡝࠳ࡄࠩᴡ")] is False:
        return False
    else:
        return True
def bstack11llll1l_opy_(args_list, bstack11l1111ll11_opy_):
    index = -1
    for value in bstack11l1111ll11_opy_:
        try:
            index = args_list.index(value)
            return index
        except Exception as e:
            return index
    return index
def bstack11ll1l11l1l_opy_(a, b):
  for k, v in b.items():
    if isinstance(v, dict) and k in a and isinstance(a[k], dict):
        bstack11ll1l11l1l_opy_(a[k], v)
    else:
        a[k] = v
class Result:
    def __init__(self, result=None, duration=None, exception=None, bstack111l1ll111_opy_=None):
        self.result = result
        self.duration = duration
        self.exception = exception
        self.exception_type = type(self.exception).__name__ if exception else None
        self.bstack111l1ll111_opy_ = bstack111l1ll111_opy_
    @classmethod
    def passed(cls):
        return Result(result=bstack11l111_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪᴢ"))
    @classmethod
    def failed(cls, exception=None):
        return Result(result=bstack11l111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᴣ"), exception=exception)
    def bstack1llllll1lll_opy_(self):
        if self.result != bstack11l111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬᴤ"):
            return None
        if isinstance(self.exception_type, str) and bstack11l111_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࠤᴥ") in self.exception_type:
            return bstack11l111_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࡈࡶࡷࡵࡲࠣᴦ")
        return bstack11l111_opy_ (u"ࠣࡗࡱ࡬ࡦࡴࡤ࡭ࡧࡧࡉࡷࡸ࡯ࡳࠤᴧ")
    def bstack111ll1l11l1_opy_(self):
        if self.result != bstack11l111_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩᴨ"):
            return None
        if self.bstack111l1ll111_opy_:
            return self.bstack111l1ll111_opy_
        return bstack111lllll11l_opy_(self.exception)
def bstack111lllll11l_opy_(exc):
    return [traceback.format_exception(exc)]
def bstack11l111ll11l_opy_(message):
    if isinstance(message, str):
        return not bool(message and message.strip())
    return True
def bstack1l11lll1l1_opy_(object, key, default_value):
    if not object or not object.__dict__:
        return default_value
    if key in object.__dict__.keys():
        return object.__dict__.get(key)
    return default_value
def bstack11llll111_opy_(config, logger):
    try:
        import playwright
        bstack11l11111ll1_opy_ = playwright.__file__
        bstack111llllll1l_opy_ = os.path.split(bstack11l11111ll1_opy_)
        bstack11l1111llll_opy_ = bstack111llllll1l_opy_[0] + bstack11l111_opy_ (u"ࠪ࠳ࡩࡸࡩࡷࡧࡵ࠳ࡵࡧࡣ࡬ࡣࡪࡩ࠴ࡲࡩࡣ࠱ࡦࡰ࡮࠵ࡣ࡭࡫࠱࡮ࡸ࠭ᴩ")
        os.environ[bstack11l111_opy_ (u"ࠫࡌࡒࡏࡃࡃࡏࡣࡆࡍࡅࡏࡖࡢࡌ࡙࡚ࡐࡠࡒࡕࡓ࡝࡟ࠧᴪ")] = bstack1lll111lll_opy_(config)
        with open(bstack11l1111llll_opy_, bstack11l111_opy_ (u"ࠬࡸࠧᴫ")) as f:
            bstack11ll11l1l1_opy_ = f.read()
            bstack111l1lll111_opy_ = bstack11l111_opy_ (u"࠭ࡧ࡭ࡱࡥࡥࡱ࠳ࡡࡨࡧࡱࡸࠬᴬ")
            bstack111lll11ll1_opy_ = bstack11ll11l1l1_opy_.find(bstack111l1lll111_opy_)
            if bstack111lll11ll1_opy_ == -1:
              process = subprocess.Popen(bstack11l111_opy_ (u"ࠢ࡯ࡲࡰࠤ࡮ࡴࡳࡵࡣ࡯ࡰࠥ࡭࡬ࡰࡤࡤࡰ࠲ࡧࡧࡦࡰࡷࠦᴭ"), shell=True, cwd=bstack111llllll1l_opy_[0])
              process.wait()
              bstack11l111l11l1_opy_ = bstack11l111_opy_ (u"ࠨࠤࡸࡷࡪࠦࡳࡵࡴ࡬ࡧࡹࠨ࠻ࠨᴮ")
              bstack111llll11l1_opy_ = bstack11l111_opy_ (u"ࠤࠥࠦࠥࡢࠢࡶࡵࡨࠤࡸࡺࡲࡪࡥࡷࡠࠧࡁࠠࡤࡱࡱࡷࡹࠦࡻࠡࡤࡲࡳࡹࡹࡴࡳࡣࡳࠤࢂࠦ࠽ࠡࡴࡨࡵࡺ࡯ࡲࡦࠪࠪ࡫ࡱࡵࡢࡢ࡮࠰ࡥ࡬࡫࡮ࡵࠩࠬ࠿ࠥ࡯ࡦࠡࠪࡳࡶࡴࡩࡥࡴࡵ࠱ࡩࡳࡼ࠮ࡈࡎࡒࡆࡆࡒ࡟ࡂࡉࡈࡒ࡙ࡥࡈࡕࡖࡓࡣࡕࡘࡏ࡙࡛ࠬࠤࡧࡵ࡯ࡵࡵࡷࡶࡦࡶࠨࠪ࠽ࠣࠦࠧࠨᴯ")
              bstack11l111lll1l_opy_ = bstack11ll11l1l1_opy_.replace(bstack11l111l11l1_opy_, bstack111llll11l1_opy_)
              with open(bstack11l1111llll_opy_, bstack11l111_opy_ (u"ࠪࡻࠬᴰ")) as f:
                f.write(bstack11l111lll1l_opy_)
    except Exception as e:
        logger.error(bstack1lll1l111l_opy_.format(str(e)))
def bstack1ll1l1111_opy_():
  try:
    bstack111ll111ll1_opy_ = os.path.join(tempfile.gettempdir(), bstack11l111_opy_ (u"ࠫࡴࡶࡴࡪ࡯ࡤࡰࡤ࡮ࡵࡣࡡࡸࡶࡱ࠴ࡪࡴࡱࡱࠫᴱ"))
    bstack111ll1llll1_opy_ = []
    if os.path.exists(bstack111ll111ll1_opy_):
      with open(bstack111ll111ll1_opy_) as f:
        bstack111ll1llll1_opy_ = json.load(f)
      os.remove(bstack111ll111ll1_opy_)
    return bstack111ll1llll1_opy_
  except:
    pass
  return []
def bstack1lll1ll1l_opy_(bstack1llll1111l_opy_):
  try:
    bstack111ll1llll1_opy_ = []
    bstack111ll111ll1_opy_ = os.path.join(tempfile.gettempdir(), bstack11l111_opy_ (u"ࠬࡵࡰࡵ࡫ࡰࡥࡱࡥࡨࡶࡤࡢࡹࡷࡲ࠮࡫ࡵࡲࡲࠬᴲ"))
    if os.path.exists(bstack111ll111ll1_opy_):
      with open(bstack111ll111ll1_opy_) as f:
        bstack111ll1llll1_opy_ = json.load(f)
    bstack111ll1llll1_opy_.append(bstack1llll1111l_opy_)
    with open(bstack111ll111ll1_opy_, bstack11l111_opy_ (u"࠭ࡷࠨᴳ")) as f:
        json.dump(bstack111ll1llll1_opy_, f)
  except:
    pass
def bstack1l1111ll_opy_(logger, bstack111ll1l1ll1_opy_ = False):
  try:
    test_name = os.environ.get(bstack11l111_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚࡟ࡕࡇࡖࡘࡤࡔࡁࡎࡇࠪᴴ"), bstack11l111_opy_ (u"ࠨࠩᴵ"))
    if test_name == bstack11l111_opy_ (u"ࠩࠪᴶ"):
        test_name = threading.current_thread().__dict__.get(bstack11l111_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࡅࡨࡩࡥࡴࡦࡵࡷࡣࡳࡧ࡭ࡦࠩᴷ"), bstack11l111_opy_ (u"ࠫࠬᴸ"))
    bstack111l1lllll1_opy_ = bstack11l111_opy_ (u"ࠬ࠲ࠠࠨᴹ").join(threading.current_thread().bstackTestErrorMessages)
    if bstack111ll1l1ll1_opy_:
        bstack1l111ll1ll_opy_ = os.environ.get(bstack11l111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ᴺ"), bstack11l111_opy_ (u"ࠧ࠱ࠩᴻ"))
        bstack1ll11l11ll_opy_ = {bstack11l111_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᴼ"): test_name, bstack11l111_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨᴽ"): bstack111l1lllll1_opy_, bstack11l111_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩᴾ"): bstack1l111ll1ll_opy_}
        bstack111lll1111l_opy_ = []
        bstack11l111l1l11_opy_ = os.path.join(tempfile.gettempdir(), bstack11l111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡵࡶࡰࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸ࠳ࡰࡳࡰࡰࠪᴿ"))
        if os.path.exists(bstack11l111l1l11_opy_):
            with open(bstack11l111l1l11_opy_) as f:
                bstack111lll1111l_opy_ = json.load(f)
        bstack111lll1111l_opy_.append(bstack1ll11l11ll_opy_)
        with open(bstack11l111l1l11_opy_, bstack11l111_opy_ (u"ࠬࡽࠧᵀ")) as f:
            json.dump(bstack111lll1111l_opy_, f)
    else:
        bstack1ll11l11ll_opy_ = {bstack11l111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᵁ"): test_name, bstack11l111_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ᵂ"): bstack111l1lllll1_opy_, bstack11l111_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧᵃ"): str(multiprocessing.current_process().name)}
        if bstack11l111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠭ᵄ") not in multiprocessing.current_process().__dict__.keys():
            multiprocessing.current_process().bstack_error_list = []
        multiprocessing.current_process().bstack_error_list.append(bstack1ll11l11ll_opy_)
  except Exception as e:
      logger.warn(bstack11l111_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡵࡱࡵࡩࠥࡶࡹࡵࡧࡶࡸࠥ࡬ࡵ࡯ࡰࡨࡰࠥࡪࡡࡵࡣ࠽ࠤࢀࢃࠢᵅ").format(e))
def bstack11ll11ll1l_opy_(error_message, test_name, index, logger):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack11l111_opy_ (u"ࠫ࡫࡯࡬ࡦ࡮ࡲࡧࡰࠦ࡮ࡰࡶࠣࡥࡻࡧࡩ࡭ࡣࡥࡰࡪ࠲ࠠࡶࡵ࡬ࡲ࡬ࠦࡢࡢࡵ࡬ࡧࠥ࡬ࡩ࡭ࡧࠣࡳࡵ࡫ࡲࡢࡶ࡬ࡳࡳࡹࠧᵆ"))
    try:
      bstack11l1111l1ll_opy_ = []
      bstack1ll11l11ll_opy_ = {bstack11l111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᵇ"): test_name, bstack11l111_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᵈ"): error_message, bstack11l111_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ᵉ"): index}
      bstack111lll1l1ll_opy_ = os.path.join(tempfile.gettempdir(), bstack11l111_opy_ (u"ࠨࡴࡲࡦࡴࡺ࡟ࡦࡴࡵࡳࡷࡥ࡬ࡪࡵࡷ࠲࡯ࡹ࡯࡯ࠩᵊ"))
      if os.path.exists(bstack111lll1l1ll_opy_):
          with open(bstack111lll1l1ll_opy_) as f:
              bstack11l1111l1ll_opy_ = json.load(f)
      bstack11l1111l1ll_opy_.append(bstack1ll11l11ll_opy_)
      with open(bstack111lll1l1ll_opy_, bstack11l111_opy_ (u"ࠩࡺࠫᵋ")) as f:
          json.dump(bstack11l1111l1ll_opy_, f)
    except Exception as e:
      logger.warn(bstack11l111_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡵࡱࡵࡩࠥࡸ࡯ࡣࡱࡷࠤ࡫ࡻ࡮࡯ࡧ࡯ࠤࡩࡧࡴࡢ࠼ࠣࡿࢂࠨᵌ").format(e))
    return
  bstack11l1111l1ll_opy_ = []
  bstack1ll11l11ll_opy_ = {bstack11l111_opy_ (u"ࠫࡳࡧ࡭ࡦࠩᵍ"): test_name, bstack11l111_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫᵎ"): error_message, bstack11l111_opy_ (u"࠭ࡩ࡯ࡦࡨࡼࠬᵏ"): index}
  bstack111lll1l1ll_opy_ = os.path.join(tempfile.gettempdir(), bstack11l111_opy_ (u"ࠧࡳࡱࡥࡳࡹࡥࡥࡳࡴࡲࡶࡤࡲࡩࡴࡶ࠱࡮ࡸࡵ࡮ࠨᵐ"))
  lock_file = bstack111lll1l1ll_opy_ + bstack11l111_opy_ (u"ࠨ࠰࡯ࡳࡨࡱࠧᵑ")
  try:
    with FileLock(lock_file, timeout=10):
      if os.path.exists(bstack111lll1l1ll_opy_):
          with open(bstack111lll1l1ll_opy_, bstack11l111_opy_ (u"ࠩࡵࠫᵒ")) as f:
              content = f.read().strip()
              if content:
                  bstack11l1111l1ll_opy_ = json.load(open(bstack111lll1l1ll_opy_))
      bstack11l1111l1ll_opy_.append(bstack1ll11l11ll_opy_)
      with open(bstack111lll1l1ll_opy_, bstack11l111_opy_ (u"ࠪࡻࠬᵓ")) as f:
          json.dump(bstack11l1111l1ll_opy_, f)
  except Exception as e:
    logger.warn(bstack11l111_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡶࡲࡶࡪࠦࡲࡰࡤࡲࡸࠥ࡬ࡵ࡯ࡰࡨࡰࠥࡪࡡࡵࡣࠣࡻ࡮ࡺࡨࠡࡨ࡬ࡰࡪࠦ࡬ࡰࡥ࡮࡭ࡳ࡭࠺ࠡࡽࢀࠦᵔ").format(e))
def bstack1ll11l1l_opy_(bstack11l1111l1l_opy_, name, logger):
  try:
    bstack1ll11l11ll_opy_ = {bstack11l111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᵕ"): name, bstack11l111_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᵖ"): bstack11l1111l1l_opy_, bstack11l111_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ᵗ"): str(threading.current_thread()._name)}
    return bstack1ll11l11ll_opy_
  except Exception as e:
    logger.warn(bstack11l111_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡺ࡯ࡳࡧࠣࡦࡪ࡮ࡡࡷࡧࠣࡪࡺࡴ࡮ࡦ࡮ࠣࡨࡦࡺࡡ࠻ࠢࡾࢁࠧᵘ").format(e))
  return
def bstack111ll1l1l11_opy_():
    return platform.system() == bstack11l111_opy_ (u"࡚ࠩ࡭ࡳࡪ࡯ࡸࡵࠪᵙ")
def bstack1l1ll1l1l1_opy_(bstack11l1111ll1l_opy_, config, logger):
    bstack111lll1lll1_opy_ = {}
    try:
        return {key: config[key] for key in config if bstack11l1111ll1l_opy_.match(key)}
    except Exception as e:
        logger.debug(bstack11l111_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡦࡪ࡮ࡷࡩࡷࠦࡣࡰࡰࡩ࡭࡬ࠦ࡫ࡦࡻࡶࠤࡧࡿࠠࡳࡧࡪࡩࡽࠦ࡭ࡢࡶࡦ࡬࠿ࠦࡻࡾࠤᵚ").format(e))
    return bstack111lll1lll1_opy_
def bstack11l111l11ll_opy_(bstack11l11l11ll1_opy_, bstack11l1111111l_opy_):
    bstack111llllll11_opy_ = version.parse(bstack11l11l11ll1_opy_)
    bstack111lll111ll_opy_ = version.parse(bstack11l1111111l_opy_)
    if bstack111llllll11_opy_ > bstack111lll111ll_opy_:
        return 1
    elif bstack111llllll11_opy_ < bstack111lll111ll_opy_:
        return -1
    else:
        return 0
def bstack111l11ll1l_opy_():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def bstack11l1111l11l_opy_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(tzinfo=None)
def bstack111ll11l111_opy_(framework):
    from browserstack_sdk._version import __version__
    return str(framework) + str(__version__)
def bstack11111l11l_opy_(options, framework, config, bstack11l11lll1l_opy_={}):
    if options is None:
        return
    if getattr(options, bstack11l111_opy_ (u"ࠫ࡬࡫ࡴࠨᵛ"), None):
        caps = options
    else:
        caps = options.to_capabilities()
    bstack1l1111l1l_opy_ = caps.get(bstack11l111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭ᵜ"))
    bstack111ll1ll111_opy_ = True
    bstack11ll11111_opy_ = os.environ[bstack11l111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᵝ")]
    bstack1l1llll1l1l_opy_ = config.get(bstack11l111_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᵞ"), False)
    if bstack1l1llll1l1l_opy_:
        bstack1lll11ll11l_opy_ = config.get(bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨᵟ"), {})
        bstack1lll11ll11l_opy_[bstack11l111_opy_ (u"ࠩࡤࡹࡹ࡮ࡔࡰ࡭ࡨࡲࠬᵠ")] = os.getenv(bstack11l111_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨᵡ"))
        bstack11ll111llll_opy_ = json.loads(os.getenv(bstack11l111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬᵢ"), bstack11l111_opy_ (u"ࠬࢁࡽࠨᵣ"))).get(bstack11l111_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᵤ"))
    if bstack11l11111l1l_opy_(caps.get(bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡵࡴࡧ࡚࠷ࡈ࠭ᵥ"))) or bstack11l11111l1l_opy_(caps.get(bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡶࡵࡨࡣࡼ࠹ࡣࠨᵦ"))):
        bstack111ll1ll111_opy_ = False
    if bstack11l1lll1ll_opy_({bstack11l111_opy_ (u"ࠤࡸࡷࡪ࡝࠳ࡄࠤᵧ"): bstack111ll1ll111_opy_}):
        bstack1l1111l1l_opy_ = bstack1l1111l1l_opy_ or {}
        bstack1l1111l1l_opy_[bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬᵨ")] = bstack111ll11l111_opy_(framework)
        bstack1l1111l1l_opy_[bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᵩ")] = bstack1l1l1l1l1ll_opy_()
        bstack1l1111l1l_opy_[bstack11l111_opy_ (u"ࠬࡺࡥࡴࡶ࡫ࡹࡧࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨᵪ")] = bstack11ll11111_opy_
        bstack1l1111l1l_opy_[bstack11l111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡕࡸ࡯ࡥࡷࡦࡸࡒࡧࡰࠨᵫ")] = bstack11l11lll1l_opy_
        if bstack1l1llll1l1l_opy_:
            bstack1l1111l1l_opy_[bstack11l111_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᵬ")] = bstack1l1llll1l1l_opy_
            bstack1l1111l1l_opy_[bstack11l111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨᵭ")] = bstack1lll11ll11l_opy_
            bstack1l1111l1l_opy_[bstack11l111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᵮ")][bstack11l111_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᵯ")] = bstack11ll111llll_opy_
        if getattr(options, bstack11l111_opy_ (u"ࠫࡸ࡫ࡴࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷࡽࠬᵰ"), None):
            options.set_capability(bstack11l111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭ᵱ"), bstack1l1111l1l_opy_)
        else:
            options[bstack11l111_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᵲ")] = bstack1l1111l1l_opy_
    else:
        if getattr(options, bstack11l111_opy_ (u"ࠧࡴࡧࡷࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡹࠨᵳ"), None):
            options.set_capability(bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩᵴ"), bstack111ll11l111_opy_(framework))
            options.set_capability(bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᵵ"), bstack1l1l1l1l1ll_opy_())
            options.set_capability(bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡷࡩࡸࡺࡨࡶࡤࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬᵶ"), bstack11ll11111_opy_)
            options.set_capability(bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡺ࡯࡬ࡥࡒࡵࡳࡩࡻࡣࡵࡏࡤࡴࠬᵷ"), bstack11l11lll1l_opy_)
            if bstack1l1llll1l1l_opy_:
                options.set_capability(bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᵸ"), bstack1l1llll1l1l_opy_)
                options.set_capability(bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᵹ"), bstack1lll11ll11l_opy_)
                options.set_capability(bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠴ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᵺ"), bstack11ll111llll_opy_)
        else:
            options[bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩᵻ")] = bstack111ll11l111_opy_(framework)
            options[bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᵼ")] = bstack1l1l1l1l1ll_opy_()
            options[bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡷࡩࡸࡺࡨࡶࡤࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬᵽ")] = bstack11ll11111_opy_
            options[bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡺ࡯࡬ࡥࡒࡵࡳࡩࡻࡣࡵࡏࡤࡴࠬᵾ")] = bstack11l11lll1l_opy_
            if bstack1l1llll1l1l_opy_:
                options[bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᵿ")] = bstack1l1llll1l1l_opy_
                options[bstack11l111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᶀ")] = bstack1lll11ll11l_opy_
                options[bstack11l111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᶁ")][bstack11l111_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᶂ")] = bstack11ll111llll_opy_
    return options
def bstack11l111l1111_opy_(bstack111ll11lll1_opy_, framework):
    bstack11l11lll1l_opy_ = bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠤࡓࡐࡆ࡟ࡗࡓࡋࡊࡌ࡙ࡥࡐࡓࡑࡇ࡙ࡈ࡚࡟ࡎࡃࡓࠦᶃ"))
    if bstack111ll11lll1_opy_ and len(bstack111ll11lll1_opy_.split(bstack11l111_opy_ (u"ࠪࡧࡦࡶࡳ࠾ࠩᶄ"))) > 1:
        ws_url = bstack111ll11lll1_opy_.split(bstack11l111_opy_ (u"ࠫࡨࡧࡰࡴ࠿ࠪᶅ"))[0]
        if bstack11l111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭ࠨᶆ") in ws_url:
            from browserstack_sdk._version import __version__
            bstack111llll1ll1_opy_ = json.loads(urllib.parse.unquote(bstack111ll11lll1_opy_.split(bstack11l111_opy_ (u"࠭ࡣࡢࡲࡶࡁࠬᶇ"))[1]))
            bstack111llll1ll1_opy_ = bstack111llll1ll1_opy_ or {}
            bstack11ll11111_opy_ = os.environ[bstack11l111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᶈ")]
            bstack111llll1ll1_opy_[bstack11l111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩᶉ")] = str(framework) + str(__version__)
            bstack111llll1ll1_opy_[bstack11l111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᶊ")] = bstack1l1l1l1l1ll_opy_()
            bstack111llll1ll1_opy_[bstack11l111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡷࡩࡸࡺࡨࡶࡤࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬᶋ")] = bstack11ll11111_opy_
            bstack111llll1ll1_opy_[bstack11l111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡺ࡯࡬ࡥࡒࡵࡳࡩࡻࡣࡵࡏࡤࡴࠬᶌ")] = bstack11l11lll1l_opy_
            bstack111ll11lll1_opy_ = bstack111ll11lll1_opy_.split(bstack11l111_opy_ (u"ࠬࡩࡡࡱࡵࡀࠫᶍ"))[0] + bstack11l111_opy_ (u"࠭ࡣࡢࡲࡶࡁࠬᶎ") + urllib.parse.quote(json.dumps(bstack111llll1ll1_opy_))
    return bstack111ll11lll1_opy_
def bstack1l111l1l_opy_():
    global bstack111llll11_opy_
    from playwright._impl._browser_type import BrowserType
    bstack111llll11_opy_ = BrowserType.connect
    return bstack111llll11_opy_
def bstack11ll111ll1_opy_(framework_name):
    global bstack1ll1111l_opy_
    bstack1ll1111l_opy_ = framework_name
    return framework_name
def bstack1ll111ll1l_opy_(self, *args, **kwargs):
    global bstack111llll11_opy_
    try:
        global bstack1ll1111l_opy_
        if bstack11l111_opy_ (u"ࠧࡸࡵࡈࡲࡩࡶ࡯ࡪࡰࡷࠫᶏ") in kwargs:
            kwargs[bstack11l111_opy_ (u"ࠨࡹࡶࡉࡳࡪࡰࡰ࡫ࡱࡸࠬᶐ")] = bstack11l111l1111_opy_(
                kwargs.get(bstack11l111_opy_ (u"ࠩࡺࡷࡊࡴࡤࡱࡱ࡬ࡲࡹ࠭ᶑ"), None),
                bstack1ll1111l_opy_
            )
    except Exception as e:
        logger.error(bstack11l111_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬ࡪࡴࠠࡱࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡘࡊࡋࠡࡥࡤࡴࡸࡀࠠࡼࡿࠥᶒ").format(str(e)))
    return bstack111llll11_opy_(self, *args, **kwargs)
def bstack111llll1l11_opy_(bstack111lllll1ll_opy_, proxies):
    proxy_settings = {}
    try:
        if not proxies:
            proxies = bstack11111llll_opy_(bstack111lllll1ll_opy_, bstack11l111_opy_ (u"ࠦࠧᶓ"))
        if proxies and proxies.get(bstack11l111_opy_ (u"ࠧ࡮ࡴࡵࡲࡶࠦᶔ")):
            parsed_url = urlparse(proxies.get(bstack11l111_opy_ (u"ࠨࡨࡵࡶࡳࡷࠧᶕ")))
            if parsed_url and parsed_url.hostname: proxy_settings[bstack11l111_opy_ (u"ࠧࡱࡴࡲࡼࡾࡎ࡯ࡴࡶࠪᶖ")] = str(parsed_url.hostname)
            if parsed_url and parsed_url.port: proxy_settings[bstack11l111_opy_ (u"ࠨࡲࡵࡳࡽࡿࡐࡰࡴࡷࠫᶗ")] = str(parsed_url.port)
            if parsed_url and parsed_url.username: proxy_settings[bstack11l111_opy_ (u"ࠩࡳࡶࡴࡾࡹࡖࡵࡨࡶࠬᶘ")] = str(parsed_url.username)
            if parsed_url and parsed_url.password: proxy_settings[bstack11l111_opy_ (u"ࠪࡴࡷࡵࡸࡺࡒࡤࡷࡸ࠭ᶙ")] = str(parsed_url.password)
        return proxy_settings
    except:
        return proxy_settings
def bstack1l11lll11l_opy_(bstack111lllll1ll_opy_):
    bstack111lllll1l1_opy_ = {
        bstack11l1ll11111_opy_[bstack111ll1l1111_opy_]: bstack111lllll1ll_opy_[bstack111ll1l1111_opy_]
        for bstack111ll1l1111_opy_ in bstack111lllll1ll_opy_
        if bstack111ll1l1111_opy_ in bstack11l1ll11111_opy_
    }
    bstack111lllll1l1_opy_[bstack11l111_opy_ (u"ࠦࡵࡸ࡯ࡹࡻࡖࡩࡹࡺࡩ࡯ࡩࡶࠦᶚ")] = bstack111llll1l11_opy_(bstack111lllll1ll_opy_, bstack11l11ll1l_opy_.get_property(bstack11l111_opy_ (u"ࠧࡶࡲࡰࡺࡼࡗࡪࡺࡴࡪࡰࡪࡷࠧᶛ")))
    bstack111ll1ll11l_opy_ = [element.lower() for element in bstack11l1l11l1l1_opy_]
    bstack11l111111l1_opy_(bstack111lllll1l1_opy_, bstack111ll1ll11l_opy_)
    return bstack111lllll1l1_opy_
def bstack11l111111l1_opy_(d, keys):
    for key in list(d.keys()):
        if key.lower() in keys:
            d[key] = bstack11l111_opy_ (u"ࠨࠪࠫࠬ࠭ࠦᶜ")
    for value in d.values():
        if isinstance(value, dict):
            bstack11l111111l1_opy_(value, keys)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    bstack11l111111l1_opy_(item, keys)
def bstack1l1ll111lll_opy_():
    bstack111ll11ll11_opy_ = [os.environ.get(bstack11l111_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡆࡊࡎࡈࡗࡤࡊࡉࡓࠤᶝ")), os.path.join(os.path.expanduser(bstack11l111_opy_ (u"ࠣࢀࠥᶞ")), bstack11l111_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩᶟ")), os.path.join(bstack11l111_opy_ (u"ࠪ࠳ࡹࡳࡰࠨᶠ"), bstack11l111_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫᶡ"))]
    for path in bstack111ll11ll11_opy_:
        if path is None:
            continue
        try:
            if os.path.exists(path):
                logger.debug(bstack11l111_opy_ (u"ࠧࡌࡩ࡭ࡧࠣࠫࠧᶢ") + str(path) + bstack11l111_opy_ (u"ࠨࠧࠡࡧࡻ࡭ࡸࡺࡳ࠯ࠤᶣ"))
                if not os.access(path, os.W_OK):
                    logger.debug(bstack11l111_opy_ (u"ࠢࡈ࡫ࡹ࡭ࡳ࡭ࠠࡱࡧࡵࡱ࡮ࡹࡳࡪࡱࡱࡷࠥ࡬࡯ࡳࠢࠪࠦᶤ") + str(path) + bstack11l111_opy_ (u"ࠣࠩࠥᶥ"))
                    os.chmod(path, 0o777)
                else:
                    logger.debug(bstack11l111_opy_ (u"ࠤࡉ࡭ࡱ࡫ࠠࠨࠤᶦ") + str(path) + bstack11l111_opy_ (u"ࠥࠫࠥࡧ࡬ࡳࡧࡤࡨࡾࠦࡨࡢࡵࠣࡸ࡭࡫ࠠࡳࡧࡴࡹ࡮ࡸࡥࡥࠢࡳࡩࡷࡳࡩࡴࡵ࡬ࡳࡳࡹ࠮ࠣᶧ"))
            else:
                logger.debug(bstack11l111_opy_ (u"ࠦࡈࡸࡥࡢࡶ࡬ࡲ࡬ࠦࡦࡪ࡮ࡨࠤࠬࠨᶨ") + str(path) + bstack11l111_opy_ (u"ࠧ࠭ࠠࡸ࡫ࡷ࡬ࠥࡽࡲࡪࡶࡨࠤࡵ࡫ࡲ࡮࡫ࡶࡷ࡮ࡵ࡮࠯ࠤᶩ"))
                os.makedirs(path, exist_ok=True)
                os.chmod(path, 0o777)
            logger.debug(bstack11l111_opy_ (u"ࠨࡏࡱࡧࡵࡥࡹ࡯࡯࡯ࠢࡶࡹࡨࡩࡥࡦࡦࡨࡨࠥ࡬࡯ࡳࠢࠪࠦᶪ") + str(path) + bstack11l111_opy_ (u"ࠢࠨ࠰ࠥᶫ"))
            return path
        except Exception as e:
            logger.debug(bstack11l111_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸ࡫ࡴࠡࡷࡳࠤ࡫࡯࡬ࡦࠢࠪࡿࡵࡧࡴࡩࡿࠪ࠾ࠥࠨᶬ") + str(e) + bstack11l111_opy_ (u"ࠤࠥᶭ"))
    logger.debug(bstack11l111_opy_ (u"ࠥࡅࡱࡲࠠࡱࡣࡷ࡬ࡸࠦࡦࡢ࡫࡯ࡩࡩ࠴ࠢᶮ"))
    return None
@measure(event_name=EVENTS.bstack11l1l11llll_opy_, stage=STAGE.bstack1l1l111l1_opy_)
def bstack1lll1111111_opy_(binary_path, bstack1lll1l11lll_opy_, bs_config):
    logger.debug(bstack11l111_opy_ (u"ࠦࡈࡻࡲࡳࡧࡱࡸࠥࡉࡌࡊࠢࡓࡥࡹ࡮ࠠࡧࡱࡸࡲࡩࡀࠠࡼࡿࠥᶯ").format(binary_path))
    bstack11l111ll1ll_opy_ = bstack11l111_opy_ (u"ࠬ࠭ᶰ")
    bstack111l1lll1ll_opy_ = {
        bstack11l111_opy_ (u"࠭ࡳࡥ࡭ࡢࡺࡪࡸࡳࡪࡱࡱࠫᶱ"): __version__,
        bstack11l111_opy_ (u"ࠢࡰࡵࠥᶲ"): platform.system(),
        bstack11l111_opy_ (u"ࠣࡱࡶࡣࡦࡸࡣࡩࠤᶳ"): platform.machine(),
        bstack11l111_opy_ (u"ࠤࡦࡰ࡮ࡥࡶࡦࡴࡶ࡭ࡴࡴࠢᶴ"): bstack11l111_opy_ (u"ࠪ࠴ࠬᶵ"),
        bstack11l111_opy_ (u"ࠦࡸࡪ࡫ࡠ࡮ࡤࡲ࡬ࡻࡡࡨࡧࠥᶶ"): bstack11l111_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬᶷ")
    }
    bstack111ll1ll1ll_opy_(bstack111l1lll1ll_opy_)
    try:
        if binary_path:
            if bstack111ll1l1l11_opy_():
                bstack111l1lll1ll_opy_[bstack11l111_opy_ (u"࠭ࡣ࡭࡫ࡢࡺࡪࡸࡳࡪࡱࡱࠫᶸ")] = subprocess.check_output([binary_path, bstack11l111_opy_ (u"ࠢࡷࡧࡵࡷ࡮ࡵ࡮ࠣᶹ")]).strip().decode(bstack11l111_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧᶺ"))
            else:
                bstack111l1lll1ll_opy_[bstack11l111_opy_ (u"ࠩࡦࡰ࡮ࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᶻ")] = subprocess.check_output([binary_path, bstack11l111_opy_ (u"ࠥࡺࡪࡸࡳࡪࡱࡱࠦᶼ")], stderr=subprocess.DEVNULL).strip().decode(bstack11l111_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪᶽ"))
        response = requests.request(
            bstack11l111_opy_ (u"ࠬࡍࡅࡕࠩᶾ"),
            url=bstack1l1l1111l1_opy_(bstack11l1l11l1ll_opy_),
            headers=None,
            auth=(bs_config[bstack11l111_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨᶿ")], bs_config[bstack11l111_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪ᷀")]),
            json=None,
            params=bstack111l1lll1ll_opy_
        )
        data = response.json()
        if response.status_code == 200 and bstack11l111_opy_ (u"ࠨࡷࡵࡰࠬ᷁") in data.keys() and bstack11l111_opy_ (u"ࠩࡸࡴࡩࡧࡴࡦࡦࡢࡧࡱ࡯࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ᷂") in data.keys():
            logger.debug(bstack11l111_opy_ (u"ࠥࡒࡪ࡫ࡤࠡࡶࡲࠤࡺࡶࡤࡢࡶࡨࠤࡧ࡯࡮ࡢࡴࡼ࠰ࠥࡩࡵࡳࡴࡨࡲࡹࠦࡢࡪࡰࡤࡶࡾࠦࡶࡦࡴࡶ࡭ࡴࡴ࠺ࠡࡽࢀࠦ᷃").format(bstack111l1lll1ll_opy_[bstack11l111_opy_ (u"ࠫࡨࡲࡩࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ᷄")]))
            if bstack11l111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇࡏࡎࡂࡔ࡜ࡣ࡚ࡘࡌࠨ᷅") in os.environ:
                logger.debug(bstack11l111_opy_ (u"ࠨࡓ࡬࡫ࡳࡴ࡮ࡴࡧࠡࡤ࡬ࡲࡦࡸࡹࠡࡦࡲࡻࡳࡲ࡯ࡢࡦࠣࡥࡸࠦࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡉࡏࡃࡕ࡝ࡤ࡛ࡒࡍࠢ࡬ࡷࠥࡹࡥࡵࠤ᷆"))
                data[bstack11l111_opy_ (u"ࠧࡶࡴ࡯ࠫ᷇")] = os.environ[bstack11l111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡋࡑࡅࡗ࡟࡟ࡖࡔࡏࠫ᷈")]
            bstack111lll1l1l1_opy_ = bstack11l11111lll_opy_(data[bstack11l111_opy_ (u"ࠩࡸࡶࡱ࠭᷉")], bstack1lll1l11lll_opy_)
            bstack11l111ll1ll_opy_ = os.path.join(bstack1lll1l11lll_opy_, bstack111lll1l1l1_opy_)
            os.chmod(bstack11l111ll1ll_opy_, 0o777) # bstack111lll1l11l_opy_ permission
            return bstack11l111ll1ll_opy_
    except Exception as e:
        logger.debug(bstack11l111_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡦࡲࡻࡳࡲ࡯ࡢࡦ࡬ࡲ࡬ࠦ࡮ࡦࡹࠣࡗࡉࡑࠠࡼࡿ᷊ࠥ").format(e))
    return binary_path
def bstack111ll1ll1ll_opy_(bstack111l1lll1ll_opy_):
    try:
        if bstack11l111_opy_ (u"ࠫࡱ࡯࡮ࡶࡺࠪ᷋") not in bstack111l1lll1ll_opy_[bstack11l111_opy_ (u"ࠬࡵࡳࠨ᷌")].lower():
            return
        if os.path.exists(bstack11l111_opy_ (u"ࠨ࠯ࡦࡶࡦ࠳ࡴࡹ࠭ࡳࡧ࡯ࡩࡦࡹࡥࠣ᷍")):
            with open(bstack11l111_opy_ (u"ࠢ࠰ࡧࡷࡧ࠴ࡵࡳ࠮ࡴࡨࡰࡪࡧࡳࡦࠤ᷎"), bstack11l111_opy_ (u"ࠣࡴ᷏ࠥ")) as f:
                bstack111ll11ll1l_opy_ = {}
                for line in f:
                    if bstack11l111_opy_ (u"ࠤࡀ᷐ࠦ") in line:
                        key, value = line.rstrip().split(bstack11l111_opy_ (u"ࠥࡁࠧ᷑"), 1)
                        bstack111ll11ll1l_opy_[key] = value.strip(bstack11l111_opy_ (u"ࠫࠧࡢࠧࠨ᷒"))
                bstack111l1lll1ll_opy_[bstack11l111_opy_ (u"ࠬࡪࡩࡴࡶࡵࡳࠬᷓ")] = bstack111ll11ll1l_opy_.get(bstack11l111_opy_ (u"ࠨࡉࡅࠤᷔ"), bstack11l111_opy_ (u"ࠢࠣᷕ"))
        elif os.path.exists(bstack11l111_opy_ (u"ࠣ࠱ࡨࡸࡨ࠵ࡡ࡭ࡲ࡬ࡲࡪ࠳ࡲࡦ࡮ࡨࡥࡸ࡫ࠢᷖ")):
            bstack111l1lll1ll_opy_[bstack11l111_opy_ (u"ࠩࡧ࡭ࡸࡺࡲࡰࠩᷗ")] = bstack11l111_opy_ (u"ࠪࡥࡱࡶࡩ࡯ࡧࠪᷘ")
    except Exception as e:
        logger.debug(bstack11l111_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡨࡧࡷࠤࡩ࡯ࡳࡵࡴࡲࠤࡴ࡬ࠠ࡭࡫ࡱࡹࡽࠨᷙ") + e)
@measure(event_name=EVENTS.bstack11l1ll111l1_opy_, stage=STAGE.bstack1l1l111l1_opy_)
def bstack11l11111lll_opy_(bstack111ll1lllll_opy_, bstack11l111l1lll_opy_):
    logger.debug(bstack11l111_opy_ (u"ࠧࡊ࡯ࡸࡰ࡯ࡳࡦࡪࡩ࡯ࡩࠣࡗࡉࡑࠠࡣ࡫ࡱࡥࡷࡿࠠࡧࡴࡲࡱ࠿ࠦࠢᷚ") + str(bstack111ll1lllll_opy_) + bstack11l111_opy_ (u"ࠨࠢᷛ"))
    zip_path = os.path.join(bstack11l111l1lll_opy_, bstack11l111_opy_ (u"ࠢࡥࡱࡺࡲࡱࡵࡡࡥࡧࡧࡣ࡫࡯࡬ࡦ࠰ࡽ࡭ࡵࠨᷜ"))
    bstack111lll1l1l1_opy_ = bstack11l111_opy_ (u"ࠨࠩᷝ")
    with requests.get(bstack111ll1lllll_opy_, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, bstack11l111_opy_ (u"ࠤࡺࡦࠧᷞ")) as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logger.debug(bstack11l111_opy_ (u"ࠥࡊ࡮ࡲࡥࠡࡦࡲࡻࡳࡲ࡯ࡢࡦࡨࡨࠥࡹࡵࡤࡥࡨࡷࡸ࡬ࡵ࡭࡮ࡼ࠲ࠧᷟ"))
    with zipfile.ZipFile(zip_path, bstack11l111_opy_ (u"ࠫࡷ࠭ᷠ")) as zip_ref:
        bstack11l11111l11_opy_ = zip_ref.namelist()
        if len(bstack11l11111l11_opy_) > 0:
            bstack111lll1l1l1_opy_ = bstack11l11111l11_opy_[0] # bstack111ll111l11_opy_ bstack11l1l1l111l_opy_ will be bstack111llll111l_opy_ 1 file i.e. the binary in the zip
        zip_ref.extractall(bstack11l111l1lll_opy_)
        logger.debug(bstack11l111_opy_ (u"ࠧࡌࡩ࡭ࡧࡶࠤࡸࡻࡣࡤࡧࡶࡷ࡫ࡻ࡬࡭ࡻࠣࡩࡽࡺࡲࡢࡥࡷࡩࡩࠦࡴࡰࠢࠪࠦᷡ") + str(bstack11l111l1lll_opy_) + bstack11l111_opy_ (u"ࠨࠧࠣᷢ"))
    os.remove(zip_path)
    return bstack111lll1l1l1_opy_
def get_cli_dir():
    bstack11l11l111l1_opy_ = bstack1l1ll111lll_opy_()
    if bstack11l11l111l1_opy_:
        bstack1lll1l11lll_opy_ = os.path.join(bstack11l11l111l1_opy_, bstack11l111_opy_ (u"ࠢࡤ࡮࡬ࠦᷣ"))
        if not os.path.exists(bstack1lll1l11lll_opy_):
            os.makedirs(bstack1lll1l11lll_opy_, mode=0o777, exist_ok=True)
        return bstack1lll1l11lll_opy_
    else:
        raise FileNotFoundError(bstack11l111_opy_ (u"ࠣࡐࡲࠤࡼࡸࡩࡵࡣࡥࡰࡪࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺࠢࡤࡺࡦ࡯࡬ࡢࡤ࡯ࡩࠥ࡬࡯ࡳࠢࡷ࡬ࡪࠦࡓࡅࡍࠣࡦ࡮ࡴࡡࡳࡻ࠱ࠦᷤ"))
def bstack1ll1l111lll_opy_(bstack1lll1l11lll_opy_):
    bstack11l111_opy_ (u"ࠤࠥࠦࡌ࡫ࡴࠡࡶ࡫ࡩࠥࡶࡡࡵࡪࠣࡪࡴࡸࠠࡵࡪࡨࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࡗࡉࡑࠠࡣ࡫ࡱࡥࡷࡿࠠࡪࡰࠣࡥࠥࡽࡲࡪࡶࡤࡦࡱ࡫ࠠࡥ࡫ࡵࡩࡨࡺ࡯ࡳࡻ࠱ࠦࠧࠨᷥ")
    bstack111ll11l11l_opy_ = [
        os.path.join(bstack1lll1l11lll_opy_, f)
        for f in os.listdir(bstack1lll1l11lll_opy_)
        if os.path.isfile(os.path.join(bstack1lll1l11lll_opy_, f)) and f.startswith(bstack11l111_opy_ (u"ࠥࡦ࡮ࡴࡡࡳࡻ࠰ࠦᷦ"))
    ]
    if len(bstack111ll11l11l_opy_) > 0:
        return max(bstack111ll11l11l_opy_, key=os.path.getmtime) # get bstack11l11l1111l_opy_ binary
    return bstack11l111_opy_ (u"ࠦࠧᷧ")
def bstack11ll111l11l_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1ll1111ll1l_opy_(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = bstack1ll1111ll1l_opy_(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack111111ll_opy_(data, keys, default=None):
    bstack11l111_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤ࡙ࠥࡡࡧࡧ࡯ࡽࠥ࡭ࡥࡵࠢࡤࠤࡳ࡫ࡳࡵࡧࡧࠤࡻࡧ࡬ࡶࡧࠣࡪࡷࡵ࡭ࠡࡣࠣࡨ࡮ࡩࡴࡪࡱࡱࡥࡷࡿࠠࡰࡴࠣࡰ࡮ࡹࡴ࠯ࠌࠣࠤࠥࠦ࠺ࡱࡣࡵࡥࡲࠦࡤࡢࡶࡤ࠾࡚ࠥࡨࡦࠢࡧ࡭ࡨࡺࡩࡰࡰࡤࡶࡾࠦ࡯ࡳࠢ࡯࡭ࡸࡺࠠࡵࡱࠣࡸࡷࡧࡶࡦࡴࡶࡩ࠳ࠐࠠࠡࠢࠣ࠾ࡵࡧࡲࡢ࡯ࠣ࡯ࡪࡿࡳ࠻ࠢࡄࠤࡱ࡯ࡳࡵࠢࡲࡪࠥࡱࡥࡺࡵ࠲࡭ࡳࡪࡩࡤࡧࡶࠤࡷ࡫ࡰࡳࡧࡶࡩࡳࡺࡩ࡯ࡩࠣࡸ࡭࡫ࠠࡱࡣࡷ࡬࠳ࠐࠠࠡࠢࠣ࠾ࡵࡧࡲࡢ࡯ࠣࡨࡪ࡬ࡡࡶ࡮ࡷ࠾ࠥ࡜ࡡ࡭ࡷࡨࠤࡹࡵࠠࡳࡧࡷࡹࡷࡴࠠࡪࡨࠣࡸ࡭࡫ࠠࡱࡣࡷ࡬ࠥࡪ࡯ࡦࡵࠣࡲࡴࡺࠠࡦࡺ࡬ࡷࡹ࠴ࠊࠡࠢࠣࠤ࠿ࡸࡥࡵࡷࡵࡲ࠿ࠦࡔࡩࡧࠣࡺࡦࡲࡵࡦࠢࡤࡸࠥࡺࡨࡦࠢࡱࡩࡸࡺࡥࡥࠢࡳࡥࡹ࡮ࠬࠡࡱࡵࠤࡩ࡫ࡦࡢࡷ࡯ࡸࠥ࡯ࡦࠡࡰࡲࡸࠥ࡬࡯ࡶࡰࡧ࠲ࠏࠦࠠࠡࠢࠥࠦࠧᷨ")
    if not data:
        return default
    current = data
    try:
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list) and isinstance(key, int):
                current = current[key]
            else:
                return default
        return current
    except (KeyError, IndexError, TypeError):
        return default