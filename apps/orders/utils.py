from math import radians, sin, cos, sqrt, atan2


def calculate_distance(lat1, lon1, lat2, lon2):
    
    if not all([lat1, lon1, lat2, lon2]):
        return float('inf') 
    
    R = 6371.0
    
    lat1_rad = radians(float(lat1))
    lon1_rad = radians(float(lon1))
    lat2_rad = radians(float(lat2))
    lon2_rad = radians(float(lon2))
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)


def filter_orders_by_distance(executor, orders, max_distance_km=10):
    if not hasattr(executor, 'executor_profile'):
        return []
    
    profile = executor.executor_profile
    if not profile.latitude or not profile.longitude:
        return []
    
    filtered_orders = []
    
    for order in orders:
        if order.latitude and order.longitude:
            distance = calculate_distance(
                profile.latitude, profile.longitude,
                order.latitude, order.longitude
            )
            
            if distance <= max_distance_km:
                order.distance = distance  # Добавляем расстояние к заказу
                filtered_orders.append(order)
    
    # Сортируем по расстоянию
    filtered_orders.sort(key=lambda x: x.distance)
    
    return filtered_orders