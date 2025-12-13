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
        # Mengganti 'finish_steps' dengan 'level_results' untuk menyimpan status (FINISHED, DIED, QUIT) dan langkah
        'AStar': {'level_results': {}, 'deaths': 0, 'total_steps': 0, 'total_nodes': 0}, 
        'BFS': {'level_results': {}, 'deaths': 0, 'total_steps': 0, 'total_nodes': 0}
    }

def print_loop_summary(loop_data):
    """Mencetak ringkasan untuk satu loop (L1-L3) yang telah selesai."""
    loop_num = loop_data['loop_number']
    stats = loop_data
    
    astar_results = stats['AStar']['level_results']
    bfs_results = stats['BFS']['level_results']
    
    astar_wins = sum(1 for res in astar_results.values() if res['status'] == 'FINISHED')
    bfs_wins = sum(1 for res in bfs_results.values() if res['status'] == 'FINISHED')
    
    astar_win_steps = [res['steps'] for res in astar_results.values() if res['status'] == 'FINISHED']
    bfs_win_steps = [res['steps'] for res in bfs_results.values() if res['status'] == 'FINISHED']
    
    avg_astar_steps = sum(astar_win_steps) / len(astar_win_steps) if astar_win_steps else 0
    avg_bfs_steps = sum(bfs_win_steps) / len(bfs_win_steps) if bfs_win_steps else 0
    
    print("\n" + "═"*70)
    print(f"             RANGKUMAN LOOP KE-{loop_num} (LEVEL 1-3)")
    print("═"*70)
    
    # Jumlah Kemenangan Level Per Loop
    print(f"{'Metric':<25} | {'A* Agent':<15} | {'BFS Agent':<15}")
    print("-" * 65)
    print(f"{'Level Selesai (Win)':<25} | {astar_wins:<15} | {bfs_wins:<15}")
    print(f"{'Avg Langkah (Win Only)':<25} | {avg_astar_steps:<15.1f} | {avg_bfs_steps:<15.1f}")
    print(f"{'Total Komputasi (Node)':<25} | {stats['AStar']['total_nodes']:<15} | {stats['BFS']['total_nodes']:<15}")
    print("-" * 65)

    # 1. Hasil dan Langkah Per Level
    print("\n--- Hasil dan Langkah Per Level ---")
    status_map = {'FINISHED': 'MENANG', 'DIED': 'MATI', 'QUIT': 'TIDAK SELESAI (Keluar)'}
    
    print(f"{'A* Agent':<15}: Total {astar_wins}/{3} level diselesaikan.")
    for level in range(1, 4):
        res_a = astar_results.get(level, {'status': '-', 'steps': 0})
        res_b = bfs_results.get(level, {'status': '-', 'steps': 0})
        
        stat_a = status_map.get(res_a['status'], '-')
        stat_b = status_map.get(res_b['status'], '-')
        
        print(f"Level {level}: A* [{stat_a}, {res_a['steps']} step] vs BFS [{stat_b}, {res_b['steps']} step]")
    print("═"*70)

def print_final_summary(all_data):
    total_astar_wins = 0
    total_bfs_wins = 0
    total_astar_win_steps = 0
    total_bfs_win_steps = 0
    
    total_astar_nodes = sum(d['AStar']['total_nodes'] for d in all_data)
    total_bfs_nodes = sum(d['BFS']['total_nodes'] for d in all_data)
    
    total_astar_deaths = sum(d['AStar']['deaths'] for d in all_data)
    total_bfs_deaths = sum(d['BFS']['deaths'] for d in all_data)

    # Akumulasi Data Kemenangan Saja
    for d in all_data:
        # A*
        for res in d['AStar']['level_results'].values():
            if res['status'] == 'FINISHED':
                total_astar_wins += 1
                total_astar_win_steps += res['steps']
        # BFS
        for res in d['BFS']['level_results'].values():
            if res['status'] == 'FINISHED':
                total_bfs_wins += 1
                total_bfs_win_steps += res['steps']

    avg_astar = total_astar_win_steps / total_astar_wins if total_astar_wins > 0 else 0
    avg_bfs = total_bfs_win_steps / total_bfs_wins if total_bfs_wins > 0 else 0

    print("\n" + "█"*70)
    print("             KESIMPULAN AKHIR (DATA SCIENTIFIC)")
    print("█"*70)
    
    print(f"{'METRIK PERFORMA':<30} | {'A* (Smart)':<15} | {'BFS (Basic)':<15}")
    print("=" * 70)
    print(f"{'Total Menang':<30} | {total_astar_wins:<15} | {total_bfs_wins:<15}")
    print(f"{'Rata-rata Langkah (Efisiensi)':<30} | {avg_astar:<15.1f} | {avg_bfs:<15.1f}")
    print(f"{'Total Beban Komputasi (Node)':<30} | {total_astar_nodes:<15} | {total_bfs_nodes:<15}")
    print(f"{'Total Kematian':<30} | {total_astar_deaths:<15} | {total_bfs_deaths:<15}")
    print("=" * 70)
    
    # print("\nANALISIS:")
    # if avg_astar < avg_bfs and avg_astar > 0:
    #     print(">> A* terbukti LEBIH EFISIEN dalam pergerakan (langkah lebih sedikit).")
    # elif avg_astar > 0:
    #     print(">> A* mengambil langkah lebih banyak (mungkin karena terlalu sering menghindar).")
        
    # if total_astar_nodes > total_bfs_nodes:
    #     print(">> A* memiliki Beban Komputasi TINGGI karena fitur 'Danger Zone' (berpikir keras untuk menghindar).")
    #     print("   Ini menunjukkan A* lebih responsif terhadap ancaman dinamis dibanding BFS.")
    
    # print("█"*70)

