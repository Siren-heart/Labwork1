# Practice 6: writing and appending files

from pathlib import Path


base_path = Path(__file__).resolve().parent
output_file = base_path / "notes.txt"

# Write new content with write mode.
with output_file.open("w", encoding="utf-8") as file:
    file.write("Python file handling examples\n")
    file.write("This file was created with write mode.\n")

# Append extra content without removing the old text.
with output_file.open("a", encoding="utf-8") as file:
    file.write("This line was added with append mode.\n")
    file.write("The with statement closes the file automatically.\n")

print(output_file.read_text(encoding="utf-8"))
