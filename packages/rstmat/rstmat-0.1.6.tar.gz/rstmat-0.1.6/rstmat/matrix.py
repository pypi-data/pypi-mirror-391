import sys
import time
import warnings
import inspect
import math
import random
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence

import numpy as np
import scipy.linalg
import torch
from torch.nn import functional as F

from .rng import RNG

MAX_LINALG_NUMEL: int = 512 * 512
"""Controls max number of entries for expensive operations (some use two or four times this value)."""

MAX_LINALG_SIZE: int = 512
"""Controls max size of largest dim for expensive operations (some use two or four times this value)."""

VERBOSE: bool = False
"""If true, prints which matrices are picked"""
VERBOSE_FILE = sys.stdout

WARN_SECONDS_TO_GENERATE: float | None = None
"""If not None, whenever matrix takes more than this many seconds to generate, emits a warning"""

class Matrix(ABC):
    """
    Generator for some type of random matrix.

    __init__ should accept no arguments because some matrices generate random child matrices.
    """
    ABSTRACT = False
    """Set to ``True`` to prevent this class from being selected by ``random_matrix``.
    Classes with ``abstractmethod`` are never picked regardless of this attribute."""

    BASE = True
    """If ``True``, this can be picked as a base matrix. If ``False``, this can only be picked recursively
    (i.e. when ``AB`` generates two random matrices to matmul, one of them doesn't have to be base.).

    If a matrix is not sufficiently random, i.e. a filled matrix, it shouldn't be base because otherwise
    the batch wouldn't have enough variance.
    """

    SQUARE = False
    """if True, this can only generate square matrices."""

    WEIGHT = 1.0
    """weight for picking this matrix"""

    MAX_NUMEL = np.inf
    MAX_SIZE = np.inf
    BRANCHES = False
    INCREASE_PROB: bool = False

    def __init__(self, level: int, num_ops: int, branch_penalty: float, ops_penalty: float, device, dtype, rng):
        self.level = level
        self.num_ops = num_ops
        self.branch_penalty = branch_penalty
        self.ops_penalty = ops_penalty

        self.device = device
        self.dtype = dtype
        self.rng = RNG(rng)
        self.generator = self.rng.torch(device)

    def get_random_matrix(self, b: int, h: int, w: int, base:bool):
        self.num_ops += 1

        if VERBOSE:
            t = '|'*(self.level-1)
            t = f'{t} '
            print(f'{t}{self.__class__.__name__} requested a {(b, h, w)} matrix, level = {self.level}.', file=VERBOSE_FILE)

        return _get_random_matrix(
            b=b,
            h=h,
            w=w,
            dtype=self.dtype,
            device=self.device,
            rng=self.rng,
            base=base,
            level=self.level + 1,
            num_ops=self.num_ops,
            branch_penalty=self.branch_penalty,
            ops_penalty=self.ops_penalty,
        )

    @abstractmethod
    def generate(self, b: int, h: int, w: int) -> torch.Tensor:
        """Returns batch of matrices of shape (b, h, w), use self.dtype, self.device and self.rng"""


class RandomNormal(Matrix):
    INCREASE_PROB = True
    def generate(self, b, h, w):
        return torch.randn((b, h, w), dtype=self.dtype, device=self.device, generator=self.generator)

class RandomUniform(Matrix):
    INCREASE_PROB = True
    def generate(self, b, h, w):
        return torch.empty((b, h, w), dtype=self.dtype, device=self.device).uniform_(-1, 1, generator=self.generator)

class RandomRademacher(Matrix):
    INCREASE_PROB = True
    WEIGHT = 0.5
    def generate(self, b, h, w):
        return torch.randint(0, 2, size=(b, h, w), device=self.device, dtype=self.dtype, generator=self.generator) * 2 - 1

_DISTRIBUTIONS = (
    torch.distributions.Laplace(loc=0, scale=1),
    torch.distributions.Cauchy(loc=0, scale=1),
    torch.distributions.Exponential(1),
    torch.distributions.Poisson(4),
    torch.distributions.Gamma(1, 1),
)
class RandomDistribution(Matrix):
    INCREASE_PROB = True
    def generate(self, b, h, w):
        dist = self.rng.random.choice(_DISTRIBUTIONS)
        return dist.sample((b, h, w)).to(dtype=self.dtype, device=self.device)



class Bernoulli(Matrix):
    """Bernoulli entries with probabilities given by another matrix"""
    WEIGHT = 0.5
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        # rescale to 0,1 for bernoulli
        A -= A.amin()
        max = A.amax()
        if max <= torch.finfo(A.dtype).tiny * 2: return torch.randn_like(A)

        if self.rng.random.random() < 0.2:
            max = max.clip(min=1)

        A /= max
        A = A.nan_to_num(0.5, 0.5, 0.5)
        try:
            eps = torch.finfo(A.dtype).eps
            return torch.bernoulli(A.clip(eps, 1-eps), generator=self.generator)
        except RuntimeError:
            # for some reason every once in a while it would think A has entries larger than 1
            return torch.randn_like(A)

class Sparsify(Matrix):
    WEIGHT = 0.5
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        p = self.rng.random.triangular(1e-12, 1, 1e-12) ** 2
        mask = torch.bernoulli(
            torch.full_like(A, fill_value=p, device=self.device, dtype=self.dtype),
            generator=self.generator
        )
        return A * mask

class SparsifyRows(Matrix):
    WEIGHT = 0.25
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        p = self.rng.random.triangular(1e-12, 1, 1e-12) ** 2
        mask = torch.bernoulli(
            torch.full((b, 1, w), device=self.device, dtype=self.dtype, fill_value=p),
            generator=self.generator
        )
        return A * mask

class SparsifyCols(Matrix):
    WEIGHT = 0.25
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        p = self.rng.random.triangular(1e-12, 1, 1e-12) ** 2
        mask = torch.bernoulli(
            torch.full((b, h, 1), device=self.device, dtype=self.dtype, fill_value=p),
            generator=self.generator
        )
        return A * mask


class Full(Matrix):
    BASE = False
    WEIGHT = 0.05
    def generate(self, b, h, w):
        fill_value = self.rng.random.uniform(-2, 2)
        return torch.full(size=(b, h, w), fill_value=fill_value, dtype=self.dtype, device=self.device)

class Zeros(Matrix):
    BASE = False
    WEIGHT = 0.05
    def generate(self, b, h, w):
        return torch.zeros(size=(b, h, w), dtype=self.dtype, device=self.device)

class Identity(Matrix):
    """Square identity (for rectangular ReplaceDiag can generate it), this increases odds of identity"""
    BASE = False
    SQUARE = True
    WEIGHT = 0.05
    def generate(self, b, h, w):
        return torch.eye(h, dtype=self.dtype, device=self.device).unsqueeze(0).repeat_interleave(repeats=b, dim=0).clone()

class Transpose(Matrix):
    """A^T"""
    def generate(self, b, h, w):
        return self.get_random_matrix(b, w, h, base=True).mH

class Flip(Matrix):
    """Flip of another matrix along rows or columns"""
    def generate(self, b, h, w):
        dim = self.rng.random.choice([-1, -2])
        return self.get_random_matrix(b, h, w, base=True).flip(dim)

def apply_diag_fn_(A: torch.Tensor, diag: torch.Tensor, fn, rng:RNG):
    """picks a random square part of A and sets diagonal to ``fn(A_sq.diagonal(), diag)``"""
    b, h, w = A.size()

    if h >= w:
        # pick W, W
        start = rng.random.randint(0, h-w)
        end = start + w
        A_sq = A[:, start:end]

        new_diag = fn(A_sq.diagonal(dim1=-2, dim2=-1), diag)
        A_sq[:, range(w), range(w)] = new_diag
        return A

    return apply_diag_fn_(A.mH, diag, fn, rng).mH

_BINARY_FUNCS = (
    lambda c,n: n,
    lambda c,n: c+n,
    lambda c,n: c-n,
    lambda c,n: c*n,
    torch.maximum,
    torch.minimum,
)

