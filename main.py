import pygame, sys, random
import core.map_generator as map_generator
import core.settings as settings
import core.renderer as renderer
from Agen.guardian import Guardian
from Agen.A_Star import AStarAgent
from Agen.BFS import BFSAgent

pygame.init()
renderer.init_fonts()
LEVEL = 1

def find_positions(grid):
    start, goal, keys = None, None, []
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            if val == 'S': start = (x, y)
            elif val == 'G': goal = (x, y)
            elif val == 'K': keys.append((x, y))
    return start, goal, keys

def reset_level(level_num):
    grid = map_generator.generate_maze(level_num)
    start, goal, keys = find_positions(grid)
    astar = AStarAgent(start[0], start[1], keys, goal)
    bfs = BFSAgent(start[0], start[1], keys, goal)

    # --- MODIFIED GUARDIAN SPAWNING ---
    # Find all valid passage cells that are not the start, goal, or key
    h, w = len(grid), len(grid[0])
    passage_cells = []
    for y in range(h):
        for x in range(w):
            if grid[y][x] == '.':
                passage_cells.append((x,y))
    
    # Ensure spawn points are not on the player, goal, or keys
    forbidden_spawns = {start, goal} | set(keys)
    valid_spawns = [p for p in passage_cells if p not in forbidden_spawns]
    
    guardian_colors = [(180, 0, 255), (255, 0, 150)]
    guardians = []
    
    for color in guardian_colors:
        if valid_spawns:
            # Pick a random valid spawn and remove it from the list
            spawn_pos = random.choice(valid_spawns)
            valid_spawns.remove(spawn_pos)
            guardians.append(Guardian(grid, spawn_pos, color))
        else:
            # Fallback if no valid spots (unlikely), spawn near start
            print("Warning: No valid spawn points found. Spawning near player.")
            guardians.append(Guardian(grid, (start[0]+1, start[1]), color)) # Simple fallback
    # --- END OF MODIFICATION ---
            
    return grid, astar, bfs, guardians, goal

def main():
    global LEVEL
    screen = pygame.display.set_mode((settings.WINDOW_SIZE, settings.WINDOW_SIZE))
    pygame.display.set_caption('Maze: Pacman Neo Edition')
    clock = pygame.time.Clock()
    grid, astar, bfs, guardians, goal = reset_level(LEVEL)
    angle = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                grid, astar, bfs, guardians, goal = reset_level(LEVEL)

        # Logic Step
        nx, ny = astar.step(grid)
        if nx != astar.x or ny != astar.y:
            angle = 0 if nx > astar.x else 180 if nx < astar.x else 90 if ny > astar.y else 270
        astar.x, astar.y = nx, ny
        bfs.x, bfs.y = bfs.step(grid)
        
        # Update guardians based on A* agent's (player) position
        for g in guardians: 
            g.move_towards_player(astar.x, astar.y)

        # Check Conditions
        if any((g.x, g.y) == (astar.x, astar.y) for g in guardians):
            print("💀 Caught! Resetting level...")
            grid, astar, bfs, guardians, goal = reset_level(LEVEL)
            angle = 0 # Reset pacman angle
            continue # Restart the loop for the new level state
        if astar.has_key and (astar.x, astar.y) == goal:
            renderer.show_win_message(screen, LEVEL)
            LEVEL = LEVEL + 1 if LEVEL < 3 else 1
            grid, astar, bfs, guardians, goal = reset_level(LEVEL)
            continue

        # Draw
        tile = settings.WINDOW_SIZE // len(grid)
        screen.fill(renderer.COLOR_BG)
        renderer.draw_modern_grid(screen, grid, tile)
        renderer.draw_pacman(screen, astar.x, astar.y, tile, angle)
        renderer.draw_bfs(screen, bfs, tile)
        for g in guardians: renderer.draw_guardian(screen, g, tile)
        pygame.display.flip()
        clock.tick(6)

if __name__ == '__main__':
    main()