def draw_agent_path(screen, agent, tile_size, color):
    """Menggambar garis rencana rute agen"""
    if not agent.alive or not agent.path:
        return
        
    # Ambil titik pusat agen saat ini
    points = [(agent.x * tile_size + tile_size//2, agent.y * tile_size + tile_size//2)]
    
    # Masukkan semua titik di path rencana
    for (x, y) in agent.path:
        points.append((x * tile_size + tile_size//2, y * tile_size + tile_size//2))
        
    if len(points) > 1:
        pygame.draw.lines(screen, color, False, points, 3) # Ketebalan 3
        
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
            
def play_scan_animation(screen, grid, tile_size, astar_scan, bfs_scan):
    """
    Memainkan animasi 'loading' dengan fitur COLOR MIXING saat tumpang tindih.
    """
    max_steps = max(len(astar_scan), len(bfs_scan))
    if max_steps == 0: return

    anim_clock = pygame.time.Clock()
    dynamic_speed = max(1, max_steps // 500) # Kecepatan dinamis
    
    for i in range(0, max_steps, dynamic_speed):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
                
        draw_grid(screen, grid, tile_size)
            
        limit_bfs = min(i + dynamic_speed, len(bfs_scan))
        current_bfs = bfs_scan[:limit_bfs]
        
        limit_astar = min(i + dynamic_speed, len(astar_scan))
        current_astar = astar_scan[:limit_astar]

        set_bfs = set(current_bfs)
        set_astar = set(current_astar)
        
        overlap = set_bfs.intersection(set_astar)
        
        only_bfs = set_bfs - overlap
        only_astar = set_astar - overlap
        
        for node in only_bfs:
            x, y = node
            shrink = 4
            small_rect = pygame.Rect(x * tile_size + shrink, y * tile_size + shrink, tile_size - shrink*2, tile_size - shrink*2)
            pygame.draw.rect(screen, settings.COLOR_SCAN_BFS, small_rect)

        for node in only_astar:
            x, y = node
            shrink = 4
            small_rect = pygame.Rect(x * tile_size + shrink, y * tile_size + shrink, tile_size - shrink*2, tile_size - shrink*2)
            pygame.draw.rect(screen, settings.COLOR_SCAN_ASTAR, small_rect)

        for node in overlap:
            x, y = node
            shrink = 4
            small_rect = pygame.Rect(x * tile_size + shrink, y * tile_size + shrink, tile_size - shrink*2, tile_size - shrink*2)
            pygame.draw.rect(screen, settings.COLOR_SCAN_OVERLAP, small_rect)

        pygame.display.update()
        anim_clock.tick(120)

def make_window():
    screen = pygame.display.set_mode((settings.WINDOW_SIZE, settings.WINDOW_SIZE))
    pygame.display.set_caption('Maze')
    return screen

def find_positions(grid):
    """Menentukan start, goal, dan key berdasarkan penanda grid 'S', 'G', dan 'K'"""
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
            
def spawn_guardians(grid, count, forbidden_positions):
    rows = len(grid)
    cols = len(grid[0])
    guardians = []
    tries = 0
    while len(guardians) < count and tries < 2000:
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
    
    size = map_generator.get_size_for_level(LEVEL)
    tile_size = settings.WINDOW_SIZE // size

    start, goal, keys = find_positions(grid)

    astar = AStarAgent(start[0], start[1], copy.copy(keys), goal)
    bfs = BFSAgent(start[0], start[1], copy.copy(keys), goal)
    num_guardians_map = {1: 0, 2: 1, 3: 2}
    count = num_guardians_map.get(LEVEL, 2)
    forbidden = [start, goal] + keys
    guardians = spawn_guardians(grid, count, [start, goal] + keys)
    
    running = True

    game_steps = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
                running = False
                
                current_loop_data['AStar']['total_steps'] += astar.current_run_steps
                if LEVEL not in current_loop_data['AStar']['level_results']:
                    if astar.finished:
                        current_loop_data['AStar']['level_results'][LEVEL] = {'status': 'FINISHED', 'steps': game_steps}
                    elif astar.alive:
                        current_loop_data['AStar']['level_results'][LEVEL] = {'status': 'QUIT', 'steps': game_steps}

                # Logic untuk BFS Agent
                current_loop_data['BFS']['total_steps'] += bfs.current_run_steps
                if LEVEL not in current_loop_data['BFS']['level_results']:
                    if bfs.finished:
                        current_loop_data['BFS']['level_results'][LEVEL] = {'status': 'FINISHED', 'steps': game_steps}
                    elif bfs.alive:
                        current_loop_data['BFS']['level_results'][LEVEL] = {'status': 'QUIT', 'steps': game_steps}

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_steps = 0
                    
                    grid = map_generator.generate_maze(LEVEL)
                    start, goal, keys = find_positions(grid)
                    astar = AStarAgent(start[0], start[1], copy.copy(keys), goal)
                    bfs = BFSAgent(start[0], start[1], copy.copy(keys), goal)
                    guardians = spawn_guardians(grid, count, [start, goal] + keys)
                            
                    grid = map_generator.generate_maze(LEVEL)
                    start, goal, keys = find_positions(grid)
                    astar = AStarAgent(start[0], start[1], copy.copy(keys), goal)
                    bfs = BFSAgent(start[0], start[1], copy.copy(keys), goal)
                    guardian_count = {1: 0, 2: 1, 3: 2}.get(LEVEL, 2)
                    guardians = spawn_guardians(grid, guardian_count, [start, goal] + keys) 

                elif event.key == pygame.K_n:
                    if astar.alive and not astar.finished:
                        current_loop_data['AStar']['total_steps'] += astar.current_run_steps
                        current_loop_data['AStar']['total_nodes'] += astar.nodes_expanded
                        current_loop_data['AStar']['level_results'][LEVEL] = {'status': 'QUIT', 'steps': astar.current_run_steps}
                    if bfs.alive and not bfs.finished:
                        current_loop_data['BFS']['total_steps'] += bfs.current_run_steps
                        current_loop_data['BFS']['total_nodes'] += bfs.nodes_expanded
                        current_loop_data['BFS']['level_results'][LEVEL] = {'status': 'QUIT', 'steps': bfs.current_run_steps}
                    
                    # Lanjut ke level berikutnya
                    LEVEL = LEVEL + 1 if LEVEL < 3 else 1
                    game_steps = 0
                    grid = map_generator.generate_maze(LEVEL)
                    size = map_generator.get_size_for_level(LEVEL)
                    tile_size = settings.WINDOW_SIZE // size
                    start, goal, keys = find_positions(grid)
                    astar = AStarAgent(start[0], start[1], copy.copy(keys), goal)
                    bfs = BFSAgent(start[0], start[1], copy.copy(keys), goal)
                    guardian_count = {1: 0, 2: 1, 3: 2}.get(LEVEL, 2)
                    guardians = spawn_guardians(grid, guardian_count, [start, goal] + keys)

        game_steps += 1 
        astar.step(grid, guardians)
        bfs.step(grid, guardians)
        
        if astar.just_replanned or bfs.just_replanned:
            play_scan_animation(screen, grid, tile_size, astar.latest_scan, bfs.latest_scan)
            astar.just_replanned = False
            bfs.just_replanned = False
            astar.latest_scan = []
            bfs.latest_scan = []
            
        draw_grid(screen, grid, tile_size)
        for g in guardians:
            d_ast = abs(g.x - astar.x) + abs(g.y - astar.y) if astar.alive else 9999
            d_bfs = abs(g.x - bfs.x) + abs(g.y - bfs.y) if bfs.alive else 9999
            if d_ast < d_bfs: target = (astar.x, astar.y)
            elif d_bfs < d_ast: target = (bfs.x, bfs.y)
            else: target = random.choice([(astar.x, astar.y), (bfs.x, bfs.y)])
            g.move_towards_player(target[0], target[1])

        # astar.step(grid, guardians)
        # bfs.step(grid, guardians)
        
        for g in guardians:
            if astar.alive and (astar.x, astar.y) == (g.x, g.y):
                print(f"[Level {LEVEL}] A* Mati")
                astar.alive = False
                current_loop_data['AStar']['deaths'] += 1
                # Catat status DIED dan langkah/ticks
                if not astar.finished and LEVEL not in current_loop_data['AStar']['level_results']:
                    current_loop_data['AStar']['level_results'][LEVEL] = {'status': 'DIED', 'steps': game_steps}
                    current_loop_data['AStar']['total_nodes'] += astar.nodes_expanded

            if bfs.alive and (bfs.x, bfs.y) == (g.x, g.y):
                print(f"[Level {LEVEL}] BFS Mati")
                bfs.alive = False
                current_loop_data['BFS']['deaths'] += 1
                if not bfs.finished and LEVEL not in current_loop_data['BFS']['level_results']:
                    current_loop_data['BFS']['level_results'][LEVEL] = {'status': 'DIED', 'steps': game_steps}
                    current_loop_data['BFS']['total_nodes'] += bfs.nodes_expanded                

        astar_settled = astar.finished or not astar.alive
        bfs_settled = bfs.finished or not bfs.alive
        
        re_initialize = False
        
        if astar_settled and bfs_settled:
            re_initialize = True
            if LEVEL not in current_loop_data['AStar']['level_results'] or current_loop_data['AStar']['level_results'][LEVEL]['status'] in ('DIED', 'QUIT'):
                if astar.finished:
                    current_loop_data['AStar']['total_steps'] += astar.current_run_steps
                    current_loop_data['AStar']['total_nodes'] += astar.nodes_expanded
            
            if astar.finished:
                current_loop_data['AStar']['level_results'][LEVEL] = {'status': 'FINISHED', 'steps': game_steps}
                
            if LEVEL not in current_loop_data['BFS']['level_results'] or current_loop_data['BFS']['level_results'][LEVEL]['status'] in ('DIED', 'QUIT'):
                if bfs.finished:
                    current_loop_data['BFS']['total_steps'] += bfs.current_run_steps
                    current_loop_data['BFS']['total_nodes'] += bfs.nodes_expanded
                
            if bfs.finished:
                current_loop_data['BFS']['level_results'][LEVEL] = {'status': 'FINISHED', 'steps': game_steps}
                
            if astar.finished and bfs.finished:
                print(f"Kedua Agen menang di level {LEVEL}")
            elif astar.finished:
                print(f"A* menang, BFS gagal/mati di level {LEVEL}")
            elif bfs.finished:
                print(f"BFS menang, A* gagal/mati di level {LEVEL}")
            else: # Keduanya !alive (mati/gagal)
                print(f"Guardian menang di level {LEVEL}")

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
            size = map_generator.get_size_for_level(LEVEL)
            tile_size = settings.WINDOW_SIZE // size
            start, goal, keys = find_positions(grid)
            astar = AStarAgent(start[0], start[1], copy.copy(keys), goal) 
            bfs = BFSAgent(start[0], start[1], copy.copy(keys), goal)
            guardian_count = {1: 0, 2: 1, 3: 2}.get(LEVEL, 2)
            guardians = spawn_guardians(grid, guardian_count, [start, goal] + keys)
            continue


        size = map_generator.get_size_for_level(LEVEL)
        tile_size = settings.WINDOW_SIZE // size

        draw_grid(screen, grid, tile_size)
        draw_agent_path(screen, astar, tile_size, (180, 0, 180))
        draw_agent_path(screen, bfs, tile_size, (0, 180, 180))

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
            offset_x = -tile_size//4 if (astar.x == bfs.x and astar.y == bfs.y and bfs.alive) else 0
            pygame.draw.circle(
                screen, settings.COLOR_ASTAR_AGENT,
                (astar.x * tile_size + tile_size//2 + offset_x, astar.y * tile_size + tile_size//2),
                max(4, tile_size // 3)
            )

        if bfs.alive:
            offset_x = tile_size//4 if (astar.x == bfs.x and astar.y == bfs.y and astar.alive) else 0
            pygame.draw.circle(
                screen, settings.COLOR_BFS_AGENT,
                (bfs.x * tile_size + tile_size//2 + offset_x, bfs.y * tile_size + tile_size//2),
                max(4, tile_size // 3)
            )

        pygame.display.flip()
        clock.tick(settings.FPS)

    print_final_summary(all_loops_stats)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()