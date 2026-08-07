from pathlib import Path


class Transcript:
    def __init__(self, path):
        self.path = Path(__file__).with_name(path)
        self.handle = self.path.open("a", encoding="utf-8")

    def write(self, role, text):
        self.handle.write(f"{role}: {text}\n")
        self.handle.flush()

    def close(self):
        self.handle.close()
