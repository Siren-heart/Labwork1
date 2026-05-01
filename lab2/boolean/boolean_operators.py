# Boolean operators combine conditions.

x = 5

# "and" is True only when both conditions are True.
print(x > 3 and x < 10)

# "or" is True when at least one condition is True.
print(x > 3 or x > 10)

# "not" reverses the result.
print(not (x > 3 and x < 10))

age = 20
has_id = True

if age >= 18 and has_id:
    print("You may enter.")
else:
    print("Entry denied.")
