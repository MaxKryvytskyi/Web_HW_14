import unittest

def multiply_numbers(x, y):

    result = x * y
    return result

class TestMultiplication(unittest.TestCase):
    def test_multiply_two_positive_numbers(self):
        result = multiply_numbers(2, 3)
        self.assertEqual(result, 6)
    
    def test_multiply_positive_and_negative_numbers(self):
        result = multiply_numbers(2, -3)
        self.assertEqual(result, -6)
    
    def test_multiply_two_negative_numbers(self):
        result = multiply_numbers(-2, -3)
        self.assertEqual(result, 6)

    def test_multiply_two_null_numbers(self):
        result = multiply_numbers(0, 0)
        self.assertEqual(result, 0)

    def test_multiply_string_and_number(self):
        result = multiply_numbers("14", 0)
        self.assertRaises(TypeError, result)
    
    def test_multiply_string_and_number1(self):
        result = multiply_numbers("14", 0)
        self.assertEqual(result, '')

if __name__ == '__main__':
    unittest.main()

