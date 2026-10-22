"""Check Markdown structure with Python standard library only."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote

root = Path(__file__).resolve().parents[1]
errors = []
required = ["README.md", "LICENSE", "CONTRIBUTING.md", "THIRD_PARTY_NOTICES.md",
            "docs/guide.ru.md", "docs/RELEASE_CHECK.md"]
for name in required:
    if not (root / name).is_file():
        errors.append(f"Missing: {name}")
files = sorted(root.rglob("*.md"))
links = 0
for file in files:
    text = file.read_text(encoding="utf-8")
    if len(re.findall(r"^```", text, re.M)) % 2:
        errors.append(f"Unbalanced code fences: {file.relative_to(root)}")
    if "[[" in text or "\ufffd" in text:
        errors.append(f"Wiki link or replacement character: {file.relative_to(root)}")
    visible = re.sub(r"```.*?```", "", text, flags=re.S)
    for target in re.findall(r"\]\(([^)]+)\)", visible):
        if target.startswith(("https://", "http://")):
            continue
        links += 1
        path, _, anchor = unquote(target).partition("#")
        dest = (file.parent / path).resolve() if path else file
        if not dest.is_relative_to(root) or not dest.is_file():
            errors.append(f"Invalid local link: {file.name}: {target}")
        elif anchor and f'id="{anchor}"' not in dest.read_text(encoding="utf-8"):
            errors.append(f"Missing explicit anchor: {file.name}: {target}")
guide = (root / "docs/guide.ru.md").read_text(encoding="utf-8")
if len(re.findall(r"^## \d+\.", guide, re.M)) != 19:
    errors.append("Expected 19 guide sections")
if len(re.findall(r"^### 16\.\d+\.", guide, re.M)) != 10:
    errors.append("Expected 10 prompts")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"PASS: {len(files)} Markdown files, {links} local links, 19 sections, 10 prompts")
