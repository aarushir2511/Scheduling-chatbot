class MemoryStore:
    def __init__(self):
        self.slots = {}

    def remember(self, key, value):
        self.slots[key] = value

    def recall(self, key):
        return self.slots.get(key, None)

    def has(self, key):
        return key in self.slots