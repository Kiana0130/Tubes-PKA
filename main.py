import pygame
import sys
import pandas as pd  # Added
from Agen.guardian import Guardian
from core import map_generator
from core import settings
from Agen.A_Star import AStarAgent
from Agen.BFS import BFSAgent
import random
import copy 

pygame.init()
SCAN_SPEED_NODES_PER_FRAME = 30 

LEVEL = 1
STAGE = 1        

# Global Variables
LOOP_COUNT = 1
all_loops_stats = []

def init_new_loop_stats(loop_count):
    return {
        "loop": loop_count,
        "stages": {
            1: init_stage_stats(),
            2: init_stage_stats(),
            3: init_stage_stats()
        }
    }

def init_stage_stats():
    return {
        "AStar": init_single_agent_stats(),
        "BFS": init_single_agent_stats()
    }

def init_single_agent_stats():
    return {
        "total_steps": 0,
        "total_nodes": 0,
        "total_time": 0,
        "total_computations": 0,
        "deaths": 0,
        "level_results": {}
    }

def export_to_excel(all_data):
    """Parses all_loops_stats and saves to Excel with two sheets."""
    print("Exporting data to Excel...")
    
    summary_data = []
    level_data = []

    for loop_entry in all_data:
        loop_num = loop_entry['loop']
        stages = loop_entry['stages']

        for stage_num, stage_stats in stages.items():
            guardian_count = stage_num - 1
            
            for agent_name in ['AStar', 'BFS']:
                stats = stage_stats[agent_name]

                # 1. Prepare Summary Data (Per Stage)
                summary_data.append({
                    "Loop": loop_num,
                    "Stage": stage_num,
                    "Guardian Count": guardian_count,
                    "Agent": agent_name,
                    "Total Steps": stats['total_steps'],
                    "Total Nodes Expanded": stats['total_nodes'],
                    "Total Time (ms)": stats['total_time'],
                    "Deaths": stats['deaths']
                })

                # 2. Prepare Detailed Data (Per Level)
                for level_num, result in stats['level_results'].items():
                    level_data.append({
                        "Loop": loop_num,
                        "Stage": stage_num,
                        "Level": level_num,
                        "Agent": agent_name,
                        "Status": result['status'],
                        "Steps": result['steps']
                    })

    df_summary = pd.DataFrame(summary_data)
    df_levels = pd.DataFrame(level_data)

    try:
        with pd.ExcelWriter('simulation_results.xlsx', engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='Stage Summary', index=False)
            df_levels.to_excel(writer, sheet_name='Level Details', index=False)
        print("Successfully saved to 'simulation_results.xlsx'")
    except Exception as e:
        print(f"Failed to export Excel: {e}")

def print_loop_summary(loop_data):
    loop_num = loop_data['loop']
    stages = loop_data['stages']

    print("\n" + "═"*90)
    print(f"                  RANGKUMAN LOOP KE-{loop_num}")
    print("═"*90)

    status_map = {'FINISHED': 'MENANG', 'DIED': 'MATI', 'QUIT': 'TIDAK SELESAI', '-': '-'}

    for stage in range(1, 4):
        stage_data = stages[stage]
        astar_stats = stage_data['AStar']
        bfs_stats = stage_data['BFS']
        astar_results = astar_stats['level_results']
        bfs_results = bfs_stats['level_results']

        astar_wins = sum(1 for r in astar_results.values() if r['status'] == 'FINISHED')
        bfs_wins = sum(1 for r in bfs_results.values() if r['status'] == 'FINISHED')
        astar_win_steps = [r['steps'] for r in astar_results.values() if r['status'] == 'FINISHED']
        bfs_win_steps = [r['steps'] for r in bfs_results.values() if r['status'] == 'FINISHED']
        avg_astar_steps = sum(astar_win_steps) / len(astar_win_steps) if astar_win_steps else 0
        avg_bfs_steps = sum(bfs_win_steps) / len(bfs_win_steps) if bfs_win_steps else 0

        print(f"\n▶ STAGE {stage} (Guardian = {stage - 1})")
        print("-"*90)
        print(f"{'Metric':<30} | {'A*':<15} | {'BFS':<15}")
        print("-"*90)
        print(f"{'Level Diselesaikan':<30} | {astar_wins:<15} | {bfs_wins:<15}")
        print(f"{'Rata-rata Langkah (Win)':<30} | {avg_astar_steps:<15.1f} | {avg_bfs_steps:<15.1f}")
        print(f"{'Total Node Diekspansi':<30} | {astar_stats['total_nodes']:<15} | {bfs_stats['total_nodes']:<15}")
        print(f"{'Total Waktu Komputasi (ms)':<30} | {astar_stats['total_time']:<15.2f} | {bfs_stats['total_time']:<15.2f}")

        print("\nDetail per Level:")
        for level in range(1, 4):
            res_a = astar_results.get(level, {'status': '-', 'steps': 0})
            res_b = bfs_results.get(level, {'status': '-', 'steps': 0})
            stat_a = status_map.get(res_a['status'], '-')
            stat_b = status_map.get(res_b['status'], '-')
            print(f"  Level {level}: A* [{stat_a}, {res_a['steps']} step] | BFS [{stat_b}, {res_b['steps']} step]")
    print("═"*90)
    
