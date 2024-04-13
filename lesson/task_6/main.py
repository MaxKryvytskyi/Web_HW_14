import unittest
from unittest.mock import MagicMock
from my_module import ProductionClass
from unittest.mock import patch
import module

thing = ProductionClass()
thing.method = MagicMock(return_value=3)
thing.method(1, 2, 3, key='value')

thing.method.assert_called_with(1, 2, 3, key='value')

with patch.object(ProductionClass, 'method', return_value=3) as mock_method:
    thing = ProductionClass()
    thing.method(1, 2, 3)
    mock_method.assert_called_once_with(1, 2, 3)






@patch('module.ClassName2')
@patch('module.ClassName1')
def test_class(MockClass1, MockClass2):
    module.ClassName1()
    module.ClassName2()
    assert MockClass1 is module.ClassName1
    assert MockClass2 is module.ClassName2
    assert MockClass1.called
    assert MockClass2.called

 


if __name__ == '__main__':
    unittest.main()

# with patch.object(ProductionClass, 'method', return_value=3) as mock_method:
#     thing = ProductionClass()
#     thing.method(1, 2, 3)
#     mock_method.assert_called_once_with(1, 2, 3)

# from unittest.mock import patch


# @patch('module.ClassName2')
# @patch('module.ClassName1')
# def test_class(MockClass1, MockClass2):
#     module.ClassName1()
#     module.ClassName2()
#     assert MockClass1 is module.ClassName1
#     assert MockClass2 is module.ClassName2
#     assert MockClass1.called
#     assert MockClass2.called

