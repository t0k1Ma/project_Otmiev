document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('auth_token');
    
    // Проверка авторизации
    if (!token) {
        window.location.href = '/login/';
        return;
    }
    
    // Загрузка данных профиля
    loadProfile();
    
    // Обработчик загрузки аватара
    const avatarInput = document.getElementById('avatarInput');
    if (avatarInput) {
        avatarInput.addEventListener('change', handleAvatarUpload);
    }
    
    // Обработчик сохранения
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', saveProfile);
    }
    
    // Обработчик выхода из профиля
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            if (confirm('Вы уверены что хотите выйти?')) {
                localStorage.removeItem('auth_token');
                localStorage.removeItem('user_role');
                window.location.href = '/login/';
            }
        });
    }
});

// Загрузка профиля
async function loadProfile() {
    const token = localStorage.getItem('auth_token');
    
    try {
        const response = await fetch('/api/users/executor-profile/', {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            fillProfileData(data);
        } else {
            console.error('Ошибка загрузки профиля');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Заполнение данных профиля
function fillProfileData(data) {
    // Основные данные пользователя
    if (data.user) {
        document.getElementById('firstName').value = data.user.first_name || '';
        document.getElementById('lastName').value = data.user.last_name || '';
        document.getElementById('phone').value = data.user.phone || '';
        document.getElementById('email').value = data.user.email || '';
        document.getElementById('city').value = data.user.city || '';
        document.getElementById('address').value = data.address || '';
    }
    
    // Данные профиля исполнителя
    document.getElementById('experience').value = data.experience_years || '';
    document.getElementById('about').value = data.about || '';
    document.getElementById('totalOrders').value = data.total_orders || '0';
    document.getElementById('ratingValue').textContent = data.rating || '5.00';
    
    // Типы уборки (специализации)
    if (data.specializations) {
        const checkboxes = document.querySelectorAll('input[name="cleaning_type"]');
        checkboxes.forEach(checkbox => {
            if (data.specializations.includes(checkbox.value)) {
                checkbox.checked = true;
            }
        });
    }
    
    // Аватар
    if (data.user && data.user.avatar) {
        document.getElementById('avatarImg').src = data.user.avatar;
        document.getElementById('avatarImg').style.display = 'block';
        document.getElementById('avatarPlaceholder').style.display = 'none';
    }
    
    // Отзывы - показываем только если есть
    if (data.reviews && data.reviews.length > 0) {
        displayReviews(data.reviews);
    } else {
        document.getElementById('reviewsSection').style.display = 'none';
    }
}

// Отображение отзывов
function displayReviews(reviews) {
    const carousel = document.getElementById('reviewsCarousel');
    const reviewsSection = document.getElementById('reviewsSection');
    
    carousel.innerHTML = '';
    reviewsSection.style.display = 'block';
    
    reviews.forEach(review => {
        const card = document.createElement('div');
        card.className = 'review-card';
        card.innerHTML = `
            <div class="review-header">
                <div class="review-author">${review.author}</div>
                <div class="review-rating">⭐ ${review.rating}</div>
            </div>
            <div class="review-text">${review.text}</div>
        `;
        carousel.appendChild(card);
    });
}

// Загрузка аватара
// Загрузка аватара
async function handleAvatarUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('avatar', file);
    
    const token = localStorage.getItem('auth_token');
    
    try {
        const response = await fetch('/api/users/upload-avatar/', {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`
                // НЕ добавляй Content-Type для FormData!
            },
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Аватар загружен:', data);
            document.getElementById('avatarImg').src = data.avatar_url;
            document.getElementById('avatarImg').style.display = 'block';
            document.getElementById('avatarPlaceholder').style.display = 'none';
        } else {
            const error = await response.json();
            alert('Ошибка загрузки: ' + error.error);
        }
    } catch (error) {
        console.error('Error uploading avatar:', error);
        alert('Произошла ошибка при загрузке');
    }
}

// Сохранение профиля
async function saveProfile(e) {
    e.preventDefault();
    
    const token = localStorage.getItem('auth_token');
    
    // Собираем выбранные типы уборки
    const cleaningTypes = [];
    document.querySelectorAll('input[name="cleaning_type"]:checked').forEach(checkbox => {
        cleaningTypes.push(checkbox.value);
    });
    
    const data = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        city: document.getElementById('city').value,
        address: document.getElementById('address').value,
        experience_years: document.getElementById('experience').value,
        about: document.getElementById('about').value,
        specializations: cleaningTypes
    };
    
    try {
        const response = await fetch('/api/users/executor-profile/', {
            method: 'PUT',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert('Профиль сохранен!');
        } else {
            const errorData = await response.json();
            alert('Ошибка сохранения: ' + JSON.stringify(errorData));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Произошла ошибка');
    }
}