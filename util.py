from collections import defaultdict as ddict




scores = {
    'ONE': 10,
    'TWO': 100,
    'THREE': 1000,
    'FOUR': 100000,
    'FIVE': 10000000,
    'BLOCKED_ONE': 1,
    'BLOCKED_TWO': 10,
    'BLOCKED_THREE': 100,
    'BLOCKED_FOUR': 10000
}







situations = (
    {1: scores['ONE'], 2: scores['TWO'], 3: scores['THREE'], 4: scores['FOUR']},
    {1: scores['BLOCKED_ONE'], 2: scores['BLOCKED_TWO'], 3: scores['BLOCKED_THREE'], 4: scores['BLOCKED_FOUR']},
    {2: scores['TWO'] / 2, 3: scores['THREE'], 4: scores['BLOCKED_FOUR'], 5: scores['FOUR']},
    {2: scores['BLOCKED_TWO'], 3: scores['BLOCKED_THREE'], 4: scores['BLOCKED_FOUR'], 5: scores['BLOCKED_FOUR']},
    {3: scores['THREE'], 4: 0, 5: scores['BLOCKED_FOUR'], 6: scores['FOUR']},
    {3: scores['BLOCKED_THREE'], 4: scores['BLOCKED_FOUR'], 5: scores['BLOCKED_FOUR'], 6: scores['FOUR']},
    {4: 0, 5: 0, 6: scores['BLOCKED_FOUR']},
    {4: 0, 5: scores['THREE'], 6: scores['BLOCKED_FOUR'], 7: scores['FOUR']},
    {4: 0, 5: 0, 6: scores['BLOCKED_FOUR'], 7: scores['FOUR']},
    {4: 0, 5: 0, 6: 0, 7: scores['BLOCKED_FOUR']},
    {5: 0, 6: 0, 7: 0, 8: scores['FOUR']},
    {4: 0, 5: 0, 6: 0, 7: scores['BLOCKED_FOUR'], 8: scores['FOUR']},
    {5: 0, 6: 0, 7: 0, 8: scores['BLOCKED_FOUR']}
)

