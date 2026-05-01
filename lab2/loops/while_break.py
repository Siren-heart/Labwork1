# break stops the loop immediately.

i = 1
while i < 6:
    print(i)
    if i == 3:
        break
    i += 1

number = 10
while number > 0:
    if number == 7:
        print("Stopping at 7")
        break
    print(number)
    number -= 1
