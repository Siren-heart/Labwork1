# continue skips the current loop step and moves to the next one.

i = 0
while i < 6:
    i += 1
    if i == 3:
        continue
    print(i)

number = 0
while number < 5:
    number += 1
    if number % 2 == 0:
        continue
    print("Odd number:", number)
