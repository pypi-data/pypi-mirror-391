class Calculator:
    def add(self, a, b):
        print("im in da add")
        return a + b
    def subtract(self, a, b):
        return a - b
    def multiply(self, a, b):
        return a * b
    def divide(self, a, b):
        return a / b

if __name__ == '__main__':
    calc = Calculator()
    print(calc.divide(4, 2.0))
