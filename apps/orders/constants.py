EXTRA_SERVICES_CATALOG = {
    'window_cleaning': {
        'name': 'Мытье окна',
        'price': 490,
        'unit': 'за 1 окно',
        'description': 'Мытье одного окна с двух сторон'
    },
    'sofa_cleaning': {
        'name': 'Химчистка дивана/ковра',
        'price': 990,
        'unit': 'за 1 штуку',
        'description': 'Химчистка одного дивана или ковра'
    },
    'fridge_cleaning': {
        'name': 'Мытье холодильника',
        'price': 299,
        'unit': 'за 1 штуку',
        'description': 'Полная мойка холодильника внутри и снаружи'
    },
    'oven_cleaning': {
        'name': 'Мытье духовки',
        'price': 399,
        'unit': 'за 1 штуку',
        'description': 'Чистка духового шкафа'
    },
}


BASE_PRICES_PER_SQM = {
    'standard': 25,
    'general': 40,
    'after_repair': 60,
    'office': 55,
}


PLACEMENT_TARIFFS = {
    'three_days': {
        'name': '3 дня',
        'price': 25,
        'days': 3
    },
    'week': {
        'name': '1 неделя',
        'price': 50,
        'days': 7
    },
    'month': {
        'name': '1 месяц',
        'price': 150,
        'days': 30
    },
}

URGENCY_FEE = 100


CLEANING_TYPES = (
    ('standard', 'Стандартная уборка'),
    ('general', 'Генеральная уборка'),
    ('after_repair', 'После ремонта'),
    ('office', 'Офисная уборка'),
)

ORDER_STATUS_CHOICES = (
    ('draft', 'Черновик'),
    ('published', 'Опубликован'),
    ('in_progress', 'В работе'),
    ('completed', 'Завершен'),
    ('cancelled', 'Отменен'),
    ('expired', 'Срок размещения истек'),
)

URGENCY_CHOICES = (
    ('normal', 'Обычный'),
    ('urgent', 'Срочный (+100 руб)'),
)

TARIFF_CHOICES = (
    ('three_days', '3 дня (25 руб)'),
    ('week', '1 неделя (50 руб)'),
    ('month', '1 месяц (150 руб)'),
)

PAYMENT_STATUS_CHOICES = (
    ('pending', 'Ожидает оплаты'),
    ('paid', 'Оплачен'),
    ('refunded', 'Возврат'),
)