class ReplaceDiagonal(Matrix):
    """Takes a matrix and applies random binary function with diagonal of another matrix"""

    BRANCHES = True
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)

        # make sure H >= W
        T = False
        if h < w:
            T = True
            A = A.mH
            h, w = w, h

        # matrix to take diagonal from
        if h == w or self.rng.random.random() > 0.5: offset = 0
        else: offset = self.rng.random.randint(0, h-w)
        diag = A.diagonal(offset=-offset, dim1=-2, dim2=-1)

        # matrix to replace diagonal in
        B = self.get_random_matrix(b, h, w, base=False)

        embedded = apply_diag_fn_(B, diag, fn=self.rng.random.choice(_BINARY_FUNCS), rng=self.rng)

        if T:
            embedded = embedded.mH

        return embedded


class Symmetrize(Matrix):
    """A + A^T"""
    SQUARE = True
    WEIGHT = 0.75
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        S = A + A.mH
        if self.rng.random.random() > 0.5:
            S = S.diagonal_scatter(S.diagonal(dim1=-2,dim2=-1)/2, dim1=-2, dim2=-1)
        return S

class SymmetrizeT(Matrix):
    """(A + A^T)^T"""
    SQUARE = True
    WEIGHT = 0.25
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        S = A + A.mH
        if self.rng.random.random() > 0.5:
            S = S.diagonal_scatter(S.diagonal(dim1=-2,dim2=-1)/2, dim1=-2, dim2=-1)
        return S.mH


class ATA(Matrix):
    """A^T A, also takes care of symmetric low rank"""
    SQUARE = True
    WEIGHT = 0.8
    def generate(self, b, h, w):
        k = self.rng.random.randint(1, h * 2)
        A = self.get_random_matrix(b, k, h, base=True)
        C = A.mH @ A
        if self.rng.random.random() > 0.5:
            C = C.diagonal_scatter(C.diagonal(dim1=-2, dim2=-1).sqrt(), dim1=-2, dim2=-1)
        return A.mH @ A

class SPD(Matrix):
    """A^T A + yI"""
    SQUARE = True
    WEIGHT = 0.2
    def generate(self, b, h, w):
        k = self.rng.random.randint(1, h * 2)
        A = self.get_random_matrix(b, k, h, base=True)
        reg = self.rng.random.triangular(0, 1)**2
        I = torch.eye(h, device=self.device, dtype=self.dtype)
        return (A.mH @ A) + (I * reg)

class Regularize(Matrix):
    """A^T A + I"""
    WEIGHT = 0.25
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        reg = self.rng.random.triangular(0, 1)**4
        if self.rng.random.random() < 0.1: reg = -reg
        r = max(h-1, 1)
        if self.rng.random.random() > 0.5: offset = 0
        else: offset = self.rng.random.randint(-r, r)
        return A.diagonal_scatter(A.diagonal(offset=offset, dim1=-2,dim2=-1) + reg, offset=offset, dim1=-2,dim2=-1)

class ScaleDiag(Matrix):
    WEIGHT = 0.25
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        scale = self.rng.random.uniform(-2, 2)
        r = max(h-1, 1)
        if self.rng.random.random() > 0.5: offset = 0
        else: offset = self.rng.random.randint(-r, r)
        return A.diagonal_scatter(A.diagonal(offset=offset, dim1=-2,dim2=-1) * scale, offset=offset, dim1=-2,dim2=-1)

class AB(Matrix):
    """Matmul of two matrices, also takes care of low rank"""
    BRANCHES = True
    def generate(self, b, h, w):
        k = self.rng.random.randint(1, min(h,w) * 2)
        A = self.get_random_matrix(b, h, k, base=False)
        B = self.get_random_matrix(b, k, w, base=False)
        return A @ B

