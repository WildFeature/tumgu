items = {
    'milk15': {'name': 'молоко 1.5%', 'count': 34, 'price': 89.9},
    'cheese': {'name': 'сыр молочный 1 кг.', 'count': 12, 'price': 990.9},
    'sausage': {'name': 'колбаса 1 кг.', 'count': 122, 'price': 1990.9}
}

# Формируем словарь с критерием: True, если count < 20, иначе False
price_less_20 = {key: (item['count'] < 20) for key, item in items.items()}

print(price_less_20)