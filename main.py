import pygame
import sys
from Agen.guardian import Guardian
from core import map_generator
from core import settings
from Agen.A_Star import AStarAgent
from Agen.BFS import BFSAgent
import random

pygame.init()

LEVEL = 1

def draw_grid(screen, grid, tile_size):
    rows = len(grid)
    cols = len(grid[0])
    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            val = grid[y][x]

            if val == '#':
                color = settings.COLOR_WALL
            elif val == '.':
                color = settings.COLOR_PASSAGE
            elif val == 'G':
                color = settings.COLOR_GOAL
            elif val == 'K':
                color = settings.COLOR_KEY
            else:
                color = settings.COLOR_PASSAGE

            pygame.draw.rect(screen, color, rect)


def make_window():
    screen = pygame.display.set_mode((settings.WINDOW_SIZE, settings.WINDOW_SIZE))
    pygame.display.set_caption('Maze')
    return screen

def find_positions(grid):
    """Menentukan start, goal, dan key berdasarkan penanda grid 'S', 'G', dan 'K'."""
    h = len(grid)
    w = len(grid[0])
    
    start = None
    goal = None
    keys = []
    
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            if val == 'S':
                start = (x, y)
            elif val == 'G':
                goal = (x, y)
            elif val == 'K':
                keys.append((x, y))

    # Jika Start belum ditemukan (misalnya, jika generator teman Anda tidak menandai 'S' secara eksplisit)
    if not start:
        # Pengecekan aman di tepi atau sel pertama yang bisa dilalui
        walkable = [(x, y) for y in range(h) for x in range(w) if grid[y][x] in ('.', 'G', 'K')]
        start = walkable[0] if walkable else (1, 1)

    # Catatan: Karena generator teman Anda menjamin 'G' dan 'K' ada, 
    # Anda tidak perlu lagi kode 'autofix' Goal dan Key yang kompleks di versi lama.
    
    return start, goal, keys
            
    return start, goal, keys

def spawn_guardians(grid, level, forbidden_positions):
    rows = len(grid)
    cols = len(grid[0])
    guardians = []
    tries = 0
    while len(guardians) < level and tries < 2000:
        tries += 1
        x = random.randint(1, cols-2)
        y = random.randint(1, rows-2)
        if grid[y][x] != '.':
            continue
        if (x,y) in forbidden_positions:
            continue
        too_close = any(abs(x-fx)+abs(y-fy) <= 3 for fx,fy in forbidden_positions)
        if too_close:
            continue
        g = Guardian(grid, (x,y), color=(200, 30, 30))
        guardians.append(g)
    return guardians

def main():
    global LEVEL
    clock = pygame.time.Clock()

    grid = map_generator.generate_maze(LEVEL)
    screen = make_window()

    start, goal, keys = find_positions(grid)

    astar = AStarAgent(start[0], start[1], keys, goal)
    bfs = BFSAgent(start[0], start[1], keys, goal)
    
    forbidden = [start, goal] + keys
    guardians = spawn_guardians(grid, LEVEL, forbidden)
    
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False

                elif event.key == pygame.K_r:
                    grid = map_generator.generate_maze(LEVEL)
                    start, goal, keys = find_positions(grid)
                    astar = AStarAgent(start[0], start[1], keys, goal)
                    bfs = BFSAgent(start[0], start[1], keys, goal)
                    guardians = spawn_guardians(grid, LEVEL, [start, goal] + keys)

                elif event.key == pygame.K_n:
                    LEVEL = LEVEL + 1 if LEVEL < 3 else 1
                    grid = map_generator.generate_maze(LEVEL)
                    start, goal, keys = find_positions(grid)
                    astar = AStarAgent(start[0], start[1], keys, goal)
                    bfs = BFSAgent(start[0], start[1], keys, goal)
                    guardians = spawn_guardians(grid, LEVEL, [start, goal] + keys)

        for g in guardians:
            d_ast = abs(g.x - astar.x) + abs(g.y - astar.y) if astar.alive else 9999
            d_bfs = abs(g.x - bfs.x) + abs(g.y - bfs.y) if bfs.alive else 9999

            if d_ast < d_bfs:
                target = (astar.x, astar.y)
            elif d_bfs < d_ast:
                target = (bfs.x, bfs.y)
            else:
                target = random.choice([(astar.x, astar.y), (bfs.x, bfs.y)])

            g.move_towards_player(target[0], target[1])

        astar.step(grid, guardians)
        bfs.step(grid, guardians)
        
        for g in guardians:
            if astar.alive and (astar.x, astar.y) == (g.x, g.y):
                print("A* Mati")
                astar.alive = False

            if bfs.alive and (bfs.x, bfs.y) == (g.x, g.y):
                print("BFS Mati")
                bfs.alive = False
                
        if not astar.alive and not bfs.alive:
            print("Guardian menang di level", LEVEL)
            
            LEVEL = LEVEL + 1 if LEVEL < 3 else 1
            grid = map_generator.generate_maze(LEVEL)
            start, goal, keys = find_positions(grid)
            astar = AStarAgent(start[0], start[1], keys, goal)
            bfs = BFSAgent(start[0], start[1], keys, goal)
            guardians = spawn_guardians(grid, LEVEL, [start, goal] + keys)
            continue
    
        if astar.has_key and (astar.x, astar.y) == goal:
            print("A* menang level", LEVEL)
            LEVEL = LEVEL + 1 if LEVEL < 3 else 1
            grid = map_generator.generate_maze(LEVEL)
            start, goal, keys = find_positions(grid)
            astar = AStarAgent(start[0], start[1], keys, goal)
            bfs = BFSAgent(start[0], start[1], keys, goal)
            guardians = spawn_guardians(grid, LEVEL, [start, goal] + keys)
            continue

        if bfs.has_key and (bfs.x, bfs.y) == goal:
            print("BFS menang level", LEVEL)
            LEVEL = LEVEL + 1 if LEVEL < 3 else 1
            grid = map_generator.generate_maze(LEVEL)
            start, goal, keys = find_positions(grid)
            astar = AStarAgent(start[0], start[1], keys, goal)
            bfs = BFSAgent(start[0], start[1], keys, goal)
            guardians = spawn_guardians(grid, LEVEL, [start, goal] + keys)
            continue

        size = map_generator.get_size_for_level(LEVEL)
        tile_size = settings.WINDOW_SIZE // size

##        screen.fill(settings.COLOR_BG)
        draw_grid(screen, grid, tile_size)

        pygame.draw.circle(
            screen, settings.COLOR_START,
            (start[0] * tile_size + tile_size//2, start[1] * tile_size + tile_size//2),
            max(4, tile_size // 3)
        )

        for g in guardians:
            pygame.draw.circle(
                screen, g.color,
                (g.x * tile_size + tile_size//2, g.y * tile_size + tile_size//2),
                max(4, tile_size // 3)
            )

        if astar.alive:
            pygame.draw.circle(
                screen, settings.COLOR_ASTAR_AGENT,
                (astar.x * tile_size + tile_size//2, astar.y * tile_size + tile_size//2),
                max(4, tile_size // 3)
            )

        if bfs.alive:
            pygame.draw.circle(
                screen, settings.COLOR_BFS_AGENT,
                (bfs.x * tile_size + tile_size//2, bfs.y * tile_size + tile_size//2),
                max(4, tile_size // 3)
            )

        pygame.display.flip()
        clock.tick(settings.FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
