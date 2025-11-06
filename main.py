import pygame
import sys
import map_generator
import settings

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
      elif val == 'S':
        color = settings.COLOR_START
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

def main():
  global LEVEL
  clock = pygame.time.Clock()
  
  grid = map_generator.generate_maze(LEVEL)
  screen = make_window()

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
        elif event.key == pygame.K_n:
          LEVEL = LEVEL + 1 if LEVEL < 3 else 1
          grid = map_generator.generate_maze(LEVEL)
          
    size = map_generator.get_size_for_level(LEVEL)
    tile_size = settings.WINDOW_SIZE // size
    
    screen.fill((0, 0, 0))
    draw_grid(screen, grid, tile_size)
    pygame.display.flip()
    clock.tick(settings.FPS)

  pygame.quit()
  sys.exit()

if __name__ == '__main__':
  main()