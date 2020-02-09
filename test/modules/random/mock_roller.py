class MockRoller:
    def __init__(self):
        self.answer = 0
        self.last_min = None
        self.last_max = None
        self.last_count = None

    def roll(self, min_int, max_int, count=1):
        self.last_min = min_int
        self.last_max = max_int
        self.last_count = count
        if isinstance(self.answer, list):
            return self.answer
        return [self.answer] * count
