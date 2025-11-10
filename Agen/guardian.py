import random

class Guardian:
    def __init__(self, grid, start_pos, color):
        """
        Initializes the Guardian agent.
        
        Args:
            grid (List[List[str]]): The map grid.
            start_pos (tuple[int, int]): The (x, y) starting position.
            color (tuple[int, int, int]): The RGB color for this guardian.
        """
        self.x, self.y = start_pos
        self.color = color
        self.grid_height = len(grid)
        self.grid_width = len(grid[0])

    def _get_valid_neighbors(self, grid, x, y):
        """
        Finds all walkable neighboring cells.
        """
        neighbors = []
        walkable = {'.', 'S', 'G', 'K'}
        
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            
            # Check bounds
            if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                # Check if walkable
                if grid[ny][nx] in walkable:
                    neighbors.append((nx, ny))
        return neighbors

    def roam(self, grid):
        """
        Moves the guardian to a random valid neighboring cell.
        """
        # Get all possible moves from the current position
        valid_moves = self._get_valid_neighbors(grid, self.x, self.y)
        
        if valid_moves:
            # Pick one random move
            self.x, self.y = random.choice(valid_moves)
            
    def move_towards_player(self, player_x, player_y):
        """
        (Original function, now unused but kept for reference)
        A simple, non-pathfinding move towards the player.
        """
        # This is a basic "move towards" logic.
        # A real implementation would use a pathfinding algorithm like BFS or A*.
        if self.x < player_x:
            self.x += 1
        elif self.x > player_x:
            self.x -= 1
        
        if self.y < player_y:
            self.y += 1
        elif self.y > player_y:
            self.y -= 1