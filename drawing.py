# drawing.py
import pygame
import math
import sys
import settings

def draw_modern_grid(screen, grid, tile_size):
    rows = len(grid)
    cols = len(grid[0])
    for y in range(rows):
        for x in range(cols):
            val = grid[y][x]
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)

            if val == '#':
                # Dinding neon biru
                pygame.draw.rect(screen, settings.COLOR_WALL, rect)
                inner_rect = rect.inflate(-tile_size // 8, -tile_size // 8)
                pygame.draw.rect(screen, settings.COLOR_WALL_GLOW, inner_rect, 2)
            elif val in ['.', 'S', 'G', 'K']:
                # Jalan dengan efek gelap lembut
                pygame.draw.rect(screen, settings.COLOR_PASSAGE, rect)
                if val == 'S':
                    pygame.draw.circle(screen, settings.COLOR_START,
                        (x * tile_size + tile_size // 2, y * tile_size + tile_size // 2), tile_size // 4)
                elif val == 'G':
                    pygame.draw.circle(screen, settings.COLOR_GOAL,
                        (x * tile_size + tile_size // 2, y * tile_size + tile_size // 2), tile_size // 4)
                elif val == 'K':
                    pygame.draw.circle(screen, settings.COLOR_KEY,
                        (x * tile_size + tile_size // 2, y * tile_size + tile_size // 2), tile_size // 6)

def draw_pacman(screen, x, y, tile_size, angle, color=(255,255,0)):
    """Draws the player (Pac-Man)"""
    cx = x * tile_size + tile_size // 2
    cy = y * tile_size + tile_size // 2
    radius = tile_size // 2 - 3
    
    # Calculate mouth angles
    start_angle = math.radians(angle + 30)
    end_angle = math.radians(angle - 30 + 360) # Use 360-degree logic
    
    # Body
    pygame.draw.circle(screen, color, (cx, cy), radius)
    
    # Mouth (draw a pie slice of the background color)
    points = [(cx, cy)]
    for n in range(int(start_angle * 180 / math.pi), int(end_angle * 180 / math.pi)):
        px = cx + radius * math.cos(math.radians(n))
        py = cy + radius * math.sin(math.radians(n))
        points.append((px, py))
    points.append((cx, cy))

    if len(points) > 2:
        pygame.draw.polygon(screen, settings.COLOR_PASSAGE, points)


def draw_guardian_monster(screen, x, y, tile_size, color):
    """Draws the enemy (Guardian)"""
    cx = x * tile_size + tile_size // 2
    cy = y * tile_size + tile_size // 2
    radius = tile_size // 2 - 3

    # badan monster
    body_rect = pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)
    pygame.draw.ellipse(screen, color, body_rect)

    # kaki monster
    leg_w = radius // 2
    leg_y = cy + radius // 2
    for i in range(-1, 2):
        pygame.draw.circle(screen, (50, 0, 70), (cx + i * leg_w, leg_y), radius // 4)

    # mata putih & pupil
    eye_offset = radius // 3
    pygame.draw.circle(screen, (255, 255, 255), (cx - eye_offset, cy - eye_offset // 2), radius // 4)
    pygame.draw.circle(screen, (255, 255, 255), (cx + eye_offset, cy - eye_offset // 2), radius // 4)
    pygame.draw.circle(screen, (0, 0, 0), (cx - eye_offset, cy - eye_offset // 2), radius // 8)
    pygame.draw.circle(screen, (0, 0, 0), (cx + eye_offset, cy - eye_offset // 2), radius // 8)


def show_win_message(screen, level, font_big, font_small):
    """Displays the level complete screen"""
    screen.fill(settings.COLOR_BG)
    title = font_big.render(f"🏆 LEVEL {level} COMPLETED!", True, (255, 255, 0))
    msg = font_small.render("Press [N] to go to Next Level", True, (200, 200, 200))
    screen.blit(title, (settings.WINDOW_SIZE // 2 - title.get_width() // 2, settings.WINDOW_SIZE // 2 - 50))
    screen.blit(msg, (settings.WINDOW_SIZE // 2 - msg.get_width() // 2, settings.WINDOW_SIZE // 2 + 10))
    pygame.display.flip()

    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_n:
                waiting = False
        pygame.time.delay(100)