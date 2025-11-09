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
    \"\"\"Generate a maze for given level.
    Returns a grid (list of lists) containing characters:
      '#' = wall, '.' = passage, 'S' = start, 'G' = goal, 'K' = key
    The function is a modified Prim's algorithm producing an imperfect maze
    with controlled loops (extra connections) to create many alternative routes.
    \"\"\"\n
    size = get_size_for_level(level)
    w = h = size

    # Start with all walls
    grid = [['#' for _ in range(w)] for _ in range(h)]

    # Prim: pick a random starting cell and mark as passage
    sx = random.randrange(0, w)
    sy = random.randrange(0, h)
    grid[sy][sx] = '.'

    # frontier walls: store (wx, wy, origin_x, origin_y)
    frontier = []
    for nx, ny in _neighbors(sx, sy, w, h):
        frontier.append((nx, ny, sx, sy))

    while frontier:
        idx = random.randrange(0, len(frontier))
        x, y, ox, oy = frontier.pop(idx)
        if grid[y][x] == '.':
            continue

        # count adjacent passages (to avoid creating large open areas)
        passages = 0
        for nx, ny in _neighbors(x, y, w, h):
            if grid[ny][nx] == '.':
                passages += 1

        # If it touches exactly one passage, carve it
        if passages == 1:
            grid[y][x] = '.'
            for nx, ny in _neighbors(x, y, w, h):
                if grid[ny][nx] == '#':
                    frontier.append((nx, ny, x, y))

    # Controlled carving to create loops (make maze imperfect)
    candidate_walls = set()
    for y in range(1, h-1):
        for x in range(1, w-1):
            if grid[y][x] != '#':
                continue
            if grid[y-1][x] == '.' and grid[y+1][x] == '.':
                candidate_walls.add((x, y))
            if grid[y][x-1] == '.' and grid[y][x+1] == '.':
                candidate_walls.add((x, y))

    loop_chance_map = {1: 0.12, 2: 0.08, 3: 0.05}
    loop_chance = loop_chance_map.get(level, 0.08)
    num_to_open = int(len(candidate_walls) * loop_chance)

    if num_to_open > 0 and candidate_walls:
        to_open = random.sample(list(candidate_walls), k=min(num_to_open, len(candidate_walls)))
        for x, y in to_open:
            grid[y][x] = '.'

    # Place start and goal on opposite sides (ensure they are on passage cells)
    start, goal = _place_start_and_goal(grid)

    # Place keys (NUM_KEYS) all in the same location (represented by a single 'K' cell)
    key_pos = _place_keys(grid, settings.NUM_KEYS, forbidden={start, goal})
    kxky = key_pos[0] if key_pos else None

    # mark S G K on grid
    sx, sy = start
    gx, gy = goal
    grid[sy][sx] = 'S'
    grid[gy][gx] = 'G'
    if kxky:
        kx, ky = kxky
        grid[ky][kx] = 'K'

    # Final safety: ensure reachability; if not reachable, carve a path between S and G
    if not _is_reachable(grid, start, goal):
        _carve_path_between(grid, start, goal)

    return grid

def _place_start_and_goal(grid: List[List[str]]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    h = len(grid)
    w = len(grid[0])
    pair = random.choice([('top', 'bottom'), ('left', 'right')])

    def find_passage_on_side(side):
        if side == 'top':
            y = 0
            xs = list(range(w))
            random.shuffle(xs)
            for x in xs:
                if grid[y][x] == '.':
                    return (x, y)
        if side == 'bottom':
            y = h - 1
            xs = list(range(w))
            random.shuffle(xs)
            for x in xs:
                if grid[y][x] == '.':
                    return (x, y)
        if side == 'left':
            x = 0
            ys = list(range(h))
            random.shuffle(ys)
            for y in ys:
                if grid[y][x] == '.':
                    return (x, y)
        if side == 'right':
            x = w - 1
            ys = list(range(h))
            random.shuffle(ys)
            for y in ys:
                if grid[y][x] == '.':
                    return (x, y)
        return None

    start = find_passage_on_side(pair[0])
    goal = find_passage_on_side(pair[1])

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
            raise RuntimeError("Cannot place start and goal: not enough passage cells")
    return start, goal

def _find_any_passage_on_side(grid: List[List[str]], side: str):
    h = len(grid)
    w = len(grid[0])
    if side == 'top':
        for x in range(w):
            if grid[0][x] == '.':
                return (x, 0)
    if side == 'bottom':
        for x in range(w):
            if grid[h - 1][x] == '.':
                return (x, h - 1)
    if side == 'left':
        for y in range(h):
            if grid[y][0] == '.':
                return (0, y)
    if side == 'right':
        for y in range(h):
            if grid[y][w - 1] == '.':
                return (w - 1, y)
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

def _carve_path_between(grid: List[List[str]], start: Tuple[int, int], goal: Tuple[int, int]):
    \"\"\"Carve a path between start and goal by finding a path that may go through walls
    and converting those cells to passages. This ensures connectivity without full regeneration.
    \"\"\"\n
    h = len(grid)
    w = len(grid[0])
    sx, sy = start
    gx, gy = goal

    # BFS that allows traversing walls but records parent to reconstruct path
    visited = [[False] * w for _ in range(h)]
    parent = [[None] * w for _ in range(h)]
    dq = deque()
    dq.append((sx, sy))
    visited[sy][sx] = True

    while dq:
        x, y = dq.popleft()
        if (x, y) == (gx, gy):
            break
        for nx, ny in _neighbors(x, y, w, h):
            if not visited[ny][nx]:
                visited[ny][nx] = True
                parent[ny][nx] = (x, y)
                dq.append((nx, ny))

    if not visited[gy][gx]:
        return

    cur = (gx, gy)
    while cur != (sx, sy):
        x, y = cur
        if grid[y][x] == '#':
            grid[y][x] = '.'
        cur = parent[y][x]
        if cur is None:
            break

    return
