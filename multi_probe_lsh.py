import numpy as np
from basic_lsh import BasicLSH
import heapq


class MultiProbeLSH(BasicLSH):
    def __init__(self, dim, l, m, w, seed=1):
        super(MultiProbeLSH, self).__init__(dim, l, m, w, seed)

    def is_valid(self, perturb_set):
        for perturb in perturb_set:
            if (2 * self.m + 1 - perturb) in perturb_set:
                return False
            if perturb > 2 * self.m:
                return False
        return True

    def has_max(self, perturb_set):
        if perturb_set[-1] == self.m * 2 - 1:
            return True
        return False

    def shift(self, perturb_set):
        next = perturb_set.copy()
        next[-1] = perturb_set[-1] + 1
        return next

    def expand(self, perturb_set):
        next = perturb_set.copy()
        next.append(perturb_set[-1] + 1)
        return next

    def score(self, query, i, j, perturb):
        if perturb == -1:
            f = np.dot(self.a[j][i], query) + self.b[j][i]
            h = self.hash(query)[j][i]
            return f - h * self.w
        if perturb == 1:
            return self.w - self.score(query, i, j, -1)

    class PiPair:
        def __init__(self, i, delta):
            self.i = i
            self.delta = delta

    def pi_list(self, query, j):
        pi_list = []
        for i in range(self.m):
            pi_list.append((self.PiPair(i+1, 1), self.score(query, i, j, 1)))
            pi_list.append((self.PiPair(i+1, -1), self.score(query, i, j, -1)))
        self.quick_sort(pi_list, 0, len(pi_list) - 1)
        return pi_list

    def quick_sort(self, alist, start, end):
        if start >= end:
            return
        mid = alist[start]
        left = start
        right = end
        while left < right:
            while left < right and alist[right][1] >= mid[1]:
                right -= 1
            while left < right and alist[left][1] <= mid[1]:
                left += 1
            if left < right:
                tmp = alist[right]
                alist[right] = alist[left]
                alist[left] = tmp
        alist[start] = alist[left]
        alist[left] = mid
        self.quick_sort(alist, start, left - 1)
        self.quick_sort(alist, left + 1, end)

    def _class_perturb_set(self):
        outer = self

        class PerturbSet:
            def __init__(self, perturb_set, query, m, j):
                self.perturb_set = perturb_set
                pi_list = outer.pi_list(query, j)
                score = 0
                for perturb in perturb_set:
                    score += pi_list[perturb - 1][1]
                self.score = score

            def __lt__(self, other):
                return self.score < other.score

        return PerturbSet

    def probe_sequence(self, query, j):
        result = []
        perturb_set_begin = self._class_perturb_set()([1], query, self.m, j)
        heap = []
        heapq.heappush(heap, perturb_set_begin)
        while True:
            perturb_set = heapq.heappop(heap)
            if self.is_valid(perturb_set.perturb_set):
                result.append(perturb_set.perturb_set)
            else:
                break

            if not self.has_max(perturb_set.perturb_set):
                shift = self._class_perturb_set()(self.shift(perturb_set.perturb_set), query, self.m, j)
                expand = self._class_perturb_set()(self.expand(perturb_set.perturb_set), query, self.m, j)
                heapq.heappush(heap, shift)
                heapq.heappush(heap, expand)
        return result

    def query(self, point):
        results = set()
        hash_values = self.hash(point)
        for j in range(self.l):
            pi_list = self.pi_list(point, j)

            key = hash_values[j].copy()
            target = self.hash_tables[j].get(tuple(key))
            if target:
                results.add(target)

            probe_sequence = self.probe_sequence(point, j)
            for perturb_set in probe_sequence:
                tmp = key.copy()
                for perturb in perturb_set:
                    perturb_index, perturb_value = pi_list[perturb - 1][0].i, pi_list[perturb - 1][0].delta
                    tmp[perturb_index - 1] += perturb_value
                perturb_target = self.hash_tables[j].get(tuple(tmp))
                if perturb_target:
                    results.add(perturb_target)

        return results
