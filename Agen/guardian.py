import random
from collections import deque
import math

class Guardian:
    def __init__(self, grid, start_pos, color):
        self.x, self.y = start_pos
        self.grid = grid
        self.rows = len(grid) 
        self.cols = len(grid[0])
        self.color = color
        self.state = 'SCOUTING'
        self.current_path = []
        self.vision_range = 10
        self.minimax_depth = 6

    def _is_valid(self, x, y, check_walls=True):
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
        if check_walls and self.grid[y][x] == '#':
            return False
        return True

    def _neighbors(self, x, y):
        moves = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if self._is_valid(nx, ny):
                moves.append((nx, ny))
        return moves

    def _find_path_bfs(self, start, goal):
        if not self._is_valid(goal[0], goal[1]):
            return []

        q = deque([start])
        came_from = {start: None}
        
        while q:
            current = q.popleft()
            if current == goal:
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                return path[::-1][1:]

            for next_node in self._neighbors(current[0], current[1]):
                if next_node not in came_from:
                    came_from[next_node] = current
                    q.append(next_node)
        return []

    def _get_random_target(self):
        while True:
            x = random.randint(0, self.cols - 1)
            y = random.randint(0, self.rows - 1)
            if self._is_valid(x, y):
                return (x, y)

    def _can_see_player(self, player_x, player_y):
        dist = abs(self.x - player_x) + abs(self.y - player_y)
        if dist > self.vision_range:
            return False

        x, y = self.x, self.y
        dx = abs(player_x - x)
        dy = -abs(player_y - y)
        sx = 1 if x < player_x else -1
        sy = 1 if y < player_y else -1
        err = dx + dy

        while True:
            if (x, y) != (self.x, self.y) and not self._is_valid(x, y):
                return False
            
            if (x, y) == (player_x, player_y):
                return True
            
            e2 = 2 * err
            if e2 >= dy:
                if x == player_x: break
                err += dy
                x += sx
            if e2 <= dx:
                if y == player_y: break
                err += dx
                y += sy
        return False

    def _heuristic(self, guardian_pos, player_pos):
        return abs(guardian_pos[0] - player_pos[0]) + abs(guardian_pos[1] - player_pos[1])

    def _minimax(self, guardian_pos, player_pos, depth, is_guardian_turn):
        if depth == 0 or guardian_pos == player_pos:
            if guardian_pos == player_pos:
                return -math.inf
            else:
                return self._heuristic(guardian_pos, player_pos)

        if is_guardian_turn:
            min_eval = math.inf
            for move in self._neighbors(guardian_pos[0], guardian_pos[1]):
                evaluation = self._minimax(move, player_pos, depth - 1, False)
                min_eval = min(min_eval, evaluation)
            return min_eval
        else:
            max_eval = -math.inf
            for move in self._neighbors(player_pos[0], player_pos[1]):
                evaluation = self._minimax(guardian_pos, move, depth - 1, True)
                max_eval = max(max_eval, evaluation)
            return max_eval

    def _find_best_move_minimax(self, player_pos):
        best_move = (self.x, self.y)
        best_eval = math.inf
        
        possible_moves = self._neighbors(self.x, self.y)
        if not possible_moves:
            return best_move

        for move in possible_moves:
            evaluation = self._minimax(move, player_pos, self.minimax_depth - 1, False)
            if evaluation < best_eval:
                best_eval = evaluation
                best_move = move
        return best_move

    def move_towards_player(self, player_x, player_y):
        can_see = self._can_see_player(player_x, player_y)
        
        if can_see:
            if self.state == 'SCOUTING':
                self.current_path = []
            self.state = 'CHASING'
        else:
            if self.state == 'CHASING':
                self.state = 'SCOUTING'
                self.current_path = []
                
        if self.state == 'CHASING':
            next_move = self._find_best_move_minimax((player_x, player_y))
            self.x, self.y = next_move
        elif self.state == 'SCOUTING':
            if not self.current_path:
                target = self._get_random_target()
                self.current_path = self._find_path_bfs((self.x, self.y), target)
            
            if self.current_path:
                next_step = self.current_path.pop(0)
                self.x, self.y = next_step