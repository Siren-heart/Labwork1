# Practice 6: enumerate and zip examples

names = ["Aruzhan", "Dias", "Malika"]
scores = [88, 91, 95]

# enumerate() gives index and value together.
for index, name in enumerate(names, start=1):
    print(index, name)

# zip() joins items from two lists.
for name, score in zip(names, scores):
    print(name, score)

# sorted() returns a new sorted list.
unsorted_numbers = [9, 2, 7, 1, 5]
print(sorted(unsorted_numbers))

# Combine enumerate and zip in one example.
for index, pair in enumerate(zip(names, scores), start=1):
    name, score = pair
    print(f"{index}. {name} scored {score}")
