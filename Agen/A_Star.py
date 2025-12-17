import heapq
import math
import random
import time
from collections import deque

class AStarAgent:
    def __init__(self, start_x, start_y, keys, goal):
        self.x = start_x
        self.y = start_y
        self.prev = (None)
        
        self.true_keys = set(keys)
        self.true_goal = goal
        
        self.memory_keys = []
        self.memory_goal = None
        self.has_key = False
        
        self.alive = True
        self.finished = False
        self.current_run_steps = 0
        self.nodes_expanded = 0
        
        self.path = []
        self.vision_radius = 5          
        self.explored = set()
        self.explored.add((self.x, self.y))
        
        self.latest_scan = []
        self.just_replanned = False
        
        self.total_compute_time = 0.0  
        self.last_compute_time = 0.0  
        self.compute_counts = 0
        
        self.position_history = deque(maxlen=6) 
        self.patience = 5                       
        self.rush_mode = False

    def scan_surroundings(self, maze, specific_radius=None):
        """Mengecek area sekitar untuk mencari Key atau Goal"""
        radius = specific_radius if specific_radius is not None else self.vision_radius
        min_x = max(0, self.x - radius)
        max_x = min(len(maze[0]), self.x + radius + 1)
        min_y = max(0, self.y - radius)
        max_y = min(len(maze), self.y + radius + 1)

        found_something_new = False

        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                if (x, y) in self.true_keys and (x, y) not in self.memory_keys:
                    self.memory_keys.append((x, y))
                    found_something_new = True
                    # print(f"A* Agent melihat KUNCI di {(x, y)}!")
                if (x, y) == self.true_goal and self.memory_goal is None:
                    self.memory_goal = (x, y)
                    found_something_new = True
                    # print(f"A* Agent melihat GOAL di {(x, y)}!")
        
        return super().scan_surroundings(maze, specific_radius) if hasattr(super(), 'scan_surroundings') else self._original_scan(maze, specific_radius)
    
    def _original_scan(self, maze, specific_radius=None):
        pass

    def is_guardian_near(self, guardians, radius=1):
        if not guardians:
            return False
        for g in guardians:
            if abs(self.x - g.x) + abs(self.y - g.y) <= radius:
                return True
        return False

    def get_avoid_direction(self, maze, guardians):
        best = None
        best_score = -9999
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
        weight = 1.5
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def compute_path(self, maze, target, guardians=[], visualize=True, ignore_danger=False):
        start_timer = time.perf_counter()
        if visualize:
            self.latest_scan = []
            self.just_replanned = True
        
        start = (self.x, self.y)
        goal = target
        
        
        danger_zone = set()
        if guardians and not ignore_danger:
            for g in guardians:
                for dy in range(-3, 4):
                    for dx in range(-3, 4):
                        if abs(dx) + abs(dy) <= 3:
                            danger_zone.add((g.x + dx, g.y + dy))
                            
        open_set = []
        heapq.heappush(open_set, (0, 0, start))
        came_from = {start: None}
        gscore = {start: 0}
        
        while open_set:
            _, cost, current = heapq.heappop(open_set)
            
            if current != start:
                self.latest_scan.append(current)
            
            self.nodes_expanded += 1
            
            if current == goal:
                break

            for nb in self._neighbors(current[0], current[1], maze):
                extra_cost = 0
                if nb in danger_zone:
                    extra_cost = 50
                tentative = gscore[current] + 1 + extra_cost
                if nb not in gscore or tentative < gscore[nb]:
                    gscore[nb] = tentative
                    priority = tentative + (self._heuristic(nb, goal) * 1.5)
                    heapq.heappush(open_set, (priority, tentative, nb))
                    came_from[nb] = current

        end_timer = time.perf_counter() # STOP TIMER
        execution_time = (end_timer - start_timer) * 1000 # Konversi ke ms
        self.last_compute_time = execution_time
        self.total_compute_time += execution_time
        self.compute_counts += 1

        if goal not in came_from:
            return []

        path = []
        node = goal
        while node != start:
            path.append(node)
            node = came_from[node]
        path.reverse()
        return path
    
    def get_exploration_target(self, maze):
        neighbors = self._neighbors(self.x, self.y, maze)
        unvisited = [n for n in neighbors if n not in self.explored]
        
        if unvisited:
            return random.choice(unvisited)
        candidates = [n for n in neighbors if n != self.prev]
        if candidates:
            return random.choice(candidates)
        elif neighbors:
            return random.choice(neighbors)
            
        return (self.x, self.y)
    
    def check_deadlock(self):
        """Mendeteksi apakah agen bolak-balik di tempat yang sama (panik)."""
        self.position_history.append((self.x, self.y))
        
        if len(self.position_history) < 6:
            return False
            
        # Jika dalam 6 langkah terakhir jumlah posisi uniknya sedikit (misal cuma 2 atau 3)
        # Berarti dia cuma bolak-balik A-B-A-B atau A-B-C-B-A
        unique_pos = set(self.position_history)
        if len(unique_pos) <= 3:
            return True
        return False

    def step(self, maze, guardians):
        if not self.alive or self.finished:
            return

        # 1. SCAN GLOBAL (Hanya Visualisasi di sini!)
        # Scan Key Awal
        if not self.has_key and not self.memory_keys:
            self.scan_surroundings(maze, specific_radius=999)
            # Tidak perlu return, biarkan lanjut ke logika pathfinding
            
        # Scan Goal setelah dapat Key
        if self.has_key and self.memory_goal is None:
            self.scan_surroundings(maze, specific_radius=999)

        # Scan rutin (radius pendek) - TIDAK BOLEH MEMICU ANIMASI
        found_new_info = self.scan_surroundings(maze) 
        is_stuck = self.check_deadlock()
        if is_stuck:
            self.patience -= 1
            # print(f"A* Frustasi... Kesabaran: {self.patience}")
        else:
            self.patience = 5 # Reset jika bergerak lancar
            self.rush_mode = False

        if self.patience <= 0:
            self.rush_mode = True # AKTIFKAN MODE NEKAT
            # print("A* MARAH! Menerobos Danger Zone!")
        current_target = None
        
        # 2. TENTUKAN TARGET
        if not self.has_key:
            if (self.x, self.y) in self.true_keys:
                self.has_key = True
                self.true_keys.remove((self.x, self.y))
                if (self.x, self.y) in self.memory_keys:
                    self.memory_keys.remove((self.x, self.y))
                self.path = [] 
                
                # Visualisasi Scan Pintu (Hanya saat momen dapat kunci)
                self.scan_surroundings(maze, specific_radius=999) 
                self.position_history.clear()
                self.patience = 5
                
                if self.memory_goal:
                    current_target = self.memory_goal
            elif self.memory_keys:
                current_target = self.memory_keys[0]
            else:
                current_target = None
        else:
            if (self.x, self.y) == self.true_goal:
                self.finished = True
                return
            if self.memory_goal:
                current_target = self.memory_goal
            else:
                current_target = None

        # 3. LOGIKA MENGHINDAR (PRIORITAS TERTINGGI)
        # Gunakan if-elif-else agar logika di bawahnya tidak menimpa hasil menghindar
        must_avoid = self.is_guardian_near(guardians, radius=2)
        if self.rush_mode:
            must_avoid = False
        if must_avoid:
            avoid_pos = self.get_avoid_direction(maze, guardians)
            if avoid_pos:
                self.prev = (self.x, self.y)
                self.x, self.y = avoid_pos
                self.current_run_steps += 1
                
                if current_target:
                    # Replan tanpa visualisasi
                    self.path = self.compute_path(maze, current_target, guardians, visualize=False)
                else:
                    self.path = []
                return

        # 4. PATHFINDING RUTIN
        if found_new_info or not self.path or (self.rush_mode and is_stuck):
            if current_target:
                do_visualize = False 
                if self.current_run_steps == 0:
                    do_visualize = True

                # KIRIM PARAMETER ignore_danger BERDASARKAN RUSH MODE
                self.path = self.compute_path(maze, current_target, guardians, visualize=do_visualize, ignore_danger=self.rush_mode)
            else:
                next_step = self.get_exploration_target(maze)
                if next_step:
                    self.path = [next_step]

        # 5. EKSEKUSI LANGKAH
        if self.path:
            next_pos = self.path.pop(0)
            death = False
            for g in guardians:
                if (g.x, g.y) == next_pos:
                    death = True
            
            if not death:
                self.prev = (self.x, self.y)
                self.x, self.y = next_pos
                self.explored.add((self.x, self.y))
                self.current_run_steps += 1