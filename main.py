import pygame
import sys
import map_generator
import settings
from Agen.A_Star import AStarAgent
from Agen.BFS import BFSAgent

pygame.init()

LEVEL = 2
  
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

  start, goal, keys = find_positions(grid)
  astar = AStarAgent(start[0], start[1], keys, goal) 
  bfs   = BFSAgent(start[0], start[1], keys, goal)   
    
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
          
    nx, ny = astar.step(grid)
    astar.x, astar.y = nx, ny
    
    bx, by = bfs.step(grid)
    bfs.x, bfs.y = bx, by

    
    if astar.has_key and (astar.x, astar.y) == goal:
      print("Player menang level", LEVEL)

      LEVEL = LEVEL + 1 if LEVEL < 3 else 1

      grid = map_generator.generate_maze(LEVEL)
      start, goal, keys = find_positions(grid)
      astar = AStarAgent(start[0], start[1], keys, goal)
      bfs = BFSAgent(start[0], start[1], keys, goal)
      continue
    
    size = map_generator.get_size_for_level(LEVEL)
    tile_size = settings.WINDOW_SIZE // size
    
    screen.fill((0, 0, 0))
    draw_grid(screen, grid, tile_size)

    pygame.draw.circle(
        screen,(0,0,255),
        (astar.x*tile_size + tile_size//2, astar.y*tile_size + tile_size//2),
        tile_size//3
    )
    
    pygame.draw.circle(
        screen,(255,140,0), 
        (bfs.x*tile_size + tile_size//2, bfs.y*tile_size + tile_size//2),
        tile_size//3
    )


    pygame.display.flip()
    clock.tick(5)

  pygame.quit()
  sys.exit()

def find_positions(grid):
    start = None
    goal  = None
    keys = []
    
    for y,row in enumerate(grid):
        for x,val in enumerate(row):
            if val == 'S':
                start = (x,y)
            elif val == 'G':
                goal = (x,y)
            elif val == 'K':
                keys.append( (x,y) )
    return start, goal, keys

if __name__ == '__main__':
  main()