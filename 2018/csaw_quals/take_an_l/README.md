# Take an L

## Challenge details
| Category | Points |
|:---------|-------:|
| misc     | 200    |

### Description
> Fill the grid with L's but avoid the marked spot for the W
> The origin is at (0,0) on the top left

## Write-up

`description.pdf` holds further details of the problem.
One important detail is that the grid is always `64 x 64`
and we have 5 seconds to send a response.

The solution is simple enough to express recursively:
- base case: a `2 x 2` square with a mark is tiled in the obvious way
- inductive step: if a `2^k x 2^k` square with a mark can be tiled,
  we tile a `2^(k + 1) x 2^(k + 1)` square by splitting it into four
  `2^k x 2^k` quadrants and tiling an L with one cell in each
  quadrant except the one with the mark. Consider the cells
  used for the tiling marked. Now all quadrants  are `2^k x 2^k`
  and contain one mark, so they can be tiled recursively.

The implementation is in `tile.c` and `takel.py`, invoked as:
```sh
$ gcc -O2 tile.c -o tile
$ python takel.py
```
#### Flag
```
flag{m@n_that_was_sup3r_hard_i_sh0uld_have_just_taken_the_L}
```
