import random

class UniquePriorityPicker:
    def __init__(self, init_integer):
        self.init_integer = init_integer
        self.multiplier = 1
        self.calculate_multiplier()
        self.integer_list = self.create_integer_list()
    def create_integer_list(self):
        # Creates a list from 0 to init_integer
        return list(range(self.init_integer + 1))

    def calculate_multiplier(self):
        # Multiplies self.multiplier by 10 until it's larger than init_integer
        while self.multiplier <= self.init_integer:
            self.multiplier *= 10

    def get_random_integer_and_multiplier(self):
        # Returns a tuple of a random integer from the list (and removes it) and the multiplier
        if not self.integer_list:  # Checks if the list is empty
            return None, self.multiplier  # Returns None if the list is empty

        random_integer = random.choice(self.integer_list)
        self.integer_list.remove(random_integer)
        return random_integer, self.multiplier