import time

class AStarAgent:
    def __init__(self, x, y, keys, goal):
        self.x = x
        self.y = y
        self.keys = keys
        self.goal = goal 
        self.has_key = False
        self.current_goal = keys[0] if keys else goal
        
        self.current_path = None 

    def _heuristic(self, a, b):
        (x1,y1) = a
        (x2,y2) = b
        return abs(x1-x2)+abs(y1-y2)

    def _neighbors(self,x,y):
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            yield (x+dx,y+dy)

    def find_path(self,grid,start,goal):
        walk = {'.','S','G','K'}
        open_set = {start}
        came = {}
        g = {start:0}
        f = {start:self._heuristic(start,goal)}
        
        while open_set:
            current = min(open_set, key=lambda o: f.get(o,999999))
            
            if current == goal:
                path=[current]
                while current in came:
                    current=came[current]
                    path.append(current)
                return path[::-1], len(g) 
            
            open_set.remove(current)
            cx,cy=current
            
            for nx,ny in self._neighbors(cx,cy):
                if ny<0 or ny>=len(grid) or nx<0 or nx>=len(grid[0]):
                    continue
                if grid[ny][nx] not in walk:
                    continue
                
                tg=g[current]+1
                
                if tg<g.get((nx,ny),999999):
                    came[(nx,ny)]=current
                    g[(nx,ny)]=tg 
                    f[(nx,ny)]=tg+self._heuristic((nx,ny),goal)
                    open_set.add((nx,ny))
                    
        return None, len(g)

    def step(self, grid):
        if not self.has_key and (self.x, self.y) in self.keys:
            print("[A* Agent] Mengambil Kunci!")
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
                
                print("--- [A* Agent] Menghitung Path Baru ---")
                print(f"  > Target: {self.current_goal}")
                print(f"  > 1. Waktu Komputasi: {computation_time:.8f} detik")
                print(f"  > 2. Node Dieksplorasi: {explored_count} node")
                print(f"  > 3. Panjang Path: {len(self.current_path)} langkah")
                print("------------------------------------------")
                
            else:
                print("[A* Agent] Tidak ada path ditemukan!")
                self.current_path = []
                return self.x, self.y

        if self.current_path:
            next_step = self.current_path.pop(0)
            self.x, self.y = next_step
            return self.x, self.y
        else:
            return self.x, self.y