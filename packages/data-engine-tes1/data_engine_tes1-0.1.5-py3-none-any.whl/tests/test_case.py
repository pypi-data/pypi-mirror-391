# test_module.py
class MyProcessor:
    def __init__(self, factor=2):
        self.factor = factor

    def process(self, x):
        return x * self.factor
