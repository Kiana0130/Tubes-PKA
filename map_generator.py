import random
from typing import List, Tuple
from collections import deque
import settings

def get_size_for_level(level: int) -> int:
  return settings.LEVEL_SIZES.get(level, 16)

def _in_bounds(x: int, y: int, w: int, h: int) -> bool:
  return 0 <= x < w and 0 <= y < h

def _neighbors(x: int, y: int, w: int, h: int):
  for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    nx, ny = x + dx, y + dy
    if _in_bounds(nx, ny, w, h):
      yield nx, ny

def generate_maze(level: int) -> List[List[str]]:
  n = get_size_for_level(level)
  w = h = n

  grid = [['#' for _ in range(w)] for _ in range(h)]
  
  frontier = []

  sx = random.randrange(0, w)
  sy = random.randrange(0, h)
  grid[sy][sx] = '.'

  for nx, ny in _neighbors(sx, sy, w, h):
      frontier.append((nx, ny, sx, sy))

  while frontier:
    idx = random.randrange(0, len(frontier))
    x, y, from_x, from_y = frontier.pop(idx)

    if grid[y][x] == '.':
      continue

    passages = 0
    for nx, ny in _neighbors(x, y, w, h):
      if grid[ny][nx] == '.':
        passages += 1

    if passages == 1:
      grid[y][x] = '.'
      for nx, ny in _neighbors(x, y, w, h):
        if grid[ny][nx] == '#':
          frontier.append((nx, ny, x, y))

  start, goal = _place_start_and_goal(grid)

  key_positions = _place_keys(grid, settings.NUM_KEYS, forbidden={start, goal})

  sx, sy = start
  gx, gy = goal
  grid[sy][sx] = 'S'
  grid[gy][gx] = 'G'
  for kx, ky in key_positions:
    grid[ky][kx] = 'K'

  if not _is_reachable(grid, start, goal):
    return generate_maze(level)

  return grid

def _place_start_and_goal(grid: List[List[str]]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
  h = len(grid)
  w = len(grid[0])

  sides = ['top', 'bottom', 'left', 'right']
  pair = random.choice([('top', 'bottom'), ('left', 'right')])

  def random_on_side(side):
    if side == 'top':
      y = 0
      xs = list(range(w))
      random.shuffle(xs)
      for x in xs:
        if grid[y][x] == '.':
          return x, y
    if side == 'bottom':
      y = h - 1
      xs = list(range(w))
      random.shuffle(xs)
      for x in xs:
        if grid[y][x] == '.':
          return x, y
    if side == 'left':
      x = 0
      ys = list(range(h))
      random.shuffle(ys)
      for y in ys:
        if grid[y][x] == '.':
          return x, y
    if side == 'right':
      x = w - 1
      ys = list(range(h))
      random.shuffle(ys)
      for y in ys:
        if grid[y][x] == '.':
          return x, y
    return None
  
  start = random_on_side(pair[0])
  goal = random_on_side(pair[1])

  if start is None:
    start = _find_any_passage_on_side(grid, pair[0])
  if goal is None:
    goal = _find_any_passage_on_side(grid, pair[1])

  if start is None or goal is None or start == goal:
    passage_cells = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == '.']
    if len(passage_cells) >= 2:
      start = passage_cells[0]
      goal = passage_cells[-1]
    else:
      return _place_start_and_goal(grid)

  return start, goal

def _find_any_passage_on_side(grid: List[List[str]], side: str):
  h = len(grid)
  w = len(grid[0])
  if side == 'top':
    for x in range(w):
      if grid[0][x] == '.':
        return x, 0
  if side == 'bottom':
    for x in range(w):
      if grid[h - 1][x] == '.':
        return x, h - 1
  if side == 'left':
    for y in range(h):
      if grid[y][0] == '.':
        return 0, y
  if side == 'right':
    for y in range(h):
      if grid[y][w - 1] == '.':
        return w - 1, y
  return None

def _place_keys(grid: List[List[str]], num_keys: int, forbidden: set) -> List[Tuple[int, int]]:
  h = len(grid)
  w = len(grid[0])
  passage_cells = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == '.']
  passage_cells = [p for p in passage_cells if p not in forbidden]
  if not passage_cells:
    return []
  pos = random.choice(passage_cells)
  return [pos for _ in range(num_keys)]

def _is_reachable(grid: List[List[str]], start: Tuple[int, int], goal: Tuple[int, int]) -> bool:
  h = len(grid)
  w = len(grid[0])
  sx, sy = start
  gx, gy = goal
  if grid[sy][sx] == '#' or grid[gy][gx] == '#':
    return False
  
  visited = [[False] * w for _ in range(h)]
  dq = deque()
  dq.append((sx, sy))
  visited[sy][sx] = True

  while dq:
    x, y = dq.popleft()
    if (x, y) == (gx, gy):
      return True
    for nx, ny in _neighbors(x, y, w, h):
      if not visited[ny][nx] and grid[ny][nx] in ('.', 'S', 'G', 'K'):
        visited[ny][nx] = True
        dq.append((nx, ny))
  return False