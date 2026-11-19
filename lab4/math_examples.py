# Practice 4: math and random

import math
import random

# Built-in math-related functions.
print("Minimum:", min(4, 9, 2, 7))
print("Maximum:", max(4, 9, 2, 7))
print("Absolute value:", abs(-15.7))
print("Rounded value:", round(4.6))
print("Power:", pow(2, 5))

# math module functions.
print("Square root:", math.sqrt(64))
print("Ceil:", math.ceil(2.3))
print("Floor:", math.floor(2.9))
print("Sin(90 degrees):", round(math.sin(math.radians(90)), 2))
print("Cos(0 degrees):", round(math.cos(math.radians(0)), 2))
print("Pi:", math.pi)
print("Euler's number:", math.e)

# random module examples.
print("Random float:", random.random())
print("Random integer:", random.randint(1, 10))

colors = ["red", "green", "blue", "yellow"]
print("Random choice:", random.choice(colors))

random.shuffle(colors)
print("Shuffled colors:", colors)
