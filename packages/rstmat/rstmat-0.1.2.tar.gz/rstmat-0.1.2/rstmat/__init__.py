import math
from collections.abc import Sequence

import torch

from .matrix import _get_random_matrix
from .rng import RNG

__all__ = [
    "random_matrix",
]

def random_matrix(
    size: int | Sequence[int],
    dtype: torch.dtype = torch.get_default_dtype(),
    device: torch.types.Device = torch.get_default_device(),

    branch_penalty: float = 0.9,
    ops_penalty: float = 0.9,

    seed: int | None | RNG = None,
):
    rng = RNG(seed)

    if isinstance(size, int):
        size = (size, size)
    else:
        size = tuple(size)

    *b_l, h, w = size
    if len(b_l) == 0:
        b = 1
    else:
        b = math.prod(b_l)

    A = _get_random_matrix(
        b=b, h=h, w=w, base=True, level=1, num_ops=1, branch_penalty=branch_penalty,
        ops_penalty=ops_penalty, dtype=dtype, device=device, rng=rng,
    )

    if len(b_l) == 0: return A[0]
    return A.reshape(*b_l, h, w)