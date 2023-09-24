import numpy as np


class BasicLSH:
    def __init__(self, dim, l, m, w, seed=1):
        self.dim = dim
        self.l = l
        self.m = m
        self.w = w

        np.random.seed(seed)
        self.a = np.random.randn(l, m, dim)
        self.b = np.random.rand(l, m)

        self.hash_tables = []
        for i in range(l):
            self.hash_tables.append({})

    def hash(self, point):
        hash_values = np.floor((np.dot(self.a, point) + self.b) / self.w)
        hash_values.astype(np.int16)
        return hash_values

    def insert(self, point, label):
        hash_values = self.hash(point)
        for i in range(hash_values.shape[0]):
            self.hash_tables[i][tuple(hash_values[i])] = label

    def query(self, point):
        results = set()

        hash_values = self.hash(point)
        for i in range(self.l):
            key = tuple(hash_values[i])
            target = self.hash_tables[i].get(key)
            if target:
                results.add(target)
        return results
