#include <stdio.h>
#include <stdlib.h>

enum { GRID_SIZE = 1 << 6 };

struct point {
  int x, y;
};

int last = 0;
char seen[(GRID_SIZE * GRID_SIZE - 1) / 3] = {0};
int array[GRID_SIZE][GRID_SIZE] = {{0}};

void print(void) {
  for (int j = 0; j < GRID_SIZE; ++j) {
    for (int i = 0; i < GRID_SIZE; ++i) {
      int val = array[i][j];
      if (val != -1 && !seen[val]) {
        seen[val] = 1;
        printf("(%d, %d)", i, j);
        if (array[i][j + 1] == val)
          printf(", (%d, %d)", i, j + 1);
        if (array[i + 1][j] == val)
          printf(", (%d, %d)", i + 1, j);
        if (array[i + 1][j + 1] == val)
          printf(", (%d, %d)", i + 1, j + 1);
        if (i > 0 && array[i - 1][j + 1] == val)
          printf(", (%d, %d)", i - 1, j + 1);
        printf("\n");
      }
    }
  }
}

void tile(int sz, struct point mark, struct point cur) {
  // 2x2, one is mark
  // * *  * X  X *  * *
  // * X  * *  * *  X *
  // can only be tiled in one way
  if (sz == 2) {
    ++last;
    for (int i = cur.x; i < (cur.x + 2); ++i) {
      for (int j = cur.y; j < (cur.y + 2); ++j) {
        if (!(i == mark.x && j == mark.y)) {
          array[i][j] = last;
        }
      }
    }
    return;
  }

  // middle and new marks: top right, top left, bottom right, bottom left
  struct point mid, tr, tl, br, bl;

  mid.x = cur.x + sz / 2;
  mid.y = cur.y + sz / 2;
  ++last;

  // the quadrant that contains the old mark is untouched
  // for the rest, tile an L with one cell in each quadrant
  // and make these cell their marks
  if (mark.x < mid.x && mark.y < mid.y) {
    tl = mark;
    tr = bl = br = mid;
    --tr.x;
    --bl.y;
    array[tr.x][tr.y] = array[bl.x][bl.y] = array[br.x][br.y] = last;
  } else if (mark.x < mid.x && mark.y >= mid.y) {
    tr = mark;
    tl = bl = br = mid;
    --tl.x;
    --tl.y;
    --bl.y;
    array[tl.x][tl.y] = array[bl.x][bl.y] = array[br.x][br.y] = last;
  } else if (mark.x >= mid.x && mark.y < mid.y) {
    bl = mark;
    tl = tr = br = mid;
    --tl.x;
    --tl.y;
    --tr.x;
    array[tl.x][tl.y] = array[tr.x][tr.y] = array[br.x][br.y] = last;
  } else if (mark.x >= mid.x && mark.y >= mid.y) {
    br = mark;
    tl = tr = bl = mid;
    --tl.x;
    --tl.y;
    --tr.x;
    --bl.y;
    array[tl.x][tl.y] = array[tr.x][tr.y] = array[bl.x][bl.y] = last;
  }

  tile(sz / 2, tl, cur);
  tile(sz / 2, tr, (struct point){cur.x, mid.y});
  tile(sz / 2, bl, (struct point){mid.x, cur.y});
  tile(sz / 2, br, (struct point){mid.x, mid.y});
}

int main(int argc, char *argv[]) {
  if (argc != 3) {
    fprintf(stderr, "Usage: %s X Y\n", argv[0]);
    return 1;
  }

  int x = atoi(argv[1]);
  int y = atoi(argv[2]);
  last = 0;

  if (x >= GRID_SIZE || y >= GRID_SIZE) {
    fprintf(stderr, "Invalid coords: %d %d\n", x, y);
    return 2;
  }

  array[x][y] = -1;
  tile(GRID_SIZE, (struct point){x, y}, (struct point){0, 0});
  print();

  return 0;
}