class Board:

    def __init__(self, board=None, sizex=20, sizey=20):
        if board == None:
            self._board = [[0 for i in range(sizex)] for j in range(sizey)]
            self.size = (sizex, sizey)
            self.step_count = 0
        else:
            self._board = board
            self.size = (len(board[0]), len(board))
            self.step_count = 0
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    if self[i, j] != 0:
                        self.step_count += 1
        self.score_1 = ddict(lambda: 0.0)
        self.score_2 = ddict(lambda: 0.0)
        self.score_cache = {
            1: {
                'h': ddict(lambda: 0.0),
                'v': ddict(lambda: 0.0),
                'r': ddict(lambda: 0.0),
                'l': ddict(lambda: 0.0)
            },
            2: {
                'h': ddict(lambda: 0.0),
                'v': ddict(lambda: 0.0),
                'r': ddict(lambda: 0.0),
                'l': ddict(lambda: 0.0)
            }
        }
        self._init_score()

    def __getitem__(self, indices):
        y, x = indices
        return self._board[x][y]

    def __setitem__(self, indices, role):      
        x, y = indices
        self._board[y][x] = role
        if role == 0:
            self.step_count -= 1
        else:
            self.step_count += 1
        self._update_score(x, y)

    def __eq__(self, obj):
        if type(self) == type(obj):
            return self._board == obj._board
        else:
            return self._board == obj

    def __repr__(self):
        if isinstance(self._board[0], list):
            l = [str(row) for row in self._board]
            return '\n'.join(l)
        else:
            return str(self._board)
    def flip(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self[i, j] == 1:
                    self[i, j] = 2
                elif self[i, j] == 2:
                    self[i, j] = 1
        score_t = self.score_1
        self.score_1 = self.score_2
        self.score_2 = score_t
        score_cache_t = self.score_cache[1]
        self.score_cache[1] = self.score_cache[2]
        self.score_cache[2] = score_cache_t
        
    def evaluate(self, role=1):
        max_score_1 = 0
        max_score_2 = 0
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self[i, j] == 1:
                    max_score_1 += self._fix_evaluation(self.score_1[(i, j)], i, j, 1)
                    # max_score_1 = max(self.score_1[(i, j)], max_score_1)
                elif self[i, j] == 2:
                    max_score_2 += self._fix_evaluation(self.score_2[(i, j)], i, j, 2)
                    # max_score_2 = max(self.score_2[(i, j)], max_score_2)
        
        # max_score_1 = self._fix_evaluation(max_score_1)
        # max_score_2 = self._fix_evaluation(max_score_2)
        result = (1 if role == 1 else -1) * (max_score_1 - max_score_2)
        return result

    def _init_score(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self[i, j] == 1 or self[i, j] == 0:
                    self.score_1[(i, j)] = self._get_point_score(i, j, 1)
                if self[i, j] == 2 or self[i, j] == 0:
                    self.score_2[(i, j)] = self._get_point_score(i, j, 2)

    def _update_score(self, x, y, radius=6):
        size = self.size[0]
        directions = [['h',[1,0]],['v',[0,1]],['r',[1,1]],['l',[1,-1]]]
        # h v r l
        for data in directions:
            for i in range(-radius, radius):
                xi = x + i * data[1][0]
                yi = y + i * data[1][1]
                if xi < 0 or yi < 0 or xi >= size or yi >= size:
                    continue
                self._update_score_sub(xi, yi, data[0])
        self._update_score_sub(x, y, None)

    def _update_score_sub(self, x, y, direction):
        role = self[x, y]
        if role == 0 or role == 1:
            if direction:
                self.score_1[(x, y)] -= self.score_cache[1][direction][(x, y)]
                self.score_1[(x, y)] += self._get_point_score(x, y, 1, direction)
            else:
                self.score_1[(x, y)] = self._get_point_score(x, y, 1)
        else:
            self.score_1[(x, y)] = 0

        if role == 0 or role == 2:
            if direction:
                self.score_2[(x, y)] -= self.score_cache[2][direction][(x, y)]
                self.score_2[(x, y)] += self._get_point_score(x, y, 2, direction)
            else:
                self.score_2[(x, y)] = self._get_point_score(x, y, 2)
        else:
            self.score_2[(x, y)] = 0

    def candidate(self):
        fives = list()
        fours = list()
        point_scores = list()
        if self.step_count == 0:
            return [(int(self.size[0] / 2), int(self.size[1] / 2))]
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                if self._has_neighbor(x, y) and self[x, y] == 0:
                    score_1 = self.score_1[(x, y)]
                    score_2 = self.score_2[(x, y)]
                    if self._is_five(x, y, 1):
                        return [(x, y)]
                    elif self._is_five(x, y, 2):
                        fives.append((x, y))
                    elif score_1 >= scores['FOUR']:
                        fours.insert(0, (x, y))
                    elif score_2 >= scores['FOUR']:
                        fours.append((x, y))
                    else:
                        point_scores.append((x, y))
        # If forced moves exist, return them
        if fives:
            return [fives[0]]
        if fours:
            return fours
        # If no forced move, sort all candidate with scores
        candidate = sorted(point_scores, key=lambda p: max(self.score_1[p], self.score_2[p]), reverse=True)
        return candidate

    def _has_neighbor(self, x, y, dist=1):
        for i in range(max(x - dist, 0), min(x + dist + 1, self.size[0])):
            for j in range(max(y - dist, 0), min(y + dist + 1, self.size[1])):
                if not (i == x and j == y) and self[i, j]:
                    return True
        return False

    def _get_point_score(self, x, y, role, direction=None):
        result = 0
        count = 0
        block = 0
        empty = 0
        
        directions = [['h',[1,0]],['v',[0,1]], ['r',[1,1]], ['l',[1,-1]]]
        for data in directions:           
            if direction == None or direction == data[0]:        
                count = 1
                block = 0
                empty = -1
                i = 0
                while True:
                    i += 1
                    xi = x + data[1][0] * i
                    yi = y + data[1][1] * i
                    if xi < 0 or xi >= self.size[0] or yi < 0 or yi >= self.size[1]:
                        block += 1
                        break
                    t = self[xi, yi]
                    if t == 0:
                        xii = xi + data[1][0]
                        yii = yi + data[1][1]
                        if empty == -1 and xii >= 0 and xii < self.size[0] and yii >= 0 and yii < self.size[1] and self[xii, yii] == role:
                            empty = count
                            continue
                        else:
                            break
                    if t == role:
                        count += 1
                        continue
                    else:
                        block += 1
                        break
                i = 0
                while True:
                    i += 1
                    xi = x - data[1][0] * i
                    yi = y - data[1][1] * i
                    if xi < 0 or xi >= self.size[0] or yi < 0 or yi >= self.size[1]:
                        block += 1
                        break
                    t = self[xi, yi]
                    if t == 0:
                        xii = xi - data[1][0]
                        yii = yi - data[1][1]
                        if empty == -1 and xii >= 0 and xii < self.size[0] and yii >= 0 and yii < self.size[1] and self[xii, yii] == role:
                            empty = 0
                            continue
                        else:
                            break
                    if t == role:
                        count += 1
                        if empty != -1 and empty:
                            empty += 1
                        continue
                    else:
                        block += 1
                        break
                v = self._count_to_score(count, block, empty)
                self.score_cache[role][data[0]][(x, y)] = v
                result += v
        return result

    def _count_to_score(self, count, block, empty):
        if not empty:
            empty = 0
        if empty <= 0:
            if count >= 5:
                return scores['FIVE']
            if block == 0 and count in situations[0]:
                return situations[0][count]
            if block == 1 and count in situations[1]:
                return situations[1][count]
        elif empty == 1 or empty == count - 1:
            if count >= 6:
                return scores['FIVE']
            if block == 0 and count in situations[2]:
                return situations[2][count]
            if block == 1 and count in situations[3]:
                return situations[3][count]
        elif empty == 2 or empty == count - 2:
            if count >= 7:
                return scores['FIVE']
            if block == 0 and count in situations[4]:
                return situations[4][count]
            if block == 1 and count in situations[5]:
                return situations[5][count]
            if block == 2 and count in situations[6]:
                return situations[6][count]
        elif empty == 3 or empty == count - 3:
            if count >= 8:
                return scores['FIVE']
            if block == 0 and count in situations[7]:
                return situations[7][count]
            if block == 1 and count in situations[8]:
                return situations[8][count]
            if block == 2 and count in situations[9]:
                return situations[9][count]
        elif empty == 4 or empty == count - 4:
            if count >= 9:
                return scores['FIVE']
            if block == 0 and count in situations[10]:
                return situations[10][count]
            if block == 1 and count in situations[11]:
                return situations[11][count]
            if block == 2 and count in situations[12]:
                return situations[12][count]
        elif empty == 5 or empty == count - 5:
            return scores['FIVE']

        return 0
    

    def _is_five(self, x, y, role):
        directions = [[1,0],[0,1],[1,1],[1,-1]]
        for data in directions:
            l = [x - data[0],y - data[1]]
            r = [x + data[0],y + data[1]]
            count = 1
            while l[0] >= 0 and l[0] < self.size[0] and l[1] >= 0 and l[1] < self.size[1] and self[l[0], l[1]] == role:
                l[0] -= data[0]
                l[1] -= data[1]
                count += 1
            while r[0] >= 0 and r[0] < self.size[0] and r[1] >= 0 and r[1] < self.size[1] and self[r[0], r[1]] == role:
                r[0] += data[0]
                r[1] += data[1]
                count += 1
            if count >= 5:
                return role
        return False
    def get_winner(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                t = self[i, j]
                if t != 0:
                    role = self._is_five(i, j, t)
                    if role:
                        return role
        return False
    
    def _fix_evaluation(self, score, x, y, role):
        if score < scores['FOUR'] and score >= scores['BLOCKED_FOUR']:
            if score < scores['BLOCKED_FOUR'] + scores['THREE']:
                return scores['THREE']
            elif score >= scores['BLOCKED_FOUR'] + scores['THREE'] and score < scores['BLOCKED_FOUR'] * 2:
                return scores['FOUR']
            else:
                return scores['FOUR'] * 2
        if score >= scores['FIVE'] and not self._is_five(x, y, role):
            return scores['BLOCKED_FOUR'] * 4
        return score