# populate.py — запускать: python populate.py

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Greenleaf.settings')
django.setup()

from greenleaf_app.models import Category, Product, AboutUs, Contact

# Category
categories = [
    'Витамины',
    'Спортивное питание',
    'Косметика',
    'Чаи и напитки',
    'Суперфуды',
]

category_objects = []
for name in categories:
    cat, _ = Category.objects.get_or_create(category_name=name)
    category_objects.append(cat)
    print(f'Category: {cat.category_name}')


# Product
products = [
    ('Омега-3', 'ART-001', 'Рыбий жир высокой очистки', 1200.00, 10.5, category_objects[0]),
    ('Витамин C', 'ART-002', 'Аскорбиновая кислота 1000мг', 850.00, 7.0, category_objects[0]),
    ('Витамин D3', 'ART-003', 'Холекальциферол 2000 МЕ', 950.00, 8.0, category_objects[0]),
    ('Протеин Whey', 'ART-004', 'Сывороточный протеин ванильный', 3500.00, 30.0, category_objects[1]),
    ('Креатин', 'ART-005', 'Моногидрат креатина 300г', 2200.00, 18.0, category_objects[1]),
    ('BCAA', 'ART-006', 'Аминокислоты с разветвлённой цепью', 1800.00, 15.0, category_objects[1]),
    ('Крем для лица', 'ART-007', 'Увлажняющий крем с алоэ', 1100.00, 9.0, category_objects[2]),
    ('Шампунь', 'ART-008', 'Натуральный шампунь без SLS', 750.00, 6.0, category_objects[2]),
    ('Зелёный чай', 'ART-009', 'Органический зелёный чай 100г', 600.00, 5.0, category_objects[3]),
    ('Имбирный чай', 'ART-010', 'Чай с имбирём и лимоном', 550.00, 4.5, category_objects[3]),
    ('Спирулина', 'ART-011', 'Спирулина в таблетках 200шт', 1400.00, 12.0, category_objects[4]),
    ('Чиа семена', 'ART-012', 'Семена чиа 500г', 900.00, 7.5, category_objects[4]),
]

for product_name, article_number, description, price, pv, category in products:
    product, _ = Product.objects.get_or_create(
        article_number=article_number,
        defaults={
            'product_name': product_name,
            'description': description,
            'price': price,
            'pv': pv,
            'category': category,
            'is_available': True,
        }
    )
    print(f'Product: {product.product_name}')


# AboutUs
about, _ = AboutUs.objects.get_or_create(
    title='О компании GreenLeaf',
    defaults={
        'description': 'GreenLeaf — магазин натуральных продуктов для здоровья и красоты. '
                       'Мы предлагаем только качественные товары проверенных производителей.',
    }
)
print(f'AboutUs: {about.title}')


# Contact
contact, _ = Contact.objects.get_or_create(
    phone_number='+996700000000',
    defaults={
        'email': 'info@greenleaf.kg',
        'address': 'Бишкек, ул. Чуй 123',
        'instagram': 'https://instagram.com/greenleaf',
        'whatsapp': '+996700000000',
    }
)
print(f'Contact: {contact.phone_number}')

print('\nГотово!')