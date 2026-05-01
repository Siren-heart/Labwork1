# Practice 6: moving and copying files between directories

import shutil
from pathlib import Path


base_path = Path(__file__).resolve().parent
source_dir = base_path / "source_files"
target_dir = base_path / "target_files"

source_dir.mkdir(exist_ok=True)
target_dir.mkdir(exist_ok=True)

source_file = source_dir / "example.txt"
source_file.write_text("Move and copy example\n", encoding="utf-8")

# Copy the file first.
copied_file = target_dir / "example_copy.txt"
shutil.copy(source_file, copied_file)

# Move the original file into the target directory.
moved_file = target_dir / "example_moved.txt"
shutil.move(str(source_file), str(moved_file))

print("Copied file exists:", copied_file.exists())
print("Moved file exists:", moved_file.exists())
print("Original source file exists:", source_file.exists())
