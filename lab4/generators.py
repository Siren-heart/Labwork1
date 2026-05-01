# Practice 4: iterators and generators

# An iterator returns values one by one.
numbers = iter([10, 20, 30, 40])
print(next(numbers))
print(next(numbers))

# A loop can continue consuming the rest of an iterator.
for value in numbers:
    print("Remaining value:", value)


# This class creates a custom iterator.
class CountUp:
    def __init__(self, limit):
        self.limit = limit
        self.current = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= self.limit:
            value = self.current
            self.current += 1
            return value
        raise StopIteration


counter = CountUp(5)
for number in counter:
    print("CountUp:", number)


# A generator function uses yield instead of return.
def even_numbers(limit):
    for number in range(limit + 1):
        if number % 2 == 0:
            yield number


for even in even_numbers(10):
    print("Even:", even)


# A generator expression creates values lazily.
squares = (number * number for number in range(1, 6))
for square in squares:
    print("Square:", square)
