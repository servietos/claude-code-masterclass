import os

import config


def list_notes():
    return sorted(os.listdir(config.NOTES_DIR))


def read_note(name):
    path = os.path.join(config.NOTES_DIR, name)
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write_note(name, body):
    path = os.path.join(config.NOTES_DIR, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    return len(body)


def search(term):
    hits = []
    for name in list_notes():
        text = read_note(name)
        for line in text.splitlines():
            for word in line.split():
                if word.lower() == term.lower():
                    hits.append({"note": name, "line": line})
    return hits
