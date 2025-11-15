import pygame
import sys
import math
import random
import map_generator
import settings
from Agen.A_Star import AStarAgent
from Agen.BFS import BFSAgent

pygame.init()

LEVEL = 1

# ==============================================
# Warna gaya modern
# ==============================================
COLOR_BG = (10, 10, 20)
COLOR_WALL = (30, 50, 120)
COLOR_WALL_GLOW = (0, 150, 255)
COLOR_PASSAGE = (25, 25, 40)
COLOR_KEY = (255, 215, 0)
COLOR_GOAL = (0, 255, 100)

# Font global
FONT_BIG = pygame.font.SysFont("Consolas", 36, bold=True)
FONT_SMALL = pygame.font.SysFont("Consolas", 18)

# ==============================================
# Fungsi menggambar grid modern
# ==============================================
def draw_modern_grid(screen, grid, tile_size):
    rows = len(grid)
    cols = len(grid[0])
    for y in range(rows):
        for x in range(cols):
            val = grid[y][x]
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)

            if val == '#':
                # Dinding neon biru
                pygame.draw.rect(screen, COLOR_WALL, rect)
                inner_rect = rect.inflate(-tile_size // 8, -tile_size // 8)
                pygame.draw.rect(screen, COLOR_WALL_GLOW, inner_rect, 2)
            elif val in ['.', 'S', 'G', 'K']:
                # Jalan dengan efek gelap lembut
                pygame.draw.rect(screen, COLOR_PASSAGE, rect)
                if val == 'S':
                    pygame.draw.circle(screen, (255, 80, 80),
                        (x * tile_size + tile_size // 2, y * tile_size + tile_size // 2), tile_size // 4)
                elif val == 'G':
                    pygame.draw.circle(screen, COLOR_GOAL,
                        (x * tile_size + tile_size // 2, y * tile_size + tile_size // 2), tile_size // 4)
                elif val == 'K':
                    pygame.draw.circle(screen, COLOR_KEY,
                        (x * tile_size + tile_size // 2, y * tile_size + tile_size // 2), tile_size // 6)

# ==============================================
# Window
# ==============================================
def make_window():
    screen = pygame.display.set_mode((settings.WINDOW_SIZE, settings.WINDOW_SIZE))
    pygame.display.set_caption('Maze: Pacman Neo Edition')
    return screen

# ==============================================
# Guardian Class
# ==============================================
class Guardian:
    def __init__(self, grid, target, color=(180, 0, 255)):
        self.grid = grid
        self.target = target
        self.x, self.y = self._find_spawn_location(grid)
        self.speed_counter = 0
        self.vision_radius = 6
        self.color = color

    def _find_spawn_location(self, grid):
        h = len(grid)
        w = len(grid[0])
        candidates = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == '.']
        gx, gy = random.choice(candidates)
        return gx, gy

    def distance_to_player(self, px, py):
        return math.sqrt((self.x - px) ** 2 + (self.y - py) ** 2)

    def move_towards_player(self, px, py):
        self.speed_counter += 1
        if self.speed_counter % 2 != 0:
            return

        if self.distance_to_player(px, py) <= self.vision_radius:
            dx = px - self.x
            dy = py - self.y
            if abs(dx) > abs(dy):
                step_x = 1 if dx > 0 else -1
                if self._can_move(self.x + step_x, self.y):
                    self.x += step_x
            elif dy != 0:
                step_y = 1 if dy > 0 else -1
                if self._can_move(self.x, self.y + step_y):
                    self.y += step_y
        else:
            self._wander_randomly()

    def _wander_randomly(self):
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            if self._can_move(nx, ny):
                self.x, self.y = nx, ny
                break

    def _can_move(self, x, y):
        h = len(self.grid)
        w = len(self.grid[0])
        if 0 <= x < w and 0 <= y < h:
            return self.grid[y][x] != '#'
        return False

# ==============================================
# Gambar karakter modern
# ==============================================
def draw_pacman(screen, x, y, tile_size, angle):
    cx = x * tile_size + tile_size // 2
    cy = y * tile_size + tile_size // 2
    radius = tile_size // 2 - 3
    start_angle = math.radians(angle - 30)
    end_angle = math.radians(angle + 30)
    pygame.draw.circle(screen, (255, 255, 0), (cx, cy), radius)
    pygame.draw.polygon(
        screen, COLOR_PASSAGE,
        [(cx, cy),
         (cx + radius * math.cos(start_angle), cy + radius * math.sin(start_angle)),
         (cx + radius * math.cos(end_angle), cy + radius * math.sin(end_angle))]
    )

def draw_guardian_monster(screen, x, y, tile_size, color):
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

# ==============================================
# Posisi penting
# ==============================================
def find_positions(grid):
    start = None
    goal = None
    keys = []
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            if val == 'S': start = (x, y)
            elif val == 'G': goal = (x, y)
            elif val == 'K': keys.append((x, y))
    return start, goal, keys

# ==============================================
# Pesan kemenangan di layar
# ==============================================
def show_win_message(screen, level):
    screen.fill(COLOR_BG)
    title = FONT_BIG.render(f"🏆 LEVEL {level} COMPLETED!", True, (255, 255, 0))
    msg = FONT_SMALL.render("Press [N] to go to Next Level", True, (200, 200, 200))
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

    guardians = [
        Guardian(grid, (astar.x, astar.y), color=(180, 0, 255)),
        Guardian(grid, (astar.x, astar.y), color=(255, 0, 150))
    ]

    direction_angle = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                    running = False
                elif event.key == pygame.K_r:
                    grid = map_generator.generate_maze(LEVEL)
                elif event.key == pygame.K_n:
                    LEVEL = LEVEL + 1 if LEVEL < 3 else 1
                    grid = map_generator.generate_maze(LEVEL)

        # Langkah player
        nx, ny = astar.step(grid)
        if nx > astar.x: direction_angle = 0
        elif nx < astar.x: direction_angle = 180
        elif ny > astar.y: direction_angle = 90
        elif ny < astar.y: direction_angle = 270
        astar.x, astar.y = nx, ny

        # BFS
        bx, by = bfs.step(grid)
        bfs.x, bfs.y = bx, by

        # Guardian
        for guardian in guardians:
            guardian.target = (astar.x, astar.y)
            guardian.move_towards_player(astar.x, astar.y)

        # Cek kalah
        for guardian in guardians:
            if (guardian.x, guardian.y) == (astar.x, astar.y):
                print("💀 Guardian menang! Player tertangkap.")
                running = False

        # Cek menang
        if astar.has_key and (astar.x, astar.y) == goal:
            print("🏆 Player menang level", LEVEL)
            show_win_message(screen, LEVEL)
            LEVEL = LEVEL + 1 if LEVEL < 3 else 1
            grid = map_generator.generate_maze(LEVEL)
            start, goal, keys = find_positions(grid)
            astar = AStarAgent(start[0], start[1], keys, goal)
            bfs = BFSAgent(start[0], start[1], keys, goal)
            guardians = [
                Guardian(grid, (astar.x, astar.y), color=(180, 0, 255)),
                Guardian(grid, (astar.x, astar.y), color=(255, 0, 150))
            ]
            continue

        # --- Gambar semua ---
        size = map_generator.get_size_for_level(LEVEL)
        tile_size = settings.WINDOW_SIZE // size
        screen.fill(COLOR_BG)
        draw_modern_grid(screen, grid, tile_size)

        # Player Pac-Man
        draw_pacman(screen, astar.x, astar.y, tile_size, direction_angle)

        # BFS Agent
        pygame.draw.circle(
            screen, (255, 140, 0),
            (bfs.x * tile_size + tile_size // 2, bfs.y * tile_size + tile_size // 2),
            tile_size // 5
        )

        # Guardian Monster
        for guardian in guardians:
            draw_guardian_monster(screen, guardian.x, guardian.y, tile_size, guardian.color)

        pygame.display.flip()
        clock.tick(6)

    pygame.quit()
    sys.exit()

# ==============================================
if __name__ == '__main__':
    main()

