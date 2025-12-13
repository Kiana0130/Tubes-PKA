import random
from collections import deque

class BFSAgent:
    def __init__(self, start_x, start_y, keys, goal):
        self.x = start_x
        self.y = start_y
        self.prev = None

        self.true_keys = set(keys)
        self.true_goal = goal
        
        self.memory_keys = []
        self.memory_goal = None
        self.has_key = False
        
        # Status
        self.alive = True
        self.finished = False
        self.current_run_steps = 0
        self.nodes_expanded = 0 # METRIK PENTING: Untuk perbandingan di laporan
        
        self.path = []
        self.vision_radius = 5
        self.explored = set()
        self.explored.add((self.x, self.y))
        
        self.latest_scan = []
        self.just_replanned = False

    def scan_surroundings(self, maze, specific_radius=None):
        """Mengecek area sekitar untuk mencari Key atau Goal (Sama persis dengan A*)"""
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
                    # print(f"BFS Agent melihat KUNCI di {(x, y)}!")

                if (x, y) == self.true_goal and self.memory_goal is None:
                    self.memory_goal = (x, y)
                    found_something_new = True
                    # print(f"BFS Agent melihat GOAL di {(x, y)}!")
        
        return found_something_new

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
            current_dist = sum([abs(nx - g.x) + abs(ny - g.y) for g in guardians])
            if current_dist > best_score:
                best_score = current_dist
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

    def compute_path(self, maze, target, guardians=[], visualize=True):
        """Menghitung path menggunakan BFS (Breadth-First Search)"""
        if visualize:
            self.latest_scan = []
            self.just_replanned = True
        
        start = (self.x, self.y)
        goal = target
        
        if not goal:
            return []
        
        danger_zone = set()
        if guardians:
            for g in guardians:
                # Radius 2 (sedikit lebih kecil dari A*)
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        if abs(dx) + abs(dy) <= 2:
                            danger_zone.add((g.x + dx, g.y + dy))
        q = deque([start])
        came_from = {start: None}
                
        while q:
            current = q.popleft()
            
            if visualize and current != start:
                self.latest_scan.append(current)
            
            self.nodes_expanded += 1
            
            if current == goal:
                break

            for next_node in self._neighbors(current[0], current[1], maze):
                if next_node in danger_zone and next_node != goal:
                    continue
                
                if next_node not in came_from:
                    came_from[next_node] = current
                    q.append(next_node)
        
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
        if self.is_guardian_near(guardians, radius=2):
            avoid_pos = self.get_avoid_direction(maze, guardians)
            if avoid_pos:
                self.prev = (self.x, self.y)
                self.x, self.y = avoid_pos
                self.current_run_steps += 1
                
                # Silent Replan (Tanpa Visualisasi)
                if current_target:
                    self.path = self.compute_path(maze, current_target, guardians, visualize=False)
                else:
                    self.path = []
                return # Langsung keluar agar tidak ditimpa logika di bawah

        # 4. PATHFINDING RUTIN (JALAN MENUJU TARGET)
        # Hanya hitung ulang jika ada info baru ATAU path habis
        if found_new_info or not self.path:
            if current_target:
                # PERBAIKAN UTAMA: visualize=False untuk pergerakan rutin!
                # Kita sudah scan global di awal, jadi pergerakan biasa tidak perlu animasi scan lagi.
                # Kecuali kamu benar-benar ingin melihat scan setiap langkah, biarkan False.
                do_visualize = False 
                
                # Opsional: Jika path kosong total (awal game), boleh visualize True
                if self.current_run_steps == 0:
                    do_visualize = True

                self.path = self.compute_path(maze, current_target, guardians, visualize=do_visualize)
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