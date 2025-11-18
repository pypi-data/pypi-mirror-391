<h1 align='center'>rstmat</h1>

With `rstmat` you can generate random structured matrices:

```py
from rstmat import random_matrix
matrices = []
for i in range(128):
    matrices.append(random_matrix((64, 64)))
```

<img width="3211" height="1611" alt="image" src="https://github.com/user-attachments/assets/96a1cdeb-900d-46b7-a207-87b57737fd61" />

It can also generate rectangular matrices

```py
for i in trange(16):
    matrices.append(random_matrix((512, 64))
```

<img width="3211" height="1553" alt="image" src="https://github.com/user-attachments/assets/6751ab53-0ebb-4d66-ac4a-097c21704820" />

You can also generate a batch of matrices which is faster. However note that all matrices in one batch will share the same tree of operations, so they will basically look similar:

```py
batch = random_matrix((16, 64, 64))
```

<img width="491" height="491" alt="image" src="https://github.com/user-attachments/assets/541818d8-7003-417d-8b8f-f39755c2502e" />

## Installation

```bash
pip install rstmat
```

## Why

If you want to test some algorithm on random matrices or fit some linear algebra approximation model, performance on matrices with normally-distributed entries rarely generalizes to performance on real tasks.
So I tried to fix that by generating random structured matrices.

## How it works

It picks a random matrix type of which there are many. For example `RandomNormal` generates a matrix with normally distributed entries.

However many matrix types generate other matrices by calling `random_matrix` recursively which is how you get structured matrices.

For example, `AAT` generates another matrix and computes $A A^\text{T}$. `AB` generates two matrices and computes their product. `RowCat` generates two matrices and concatenates rows. The matrices those generate might themselves request to generate more matrices.

## Distribution of generated matrices

I tried to make the matrices to be reasonable on average, but outliers happen too. We can look at various statistics to see what matrices are generated.

#### Value range

Matrices generally have reasonable values but sometimes you get matrices with very large values, although you will never get nans or infinities. So if applicable, it might be a good idea to normalize the generated matrices.

<details>
<summary>Statistics for 32 sample matrices</summary>

```python
matrices = []
for i in range(32):
    m = random_matrix((128, 128))
    print(f'min = {m.min().item():.5f}, max={m.max().item():.5f}, mean={m.mean().item():.5f}, std={m.std().item():.5f}')
```

output:

```
min = 0.00000, max=0.36568, mean=0.00170, std=0.01367
min = -0.00160, max=0.00799, mean=0.00136, std=0.00310
min = 0.00000, max=1.00000, mean=0.99530, std=0.05258
min = -0.00000, max=253.00000, mean=127.00000, std=52.77071
min = -4.12703, max=4.27076, mean=-0.00004, std=1.00000
min = -9.12002, max=17.89858, mean=0.71432, std=1.44218
min = -629844.50000, max=535442.31250, mean=641.08203, std=35570.25781
min = -3.12680, max=1.00000, mean=-0.05708, std=0.41463
min = -24.00136, max=31.31566, mean=0.00074, std=3.94008
min = 0.00000, max=1.63427, mean=0.40847, std=0.70762
min = -1648.49512, max=1648.49512, mean=-2.10210, std=576.00549
min = -6.42549, max=5.25735, mean=0.09184, std=0.54934
min = 0.00048, max=0.35305, mean=0.00781, std=0.00293
min = -0.10753, max=0.14890, mean=0.00001, std=0.01139
min = -29.89031, max=29.92242, mean=-0.20419, std=9.60233
min = 0.00000, max=0.41209, mean=0.00781, std=0.01416
min = -11.19279, max=-0.00000, mean=-8.53553, std=2.88449
min = 0.04000, max=6.61000, mean=2.68506, std=0.89763
min = -88875.07812, max=58857.13281, mean=30.58776, std=2343.74390
min = 0.00000, max=0.27113, mean=0.06860, std=0.05070
min = 54.00000, max=32738.00000, mean=16383.07324, std=7126.35986
min = -0.03120, max=0.03276, mean=0.00016, std=0.00781
min = 14.66208, max=221.25452, mean=68.65743, std=25.70100
min = -3.81714, max=3.63805, mean=-0.01195, std=1.01938
min = -0.81774, max=0.96052, mean=0.01563, std=0.23068
min = -0.99982, max=0.99983, mean=0.00088, std=0.07071
min = 0.00000, max=0.07785, mean=0.00439, std=0.00472
min = -0.00781, max=0.00781, mean=0.00008, std=0.00781
min = -0.77746, max=0.97658, mean=0.00157, std=0.03935
min = -0.99463, max=1.02445, mean=0.00028, std=0.15895
min = -965.15588, max=-79.21937, mean=-152.21527, std=76.95900
min = -8.93437, max=16.87033, mean=0.02283, std=0.62715
```

