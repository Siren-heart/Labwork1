# Practice 6: creating and listing directories

from pathlib import Path


base_path = Path(__file__).resolve().parent
workspace = base_path / "practice_space"
nested_dir = workspace / "level1" / "level2"

# Create nested directories.
nested_dir.mkdir(parents=True, exist_ok=True)

# Create a few files for listing examples.
(workspace / "notes.txt").write_text("Notes file\n", encoding="utf-8")
(workspace / "report.csv").write_text("name,score\nAli,95\n", encoding="utf-8")
(workspace / "level1" / "image.png").write_text("fake image data\n", encoding="utf-8")

print("Current working directory parent:")
print(base_path)

print("Items in practice_space:")
for item in workspace.iterdir():
    print(item.name)

print("Files with .txt extension:")
for txt_file in workspace.rglob("*.txt"):
    print(txt_file.name)