class ABC_(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        k = self.rng.random.randint(1, min(h,w) * 2)
        l = self.rng.random.randint(1, min(h,w) * 2)
        A = self.get_random_matrix(b, h, k, base=False)
        B = self.get_random_matrix(b, k, l, base=False)
        C = self.get_random_matrix(b, l, w, base=False)
        return A @ B @ C

class ABCD(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        k = self.rng.random.randint(1, min(h,w) * 2)
        l = self.rng.random.randint(1, min(h,w) * 2)
        m = self.rng.random.randint(1, min(h,w) * 2)
        A = self.get_random_matrix(b, h, k, base=False)
        B = self.get_random_matrix(b, k, l, base=False)
        C = self.get_random_matrix(b, l, m, base=False)
        D = self.get_random_matrix(b, m, w, base=False)
        return A @ B @ C @ D

class MatrixPower(Matrix):
    SQUARE = True
    def generate(self, b, h, w):
        p = self.rng.random.randint(2, 10)
        A = self.get_random_matrix(b, h, w, base=True)
        return torch.linalg.matrix_power(A, p) # pylint:disable=not-callable

class Add(Matrix):
    """A + B"""
    BRANCHES = True
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        B = self.get_random_matrix(b, h, w, base=False)
        return A + B

class Sub(Matrix):
    """A - B"""
    BRANCHES = True
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        B = self.get_random_matrix(b, h, w, base=False)
        return A - B

class Maximum(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        B = self.get_random_matrix(b, h, w, base=False)
        return torch.maximum(A, B)

class Minimum(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        B = self.get_random_matrix(b, h, w, base=False)
        return torch.minimum(A, B)

class ElementwiseProduct(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        B = self.get_random_matrix(b, h, w, base=False)
        return A * B

class ElementwiseSign(Matrix):
    WEIGHT = 0.2
    def generate(self, b, h, w):
        return self.get_random_matrix(b, h, w, base=True).sign()

class ElementwiseAbs(Matrix):
    def generate(self, b, h, w):
        return self.get_random_matrix(b, h, w, base=True).abs()

class ElementwiseRound(Matrix):
    WEIGHT = 0.5
    def generate(self, b, h, w):
        return self.get_random_matrix(b, h, w, base=True).round(decimals=self.rng.random.randrange(0, 4))

class ElementwiseSquare(Matrix):
    def generate(self, b, h, w):
        return self.get_random_matrix(b, h, w, base=True).square()

class ElementwiseSqrtAbs(Matrix):
    def generate(self, b, h, w):
        return self.get_random_matrix(b, h, w, base=True).abs().sqrt()

class ElementwiseDivCAddAbs(Matrix):
    """element-wise A / (B.abs() + eps)"""
    BRANCHES = True
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        B = self.get_random_matrix(b, h, w, base=False)
        eps = torch.empty(b, 1, 1, device=self.device, dtype=self.dtype).uniform_(0.5, 2, generator=self.generator)
        return A / (B.abs() + eps)

class ElementwiseTanh(Matrix):
    def generate(self, b, h, w):
        return F.tanh(self.get_random_matrix(b, h, w, base=True))

class ElementwiseSin(Matrix):
    def generate(self, b, h, w):
        return self.get_random_matrix(b, h, w, base=True).sin()

class RowSoftmax(Matrix):
    WEIGHT = 0.25
    def generate(self, b, h, w):
        return self.get_random_matrix(b, h, w, base=True).softmax(-2)

class ColSoftmax(Matrix):
    WEIGHT = 0.25
    def generate(self, b, h, w):
        return self.get_random_matrix(b, h, w, base=True).softmax(-1)

class Gradient(Matrix):
    def generate(self, b, h, w):
        dim = self.rng.random.choice(((1, ), (2, ), (1, 2)))
        edge_order = self.rng.random.choice((1, 2))

        # dims should be at least edge_order + 1
        for i in dim:
            if i == 1: d = h
            elif i == 2: d = w
            else: raise RuntimeError()
            if d <= edge_order: return self.get_random_matrix(b, h, w, base=True)

        A = self.get_random_matrix(b, h, w, base=True)
        ret = torch.gradient(A, dim=dim, edge_order=edge_order)

        if len(dim) == 1: return ret[0]
        ch = self.rng.random.choice((1,2,3,4))
        if ch == 1: return ret[0]
        if ch == 2: return ret[1]
        if ch == 3: return ret[0] + ret[1]
        if ch == 4: return ret[0] * ret[1]
        raise RuntimeError()

class Standardize(Matrix):
    WEIGHT = 4
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        A -= A.mean(dim=(1,2), keepdim=True)
        A /= A.std(dim=(1,2), keepdim=True).clip(min=torch.finfo(A.dtype).tiny * 2)
        return A

class Normalize(Matrix):
    WEIGHT = 4
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)

        ord = self.rng.random.choice([1, 2, torch.inf, None])
        if ord is None:
            ord = self.rng.random.triangular(1, 10, 1)

        A /= torch.linalg.matrix_norm(A, dim=(1,2), keepdim=True).clip(min=torch.finfo(A.dtype).tiny * 2) # pylint:disable=not-callable
        return A

class Centralize(Matrix):
    WEIGHT = 4
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        A -= A.mean(dim=(1,2), keepdim=True)
        return A

class Clip(Matrix):
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        Amin = A.amin().item()
        Amax = A.amax().item()

        lower = upper = None
        mode = self.rng.random.choice([0, 1, 2])
        if mode == 0:
            lower = self.rng.random.triangular(Amin, Amax, mode=Amin)
        elif mode == 1:
            upper = self.rng.random.triangular(Amin, Amax, mode=Amax)
        elif mode == 2:
            lower = self.rng.random.triangular(Amin, Amax, mode=Amin)
            upper = self.rng.random.triangular(Amin, Amax, mode=Amax)

        return A.clip(lower, upper)

class ClipToQuantile(Matrix):
    MAX_NUMEL = 8_000_000
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        qlow = self.rng.random.triangular(0.01, 0.99, 0.01) ** 2
        qhigh = 1 - self.rng.random.triangular(0.01, 0.99, 0.99) ** 2

        lower = upper = None
        mode = self.rng.random.choice([0, 1, 2])
        if mode == 0:
            lower = A.quantile(qlow)
        elif mode == 1:
            upper = A.quantile(qhigh)
        elif mode == 2:
            lower = A.quantile(qlow)
            upper = A.quantile(qhigh)

        return A.clip(lower, upper)

class Scale(Matrix):
    def generate(self, b, h, w):
        scale = torch.randn((b, 1, 1), device=self.device, dtype=self.dtype, generator=self.generator)
        return self.get_random_matrix(b, h, w, base=True) * scale

class Shift(Matrix):
    def generate(self, b, h, w):
        shift = torch.randn((b, 1, 1), device=self.device, dtype=self.dtype, generator=self.generator)
        return self.get_random_matrix(b, h, w, base=True) + shift

class NormalizeRows(Matrix):
    WEIGHT = 2
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)

        ord = self.rng.random.choice([1, 2, torch.inf, None])
        if ord is None:
            ord = self.rng.random.triangular(1, 10, 1)

        A /= torch.linalg.vector_norm(A, dim=(1,), ord=ord, keepdim=True).clip(min=torch.finfo(A.dtype).tiny * 2) # pylint:disable=not-callable
        return A

class NormalizeCols(Matrix):
    WEIGHT = 2
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)

        ord = self.rng.random.choice([1, 2, torch.inf, None])
        if ord is None:
            ord = self.rng.random.triangular(1, 10, 1)

        A /= torch.linalg.vector_norm(A, dim=(2,), ord=ord, keepdim=True).clip(min=torch.finfo(A.dtype).tiny * 2) # pylint:disable=not-callable
        return A

class ShuffleRows(Matrix):
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        A = A[:, torch.randperm(h, device=self.device, generator=self.generator)]
        return A

class ShuffleCols(Matrix):
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        A = A[:, :, torch.randperm(w, device=self.device, generator=self.generator)]
        return A

class QR_Q(Matrix):
    """Q from QR (orthogonalizes)"""
    MAX_NUMEL = MAX_LINALG_NUMEL * 2
    MAX_SIZE = MAX_LINALG_SIZE * 2
    def generate(self, b, h, w):
        transpose = h < w
        if transpose:
            h, w = w, h

        A = self.get_random_matrix(b, h, w, base=True)
        Q, R = torch.linalg.qr(A, mode="reduced") # pylint:disable=not-callable
        if transpose: Q = Q.mH
        return Q

class QR_R(Matrix):
    """R from QR"""
    MAX_NUMEL = MAX_LINALG_NUMEL * 2
    MAX_SIZE = MAX_LINALG_SIZE * 2
    WEIGHT = 0.1
    def generate(self, b, h, w):
        T = False
        if w < h:
            h, w = w, h
            T = True

        A = self.get_random_matrix(b, h, w, base=True)
        _, R = torch.linalg.qr(A, mode="r") # pylint:disable=not-callable
        if T: R = R.mH
        return R

class Triu(Matrix):
    def generate(self, b, h, w):
        r = max(h-1, 1)
        if self.rng.random.random() > 0.5: offset = 0
        else: offset = self.rng.random.randint(-r, r)
        return self.get_random_matrix(b, h, w, base=True).triu(diagonal=offset)

class Tril(Matrix):
    def generate(self, b, h, w):
        r = max(h-1, 1)
        if self.rng.random.random() > 0.5: offset = 0
        else: offset = self.rng.random.randint(-r, r)
        return self.get_random_matrix(b, h, w, base=True).tril(diagonal=offset)

class Kron(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        h1 = int(self.rng.random.triangular(1, max(h-1, 1), 1))
        w1 = int(self.rng.random.triangular(1, max(w-1, 1), 1))

        h2 = math.ceil(h / h1)
        w2 = math.ceil(w / w1)

        A = self.get_random_matrix(b, h1, w1, base=False)
        B = self.get_random_matrix(b, h2, w2, base=False)
        return torch.einsum('iab,icd->iacbd', A, B).reshape((b, h1*h2, w1*w2))[:,:h, :w]

class AKron(Matrix):
    def generate(self, b, h, w):
        hs = math.ceil(math.sqrt(h))
        ws = math.ceil(math.sqrt(w))

        A = self.get_random_matrix(b, hs, ws, base=True)
        return torch.einsum('iab,icd->iacbd', A, A).reshape((b, hs**2, ws**2))[:,:h, :w]

class RowCat(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        if h == 1: return self.get_random_matrix(b, 1, w, base=False)
        idx = self.rng.random.randint(1, h-1)
        A = self.get_random_matrix(b, idx, w, base=False)
        B = self.get_random_matrix(b, h-idx, w, base=False)
        return torch.cat([A, B], 1)

class ColCat(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        if w == 1: return self.get_random_matrix(b, h, 1, base=False)
        idx = self.rng.random.randint(1, w-1)
        A = self.get_random_matrix(b, h, idx, base=False)
        B = self.get_random_matrix(b, h, w-idx, base=False)
        return torch.cat([A, B], 2)

class TrilTru(Matrix):
    """generates a matrix with tril from A and triu from B"""
    BRANCHES = True
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        B = self.get_random_matrix(b, h, w, base=False)

        r = max(h-2, 1)
        if self.rng.random.random() > 0.5: offset=0
        else: offset = self.rng.random.randint(-r, r)
        return A.tril(offset) + B.triu(offset+1)

class MaskedMix(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        B = self.get_random_matrix(b, h, w, base=False)
        p = self.rng.random.uniform(0, 1)
        mask = torch.bernoulli(torch.full((b, h, w), p, device=self.device), generator=self.generator).bool()
        return torch.where(mask, A, B)

class TileRows(Matrix):
    WEIGHT = 0.5
    BASE = False
    def generate(self, b, h, w):
        n = math.ceil(self.rng.random.uniform(2, h/2))
        k = math.ceil(h / n)
        A = self.get_random_matrix(b, k, w, base=False)
        return A.repeat(1, n, 1)[:, :h]

class TileCols(Matrix):
    WEIGHT = 0.5
    BASE = False
    def generate(self, b, h, w):
        n = math.ceil(self.rng.random.uniform(2, w/2))
        k = math.ceil(w / n)
        A = self.get_random_matrix(b, h, k, base=False)
        return A.repeat(1, 1, n)[:, :, :w]

class RepeatRows(Matrix):
    WEIGHT = 0.5
    BASE = False
    def generate(self, b, h, w):
        n = math.ceil(self.rng.random.uniform(2, h/2))
        k = math.ceil(h / n)
        A = self.get_random_matrix(b, k, w, base=False)
        return A.repeat_interleave(repeats=n, dim=1)[:, :h]

class RepeatCols(Matrix):
    WEIGHT = 0.5
    BASE = False
    def generate(self, b, h, w):
        n = math.ceil(self.rng.random.uniform(2, w/2))
        k = math.ceil(w / n)
        A = self.get_random_matrix(b, h, k, base=False)
        return A.repeat_interleave(repeats=n, dim=2)[:, :, :w]

class Rank1Normal(Matrix):
    WEIGHT = 0.5
    BASE = False
    def generate(self, b, h, w):
        v1 = torch.randn((b, h, 1), device=self.device, dtype=self.dtype, generator=self.generator)
        v2 = torch.randn((b, 1, w), device=self.device, dtype=self.dtype, generator=self.generator)

        return v1 @ v2

class Rank1Rademacher(Matrix):
    WEIGHT = 0.5
    BASE = False
    def generate(self, b, h, w):
        v1 = torch.randint(0, 2, size=(b, h, 1), device=self.device, dtype=self.dtype, generator=self.generator) * 2 - 1
        v2 = torch.randint(0, 2, size=(b, 1, w), device=self.device, dtype=self.dtype, generator=self.generator) * 2 - 1

        return v1 @ v2

class Rank1Sparse(Matrix):
    WEIGHT = 0.5
    BASE = False
    def generate(self, b, h, w):
        p1 = self.rng.random.triangular(1e-12, 1, 1e-12) ** 2
        p2 = self.rng.random.triangular(1e-12, 1, 1e-12) ** 2
        v1 = torch.bernoulli(torch.full((b, h, 1), p1, device=self.device, dtype=self.dtype), generator=self.generator)
        v2 = torch.bernoulli(torch.full((b, 1, w), p2, device=self.device, dtype=self.dtype), generator=self.generator)

        return v1 @ v2

class SymmetricRank1Normal(Matrix):
    SQUARE = True
    WEIGHT = 0.25
    def generate(self, b, h, w):
        v = torch.randn((b, h), device=self.device, dtype=self.dtype, generator=self.generator)
        return v.unsqueeze(-1) @ v.unsqueeze(-2)

class SymmetricRank1Sparse(Matrix):
    SQUARE = True
    WEIGHT = 0.25
    def generate(self, b, h, w):
        p = self.rng.random.triangular(1e-12, 1, 1e-12) ** 2
        v = torch.bernoulli(torch.full((b, h), p, device=self.device, dtype=self.dtype), generator=self.generator)
        return v.unsqueeze(-1) @ v.unsqueeze(-2)

class Rank1Correction(Matrix):
    def generate(self, b, h, w):
        v1 = torch.randn((b, h, 1), device=self.device, dtype=self.dtype, generator=self.generator)
        v2 = torch.randn((b, 1, w), device=self.device, dtype=self.dtype, generator=self.generator)
        return self.get_random_matrix(b, h, w, base=False) + v1 @ v2

class SR1Correction(Matrix):
    SQUARE = True
    def generate(self, b, h, w):
        v = torch.randn((b, h), device=self.device, dtype=self.dtype, generator=self.generator)
        return self.get_random_matrix(b, h, w, base=False) + v.unsqueeze(-1) @ v.unsqueeze(-2)

class TimesRank1(Matrix):
    def generate(self, b, h, w):
        v1 = torch.randn((b, h, 1), device=self.device, dtype=self.dtype, generator=self.generator)
        v2 = torch.randn((b, 1, w), device=self.device, dtype=self.dtype, generator=self.generator)
        return self.get_random_matrix(b, h, w, base=False) * (v1 @ v2)


class Tile(Matrix):
    BASE = False
    def generate(self, b, h, w):
        h_n = math.ceil(self.rng.random.uniform(2, h/2))
        h_k = math.ceil(h / h_n)

        w_n = math.ceil(self.rng.random.uniform(2, w/2))
        w_k = math.ceil(w / w_n)
        A = self.get_random_matrix(b, h_n, w_n, base=False)
        return A.tile(1, h_k, w_k)[:,:h, :w]

class ScatterTile(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        if h == 1 or w == 1:
            return self.get_random_matrix(b, h, w, base=True)

        A = self.get_random_matrix(b, math.ceil(h/2), math.ceil(w/2), base=False)
        B = self.get_random_matrix(b, math.ceil(h/2), math.ceil(w/2), base=False)

        res = torch.zeros((b, math.ceil(h/2)*2, math.ceil(w/2)*2), device=self.device, dtype=self.dtype)
        res[:, ::2, ::2] = A
        res[:, 1::2, 1::2] = B

        return res[:, :h, :w]


class ConstantRow(Matrix):
    WEIGHT = 0.2
    BASE = False
    def generate(self, b, h, w):
        v = torch.randn((b, h, 1), device=self.device, dtype=self.dtype, generator=self.generator)
        return v.repeat(1, 1, w)

class ConstantCol(Matrix):
    WEIGHT = 0.2
    BASE = False
    def generate(self, b, h, w):
        v = torch.randn((b, 1, w), device=self.device, dtype=self.dtype, generator=self.generator)
        return v.repeat(1, h, 1)

class RowMean(Matrix):
    WEIGHT = 0.2
    BASE = False
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        return A.mean(1, keepdim=True).repeat_interleave(repeats=h, dim=1).clone()

class ColMean(Matrix):
    WEIGHT = 0.2
    BASE = False
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        return A.mean(2, keepdim=True).repeat_interleave(repeats=w, dim=2).clone()

_batched_block_diagonal2 = torch.vmap(torch.block_diag, in_dims=(0,0))
_batched_block_diagonal3 = torch.vmap(torch.block_diag, in_dims=(0,0,0))
_batched_block_diagonal4 = torch.vmap(torch.block_diag, in_dims=(0,0,0,0))

def batched_block_diagonal(*tensors):
    if len(tensors) == 2: return _batched_block_diagonal2(*tensors)
    if len(tensors) == 3: return _batched_block_diagonal3(*tensors)
    if len(tensors) == 4: return _batched_block_diagonal4(*tensors)
    return torch.vmap(torch.block_diag, in_dims=tuple(0 for _ in tensors))(*tensors)

class BlockDiagonal(Matrix):
    """up to 4 blocks"""
    BRANCHES = True
    def generate(self, b, h, w):
        if min(h, w) <= 2: return self.get_random_matrix(b, h, w, base=False)
        n = min(self.rng.random.randint(2, min(h, w)), 4)

        # splits
        h_splits = self.rng.numpy.uniform(0, 1, size=n)
        h_splits *= h / h_splits.sum()
        h_splits = np.ceil(h_splits.clip(min=1)).astype(np.int32).tolist()

        w_splits = self.rng.numpy.uniform(0, 1, size=n)
        w_splits *= w / w_splits.sum()
        w_splits = np.ceil(w_splits.clip(min=1)).astype(np.int32).tolist()

        tensors = []
        for hs, ws in zip(h_splits, w_splits):
            tensors.append(self.get_random_matrix(b, hs, ws, base=False))

        return batched_block_diagonal(*tensors)[:,:h,:w]

class FFTNReal(Matrix):
    def generate(self, b, h, w):
        dim = self.rng.random.choice(((1,), (2,), (1, 2)))
        A = self.get_random_matrix(b, h, w, base=False)
        return torch.fft.fftn(A, dim=dim).real.to(self.dtype) # pylint:disable=not-callable

class FFTNImag(Matrix):
    def generate(self, b, h, w):
        dim = self.rng.random.choice(((1,), (2,), (1, 2)))
        A = self.get_random_matrix(b, h, w, base=False)
        return torch.fft.fftn(A, dim=dim).imag.to(self.dtype) # pylint:disable=not-callable

class IFFTN(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        dim = self.rng.random.choice(((1,), (2,), (1, 2)))
        s = [(b, h, w)[d] for d in dim]

        A = self.get_random_matrix(b, h, w, base=False)
        B = self.get_random_matrix(b, h, w, base=False)
        C = torch.complex(A, B)
        rec = torch.fft.ifftn(C, dim=dim, s=s) # pylint:disable=not-callable

        if self.rng.random.random() > 0.5:
            return rec.real.to(self.dtype)

        return rec.imag.to(self.dtype)

class SpectralMix(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        dim = self.rng.random.choice(((1,), (2,), (1, 2)))
        s = [(b, h, w)[d] for d in dim]

        A = self.get_random_matrix(b, h, w, base=False)
        B = self.get_random_matrix(b, h, w, base=False)

        A_fft = torch.fft.rfftn(A, dim=dim) # pylint:disable=not-callable
        B_fft = torch.fft.rfftn(B, dim=dim) # pylint:disable=not-callable

        C = torch.abs(A_fft) * torch.exp(1j * torch.angle(B_fft))
        rec = torch.fft.irfftn(C, dim=dim, s=s) # pylint:disable=not-callable

        return rec

class PassFilter(Matrix):
    def generate(self, b, h, w):
        dim = self.rng.random.choice(((1,), (2,), (1, 2)))
        s = [(b, h, w)[d] for d in dim]


        if dim == (1, ):
            trunc = (self.rng.random.randrange(1, max(h, 2)), w)
        elif dim == (2, ):
            trunc = (h, self.rng.random.randrange(1, max(w, 2)))
        elif dim == (1, 2):
            trunc = (self.rng.random.randrange(1, max(h, 2)), self.rng.random.randrange(1, max(w, 2)))
        else:
            raise ValueError(dim)

        A = self.get_random_matrix(b, h, w, base=True)
        if self.rng.random.random() > 0.5:
            A_fft = torch.fft.rfftn(A, dim=dim)[:, :trunc[0], :trunc[1]] # pylint:disable=not-callable
        else:
            A_fft = torch.fft.rfftn(A, dim=dim)[:, -trunc[0]:, -trunc[1]:] # pylint:disable=not-callable

        rec = torch.fft.irfftn(A_fft, dim=dim, s=s) # pylint:disable=not-callable

        return rec


class MoorePenrose(Matrix):
    MAX_NUMEL = MAX_LINALG_NUMEL
    MAX_SIZE = MAX_LINALG_SIZE
    WEIGHT = 0.1
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        try:
            return torch.linalg.pinv(A).mH # pylint:disable=not-callable
        except torch.linalg.LinAlgError:
            return A

class LeastSquares(Matrix):
    MAX_NUMEL = MAX_LINALG_NUMEL
    MAX_SIZE = MAX_LINALG_SIZE
    BRANCHES = True
    WEIGHT = 0.1
    def generate(self, b, h, w):
        k = self.rng.random.randint(1, min(h,w)*2)
        A = self.get_random_matrix(b, k, h, base=False)
        B = self.get_random_matrix(b, k, w, base=False)
        try:
            return torch.linalg.lstsq(A, B).solution # pylint:disable=not-callable
        except torch.linalg.LinAlgError:
            return A.mH @ B

class Vandermonde(Matrix):
    WEIGHT = 0.1
    def generate(self, b, h, w):
        if h == 1 or w == 1: return self.get_random_matrix(b,h,w, base=True)

        v = self.get_random_matrix(1, b, h, base=True)[0]
        return torch.linalg.vander(v, N=w) # pylint:disable=not-callable

class Cholesky(Matrix):
    SQUARE = True
    MAX_NUMEL = MAX_LINALG_NUMEL * 2
    MAX_SIZE = MAX_LINALG_SIZE
    WEIGHT = 0.1
    def generate(self, b, h, w):
        assert h == w

        A = self.get_random_matrix(b, h, h, base=True)
        L, info = torch.linalg.cholesky_ex(A, upper=random.choice((True, False))) # pylint:disable=not-callable
        return L

class Sketch(Matrix):
    """projects"""
    SQUARE = True
    BRANCHES = True
    MAX_NUMEL = MAX_LINALG_NUMEL * 4
    MAX_SIZE = MAX_LINALG_SIZE * 2
    def generate(self, b, h, w):
        assert h == w

        k = self.rng.random.randint(1, h)
        A = self.get_random_matrix(b, h, h, base=False)
        S = self.get_random_matrix(b, k, h, base=False)

        ch = self.rng.random.choice((1,2,3))

        if ch == 1:
            S = torch.linalg.qr(S.mH).Q.mH # pylint:disable=not-callable

        if ch == 3:
            smh = torch.linalg.pinv(S) # pylint:disable=not-callable
            return smh @ (S @ A @ smh) @ S

        return S.mH @ (S @ A @ S.mH) @ S

class Unproject(Matrix):
    """projects"""
    SQUARE = True
    BRANCHES = True
    def generate(self, b, h, w):
        assert h == w

        k = self.rng.random.randint(1, h)
        A = self.get_random_matrix(b, k, k, base=False)
        S = self.get_random_matrix(b, k, h, base=False)

        return S.mH @ A @ S

class ProjectUnproject(Matrix):
    SQUARE = True
    BRANCHES = True
    def generate(self, b, h, w):
        assert h == w
        k = self.rng.random.randint(1, h * 2)
        A = self.get_random_matrix(b, h, h, base=False)
        S = self.get_random_matrix(b, h, k, base=False)
        return (A @ S) @ S.mH

class LDL(Matrix):
    SQUARE = True
    MAX_NUMEL = MAX_LINALG_NUMEL
    MAX_SIZE = MAX_LINALG_SIZE
    WEIGHT = 0.1
    def generate(self, b, h, w):
        assert h == w

        A = self.get_random_matrix(b, h, h, base=True)
        LD, pivots, info = torch.linalg.ldl_factor_ex(A) # pylint:disable=not-callable
        return LD

class Permutation(Matrix):
    WEIGHT = 0.5
    def generate(self, b, h, w):
        I = torch.eye(h, w, device=self.device, dtype=self.dtype).unsqueeze(0).repeat_interleave(repeats=b, dim=0).clone()
        return I[:, torch.randperm(h, device=self.device)]


class ReplacePatch(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        if h <= 1 or w <= 1: return A

        h_start = self.rng.random.randrange(0, h-1)
        w_start = self.rng.random.randrange(0, w-1)
        h_end = self.rng.random.randrange(h_start+1, h)
        w_end = self.rng.random.randrange(w_start+1, w)

        A[:, h_start:h_end, w_start:w_end] = self.get_random_matrix(b, h_end-h_start, w_end-w_start, base=False)
        return A

class BinaryFuncPatch(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        if h <= 1 or w <= 1: return A

        h_start = self.rng.random.randrange(0, h-1)
        w_start = self.rng.random.randrange(0, w-1)
        h_end = self.rng.random.randrange(h_start+1, h)
        w_end = self.rng.random.randrange(w_start+1, w)

        B = self.get_random_matrix(b, h_end-h_start, w_end-w_start, base=False)
        fn = self.rng.random.choice(_BINARY_FUNCS)
        A[:, h_start:h_end, w_start:w_end] = fn(A[:, h_start:h_end, w_start:w_end], B)
        return A

class Conv2D(Matrix):
    BRANCHES = True
    MAX_NUMEL = MAX_LINALG_NUMEL * 4
    MAX_SIZE = MAX_LINALG_SIZE * 4
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        if h <= 2 or w <= 2: return A

        filt_h = min(math.floor(self.rng.random.triangular(1, h-1, 1)), 16)
        filt_w = min(math.floor(self.rng.random.triangular(1, w-1, 1)), 16)
        use_dilation = self.rng.random.random() > 0.5
        if use_dilation and min(h-1, w-1) > 1:
            dilation = min(math.floor(self.rng.random.triangular(1, min(h-1, w-1), 1)), 16)
        else:
            dilation = 1

        filt = self.get_random_matrix(b, filt_h, filt_w, base=False).unsqueeze(1)
        A = F.conv2d(A.unsqueeze(0), filt, padding='same', dilation=dilation, groups=b) # pylint:disable=not-callable

        return A.squeeze(0)

class Cut(Matrix):
    def generate(self, b, h, w):
        rows = h + self.rng.random.randrange(0, max(h//4, 1))
        cols = w + self.rng.random.randrange(0, max(w//4, 1))

        ch = self.rng.random.choice([0,1,2])
        if ch == 0: rows = h
        if ch == 1: cols = w

        A = self.get_random_matrix(b, rows, cols, base=True)

        if self.rng.random.random() > 0.5: A = A[:, :h]
        else: A = A[:, -h:]

        if self.rng.random.random() > 0.5: A = A[:, :, :w]
        else: A = A[:, :, -w:]

        return A


class GridSample(Matrix):
    BRANCHES = True
    MAX_NUMEL = MAX_LINALG_NUMEL
    MAX_SIZE = MAX_LINALG_SIZE
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)

        if self.rng.random.random() > 0.5:
            grid1 = self.get_random_matrix(b, h, w, base=False)
            grid2 = self.get_random_matrix(b, h, w, base=False)
            grid = torch.stack([grid1, grid2], -1)
        else:
            grids = self.get_random_matrix(b*2, h, w, base=False)
            grid = torch.stack([grids[:b], grids[b:]], -1)

        mode = self.rng.random.choice(['bilinear', "nearest", "bicubic"])
        padding_mode = self.rng.random.choice(['zeros', 'border', 'reflection'])
        align_corners = self.rng.random.random() > 0.5
        A = F.grid_sample(
            A.unsqueeze(1), grid, mode=mode, padding_mode=padding_mode, align_corners=align_corners
        ).squeeze(1) # pylint:disable=not-callable

        return A

class BatchOp(Matrix):
    def generate(self, b, h, w):
        A = self.get_random_matrix(b*2, h, w, base=True)
        A1 = A[:b]
        A2 = A[b:]
        fn = self.rng.random.choice(_BINARY_FUNCS)
        return fn(A1, A2)

class BatchTransposeH(Matrix):
    def generate(self, b, h, w):
        return self.get_random_matrix(h, b, w, base=True).moveaxis(1, 0)

class BatchTransposeW(Matrix):
    def generate(self, b, h, w):
        return self.get_random_matrix(h, w, b, base=True).moveaxis(-1, 0)

def sinkhorn(logits: torch.Tensor, iters: int) -> torch.Tensor:
    log_alpha = logits
    for _ in range(iters):
        log_alpha = log_alpha - torch.logsumexp(log_alpha, dim=-1, keepdim=True)
        log_alpha = log_alpha - torch.logsumexp(log_alpha, dim=-2, keepdim=True)
    return torch.exp(log_alpha)

class Sinkhorn(Matrix):
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        iters = self.rng.random.randrange(1, 10)
        return sinkhorn(A, iters)

class ReshapeMess(Matrix):
    def generate(self, b, h, w):
        if h <= 2: return self.get_random_matrix(b, h, w, base=False)
        hr = self.rng.random.randrange(1, h-1)
        wr = math.ceil((h * w) / hr)

        A = self.get_random_matrix(b, hr, wr, base=False).reshape(b, -1)
        A = A[:, :h*w]
        return A.reshape(b, h, w)

class BatchUnwrap(Matrix):
    def generate(self, b, h, w):
        if h <= 2: return self.get_random_matrix(b, h, w, base=True)
        n = b * h * w

        br = self.rng.random.randrange(1, min(max(n-2, 2), 1024))
        hr = self.rng.random.randrange(1, max(2, math.ceil(n/br - 1)))
        wr = math.ceil(n / (hr * br))

        A = self.get_random_matrix(br, hr, wr, base=False).ravel()
        A = A[:b*h*w]
        return A.reshape(b, h, w)

def _dtype_clip(v, finfo: torch.finfo):
    if v > finfo.max / 2:
        return finfo.max / 2
    if v < finfo.min:
        return finfo.min / 2
    return v

def _get_triangular_val(A: torch.Tensor, rng: RNG):
    fi = torch.finfo(A.dtype)
    Amin = _dtype_clip(A.amin().item(), fi)
    Amax = _dtype_clip(A.amax().item(), fi)
    s = _dtype_clip(Amax - Amin, fi)
    if Amax > 0: Amin = min(Amin, 0)
    if Amin < 0: Amax = max(Amax, 0)


    return rng.random.triangular(_dtype_clip(Amin-s , fi), _dtype_clip(Amax+s, fi))

class SetValue(Matrix):
    WEIGHT = 4
    def generate(self, b, h, w):
        x = self.rng.random.randrange(0, h)
        y = self.rng.random.randrange(0, w)
        A = self.get_random_matrix(b, h, w, base=True)
        A[:, x, y] = _get_triangular_val(A, self.rng)
        return A

class SetRow(Matrix):
    def generate(self, b, h, w):
        x = self.rng.random.randrange(0, h)
        A = self.get_random_matrix(b, h, w, base=True)
        A[:, x] = _get_triangular_val(A, self.rng)
        return A

class SetCol(Matrix):
    def generate(self, b, h, w):
        y = self.rng.random.randrange(0, w)
        A = self.get_random_matrix(b, h, w, base=True)
        A[:, :, y] = _get_triangular_val(A, self.rng)
        return A

class SoftenNorm(Matrix):
    WEIGHT = 10
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)

        p = self.rng.random.choice([2, torch.inf])
        norm = torch.linalg.vector_norm(A, p, dim=(-2,-1), keepdim=True) # pylint:disable=not-callable
        if (norm < torch.finfo(A.dtype).tiny * 2).any():
            A = A + torch.randn_like(A) * 0.1
            norm = torch.linalg.vector_norm(A, p, dim=(-2,-1), keepdim=True) # pylint:disable=not-callable

        target_norm = norm.lerp(torch.ones_like(norm), weight=self.rng.random.triangular(0,1,0)**2)
        scale = target_norm / norm

        return A * scale


class SoftenMean(Matrix):
    WEIGHT = 10
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        mean = A.mean((1,2), keepdim=True) * self.rng.random.triangular(0,1,0)**2
        return A - mean

class Negative(Matrix):
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        return A.amax() - A

# those three are to make matrices more random on average
class AddNoise(Matrix):
    WEIGHT = 3
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        norm = torch.linalg.vector_norm(A, dim=(-2,-1), keepdim=True) # pylint:disable=not-callable
        scale = norm * self.rng.random.triangular(0, 1, 0)**2

        r = torch.randn(A.size(), device=A.device, dtype=A.dtype, generator=self.generator) * scale
        A += r
        return A

class MulNoise(Matrix):
    WEIGHT = 3
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        scale = self.rng.random.triangular(0, 1, 0)**2
        r = torch.randn(A.size(), device=A.device, dtype=A.dtype, generator=self.generator) * scale
        A *= (r + 1)
        return A

class Jitter(Matrix):
    SQUARE = True
    WEIGHT = 5
    def generate(self, b, h, w):
        assert h == w

        A = self.get_random_matrix(b, h, h, base=False)
        eps = torch.finfo(A.dtype).eps
        return A + torch.randn(A.size(-1), device=A.device, dtype=A.dtype, generator=self.generator) * eps

class Roll(Matrix):
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        dim = self.rng.random.choice([1,2])
        maxdim = A.size(dim)
        if maxdim == 1: return A
        n = self.rng.random.randrange(1, maxdim)
        A = A.roll(n, dim)
        return A

class FlatRoll(Matrix):
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        maxdim = h * w
        if maxdim == 1: return A

        n = self.rng.random.randrange(1, maxdim)
        A = A.reshape(b, -1).roll(n, 1).reshape(b, h, w)
        return A

class Cumsum(Matrix):
    WEIGHT = 0.2
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)

        if b == 1: dim = self.rng.random.choice([1, 2])
        else: dim = self.rng.random.choice([0, 1, 2])

        return A.cumsum(dim)

class Cummax(Matrix):
    WEIGHT = 0.1
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)

        if b == 1: dim = self.rng.random.choice([1, 2])
        else: dim = self.rng.random.choice([0, 1, 2])

        values, indices = A.cummax(dim)
        return values

class Cummin(Matrix):
    WEIGHT = 0.1
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)

        if b == 1: dim = self.rng.random.choice([1, 2])
        else: dim = self.rng.random.choice([0, 1, 2])

        values, indices = A.cummin(dim)
        return values

class Cumprod(Matrix):
    WEIGHT = 0.05
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        A = A / A.std().clip(min=1).nan_to_num(1,1,1)

        if b == 1: dim = self.rng.random.choice([1, 2])
        else: dim = self.rng.random.choice([0, 1, 2])

        return A.cumprod_(dim)

class FlatCumsum(Matrix):
    WEIGHT = 0.2
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True).reshape(b, -1)
        return A.cumsum(-1).reshape(b, h, w)

class FlatCummax(Matrix):
    WEIGHT = 0.05
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True).reshape(b, -1)
        values, indices = A.cummax(-1)
        return values.reshape(b, h, w)

class FlatCummin(Matrix):
    WEIGHT = 0.05
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True).reshape(b, -1)
        values, indices = A.cummin(-1)
        return values.reshape(b, h, w)

class Sort(Matrix):
    WEIGHT = 0.5
    MAX_NUMEL = MAX_LINALG_NUMEL * 8
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)

        if b == 1: dim = self.rng.random.choice([1, 2])
        else: dim = self.rng.random.choice([0, 1, 2])

        sorted, indices = A.sort(dim)
        return sorted

class SortNorms(Matrix):
    WEIGHT = 0.5
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)

        dim = self.rng.random.choice([1, 2])
        p = self.rng.random.choice([-torch.inf, -2, -1, -0.5, 0.5, 1, 2, torch.inf])
        indices = torch.linalg.vector_norm(A, p, dim=(0, 3-dim), keepdim=True).argsort(dim) # pylint:disable=not-callable
        return A.take_along_dim(indices, dim)

class Argsort(Matrix):
    MAX_NUMEL = MAX_LINALG_NUMEL * 8
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)

        if b == 1: dim = self.rng.random.choice([1, 2])
        else: dim = self.rng.random.choice([0, 1, 2])

        return A.argsort(dim).to(dtype=A.dtype)

class Rank(Matrix):
    MAX_NUMEL = MAX_LINALG_NUMEL * 8
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)

        if b == 1: dim = self.rng.random.choice([1, 2])
        else: dim = self.rng.random.choice([0, 1, 2])

        return A.argsort(dim).argsort(dim).to(dtype=A.dtype)

class SortVia(Matrix):
    BRANCHES = True
    MAX_NUMEL = MAX_LINALG_NUMEL * 8
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        S = self.get_random_matrix(b, h, w, base=True)

        dim = self.rng.random.choice([1, 2])

        indices = S.argsort(dim)
        return A.take_along_dim(indices, dim=dim)

class FlatSort(Matrix):
    WEIGHT = 0.5
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True).reshape(b, -1)
        sorted, indices = A.sort(-1)
        return sorted.reshape(b, h, w)

class FlatArgsort(Matrix):
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True).reshape(b, -1)
        return A.argsort(-1).reshape(b, h, w).to(dtype=A.dtype)

class FlatRank(Matrix):
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True).reshape(b, -1)
        return A.argsort(-1).argsort(-1).reshape(b, h, w).to(dtype=A.dtype)

