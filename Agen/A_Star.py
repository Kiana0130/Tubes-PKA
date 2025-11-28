import heapq
import math
import random

class AStarAgent:
    def __init__(self, start_x, start_y, keys, goal):
        self.x = start_x
        self.y = start_y
        self.prev = (start_x, start_y)
        self.keys = keys
        self.goal = goal
        self.has_key = False
        self.alive = True

        self.explored = set()
        self.path = []
        self.current_goal = None
        self.finished = False
        # MODIFIKASI: Menambahkan penghitung langkah
        self.current_run_steps = 0

    def is_guardian_near(self, guardians, radius=1):
        if not guardians:
            return False
        for g in guardians:
            if abs(self.x - g.x) + abs(self.y - g.y) <= radius:
                return True
        return False

    def get_avoid_direction(self, maze, guardians):
        best = None
        best_score = -1
        for nx, ny in self._neighbors(self.x, self.y, maze):
            s = 0
            for g in guardians:
                s += -(abs(nx-g.x) + abs(ny-g.y))
            score = -s
            if score > best_score:
                best_score = score
                best = (nx, ny)
        return best

    def _neighbors(self, x, y, maze):
        moves = [(0,1),(1,0),(0,-1),(-1,0)]
        random.shuffle(moves)
        result = []
        for dx, dy in moves:
            nx, ny = x+dx, y+dy
            if 0 <= ny < len(maze) and 0 <= nx < len(maze[0]):
                if maze[ny][nx] != '#':
                    result.append((nx, ny))
        return result

    def _heuristic(self, a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def compute_path(self, maze):
        if self.current_goal is None:
            return []

        start = (self.x, self.y)
        goal = self.current_goal

        open_set = []
        heapq.heappush(open_set, (0 + self._heuristic(start, goal), 0, start))
        came_from = {start: None}
        gscore = {start: 0}
        visited = set()

        while open_set:
            _, cost, current = heapq.heappop(open_set)
            if current == goal:
                break
            if current in visited:
                continue
            visited.add(current)

            for nb in self._neighbors(current[0], current[1], maze):
                tentative = gscore[current] + 1
                if nb not in gscore or tentative < gscore[nb]:
                    gscore[nb] = tentative
                    priority = tentative + self._heuristic(nb, goal) + random.uniform(0, 0.2)
                    heapq.heappush(open_set, (priority, tentative, nb))
                    came_from[nb] = current

        if goal not in came_from:
            return []

        path = []
        node = goal
        while node != start:
            path.append(node)
            node = came_from[node]
        path.reverse()
        return path

    def _nearest_key(self):
        if not self.keys:
            return None
        best = None
        bestd = 1e9
        for k in self.keys:
            d = abs(self.x - k[0]) + abs(self.y - k[1])
            if d < bestd:
                bestd = d
                best = k
        return best

    def step(self, maze, guardians):
        if not  self.alive:
            return
        if self.finished:
            return
            
        self.prev = (self.x, self.y)
        self.explored.add((self.x, self.y))
        
        if not self.has_key and (self.x, self.y) in self.keys:
            self.has_key = True
            try:
                self.keys.remove((self.x, self.y))
            except ValueError:
                pass
                
        if self.has_key:
            self.current_goal = self.goal
        else:
            self.current_goal = self._nearest_key()
            
        if self.is_guardian_near(guardians, radius=1):
            avoid = self.get_avoid_direction(maze, guardians)
            if avoid is not None:
                if avoid == self.prev:
                    for nb in self._neighbors(self.x, self.y, maze):
                        if nb != self.prev:
                            avoid = nb
                            break
                self.x, self.y = avoid
                self.explored.add((self.x, self.y))
                # MODIFIKASI: Increment langkah setelah move menghindari guardian
                if (self.x, self.y) != self.prev:
                    self.current_run_steps += 1
                return
            else:
                self.x, self.y = self.prev
                return
                
        self.path = self.compute_path(maze)
        if self.path:
            nx, ny = self.path[0]
            self.x, self.y = nx, ny
            self.explored.add((self.x, self.y))
            # MODIFIKASI: Increment langkah setelah move pathing
            self.current_run_steps += 1
            
        else:
            neighbors = self._neighbors(self.x, self.y, maze)
            moved = False
            for nb in neighbors:
                if nb not in self.explored:
                    self.x, self.y = nb
                    self.explored.add((self.x, self.y))
                    moved = True
                    # MODIFIKASI: Increment langkah setelah move eksplorasi
                    self.current_run_steps += 1 
                    break
            if not moved and neighbors:
                self.x, self.y = neighbors[0]
                self.explored.add((self.x, self.y))
                # MODIFIKASI: Increment langkah setelah move fallback
                self.current_run_steps += 1
                

        if self.has_key and (self.x, self.y) == self.goal:
            self.finished = True