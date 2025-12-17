# enemy.py
import math
import random

class Guardian:
    def __init__(self, grid, target, color=(180, 0, 255)):
        self.grid = grid
        self.target = target
        self.x, self.y = self._find_spawn_location(grid, target)
        self.vision_radius = 10
        self.color = color
        
        # DFS-based scouting behavior
        self.visited = set()  # Track visited positions
        self.dfs_stack = []  # Stack for DFS pathfinding
        self.current_path = []  # Current path to follow
        self.path_index = 0  # Current position in path
        
    def _find_spawn_location(self, grid, player_pos):
        """Find spawn location far from player, preferring edges"""
        h = len(grid)
        w = len(grid[0])
        
        # Get all walkable positions
        candidates = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == '.']
        
        if not candidates:
            return 0, 0  # Failsafe
        
        px, py = player_pos
        
        # Filter for edge positions (close to borders)
        edge_candidates = [
            (x, y) for x, y in candidates 
            if x <= 2 or x >= w - 3 or y <= 2 or y >= h - 3
        ]
        
        # Calculate distances from player for edge candidates
        if edge_candidates:
            distances = [(x, y, math.sqrt((x - px)**2 + (y - py)**2)) 
                        for x, y in edge_candidates]
            # Sort by distance, get furthest ones
            distances.sort(key=lambda d: d[2], reverse=True)
            
            # Pick from top 30% furthest positions
            top_count = max(1, len(distances) // 3)
            furthest = distances[:top_count]
            chosen = random.choice(furthest)
            return chosen[0], chosen[1]
        
        # Fallback: just pick furthest from player
        distances = [(x, y, math.sqrt((x - px)**2 + (y - py)**2)) 
                    for x, y in candidates]
        distances.sort(key=lambda d: d[2], reverse=True)
        chosen = distances[0]
        return chosen[0], chosen[1]
    
    def distance_to_player(self, px, py):
        return math.sqrt((self.x - px) ** 2 + (self.y - py) ** 2)
    
    def has_line_of_sight(self, px, py):
        """Check if guardian can see player using raycasting (not blocked by walls)"""
        # Check distance first
        if self.distance_to_player(px, py) > self.vision_radius:
            return False
        
        # Bresenham's line algorithm to check for walls
        x0, y0 = self.x, self.y
        x1, y1 = px, py
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            # Check if current position is a wall
            if self.grid[y0][x0] == '#':
                return False
            
            # Reached the player
            if x0 == x1 and y0 == y1:
                return True
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
    
    def move_towards_player(self, px, py):
        """Main movement logic: chase if visible, otherwise DFS scout"""
        # Mark current position as visited
        self.visited.add((self.x, self.y))
        
        # Check if player is visible
        if self.has_line_of_sight(px, py):
            self._chase_player(px, py)
            # Clear DFS state when chasing
            self.current_path = []
            self.path_index = 0
        else:
            self._dfs_scout()
    
    def _chase_player(self, px, py):
        """Move directly towards the player"""
        dx = px - self.x
        dy = py - self.y
        
        # Prioritize moving in the larger direction
        if abs(dx) > abs(dy):
            step_x = 1 if dx > 0 else -1
            if self._can_move(self.x + step_x, self.y):
                self.x += step_x
            elif dy != 0:  # If blocked, try the other direction
                step_y = 1 if dy > 0 else -1
                if self._can_move(self.x, self.y + step_y):
                    self.y += step_y
        elif dy != 0:
            step_y = 1 if dy > 0 else -1
            if self._can_move(self.x, self.y + step_y):
                self.y += step_y
            elif dx != 0:  # If blocked, try the other direction
                step_x = 1 if dx > 0 else -1
                if self._can_move(self.x + step_x, self.y):
                    self.x += step_x
    
    def _dfs_scout(self):
        """DFS-based scouting: systematically explore the maze"""
        # If we have a current path, follow it
        if self.current_path and self.path_index < len(self.current_path):
            next_pos = self.current_path[self.path_index]
            self.x, self.y = next_pos
            self.path_index += 1
            return
        
        # Need to find a new path
        self.current_path = []
        self.path_index = 0
        
        # Get unvisited neighbors, prioritizing unexplored areas
        neighbors = self._get_unvisited_neighbors()
        
        if neighbors:
            # Pick an unvisited neighbor
            target = neighbors[0]
            # Create a path to it (just one step for now)
            self.current_path = [target]
            self.path_index = 0
        else:
            # All neighbors visited, find path to nearest unvisited cell
            unvisited_target = self._find_nearest_unvisited()
            
            if unvisited_target:
                # Use BFS to find path to unvisited area
                path = self._bfs_path_to(unvisited_target)
                if path and len(path) > 1:
                    self.current_path = path[1:]  # Exclude current position
                    self.path_index = 0
                else:
                    # Can't find path, reset visited to explore again
                    self.visited.clear()
                    self.visited.add((self.x, self.y))
            else:
                # Everything explored, reset visited set
                self.visited.clear()
                self.visited.add((self.x, self.y))
    
    def _get_unvisited_neighbors(self):
        """Get adjacent walkable cells that haven't been visited"""
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Up, Right, Down, Left
        neighbors = []
        
        for dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            if self._can_move(nx, ny) and (nx, ny) not in self.visited:
                neighbors.append((nx, ny))
        
        return neighbors
    
    def _find_nearest_unvisited(self):
        """Find the nearest unvisited walkable cell"""
        h = len(self.grid)
        w = len(self.grid[0])
        
        unvisited = []
        for y in range(h):
            for x in range(w):
                if self.grid[y][x] != '#' and (x, y) not in self.visited:
                    distance = abs(x - self.x) + abs(y - self.y)  # Manhattan distance
                    unvisited.append((x, y, distance))
        
        if unvisited:
            unvisited.sort(key=lambda u: u[2])
            return (unvisited[0][0], unvisited[0][1])
        
        return None
    
    def _bfs_path_to(self, target):
        """Use BFS to find shortest path to target"""
        from collections import deque
        
        queue = deque([[(self.x, self.y)]])
        visited = {(self.x, self.y)}
        
        while queue:
            path = queue.popleft()
            x, y = path[-1]
            
            if (x, y) == target:
                return path
            
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited and self._can_move(nx, ny):
                    visited.add((nx, ny))
                    queue.append(path + [(nx, ny)])
        
        return None  # No path found
    
    def _can_move(self, x, y):
        """Check if a position is walkable"""
        h = len(self.grid)
        w = len(self.grid[0])
        if 0 <= x < w and 0 <= y < h:
            return self.grid[y][x] != '#'
        return False