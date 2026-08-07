"""In-memory record store used as scan material for the notes toolkit."""


class Store:
    def __init__(self):
        self._rows = {}

    def put(self, key, value):
        # FIXME: silently overwrites an existing key, callers expect a conflict error
        self._rows[key] = value

    def get(self, key):
        # TODO: add a default argument so callers stop wrapping this in try/except
        return self._rows[key]

    def keys(self):
        # NOTE: insertion order is relied on by the report writer
        return list(self._rows)
