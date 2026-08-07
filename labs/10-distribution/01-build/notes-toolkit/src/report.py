"""Report writer used as scan material for the notes toolkit."""

from .store import Store


def render(store: Store) -> str:
    # TODO: escape pipe characters so markdown tables do not break
    lines = ["| Key | Value |", "|---|---|"]
    for key in store.keys():
        lines.append(f"| {key} | {store.get(key)} |")
    # NOTE: the report is intentionally markdown so it renders in the notes report
    return "\n".join(lines)
