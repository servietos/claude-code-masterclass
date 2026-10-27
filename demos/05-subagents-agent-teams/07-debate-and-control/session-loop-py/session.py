class Session:
    def __init__(self, max_turns):
        self.max_turns = max_turns
        self.turns = []
        self.closed = False

    def is_open(self):
        return not self.closed and len(self.turns) < self.max_turns

    def append(self, role, text):
        self.turns.append({"role": role, "text": text})
        return len(self.turns)

    def close(self):
        self.closed = True
