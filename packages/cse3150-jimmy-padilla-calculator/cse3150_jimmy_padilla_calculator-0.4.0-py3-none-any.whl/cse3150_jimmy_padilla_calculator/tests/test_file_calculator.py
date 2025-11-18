from cse3150_jimmy_padilla_calculator.file_calculator import FileCalculator
# from ..file_calculator import FileCalculator


def test_file_calculator():
    assert FileCalculator().sum_file() == 6


if __name__ == '__main__':
    FileCalculator().sum_file()
