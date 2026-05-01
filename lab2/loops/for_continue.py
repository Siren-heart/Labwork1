# continue skips one iteration in a for loop.

fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    if fruit == "banana":
        continue
    print(fruit)

for number in range(1, 8):
    if number % 2 == 0:
        continue
    print("Odd number:", number)