class FlatSortVia(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        S = self.get_random_matrix(b, h, w, base=True)

        indices = S.reshape(b, -1).argsort(-1)
        return A.reshape(b, -1).take_along_dim(indices, dim=-1).reshape(b, h, w)


def batched_eye(size:Sequence[int], dtype=None, device=None):
    n,m = size[-2:]
    eye = torch.eye(n,m, device=device,dtype=dtype)
    if len(size) > 2:
        for s in reversed(size[:-2]):
            eye = eye.unsqueeze(0).repeat_interleave(s, 0)

    return eye

def eye_like(tensor:torch.Tensor):
    return batched_eye(tensor.size(), dtype=tensor.dtype, device=tensor.device)

def zeropower_ns(X:torch.Tensor, niter):
    # X = X / (X.norm(dim=(-2, -1), keepdim=True).clip(min=torch.finfo(X.dtype).tiny * 2))
    I = eye_like(X)

    for _ in range(niter):
        X = 0.5 * X @ (3 * I - X.mT @ X)

    return X

class ZeropowerNS(Matrix):
    SQUARE = True
    def generate(self, b, h, w):
        assert h == w
        A = self.get_random_matrix(b, h, h, base=False)
        iters = self.rng.random.randrange(1, 10)
        return zeropower_ns(A, iters)

class Circulant(Matrix):
    SQUARE = True
    WEIGHT = 0.2
    BASE = False
    def generate(self, b, h, w):
        assert h == w
        c = self.get_random_matrix(1, b, h, base=True).numpy(force=True)[0]
        circulant = scipy.linalg.circulant(c).copy()
        return torch.from_numpy(circulant).contiguous().to(device=self.device, dtype=self.dtype)

class Fielder(Matrix):
    SQUARE = True
    WEIGHT = 0.2
    BASE = False
    def generate(self, b, h, w):
        assert h == w
        c = self.get_random_matrix(1, b, h, base=True).numpy(force=True)[0]
        fiedler = scipy.linalg.fiedler(c).copy()
        return torch.from_numpy(fiedler).contiguous().to(device=self.device, dtype=self.dtype)

class Toeplitz(Matrix):
    WEIGHT = 0.2
    MAX_NUMEL = 128 * 1024 * 1024
    BASE = False
    def generate(self, b, h, w):
        if b > 128: return self.get_random_matrix(b, h, w, base=True)

        c = self.get_random_matrix(1, b, h, base=True).numpy(force=True)[0]
        if h == w and self.rng.random.random() > 0.5:
            r = [None] * b
        else:
            r = self.get_random_matrix(1, b, w, base=True).numpy(force=True)[0]

        toeplitz = np.stack([scipy.linalg.toeplitz(c_i, r_i) for c_i, r_i in zip(c, r)])
        return torch.from_numpy(toeplitz).contiguous().to(device=self.device, dtype=self.dtype)

class Hankel(Matrix):
    WEIGHT = 0.2
    MAX_NUMEL = 128 * 1024 * 1024
    BASE = False
    def generate(self, b, h, w):
        if b > 128: return self.get_random_matrix(b, h, w, base=True)

        c = self.get_random_matrix(1, b, h, base=True).numpy(force=True)[0]
        if h == w and self.rng.random.random() > 0.5:
            r = [None] * b
        else:
            r = self.get_random_matrix(1, b, w, base=True).numpy(force=True)[0]

        toeplitz = np.stack([scipy.linalg.hankel(c_i, r_i) for c_i, r_i in zip(c, r)])
        return torch.from_numpy(toeplitz).contiguous().to(device=self.device, dtype=self.dtype)

class Hadamard(Matrix):
    WEIGHT = 0.2
    SQUARE = True
    BASE = False
    def generate(self, b, h, w):
        if b > 1: return self.get_random_matrix(b, h, w, base=True)
        if math.log2(h) % 1 != 0: return self.get_random_matrix(b, h, w, base=True)

        hadamard = scipy.linalg.hadamard(h)[None, :]
        return torch.from_numpy(hadamard).contiguous().to(device=self.device, dtype=self.dtype)

class DFT(Matrix):
    WEIGHT = 0.2
    SQUARE = True
    BASE = False
    def generate(self, b, h, w):
        if b > 1: return self.get_random_matrix(b, h, w, base=True)

        scale = self.rng.random.choice([None, "sqrtn", "n"])
        dft = scipy.linalg.dft(h, scale=scale)[None, :]

        if self.rng.random.random() > 0.5: A = dft.real
        else: A = dft.imag
        return torch.from_numpy(A).contiguous().to(device=self.device, dtype=self.dtype)


class CopySign(Matrix):
    BRANCHES = True
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=False)
        B = self.get_random_matrix(b, h, w, base=False)
        return A.copysign(B)

