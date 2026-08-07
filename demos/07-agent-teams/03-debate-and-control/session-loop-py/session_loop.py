import sys

import commands
import config
from session import Session
from transcript import Transcript


def reply(text):
    return f"echo: {text}"


def main():
    settings = config.load()
    session = Session(settings["max_turns"])
    transcript = Transcript(settings["transcript"])

    print("session started, /quit to end")
    while session.is_open():
        try:
            text = input(settings["prompt"]).strip()
        except EOFError:
            break
        if not text:
            continue

        answer = commands.handle(text, session)
        if answer is None:
            session.append("user", text)
            transcript.write("user", text)
            answer = reply(text)
            session.append("assistant", answer)
            transcript.write("assistant", answer)
        print(answer)

    transcript.close()
    print(f"session ended after {len(session.turns)} turns")
    return 0


if __name__ == "__main__":
    sys.exit(main())
