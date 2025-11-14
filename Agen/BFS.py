import random
from collections import deque

class BFSAgent:
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

    def is_guardian_near(self, guardians, radius=3):
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
            score = sum([abs(nx - g.x) + abs(ny - g.y) for g in guardians])
            if score > best_score:
                best_score = score
                best = (nx, ny)
        return best

    def _neighbors(self, x, y, maze):
        moves = [(0,1),(1,0),(0,-1),(-1,0)]
        random.shuffle(moves)
        res = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= ny < len(maze) and 0 <= nx < len(maze[0]):
                if maze[ny][nx] != '#':
                    res.append((nx, ny))
        return res

    def compute_path(self, maze):
        start = (self.x, self.y)
        goal = self.current_goal
        if goal is None:
            return []
        q = deque([start])
        came = {start: None}
        while q:
            cur = q.popleft()
            if cur == goal:
                break
            for nb in self._neighbors(cur[0], cur[1], maze):
                if nb not in came:
                    came[nb] = cur
                    q.append(nb)
        if goal not in came:
            return []
        path = []
        node = goal
        while node != start:
            path.append(node)
            node = came[node]
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
        """Single-tick update for BFS agent: no teleport, pathfind by BFS, fallback exploration, avoidance."""
        if not self.alive:
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

        for g in guardians:
            if (self.x, self.y) == (g.x, g.y):
                return

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
                return
            else:
                self.x, self.y = self.prev
                return

        self.path = self.compute_path(maze)
        if self.path:
            nx, ny = self.path[0]
            self.x, self.y = nx, ny
            self.explored.add((self.x, self.y))
            if self.has_key and (self.x, self.y) == self.goal:
                self.finished = True
            return

        neighbors = self._neighbors(self.x, self.y, maze)
        for nb in neighbors:
            if nb not in self.explored:
                self.x, self.y = nb
                self.explored.add((self.x, self.y))
                return

        if neighbors:
            self.x, self.y = neighbors[0]
            self.explored.add((self.x, self.y))

        if self.has_key and (self.x, self.y) == self.goal:
            self.finished = True
