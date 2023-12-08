import random

filename = "numerical_input.txt"
quantity = 150000  # Total number of random numbers to generate

with open(filename, 'w') as f:
    for _ in range(quantity):
        # Generate a random float between 0 and 1000
        f.write(f"{random.uniform(0, 1000):.2f}\n")  # Writes number with 4 decimal places

print(f"File {filename} generated with {quantity} numbers.")
