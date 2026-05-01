# Practice 6: copying, backing up, and deleting files

import shutil
from pathlib import Path


base_path = Path(__file__).resolve().parent
source_file = base_path / "data.txt"
backup_file = base_path / "data_backup.txt"
temp_file = base_path / "temp_delete_me.txt"

source_file.write_text("Important practice data\n", encoding="utf-8")
temp_file.write_text("Temporary file\n", encoding="utf-8")

# Copy the source file to create a backup.
shutil.copy(source_file, backup_file)
print("Backup exists:", backup_file.exists())

# Delete a file safely only if it exists.
if temp_file.exists():
    temp_file.unlink()

print("Temporary file exists after delete:", temp_file.exists())
