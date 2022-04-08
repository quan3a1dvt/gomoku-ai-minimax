from collections import defaultdict as ddict

score = {
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

switcher = (
    {1: score['ONE'], 2: score['TWO'], 3: score['THREE'], 4: score['FOUR']},
    {1: score['BLOCKED_ONE'], 2: score['BLOCKED_TWO'], 3: score['BLOCKED_THREE'], 4: score['BLOCKED_FOUR']},
    {2: score['TWO'] / 2, 3: score['THREE'], 4: score['BLOCKED_FOUR'], 5: score['FOUR']},
    {2: score['BLOCKED_TWO'], 3: score['BLOCKED_THREE'], 4: score['BLOCKED_FOUR'], 5: score['BLOCKED_FOUR']},
    {3: score['THREE'], 4: 0, 5: score['BLOCKED_FOUR'], 6: score['FOUR']},
    {3: score['BLOCKED_THREE'], 4: score['BLOCKED_FOUR'], 5: score['BLOCKED_FOUR'], 6: score['FOUR']},
    {4: 0, 5: 0, 6: score['BLOCKED_FOUR']},
    {4: 0, 5: score['THREE'], 6: score['BLOCKED_FOUR'], 7: score['FOUR']},
    {4: 0, 5: 0, 6: score['BLOCKED_FOUR'], 7: score['FOUR']},
    {4: 0, 5: 0, 6: 0, 7: score['BLOCKED_FOUR']},
    {5: 0, 6: 0, 7: 0, 8: score['FOUR']},
    {4: 0, 5: 0, 6: 0, 7: score['BLOCKED_FOUR'], 8: score['FOUR']},
    {5: 0, 6: 0, 7: 0, 8: score['BLOCKED_FOUR']}
)

class Board:

    def __init__(self, board=None, size=20):
        if not board:
            self._board = [[0 for i in range(size)] for j in range(size)]
            self.size = (size, size)
            self.step_count = 0
        else:
            self._board = board
            self.size = (len(board[0]), len(board))
            self.step_count = 0
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    if self[i, j] != 0:
                        self.step_count += 1
        self.xrange = range(self.size[0])
        self.yrange = range(self.size[1])
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

    def evaluate(self, role=1):
        max_score_1 = 0
        max_score_2 = 0
        for i in self.xrange:
            for j in self.yrange:
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
        for i in self.xrange:
            for j in self.yrange:
                if self[i, j] == 1 or self[i, j] == 0:
                    self.score_1[(i, j)] = self._get_point_score(i, j, 1)
                if self[i, j] == 2 or self[i, j] == 0:
                    self.score_2[(i, j)] = self._get_point_score(i, j, 2)

    def _update_score(self, x, y, radius=6):

        size = self.size[0]
        directions = [['h',[1,0]],['v',[0,1]],['r',[1,1]],['l',[1,-1]]]
        # h v r l
        for direct in directions:
            for i in range(-radius, radius):
                xi = x + i * direct[1][0]
                yi = y + i * direct[1][1]
                if xi < 0 or yi < 0:
                    continue
                if xi >= size or yi >= size:
                    break
                self._update_score_sub(xi, yi, direct[0])
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
        for x in self.xrange:
            for y in self.yrange:
                if self._has_neighbor(x, y) and self[x, y] == 0:
                    score_1 = self.score_1[(x, y)]
                    score_2 = self.score_2[(x, y)]
                    if self._is_five(x, y, 1):
                        return [(x, y)]
                    elif self._is_five(x, y, 2):
                        fives.append((x, y))
                    elif score_1 >= score['FOUR']:
                        fours.insert(0, (x, y))
                    elif score_2 >= score['FOUR']:
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

    def __getitem__(self, indices):
        y, x = indices
        if not isinstance(x, slice):  # Scalar
            return self._board[x][y]
        else:
            return [row[y] for row in self._board[x]]

    def __setitem__(self, indices, value):
        y, x = indices
        self._board[x][y] = value
        if value == 0:
            self.step_count -= 1
        else:
            self.step_count += 1
        self._update_score(y, x)

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

    def _get_point_score(self, x, y, role, direction=None):
        result = 0
        count = 0
        block = 0
        empty = 0
        second_count = 0
        size = self.size[0]
        
        directions = [['h',[1,0]],['v',[0,1]], ['r',[1,1]], ['l',[1,-1]]]
        for direct in directions:           
            if direction == None or direction == direct[0]:        
                count = 1
                block = 0
                empty = -1
                i = 0
                while True:
                    i += 1
                    xi = x + direct[1][0] * i
                    yi = y + direct[1][1] * i
                    if xi < 0 or xi >= size or yi < 0 or yi >= size:
                        block += 1
                        break
                    t = self[xi, yi]
                    if t == 0:
                        xii = xi + direct[1][0]
                        yii = yi + direct[1][1]
                        if empty == -1 and xii >= 0 and xii < size and yii >= 0 and yii < size and self[xii, yii] == role:
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
                    xi = x - direct[1][0] * i
                    yi = y - direct[1][1] * i
                    if xi < 0 or xi >= size or yi < 0 or yi >= size:
                        block += 1
                        break
                    t = self[xi, yi]
                    if t == 0:
                        xii = xi - direct[1][0]
                        yii = yi - direct[1][1]
                        if empty == -1 and xii >= 0 and xii < size and yii >= 0 and yii < size and self[xii, yii] == role:
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
                v = self._count_to_score(count, block, empty, x, y, role)
                self.score_cache[role][direct[0]][(x, y)] = v
                result += v
        return result

    def _count_to_score(self, count, block, empty, x, y, role):
        if not empty:
            empty = 0
        if empty <= 0:
            if count >= 5:
                return score['FIVE']
            if block == 0 and count in switcher[0]:
                return switcher[0][count]
            if block == 1 and count in switcher[1]:
                return switcher[1][count]
        elif empty == 1 or empty == count - 1:
            if count >= 6:
                return score['FIVE']
            if block == 0 and count in switcher[2]:
                return switcher[2][count]
            if block == 1 and count in switcher[3]:
                return switcher[3][count]
        elif empty == 2 or empty == count - 2:
            if count >= 7:
                return score['FIVE']
            if block == 0 and count in switcher[4]:
                return switcher[4][count]
            if block == 1 and count in switcher[5]:
                return switcher[5][count]
            if block == 2 and count in switcher[6]:
                return switcher[6][count]
        elif empty == 3 or empty == count - 3:
            if count >= 8:
                return score['FIVE']
            if block == 0 and count in switcher[7]:
                return switcher[7][count]
            if block == 1 and count in switcher[8]:
                return switcher[8][count]
            if block == 2 and count in switcher[9]:
                return switcher[9][count]
        elif empty == 4 or empty == count - 4:
            if count >= 9:
                return score['FIVE']
            if block == 0 and count in switcher[10]:
                return switcher[10][count]
            if block == 1 and count in switcher[11]:
                return switcher[11][count]
            if block == 2 and count in switcher[12]:
                return switcher[12][count]
        elif empty == 5 or empty == count - 5:
            return score['FIVE']

        return 0
    

    def _is_five(self, x, y, role):
        size = self.size[0]
        directs = [[1,0],[0,1],[1,1],[1,-1]]
        for direct in directs:
            l = [x - direct[0],y - direct[1]]
            r = [x + direct[0],y + direct[1]]
            count = 1
            while l[0] >= 0 and l[0] < size and l[1] >= 0 and l[1] < size and self[l[0], l[1]] == role:
                l[0] -= direct[0]
                l[1] -= direct[1]
                count += 1
            while r[0] >= 0 and r[0] < size and r[1] >= 0 and r[1] < size and self[r[0], r[1]] == role:
                r[0] += direct[0]
                r[1] += direct[1]
                count += 1
            if count >= 5:
                return role
        return False
    def get_winner(self):
        for i in self.xrange:
            for j in self.yrange:
                r = self[i, j]
                if r != 0:
                    role = self._is_five(i, j, r)
                    if role:
                        return role
        return False
    
    def _fix_evaluation(self, s, x, y, role):
        if s < score['FOUR'] and s >= score['BLOCKED_FOUR']:
            if s < score['BLOCKED_FOUR'] + score['THREE']:
                return score['THREE']
            elif s >= score['BLOCKED_FOUR'] + score['THREE'] and s < score['BLOCKED_FOUR'] * 2:
                return score['FOUR']
            else:
                return score['FOUR'] * 2
        if s >= score['FIVE'] and not self._is_five(x, y, role):
            return score['BLOCKED_FOUR'] * 4
        return s