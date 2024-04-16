# import hashlib

# def calculate_file_hash(file_path):
#     # Відкриття файлу у бінарному режимі
#     with open(file_path, "rb") as f:
#         # Створення об'єкту хешування SHA-256
#         hasher = hashlib.sha256()
        
#         # Читання файлу блоками і оновлення хешу
#         while True:
#             data = f.read(65536)  # Читання блоків по 64 КБ
#             if not data:
#                 break
#             hasher.update(data)
    
#     # Повернення обчисленого хешу
#     return hasher.hexdigest()

# # Шлях до файлу, який ви хочете перевірити
# file_path = "D:\Загрузки\Valheim v0.217.38.rar"

# # Очікуване значення хешу
# expected_hash = "87d6950445ede0849f3460a0a62224b8af4c33a68415e538934c035bb3010e06"

# # Обчислення хешу файлу
# file_hash = calculate_file_hash(file_path)
# print(file_hash)
# # Порівняння обчисленого хешу з очікуваним
# if file_hash == expected_hash:
#     print("Хеш файла співпадає з очікуваним значенням.")
# else:
#     print("Хеш файла НЕ співпадає з очікуваним значенням.")







numbers = [1971, 78, 7644, 98, 27, 5694, 73, 2646]
dict_num = {"A": None, "B": None, "C": None, "D": None}

list_num = list(set(numbers)) 
list_num.sort()
for el in dict_num:
    dict_num[el] = list_num[0]
    list_num.remove(dict_num[el])
print(dict_num["D"])
