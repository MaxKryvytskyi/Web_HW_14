from unittest.mock import Mock

mock = Mock(return_value=[1,1,1,1,1,1])
mock.get.return_value = 111
print(mock.get.return_value)
print(mock())
print(mock.get())