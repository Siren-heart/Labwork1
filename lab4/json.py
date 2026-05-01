# Practice 4: JSON parsing and creation

import json
from pathlib import Path

base_path = Path(__file__).resolve().parent
sample_file = base_path / "sample-data.json"
output_file = base_path / "student-summary.json"

# JSON syntax example as a Python string.
person_json = '{"name": "Ali", "age": 21, "city": "Shymkent"}'

# Convert JSON text into a Python dictionary.
person = json.loads(person_json)
print("Parsed person:", person)
print("Person name:", person["name"])

# Convert Python data into a JSON string.
car = {
    "brand": "Toyota",
    "model": "Camry",
    "year": 2022,
    "electric": False
}

car_json = json.dumps(car, indent=2)
print("Car as JSON:")
print(car_json)

# Read JSON data from a file.
with sample_file.open("r", encoding="utf-8") as file:
    data = json.load(file)

print("Group:", data["group"])
print("Active:", data["active"])

for student in data["students"]:
    print(student["name"], "takes", ", ".join(student["courses"]))

# Build new JSON data and write it to a file.
summary = {
    "student_count": len(data["students"]),
    "names": [student["name"] for student in data["students"]],
    "python_students": [
        student["name"]
        for student in data["students"]
        if "Python" in student["courses"]
    ]
}

with output_file.open("w", encoding="utf-8") as file:
    json.dump(summary, file, indent=2)

print("Summary written to:", output_file.name)