# ----------------------------- AI SUGGESTED ONES ---------------------------- #
class RandomGraphLaplacian(Matrix):
    """L = D - A. Symmetric Positive Semi-Definite. apparently has some kind of specific sparsity pattern"""
    SQUARE = True
    WEIGHT = 0.1
    def generate(self, b, h, w):
        assert h == w
        p = self.rng.random.uniform(0.1, 0.5)
        A = torch.bernoulli(torch.full((b, h, h), p, device=self.device, dtype=self.dtype))
        A = A.triu(1) + A.triu(1).mH
        D = torch.diag_embed(A.sum(dim=-1))
        return D - A

class Householder(Matrix):
    """I - 2vv^T / v^Tv. Symmetric and Orthogonal."""
    SQUARE = True
    WEIGHT = 0.1
    def generate(self, b, h, w):
        v = torch.randn((b, h, 1), device=self.device, dtype=self.dtype, generator=self.generator)
        v_norm_sq = (v.mH @ v)

        I = torch.eye(h, device=self.device, dtype=self.dtype).unsqueeze(0)
        H = I - 2 * (v @ v.mH) / (v_norm_sq + torch.finfo(self.dtype).eps)
        return H

class CayleyRotation(Matrix):
    """(I - A)(I + A)^-1 for skew-symmetric A. Generates rotations (SO(n))."""
    SQUARE = True
    WEIGHT = 0.2
    MAX_SIZE = MAX_LINALG_SIZE
    def generate(self, b, h, w):
        X = self.get_random_matrix(b, h, h, base=True)
        A = X - X.mH
        I = torch.eye(h, device=self.device, dtype=self.dtype).unsqueeze(0)

        # Q = (I - A)(I + A)^-1
        numer = I - A
        denom = I + A
        return torch.linalg.solve(denom, numer) # pylint:disable=not-callable

