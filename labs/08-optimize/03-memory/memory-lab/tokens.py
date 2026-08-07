import sys
from pathlib import Path

import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")
path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
print(f"{path.as_posix()}: {len(encoding.encode(text))}")
