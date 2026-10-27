HELP = "commands: /help, /turns, /quit"


def handle(text, session):
    if not text.startswith("/"):
        return None
    if text == "/quit":
        session.close()
        return "closing session"
    if text == "/turns":
        return f"{len(session.turns)} turns so far"
    if text == "/help":
        return HELP
    return f"unknown command: {text}"
