# Practice 6: map, filter, reduce, and basic built-in functions

from functools import reduce


numbers = [1, 2, 3, 4, 5, 6]

# map() applies a function to every item.
squares = list(map(lambda number: number * number, numbers))
print("Squares:", squares)

# filter() keeps only items that match a condition.
even_numbers = list(filter(lambda number: number % 2 == 0, numbers))
print("Even numbers:", even_numbers)

# reduce() combines the whole list into one value.
total = reduce(lambda left, right: left + right, numbers)
print("Reduced total:", total)

print("Length:", len(numbers))
print("Sum:", sum(numbers))
print("Minimum:", min(numbers))
print("Maximum:", max(numbers))

# Type conversions.
print(int("25"))
print(float("3.14"))
print(str(100))
