import asyncio
import unittest


async def async_add(a, b):
    print("start 1")
    await asyncio.sleep(2)
    print("end 1")
    return a + b

async def async_sum(a, b):
    print("start 2")
    await asyncio.sleep(1)
    print("end 2")
    return a * b


class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):
    async def test_add(self):
        """Add function test"""
        add_ = await async_add(2, 2)
        sum_ = await async_sum(2, 2)
        self.assertEqual(add_, sum_)

    async def test_sum(self):
        """Sum function test"""
        add_ = await async_add(2, 2)
        sum_ = await async_sum(2, 2)
        self.assertEqual(add_, sum_)


if __name__ == '__main__':
    unittest.main()