</details>

#### Rank and condition number

Around 75% of generated matrices are full-rank, condition number varies greatly. Although this depends on size of the matrix.
<details>
<summary>Statistics for 32 sample matrices</summary>

```python
matrices = []
for i in range(32):
    m = random_matrix((128, 128))
    print(f'rank = {torch.linalg.matrix_rank(m).item()}/128, cond={torch.linalg.cond(m).item()}')
```

output:

```
rank = 7/128, cond=inf
rank = 127/128, cond=212265.09375
rank = 26/128, cond=inf
rank = 128/128, cond=17851.337890625
rank = 128/128, cond=408.2425231933594
rank = 128/128, cond=2853.546630859375
rank = 68/128, cond=inf
rank = 97/128, cond=17166084.0
rank = 128/128, cond=861.2491455078125
rank = 3/128, cond=inf
rank = 64/128, cond=3450434816.0
rank = 126/128, cond=278033.75
rank = 128/128, cond=3300.02783203125
rank = 127/128, cond=40797840.0
rank = 128/128, cond=220.8697052001953
rank = 127/128, cond=72893.875
rank = 3/128, cond=inf
rank = 128/128, cond=1.0
rank = 128/128, cond=444.19927978515625
rank = 115/128, cond=880844.1875
rank = 127/128, cond=199054.265625
rank = 120/128, cond=361688704.0
rank = 128/128, cond=29997.986328125
rank = 128/128, cond=509.33160400390625
rank = 128/128, cond=11920.4072265625
rank = 2/128, cond=inf
rank = 8/128, cond=inf
rank = 79/128, cond=9.32627568546049e+22
rank = 13/128, cond=932012032000.0
rank = 128/128, cond=1.0
rank = 128/128, cond=3316.430419921875
rank = 121/128, cond=11409373184.0
```

</details>

## Performance

Generating large matrices (e.g. 4096 by 4096) might take up to a few seconds depending on how complicated the tree of operations is. You can make penalties stronger, for example:

```py
A = random_matrix((4096, 4096), branch_penalty=0.7, ops_penalty=0.7, device='cuda')
```

This will penalize very long operation trees, so you get simpler matrices, but it will be faster.

Most of the operations happen on the device you specify (default is `torch.get_default_device()` which defaults to CPU). Smaller matrices (under around 128 by 128) are typically faster to generate on CPU. Larger matrices become significantly faster on GPU.

For large matrices it is recommended to install opt_einsum and enable it:

```py
import torch.backends.opt_einsum
torch.backends.opt_einsum.enabled = opt_einsum
```

## Other stuff

It's easy to define new matrix types, you can look at the code in <https://github.com/inikishev/rstmat/blob/main/rstmat/matrix.py> .

What I found however is that when you make even a slight change to weights of matrix types, it might significantly impact final distribution, where some particular kind of matrix (e.g. sparse) becomes to dominate. All matrices have weights which determine the probabilities of getting picked, those are somewhat tuned to get diverse matrices.
