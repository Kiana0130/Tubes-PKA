import random

def generate_maze(level):
    size = get_size_for_level(level)

    maze = [['#' for _ in range(size)] for _ in range(size)]

    def neighbors(x, y):
        dirs = [(2,0),(-2,0),(0,2),(0,-2)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x+dx, y+dy
            if 1 <= nx < size-1 and 1 <= ny < size-1:
                yield nx, ny, dx, dy

    stack = [(1,1)]
    maze[1][1] = '.'

    while stack:
        x, y = stack[-1]
        carved = False
        for nx, ny, dx, dy in neighbors(x, y):
            if maze[ny][nx] == '#':
                maze[y + dy//2][x + dx//2] = '.'
                maze[ny][nx] = '.'
                stack.append((nx, ny))
                carved = True
                break
        if not carved:
            stack.pop()

    loop_count = size * 3
    for _ in range(loop_count):
        x = random.randint(2, size-3)
        y = random.randint(2, size-3)
        if maze[y][x] == '#':
            open_neighbors = 0
            if maze[y+1][x] == '.': open_neighbors += 1
            if maze[y-1][x] == '.': open_neighbors += 1
            if maze[y][x+1] == '.': open_neighbors += 1
            if maze[y][x-1] == '.': open_neighbors += 1
            if open_neighbors >= 2:
                maze[y][x] = '.'

    open_cells = [(x,y) for y in range(size) for x in range(size) if maze[y][x]=='.']
    placed = set()
    for _ in range(max(1, level)):
        open_cells = [(x,y) for x,y in open_cells if maze[y][x]=='.' and (x,y) not in placed]
        if not open_cells:
            break
        kx, ky = random.choice(open_cells)
        maze[ky][kx] = 'K'
        placed.add((kx, ky))
    return maze

def get_size_for_level(level):
    if level == 1: return 21
    if level == 2: return 31
    return 41
