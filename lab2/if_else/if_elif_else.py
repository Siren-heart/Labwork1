# if/elif/else checks multiple conditions in order.

a = 33
b = 33

if b > a:
    print("b is greater than a")
elif a == b:
    print("a and b are equal")
else:
    print("a is greater than b")

score = 84

if score >= 90:
    print("Grade: A")
elif score >= 75:
    print("Grade: B")
elif score >= 50:
    print("Grade: C")
else:
    print("Grade: F")
