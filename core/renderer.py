# renderer.py

import pygame
import math
import sys
import core.settings as settings

# Colors
COLOR_BG = (10, 10, 20)
COLOR_WALL = (30, 50, 120)
COLOR_WALL_GLOW = (0, 150, 255)
COLOR_PASSAGE = (25, 25, 40)
COLOR_KEY = (255, 215, 0)
COLOR_GOAL = (0, 255, 100)

def init_fonts():
    global FONT_BIG, FONT_SMALL
    FONT_BIG = pygame.font.SysFont("Consolas", 36, bold=True)
    FONT_SMALL = pygame.font.SysFont("Consolas", 18)

def draw_modern_grid(screen, grid, tile_size):
    rows, cols = len(grid), len(grid[0])
    for y in range(rows):
        for x in range(cols):
            val = grid[y][x]
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            if val == '#':
                pygame.draw.rect(screen, COLOR_WALL, rect)
                pygame.draw.rect(screen, COLOR_WALL_GLOW, rect.inflate(-tile_size//8, -tile_size//8), 2)
            elif val in ['.', 'S', 'G', 'K']:
                pygame.draw.rect(screen, COLOR_PASSAGE, rect)
                cx, cy = x * tile_size + tile_size // 2, y * tile_size + tile_size // 2
                if val == 'S': pygame.draw.circle(screen, (255, 80, 80), (cx, cy), tile_size // 4)
                elif val == 'G': pygame.draw.circle(screen, COLOR_GOAL, (cx, cy), tile_size // 4)
                elif val == 'K': pygame.draw.circle(screen, COLOR_KEY, (cx, cy), tile_size // 6)

def draw_pacman(screen, x, y, tile_size, angle):
    cx, cy = x * tile_size + tile_size // 2, y * tile_size + tile_size // 2
    radius = tile_size // 2 - 3
    start_a, end_a = math.radians(angle - 30), math.radians(angle + 30)
    pygame.draw.circle(screen, (255, 255, 0), (cx, cy), radius)
    pygame.draw.polygon(screen, COLOR_PASSAGE, [(cx, cy), 
        (cx + radius * math.cos(start_a), cy + radius * math.sin(start_a)),
        (cx + radius * math.cos(end_a), cy + radius * math.sin(end_a))])

def draw_guardian(screen, g, tile_size):
    cx, cy = g.x * tile_size + tile_size // 2, g.y * tile_size + tile_size // 2
    radius = tile_size // 2 - 3
    pygame.draw.ellipse(screen, g.color, (cx - radius, cy - radius, radius * 2, radius * 2))
    for i in range(-1, 2):
        pygame.draw.circle(screen, (50, 0, 70), (cx + i * (radius // 2), cy + radius // 2), radius // 4)
    off = radius // 3
    for px_off in [-off, off]:
         pygame.draw.circle(screen, (255, 255, 255), (cx + px_off, cy - off // 2), radius // 4)
         pygame.draw.circle(screen, (0, 0, 0), (cx + px_off, cy - off // 2), radius // 8)

def draw_bfs(screen, agent, tile_size):
     pygame.draw.circle(screen, (255, 140, 0),
            (agent.x * tile_size + tile_size // 2, agent.y * tile_size + tile_size // 2), tile_size // 5)

def show_win_message(screen, level):
    screen.fill(COLOR_BG)
    t = FONT_BIG.render(f"🏆 LEVEL {level} COMPLETED!", True, (255, 255, 0))
    m = FONT_SMALL.render("Press [N] to Next Level", True, (200, 200, 200))
    screen.blit(t, (settings.WINDOW_SIZE//2 - t.get_width()//2, settings.WINDOW_SIZE//2 - 50))
    screen.blit(m, (settings.WINDOW_SIZE//2 - m.get_width()//2, settings.WINDOW_SIZE//2 + 10))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_n: return