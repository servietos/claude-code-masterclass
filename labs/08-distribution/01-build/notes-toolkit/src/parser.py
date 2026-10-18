"""Tiny line parser used as scan material for the notes toolkit."""


def parse(line):
    # TODO: support quoted fields with embedded separators
    parts = line.split(",")
    # FIXME: crashes on an empty line, returns a single empty field instead of []
    return [p.strip() for p in parts]


def parse_all(lines):
    # NOTE: a streaming version would avoid holding the whole file in memory
    return [parse(line) for line in lines]
