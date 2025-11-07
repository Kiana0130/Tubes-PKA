from collections import deque
import time

class BFSAgent:
    def __init__(self, x, y, keys, goal):
        self.x = x
        self.y = y
        self.keys = keys
        self.goal = goal
        self.has_key = False
        self.current_goal = keys[0] if keys else goal
        self.current_path = None

    def _neighbors(self, x, y):
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]: 
                yield (x+dx,y+dy)

    def find_path(self, grid, start, goal):
        walk = {'.','S','G','K'}
        q = deque([start])
        came = {start:None} 
        while q:
            cx,cy = q.popleft()
            if (cx,cy) == goal:
                path=[(cx,cy)]
                while came[(cx,cy)] is not None:
                    cx,cy = came[(cx,cy)]
                    path.append((cx,cy))
                return path[::-1], len(came) 
            
            for nx,ny in self._neighbors(cx,cy):
                if 0<=ny<len(grid) and 0<=nx<len(grid[0]):
                    if grid[ny][nx] in walk and (nx,ny) not in came:
                        came[(nx,ny)] = (cx,cy) 
                        q.append((nx,ny))
        return None, len(came)

    def step(self, grid):
        if not self.has_key and (self.x, self.y) in self.keys:
            print("[BFS Agent] Mengambil Kunci!")
            self.has_key = True
            self.current_goal = self.goal
            self.current_path = None 
        if self.current_path is None:
            start = (self.x, self.y)
            start_time = time.perf_counter()
            path_result = self.find_path(grid, start, self.current_goal)
            end_time = time.perf_counter()
            computation_time = end_time - start_time

            if path_result[0]: 
                path, explored_count = path_result
                self.current_path = path[1:]
                print("--- [BFS Agent] Menghitung Path Baru ---")
                print(f"  > Target: {self.current_goal}")
                print(f"  > 1. Waktu Komputasi: {computation_time:.8f} detik")
                print(f"  > 2. Node Dieksplorasi: {explored_count} node")
                print(f"  > 3. Panjang Path: {len(self.current_path)} langkah")
                print("------------------------------------------")
            else:
                print("[BFS Agent] Tidak ada path ditemukan!")
                self.current_path = []
                return self.x, self.y

        if self.current_path:
            next_step = self.current_path.pop(0)
            self.x, self.y = next_step
            return self.x, self.y
        else:
            return self.x, self.y