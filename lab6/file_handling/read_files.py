# Practice 6: reading files

from pathlib import Path


base_path = Path(__file__).resolve().parent
sample_file = base_path / "sample.txt"

# Create sample content so the read examples always have input.
sample_file.write_text("First line\nSecond line\nThird line\n", encoding="utf-8")

# Read the whole file.
full_text = sample_file.read_text(encoding="utf-8")
print("Full text:")
print(full_text)

# Read the file line by line.
with sample_file.open("r", encoding="utf-8") as file:
    print("First line with readline():")
    print(file.readline().strip())

with sample_file.open("r", encoding="utf-8") as file:
    print("All lines with readlines():")
    print([line.strip() for line in file.readlines()])