def print_final_summary(all_data):
    total_astar_wins = 0
    total_bfs_wins = 0
    total_astar_win_steps = 0
    total_bfs_win_steps = 0
    total_astar_nodes = 0
    total_bfs_nodes = 0
    total_astar_deaths = 0
    total_bfs_deaths = 0
    total_astar_all_steps = 0
    total_bfs_all_steps = 0
    total_astar_time = 0
    total_bfs_time = 0
    total_levels_played = 0

    for loop_data in all_data:
        for stage in range(1, 4):
            stage_data = loop_data['stages'][stage]
            astar = stage_data['AStar']
            bfs = stage_data['BFS']

            total_astar_nodes += astar['total_nodes']
            total_bfs_nodes += bfs['total_nodes']
            total_astar_deaths += astar['deaths']
            total_bfs_deaths += bfs['deaths']
            total_astar_all_steps += astar['total_steps']
            total_bfs_all_steps += bfs['total_steps']
            total_astar_time += astar['total_time']
            total_bfs_time += bfs['total_time']

            for level in range(1, 4):
                total_levels_played += 1
                res_a = astar['level_results'].get(level)
                res_b = bfs['level_results'].get(level)
                if res_a and res_a['status'] == 'FINISHED':
                    total_astar_wins += 1
                    total_astar_win_steps += res_a['steps']
                if res_b and res_b['status'] == 'FINISHED':
                    total_bfs_wins += 1
                    total_bfs_win_steps += res_b['steps']

    avg_astar_steps_win = total_astar_win_steps / total_astar_wins if total_astar_wins > 0 else 0
    avg_bfs_steps_win = total_bfs_win_steps / total_bfs_wins if total_bfs_wins > 0 else 0
    avg_time_per_step_astar = total_astar_time / total_astar_all_steps if total_astar_all_steps > 0 else 0
    avg_time_per_step_bfs = total_bfs_time / total_bfs_all_steps if total_bfs_all_steps > 0 else 0
    win_rate_astar = (total_astar_wins / total_levels_played) * 100 if total_levels_played > 0 else 0
    win_rate_bfs = (total_bfs_wins / total_levels_played) * 100 if total_levels_played > 0 else 0

    print("\n" + "█"*90)
    print(f"     KESIMPULAN AKHIR EKSPERIMEN ({total_levels_played} LEVEL TOTAL)")
    print("█"*90)
    print(f"{'METRIK PERFORMA':<35} | {'A* (Smart)':<18} | {'BFS (Basic)':<18}")
    print("=" * 90)
    print(f"{'Total Menang (Win Rate)':<35} | {f'{total_astar_wins} ({win_rate_astar:.1f}%)':<18} | {f'{total_bfs_wins} ({win_rate_bfs:.1f}%)':<18}")
    print(f"{'Total Kematian':<35} | {total_astar_deaths:<18} | {total_bfs_deaths:<18}")
    print("-" * 90)
    print(f"{'Rata-rata Langkah (Saat Menang)':<35} | {avg_astar_steps_win:<18.1f} | {avg_bfs_steps_win:<18.1f}")
    print("-" * 90)
    print(f"{'Total Node Diekspansi (Space)':<35} | {total_astar_nodes:<18} | {total_bfs_nodes:<18}")
    print(f"{'Total Waktu Berpikir (ms)':<35} | {total_astar_time:<18.2f} | {total_bfs_time:<18.2f}")
    print(f"{'Avg Waktu per Langkah (ms/step)':<35} | {avg_time_per_step_astar:<18.4f} | {avg_time_per_step_bfs:<18.4f}")
    print("=" * 90)
    print("█"*90)

