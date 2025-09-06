from emit import L1bProj
from multiprocessing import Pool
import pytest


@pytest.mark.long_test
def test_l1b_proj(isolated_dir, l1_osp_dir, emit_igccol):
    p = L1bProj(emit_igccol, l1_osp_dir, emit_igccol)
    pool = Pool(10)
    res = p.proj(pool=pool)
    print(res)