class SkewSymmetric(Matrix):
    """A^T = -A. Eigenvalues are pure imaginary."""
    SQUARE = True
    WEIGHT = 0.2
    def generate(self, b, h, w):
        assert h == w
        A = self.get_random_matrix(b, h, h, base=True)
        return A - A.mH

class Nilpotent(Matrix):
    """Strictly Triangular (if square). A^k = 0 for k >= h."""
    WEIGHT = 0.2
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, w, base=True)
        if min(h, w) == 1: return A
        return A.triu(diagonal=1)

class Commutator(Matrix):
    """[A, B] = AB - BA. Trace is always 0."""
    SQUARE = True
    BRANCHES = True
    WEIGHT = 0.2
    def generate(self, b, h, w):
        A = self.get_random_matrix(b, h, h, base=False)
        B = self.get_random_matrix(b, h, h, base=False)
        return A @ B - B @ A

class Companion(Matrix):
    """
    Companion matrix of a polynomial.
    Ones on subdiagonal, random coeff on last column.
    """
    SQUARE = True
    WEIGHT = 0.1
    def generate(self, b, h, w):
        if h < 2: return self.get_random_matrix(b, h, h, base=True)

        # Subdiagonal ones
        res = torch.diag_embed(torch.ones((b, h-1), device=self.device, dtype=self.dtype), offset=-1)

        # Random last column (coefficients)
        coeffs = self.get_random_matrix(b, h, 1, base=True).squeeze(-1)
        res[:, :, -1] = -coeffs

        return res