def draw_agent_path(screen, agent, tile_size, color):
    if not agent.alive or not agent.path:
        return
    points = [(agent.x * tile_size + tile_size//2, agent.y * tile_size + tile_size//2)]
    for (x, y) in agent.path:
        points.append((x * tile_size + tile_size//2, y * tile_size + tile_size//2))
    dark_color = (color[0], color[1] // 2, color[2] //  1.5)
    if len(points) > 1:
        pygame.draw.lines(screen, dark_color, False, points, 3)
        
def draw_grid(screen, grid, tile_size):
    rows = len(grid)
    cols = len(grid[0])
    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            val = grid[y][x]
            if val == '#': color = settings.COLOR_WALL
            elif val == '.': color = settings.COLOR_PASSAGE
            elif val == 'G': color = settings.COLOR_GOAL
            elif val == 'K': color = settings.COLOR_KEY
            else: color = settings.COLOR_PASSAGE
            pygame.draw.rect(screen, color, rect)

def draw_independent_scans(screen, tile_size, astar_list, bfs_list, astar_idx, bfs_idx):
    current_astar = astar_list[:astar_idx]
    current_bfs = bfs_list[:bfs_idx]
    set_astar = set(current_astar)
    set_bfs = set(current_bfs)
    
    overlap = set_astar.intersection(set_bfs)
    only_astar = set_astar - overlap
    only_bfs = set_bfs - overlap
    
    shrink = 4 
    for node in only_bfs:
        x, y = node
        rect = pygame.Rect(x * tile_size + shrink, y * tile_size + shrink, tile_size - shrink*2, tile_size - shrink*2)
        pygame.draw.rect(screen, settings.COLOR_SCAN_BFS, rect)
    for node in only_astar:
        x, y = node
        rect = pygame.Rect(x * tile_size + shrink, y * tile_size + shrink, tile_size - shrink*2, tile_size - shrink*2)
        pygame.draw.rect(screen, settings.COLOR_SCAN_ASTAR, rect)
    for node in overlap:
        x, y = node
        rect = pygame.Rect(x * tile_size + shrink, y * tile_size + shrink, tile_size - shrink*2, tile_size - shrink*2)
        pygame.draw.rect(screen, settings.COLOR_SCAN_OVERLAP, rect)

def make_window():
    screen = pygame.display.set_mode((settings.WINDOW_SIZE, settings.WINDOW_SIZE))
    pygame.display.set_caption('Maze')
    return screen

def find_positions(grid):
    h = len(grid)
    w = len(grid[0])
    start = None; goal = None; keys = []
    
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            if val == 'S': start = (x, y)
            elif val == 'G': goal = (x, y)
            elif val == 'K': keys.append((x, y))
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
        if grid[y][x] != '.': continue
        if (x,y) in forbidden_positions: continue
        if any(abs(x-fx)+abs(y-fy) <= 3 for fx,fy in forbidden_positions): continue
        guardians.append(Guardian(grid, (x,y), color=(200, 30, 30)))
    return guardians

def main():
    global STAGE,LEVEL, all_loops_stats, LOOP_COUNT 
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
    stage_guardians = {1: 0, 2: 1, 3: 2}
    guardian_count = stage_guardians[STAGE]
    guardians = spawn_guardians(grid, guardian_count, [start, goal] + keys)
    
    astar_scan_history = []; bfs_scan_history = []
    astar_scan_idx = 0; bfs_scan_idx = 0
    astar_scanning = False; bfs_scanning = False
    
    running = True
    game_steps = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: # RESET
                    game_steps = 0
                    grid = map_generator.generate_maze(LEVEL)
                    start, goal, keys = find_positions(grid)
                    astar = AStarAgent(start[0], start[1], copy.copy(keys), goal)
                    bfs = BFSAgent(start[0], start[1], copy.copy(keys), goal)
                    guardians = spawn_guardians(grid, guardian_count, [start, goal] + keys)
                    astar_scan_history = []; bfs_scan_history = []
                    astar_scan_idx = 0; bfs_scan_idx = 0
                    astar_scanning = False; bfs_scanning = False

                elif event.key == pygame.K_n: # NEXT LEVEL
                    LEVEL = LEVEL + 1 if LEVEL < 3 else 1
                    game_steps = 0
                    grid = map_generator.generate_maze(LEVEL)
                    size = map_generator.get_size_for_level(LEVEL)
                    tile_size = settings.WINDOW_SIZE // size
                    start, goal, keys = find_positions(grid)
                    astar = AStarAgent(start[0], start[1], copy.copy(keys), goal)
                    bfs = BFSAgent(start[0], start[1], copy.copy(keys), goal)
                    stage_guardians = {1: 0, 2: 1, 3: 2}
                    guardian_count = stage_guardians[STAGE]
                    guardians = spawn_guardians(grid, guardian_count, [start, goal] + keys)
                    astar_scan_history = []; bfs_scan_history = []
                    astar_scan_idx = 0; bfs_scan_idx = 0
                    astar_scanning = False; bfs_scanning = False

        # --- UPDATE LOGIC ---
        if astar.alive:
            if astar_scanning:
                if astar_scan_idx < len(astar_scan_history):
                    astar_scan_idx += SCAN_SPEED_NODES_PER_FRAME
                else:
                    astar_scanning = False
                    astar_scan_history = [] 
                    astar_scan_idx = 0
                    astar.step(grid, guardians)
                    if astar.just_replanned:
                        astar_scan_history = astar.latest_scan
                        astar_scan_idx = 0
                        astar_scanning = True
                        astar.just_replanned = False
            else:
                astar.step(grid, guardians)
                if astar.just_replanned:
                    astar_scan_history = astar.latest_scan
                    astar_scan_idx = 0
                    astar_scanning = True
                    astar.just_replanned = False
                    
        if bfs.alive:
            if bfs_scanning:
                if bfs_scan_idx < len(bfs_scan_history):
                    bfs_scan_idx += SCAN_SPEED_NODES_PER_FRAME
                else:
                    bfs_scanning = False
                    bfs_scan_history = []
                    bfs_scan_idx = 0
                    bfs.step(grid, guardians)
                    if bfs.just_replanned:
                        bfs_scan_history = bfs.latest_scan
                        bfs_scan_idx = 0
                        bfs_scanning = True
                        bfs.just_replanned = False
            else:
                bfs.step(grid, guardians)
                if bfs.just_replanned:
                    bfs_scan_history = bfs.latest_scan
                    bfs_scan_idx = 0
                    bfs_scanning = True
                    bfs.just_replanned = False

        game_steps += 1
        
        draw_grid(screen, grid, tile_size)
        draw_independent_scans(screen, tile_size, astar_scan_history, bfs_scan_history, astar_scan_idx, bfs_scan_idx)

        for g in guardians:
            d_ast = abs(g.x - astar.x) + abs(g.y - astar.y) if astar.alive else 9999
            d_bfs = abs(g.x - bfs.x) + abs(g.y - bfs.y) if bfs.alive else 9999
            if d_ast < d_bfs: target = (astar.x, astar.y)
            elif d_bfs < d_ast: target = (bfs.x, bfs.y)
            else: target = random.choice([(astar.x, astar.y), (bfs.x, bfs.y)])
            g.move_towards_player(target[0], target[1])

        for g in guardians:
            if astar.alive and (astar.x, astar.y) == (g.x, g.y):
                print(f"[Level {LEVEL}] A* Mati")
                astar.alive = False
                current_stage_data = current_loop_data['stages'][STAGE]
                current_stage_data['AStar']['deaths'] += 1
                if not astar.finished and LEVEL not in current_loop_data['stages'][STAGE]['AStar']['level_results']:
                    current_stage_data['AStar']['level_results'][LEVEL] = {"status": "DIED", "steps": game_steps}
                    current_stage_data['AStar']['total_nodes'] += astar.nodes_expanded

            if bfs.alive and (bfs.x, bfs.y) == (g.x, g.y):
                print(f"[Level {LEVEL}] BFS Mati")
                bfs.alive = False
                current_stage_data = current_loop_data['stages'][STAGE]
                current_stage_data['BFS']['deaths'] += 1
                if not bfs.finished and LEVEL not in current_loop_data['stages'][STAGE]['BFS']['level_results']:
                    current_stage_data['BFS']['level_results'][LEVEL] = {"status": "DIED", "steps": game_steps}
                    current_stage_data['BFS']['total_nodes'] += bfs.nodes_expanded                

        astar_settled = astar.finished or not astar.alive
        bfs_settled = bfs.finished or not bfs.alive
        re_initialize = False
        
        if astar_settled and bfs_settled:
            re_initialize = True
            current_stage_data = current_loop_data['stages'][STAGE]
            
            astar_stats = current_stage_data['AStar']
            if LEVEL not in astar_stats['level_results'] or astar_stats['level_results'][LEVEL]['status'] == 'QUIT':
                if astar.finished:
                    astar_stats['total_steps'] += astar.current_run_steps
                    astar_stats['total_nodes'] += astar.nodes_expanded
                    astar_stats['total_time'] += astar.total_compute_time
                    astar_stats['total_computations'] += astar.compute_counts
                    astar_stats['level_results'][LEVEL] = {"status": "FINISHED", "steps": game_steps}

            bfs_stats = current_stage_data['BFS']
            if LEVEL not in bfs_stats['level_results'] or bfs_stats['level_results'][LEVEL]['status'] == 'QUIT':
                if bfs.finished:
                    bfs_stats['total_steps'] += bfs.current_run_steps
                    bfs_stats['total_nodes'] += bfs.nodes_expanded
                    bfs_stats['total_time'] += bfs.total_compute_time
                    bfs_stats['total_computations'] += bfs.compute_counts
                    bfs_stats['level_results'][LEVEL] = {"status": "FINISHED", "steps": game_steps}
            
            if astar.finished and bfs.finished: print(f"Kedua Agen menang di level {LEVEL}")
            elif astar.finished: print(f"A* menang, BFS gagal/mati di level {LEVEL}")
            elif bfs.finished: print(f"BFS menang, A* gagal/mati di level {LEVEL}")
            else: print(f"Guardian menang di level {LEVEL}")

        if re_initialize:
            is_last_level = LEVEL == 3
            is_last_stage = STAGE == 3
            LEVEL = LEVEL + 1 if LEVEL < 3 else 1

            if is_last_level:
                STAGE = STAGE + 1 if STAGE < 3 else 1
                if is_last_stage:
                    print_loop_summary(current_loop_data)
                    if LOOP_COUNT > 5: 
                        break
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
            guardian_count = {1: 0, 2: 1, 3: 2}[STAGE]
            guardians = spawn_guardians(grid, guardian_count, [start, goal] + keys)
            astar_scan_history = []; bfs_scan_history = []
            astar_scan_idx = 0; bfs_scan_idx = 0
            astar_scanning = False; bfs_scanning = False
            continue

        draw_agent_path(screen, astar, tile_size, settings.COLOR_ASTAR_AGENT)
        draw_agent_path(screen, bfs, tile_size, settings.COLOR_BFS_AGENT)
        spawn_rect = pygame.Rect(start[0] * tile_size + tile_size//4, start[1] * tile_size + tile_size//4, tile_size//2, tile_size//2)
        pygame.draw.rect(screen, settings.COLOR_START, spawn_rect)
        
        for g in guardians:
            pygame.draw.circle(screen, g.color, (g.x * tile_size + tile_size//2, g.y * tile_size + tile_size//2), max(4, tile_size // 3))

        if astar.alive:
            offset_x = -tile_size//4 if (astar.x == bfs.x and astar.y == bfs.y and bfs.alive) else 0
            pygame.draw.circle(screen, settings.COLOR_ASTAR_AGENT, (astar.x * tile_size + tile_size//2 + offset_x, astar.y * tile_size + tile_size//2), max(4, tile_size // 3))

        if bfs.alive:
            offset_x = tile_size//4 if (astar.x == bfs.x and astar.y == bfs.y and astar.alive) else 0
            pygame.draw.circle(screen, settings.COLOR_BFS_AGENT, (bfs.x * tile_size + tile_size//2 + offset_x, bfs.y * tile_size + tile_size//2), max(4, tile_size // 3))

        pygame.display.flip()
        clock.tick(settings.FPS)

if __name__ == '__main__':
    main()
    # --- EXPORT DATA ON EXIT ---
    print_final_summary(all_loops_stats)
    export_to_excel(all_loops_stats) # Export Triggered Here
    pygame.quit()
    sys.exit()