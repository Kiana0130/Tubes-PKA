import pygame
import sys
from Agen.guardian import Guardian
from core import map_generator
from core import settings
from Agen.A_Star import AStarAgent
from Agen.BFS import BFSAgent
import random
import copy 

pygame.init()

LEVEL = 1

# START MODIFIKASI: Variabel Global untuk Tracking Loop dan Statistik
LOOP_COUNT = 1
# all_loops_stats akan menyimpan daftar statistik untuk setiap loop
all_loops_stats = []

def init_new_loop_stats(loop_num):
    """Menginisialisasi struktur data untuk loop baru."""
    return {
        'loop_number': loop_num,
        'AStar': {'finish_steps': {}, 'deaths': 0, 'total_steps': 0}, # finish_steps menggunakan dict {level: steps}
        'BFS': {'finish_steps': {}, 'deaths': 0, 'total_steps': 0}
    }

def print_loop_summary(loop_data):
    """Mencetak ringkasan untuk satu loop (L1-L3) yang telah selesai."""
    loop_num = loop_data['loop_number']
    stats = loop_data
    
    astar_wins = len(stats['AStar']['finish_steps'])
    bfs_wins = len(stats['BFS']['finish_steps'])
    
    print("\n" + "═"*70)
    print(f"             RANGKUMAN LOOP KE-{loop_num} (LEVEL 1-3)")
    print("═"*70)
    
    # Jumlah Kemenangan Level Per Loop
    print("\n--- Jumlah Kemenangan Level Per Loop ---")
    print(f"{'A* Agent':<15}: {astar_wins} level diselesaikan")
    print(f"{'BFS Agent':<15}: {bfs_wins} level diselesaikan")

    # 1. Waktu sampai garis finish (Per Level)
    print("\n--- Waktu Sampai Finish (Total Ticks Per Level yang Selesai) ---")
    
    print(f"{'A* Agent':<15}: Total {astar_wins}/{3} level diselesaikan.")
    for level in range(1, 4):
        steps = stats['AStar']['finish_steps'].get(level, 'N/A')
        print(f"{'':<15} Level {level}: {steps} ticks")
        
    print(f"{'BFS Agent':<15}: Total {bfs_wins}/{3} level diselesaikan.")
    for level in range(1, 4):
        steps = stats['BFS']['finish_steps'].get(level, 'N/A')
        print(f"{'':<15} Level {level}: {steps} ticks")

    # 2. Jumlah mati/tertangkap
    print("\n--- Jumlah Mati/Tertangkap Guardian ---")
    print(f"{'A* Agent':<15}: {stats['AStar']['deaths']} kali")
    print(f"{'BFS Agent':<15}: {stats['BFS']['deaths']} kali")

    # 3. Biaya perjalanan (Total Langkah Bergerak)
    print("\n--- Total Biaya Perjalanan (Akumulasi Langkah Bergerak L1-L3) ---")
    print(f"A* Agent: {stats['AStar']['total_steps']} langkah")
    print(f"BFS Agent: {stats['BFS']['total_steps']} langkah")
    
    print("═"*70)

def print_final_summary(all_data):
    """Mencetak ringkasan dari semua loop (loop yang selesai dan loop yang sedang berjalan)."""
    
    # Hitung total statistik
    total_astar_deaths = sum(d['AStar']['deaths'] for d in all_data)
    total_bfs_deaths = sum(d['BFS']['deaths'] for d in all_data)
    total_astar_steps = sum(d['AStar']['total_steps'] for d in all_data)
    total_bfs_steps = sum(d['BFS']['total_steps'] for d in all_data)
    total_astar_wins = sum(len(d['AStar']['finish_steps']) for d in all_data)
    total_bfs_wins = sum(len(d['BFS']['finish_steps']) for d in all_data)
    
    # MODIFIKASI: Ambil jumlah loop
    total_loops = len(all_data)
    
    print("\n" + "█"*70)
    print("             RINGKASAN AKHIR KESELURUHAN PERMAINAN")
    # MODIFIKASI: Tambahkan informasi jumlah loop
    print(f"                 Total {total_loops} Loop Dicatat")
    print("█"*70)
    
    for loop_data in all_data:
        print_loop_summary(loop_data)

    print("\n" + "▓"*70)
    print("             TOTAL AKUMULASI SEMUA LOOP")
    print("▓"*70)
    
    # TAMBAHAN: Tampilkan Total Kemenangan
    print(f"{'Total Loop Selesai':<25}: {total_loops} kali") # MODIFIKASI: Tampilkan Total Loop
    print(f"{'Total A* Menang':<25}: {total_astar_wins} kali")
    print(f"{'Total BFS Menang':<25}: {total_bfs_wins} kali")
    
    print(f"{'Total A* Mati':<25}: {total_astar_deaths} kali")
    print(f"{'Total BFS Mati':<25}: {total_bfs_deaths} kali")
    print(f"{'Total A* Langkah':<25}: {total_astar_steps} langkah")
    print(f"{'Total BFS Langkah':<25}: {total_bfs_steps} langkah")
    print("▓"*70)
