# main.py
import random
import pygame
import sys
import map_generator
import settings
import drawing  # New import
from Agen.enemy import Guardian
from Agen.A_Star import AStarAgent
from Agen.BFS import BFSAgent


pygame.init()

# Global level state (Not ideal, but matches original structure)
LEVEL = 1

# Fonts are defined here after pygame.init()
FONT_BIG = pygame.font.SysFont("Consolas", 36, bold=True)
FONT_SMALL = pygame.font.SysFont("Consolas", 18)

# ==============================================
# Window
# ==============================================
def make_window():
    screen = pygame.display.set_mode((settings.WINDOW_SIZE, settings.WINDOW_SIZE))
    pygame.display.set_caption('Maze: Pacman Neo Edition')
    return screen

# ==============================================
# Game Utilities
# ==============================================
# Add this function to your main.py after the imports

def find_positions(grid):
    """Find start, goal, and keys positions with strategic placement"""
    h = len(grid)
    w = len(grid[0])
    
    goal = None
    keys = []
    
    # Find goal and keys first
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            if val == 'G': 
                goal = (x, y)
            elif val == 'K': 
                keys.append((x, y))
    
    # Find all walkable edge positions for player start
    walkable_edges = []
    for y in range(h):
        for x in range(w):
            if grid[y][x] in ['.', 'S']:
                # Check if position is on or near the edge
                if x <= 2 or x >= w - 3 or y <= 2 or y >= h - 3:
                    walkable_edges.append((x, y))
    
    # If we have edge positions, use them; otherwise use any walkable position
    if walkable_edges:
        start = random.choice(walkable_edges)
    else:
        # Fallback: find any walkable position
        walkable = [(x, y) for y in range(h) for x in range(w) 
                    if grid[y][x] in ['.', 'S']]
        start = walkable[0] if walkable else (1, 1)
    
    # Failsafe if goal not placed by generator
    if not goal:
        # Try to place goal far from start
        walkable = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == '.']
        if walkable:
            import math
            distances = [(x, y, math.sqrt((x - start[0])**2 + (y - start[1])**2)) 
                        for x, y in walkable]
            distances.sort(key=lambda d: d[2], reverse=True)
            goal = (distances[0][0], distances[0][1])
        else:
            goal = (w - 2, h - 2)
    
    return start, goal, keys

def create_guardians(grid, player_pos):
    """Helper function to create a list of guardians."""
    guard_count = []
    for i in range(LEVEL*2): 
        guard_count.append(Guardian(grid, player_pos, color=(180, 0, 255)))
    return guard_count

# ==============================================
# Main Game
# ==============================================
def main():
    global LEVEL
    clock = pygame.time.Clock()

    grid = map_generator.generate_maze(LEVEL)
    screen = make_window()

    start, goal, keys = find_positions(grid)
    astar = AStarAgent(start[0], start[1], keys, goal)
    bfs = BFSAgent(start[0], start[1], keys, goal)
    
    guardians = create_guardians(grid, (astar.x, astar.y))

    direction_angle = 0
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                    running = False
                elif event.key == pygame.K_r:
                    # Reset current level
                    grid = map_generator.generate_maze(LEVEL)
                elif event.key == pygame.K_n:
                    # Advance to next level
                    LEVEL = LEVEL + 1 if LEVEL < 3 else 1
                    grid = map_generator.generate_maze(LEVEL)
            
            # If grid was reset, re-init all entities
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_r, pygame.K_n]:
                start, goal, keys = find_positions(grid)
                astar = AStarAgent(start[0], start[1], keys, goal)
                bfs = BFSAgent(start[0], start[1], keys, goal)
                guardians = create_guardians(grid, (astar.x, astar.y))

        # --- Game Logic ---
        
        # Move Player (A*)
        nx, ny = astar.step(grid)
        if nx > astar.x: direction_angle = 0
        elif nx < astar.x: direction_angle = 180
        elif ny > astar.y: direction_angle = 90
        elif ny < astar.y: direction_angle = 270
        astar.x, astar.y = nx, ny

        # Move BFS Agent
        bx, by = bfs.step(grid)
        bfs.x, bfs.y = bx, by

        # Move Guardians
        for guardian in guardians:
            guardian.target = (astar.x, astar.y)
            guardian.move_towards_player(astar.x, astar.y)

        # --- Collision / State Checks ---

        # Check for loss (player caught)
        player_caught = False
        for guardian in guardians:
            if (guardian.x, guardian.y) == (astar.x, astar.y):
                player_caught = "A*"
                break
            if (guardian.x, guardian.y) == (bfs.x, bfs.y):
                player_caught = "BFS"
                break
        
        if player_caught:
            print(f"💀 Player {player_caught} tertangkap! Mereset level {LEVEL}...")
            
            # Reset current level
            grid = map_generator.generate_maze(LEVEL)
            start, goal, keys = find_positions(grid)
            astar = AStarAgent(start[0], start[1], keys, goal)
            bfs = BFSAgent(start[0], start[1], keys, goal)
            guardians = create_guardians(grid, (astar.x, astar.y))
            continue # Restart the loop for the reset level

    # Check for win
        winner = None

        if astar.has_key and (astar.x, astar.y) == goal:
            winner = "A*"
        elif bfs.has_key and (bfs.x, bfs.y) == goal:
            winner = "BFS"

        if winner:
            print(f"🏆 Player {winner} menang level {LEVEL}")
            drawing.show_win_message(screen, LEVEL, FONT_BIG, FONT_SMALL)

            # Setup next level
            LEVEL = LEVEL + 1 if LEVEL < 3 else 1
            grid = map_generator.generate_maze(LEVEL)
            start, goal, keys = find_positions(grid)
            astar = AStarAgent(start[0], start[1], keys, goal)
            bfs = BFSAgent(start[0], start[1], keys, goal)
            guardians = create_guardians(grid, (astar.x, astar.y))
            continue


        # --- Drawing ---
        size = map_generator.get_size_for_level(LEVEL)
        tile_size = settings.WINDOW_SIZE // size
        
        screen.fill(settings.COLOR_BG)
        drawing.draw_modern_grid(screen, grid, tile_size)

        # Player Pac-Man
        drawing.draw_pacman(screen, astar.x, astar.y, tile_size, 0, (0,255,0))
        
        drawing.draw_pacman(screen, bfs.x, bfs.y, tile_size, 0, (255,255,0))

        # Guardian Monster
        for guardian in guardians:
            drawing.draw_guardian_monster(screen, guardian.x, guardian.y, tile_size, guardian.color)

        pygame.display.flip()
        clock.tick(6) # Slowed tick for visibility, adjust as needed

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()