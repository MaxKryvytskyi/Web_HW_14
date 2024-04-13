import unittest



def sum_two_var(a, b):
    if a + b == 16:
        return None
    return a + b


class TestSumTwoVar(unittest.TestCase):

    def test_sum_two_numbers0(self):
        result = sum_two_var(1, 4)
        self.assertEqual(result, 5) # - перевіряє, що значення a і b повинні бути рівними

    def test_sum_two_numbers1(self):
        result = sum_two_var(1, -4)
        self.assertNotEqual(result, -2) #  - перевіряє, що значення a і b не рівні.

    def test_sum_two_numbers2(self):
        result = sum_two_var(1, 1)
        self.assertTrue(result) # - перевіряє, що x правдиве (тобто не дорівнює False, 0, '', None).

    def test_sum_two_numbers3(self):
        result = sum_two_var(1, 1)
        self.assertIs(result, 2) # - перевіряє, що a і b посилаються на один і той самий об'єкт.

    def test_sum_two_numbers4(self):
        result = sum_two_var(1, 1)
        self.assertIsNot(result, 3) # - перевіряє, що a і b не посилаються на один і той самий об'єкт.
    
    def test_sum_two_numbers5(self):
        result = sum_two_var(8, 8)
        self.assertIsNone(result) # - перевіряє, що x дорівнює None.

    def test_sum_two_numbers6(self):
        result = sum_two_var(8, 1)
        self.assertIsNotNone(result) #  - перевіряє, що x не дорівнює None.

    def test_sum_two_numbers7(self):
        with self.assertRaises(TypeError): #  - код всередині цього контексту повинен викликати виняток, переданий у першому аргументі.
            sum_two_var(8, "1")

if __name__ == "__main__":
    unittest.main()