# END MODIFIKASI


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

    if not start:
        walkable = [(x, y) for y in range(h) for x in range(w) if grid[y][x] in ('.', 'G', 'K')]
        start = walkable[0] if walkable else (1, 1)

    return start, goal, keys
            
def spawn_guardians(grid, level, forbidden_positions):
    rows = len(grid)
    cols = len(grid[0])
    guardians = []
    tries = 0
    while len(guardians) < level and tries < 2000:
        tries += 1
        x = random.randint(1, cols-2)
        y = random.randint(0, rows-2)
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
    global LEVEL, all_loops_stats, LOOP_COUNT 
    clock = pygame.time.Clock()

    all_loops_stats.append(init_new_loop_stats(LOOP_COUNT))
    current_loop_data = all_loops_stats[LOOP_COUNT - 1]

    grid = map_generator.generate_maze(LEVEL)
    screen = make_window()

    start, goal, keys = find_positions(grid)

    astar = AStarAgent(start[0], start[1], copy.copy(keys), goal)
    bfs = BFSAgent(start[0], start[1], copy.copy(keys), goal)
    
    forbidden = [start, goal] + keys
    guardians = spawn_guardians(grid, LEVEL, forbidden)
    
    running = True

    game_steps = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
                running = False
                if astar.alive and not astar.finished:
                    current_loop_data['AStar']['total_steps'] += astar.current_run_steps
                if bfs.alive and not bfs.finished:
                    current_loop_data['BFS']['total_steps'] += bfs.current_run_steps

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_steps = 0
                    grid = map_generator.generate_maze(LEVEL)
                    start, goal, keys = find_positions(grid)
                    astar = AStarAgent(start[0], start[1], copy.copy(keys), goal)
                    bfs = BFSAgent(start[0], start[1], copy.copy(keys), goal)
                    guardians = spawn_guardians(grid, LEVEL, [start, goal] + keys)

                elif event.key == pygame.K_n:
                    LEVEL = LEVEL + 1 if LEVEL < 3 else 1
                    
                    game_steps = 0
                    grid = map_generator.generate_maze(LEVEL)
                    start, goal, keys = find_positions(grid)
                    astar = AStarAgent(start[0], start[1], copy.copy(keys), goal)
                    bfs = BFSAgent(start[0], start[1], copy.copy(keys), goal)
                    guardians = spawn_guardians(grid, LEVEL, [start, goal] + keys)

        game_steps += 1 

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
        
        re_initialize = False
        
        for g in guardians:
            if astar.alive and (astar.x, astar.y) == (g.x, g.y):
                print(f"[Level {LEVEL}] A* Mati")
                astar.alive = False
                current_loop_data['AStar']['deaths'] += 1

            if bfs.alive and (bfs.x, bfs.y) == (g.x, g.y):
                print(f"[Level {LEVEL}] BFS Mati")
                bfs.alive = False
                current_loop_data['BFS']['deaths'] += 1
                
        if not astar.alive and not bfs.alive:
            print(f"Guardian menang di level {LEVEL}")
            
            current_loop_data['AStar']['total_steps'] += astar.current_run_steps
            current_loop_data['BFS']['total_steps'] += bfs.current_run_steps
            
            re_initialize = True
            
        elif astar.has_key and (astar.x, astar.y) == goal:
            print(f"A* menang level {LEVEL}")
            
            current_loop_data['AStar']['finish_steps'][LEVEL] = game_steps
            current_loop_data['AStar']['total_steps'] += astar.current_run_steps

            re_initialize = True

        elif bfs.has_key and (bfs.x, bfs.y) == goal:
            print(f"BFS menang level {LEVEL}")
            
            current_loop_data['BFS']['finish_steps'][LEVEL] = game_steps
            current_loop_data['BFS']['total_steps'] += bfs.current_run_steps

            re_initialize = True
            
        if re_initialize:
            is_loop_complete = LEVEL == 3 
            
            LEVEL = LEVEL + 1 if LEVEL < 3 else 1
            
            if is_loop_complete:
                print_loop_summary(current_loop_data) 
                
                LOOP_COUNT += 1
                all_loops_stats.append(init_new_loop_stats(LOOP_COUNT))
                current_loop_data = all_loops_stats[LOOP_COUNT - 1]
            
            game_steps = 0
            grid = map_generator.generate_maze(LEVEL)
            start, goal, keys = find_positions(grid)
            astar = AStarAgent(start[0], start[1], copy.copy(keys), goal) 
            bfs = BFSAgent(start[0], start[1], copy.copy(keys), goal)
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

    print_final_summary(all_loops_stats)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()