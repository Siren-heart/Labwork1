# break can also stop a for loop early.

fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(fruit)
    if fruit == "banana":
        break

for number in range(1, 10):
    if number == 5:
        print("Stopping at", number)
        break
    print(number)