# ---------------------------------------------------------------------------- #
#                                 all matrices                                 #
# ---------------------------------------------------------------------------- #
def _get_recursive_subclasses(cls:type) -> set[type]:
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in _get_recursive_subclasses(c)])

_MATRICES = [t for t in _get_recursive_subclasses(Matrix) if (not t.ABSTRACT) and (not inspect.isabstract(t))]
_BASE_MATRICES = [t for t in _MATRICES if t.BASE]
_RECTANGULAR_MATRICES = [t for t in _MATRICES if not t.SQUARE]
_RECTANGULAR_BASE_MATRICES = [t for t in _RECTANGULAR_MATRICES if t.BASE]

def _get_matrices(h:int, w:int, base:bool) -> list[type[Matrix]]:
    if h == w:
        if base: return _BASE_MATRICES
        return _MATRICES

    if base: return _RECTANGULAR_BASE_MATRICES
    return _RECTANGULAR_MATRICES

def _get_weight(matrix: type[Matrix], level, num_ops, branch_penalty, ops_penalty, size):
    if math.prod(size) > matrix.MAX_NUMEL: return 0
    if max(size) > matrix.MAX_SIZE: return 0
    w = matrix.WEIGHT
    if matrix.BRANCHES:
        w = w * ((branch_penalty ** level) * (ops_penalty ** num_ops))
    if matrix.INCREASE_PROB: w = w * 1.1 ** level
    return w

