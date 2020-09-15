class MockChooser:
    def __init__(self):
        self.choice = 0
        self.last_choices = None
        self.last_count = None

    def choose(self, choices, count=1):
        self.last_choices = choices
        self.last_count = count
        return [choices[self.choice]] * count
