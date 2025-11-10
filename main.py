import pygame, sys
import core.map_generator as map_generator
import core.settings as settings
import core.renderer as renderer
from Agen.guardian import Guardian  # <-- IMPORTED Guardian
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
    
    # Use the imported Guardian class
    guardians = [Guardian(grid, (astar.x, astar.y), c) for c in [(180, 0, 255), (255, 0, 150)]]
    
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
            angle = 0 if nx > astar.x else 180 if nx < astar.x else 90 if ny < astar.y else 270 # Corrected logic
        astar.x, astar.y = nx, ny
        bfs.x, bfs.y = bfs.step(grid)
        
        # --- MODIFIED ---
        # Changed from move_towards_player to the new roam method
        for g in guardians: g.roam(grid)
        # ----------------

        # Check Conditions
        if any((g.x, g.y) == (astar.x, astar.y) for g in guardians):
            print("💀 Game Over"); return
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