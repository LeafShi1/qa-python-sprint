
import os

def count_lines(root=".", exts=(".py",)):
    total = 0
    details = []
    for folder, _, files in os.walk(root):
        if folder.startswith("./.venv") or ".venv" in folder:
            continue
        for f in files:
            if f.endswith(exts):
                path = os.path.join(folder, f)
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    lines = [line for line in fp if line.strip() != ""]
                total += len(lines)
                details.append((path, len(lines)))
    details.sort(key=lambda x: x[0])
    print("Line counts per file:")
    for p, n in details:
        print(f"{p}: {n}")
    print(f"\nTOTAL (non-empty lines): {total}")

if __name__ == "__main__":
    count_lines(".")