@torch.no_grad
def _get_random_matrix(
    b: int, h:int, w:int,

    base: bool,
    level: int,
    num_ops: int,
    branch_penalty: float,
    ops_penalty: float,

    dtype: torch.dtype,
    device: torch.types.Device,
    rng: RNG,
):
    t = '|'*(level-1)
    t = f'{t} '

    if h == 1 and w == 1:
        arr = rng.numpy.triangular(left=0, mode=0, right=1, size=(b,h,w))**10 * 10
        signs = torch.randint(0, 2, (b,h,w), generator=rng.torch(device), device=device, dtype=dtype) * 2 - 1
        return torch.as_tensor(arr, device=device, dtype=dtype).copysign(signs)

    if level >= 30 or num_ops >= 40:
        return torch.randn((b, h, w), dtype=dtype, device=device, generator=rng.torch(device))


    matrices = _get_matrices(h, w, base=base)
    weights = [_get_weight(m, level=level, num_ops=num_ops, branch_penalty=branch_penalty, ops_penalty=ops_penalty, size=(b, h, w)) for m in matrices]
    mtype = rng.random.choices(matrices, weights, k=1)[0]

    if VERBOSE:
        print(f'{t}Generating a {(b, h, w)} matrix with {mtype.__name__}, {level = }', file=VERBOSE_FILE)

    if any(i == 0 for i in (b, h, w)):
        raise RuntimeError('Requested a matrix with 0 shape')

    try:
        start = time.perf_counter()

        res = mtype(
            level=level, num_ops=num_ops, branch_penalty=branch_penalty,
            ops_penalty=ops_penalty, dtype=dtype, device=device, rng=rng
        ).generate(b, h, w)

        seconds = time.perf_counter() - start
        # if seconds > 1:
        #     if res.is_cuda: torch.cuda.empty_cache()

        if WARN_SECONDS_TO_GENERATE is not None and seconds >= WARN_SECONDS_TO_GENERATE:
            warnings.warn(f"generating a {(b, h, w)} matrix with {mtype.__name__} took {seconds} seconds.")

        if VERBOSE:
            print(f'{t}Generating a {(b, h, w)} matrix with {mtype.__name__} took {seconds:.5f} seconds, {level = }', file=VERBOSE_FILE)

    except (RuntimeError, ValueError, TypeError) as e:
        # add warning to see what type of matrix it was
        warnings.warn(f"Exception when generating a {(b, h, w)} matrix with {mtype.__name__}, {level = }")
        raise e from None # cuda out of memory

    except Exception as e:
        try:
            warnings.warn(
                f"Exception caught when generating a {(b, h, w)} matrix with {mtype.__name__}, {level = }:\n"
                f"{e.__class__.__name__}: {e}"
            )
            res = torch.randn((b, h, w), device=device, dtype=dtype, generator=rng.torch(device))
            if res.is_cuda: torch.cuda.empty_cache()

        except Exception:
             # cuda out of memory which for some reason every once in a while is a device assertion error
            warnings.warn(
                "Exception when printing exception when generating a "
                f"{(b, h, w)} matrix with {mtype.__name__}, {level = }"
            )
            raise e from None

    if res.shape != (b, h, w):
        raise RuntimeError(f"When generating a {(b, h, w)} matrix, {mtype.__name__} returned {res.shape} instead.")

    res = res.nan_to_num(0, 1, -1)

    empty_mask = (res - res.mean()).abs_().amax((1,2)) < torch.finfo(res.dtype).tiny * 2
    if empty_mask.any():
        res[empty_mask] = _get_random_matrix(
            b=int(empty_mask.sum().item()), h=h, w=w, base=base, level=level+1, num_ops=num_ops+1,
            branch_penalty=branch_penalty, ops_penalty = ops_penalty, dtype=dtype, device=device, rng=rng
        )

    return res

