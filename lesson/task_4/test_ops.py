import unittest

from ops import add, sub, mul, div


class TestExamples(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print('1 Start before all test')

    @classmethod
    def tearDownClass(cls):
        print('-1 Start after all test')

    def setUp(self):
        print('2 Start before each test')

    def tearDown(self):
        print('-2 Start after each test')

    def test_add(self):
        print("11 Add function test")
        self.assertEqual(add(2, 3), 5)

    def test_sub(self):
        print("12 Sub function test")
        self.assertEqual(sub(2, 3), -1)

    def test_mul(self):
        print("13 Mul function test")
        self.assertEqual(mul(2, 3), 6)

    def test_div(self):
        print("14 Div function test")
        self.assertAlmostEqual(add(0.31, 0.3), 0.61, places=2)
        with self.assertRaises(ZeroDivisionError) as cm:
            div(3, 0)


if __name__ == '__main__':
    unittest.main()
