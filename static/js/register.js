document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    const roleButtons = document.querySelectorAll('.role-btn');
    let selectedRole = 'customer';
    
    // ===== ПЕРЕКЛЮЧЕНИЕ РОЛИ =====
    roleButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            roleButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            selectedRole = this.dataset.role;
            console.log('Выбрана роль:', selectedRole);
        });
    });
    
    // ===== ТЕЛЕФОН: ТОЛЬКО ЦИФРЫ =====
    const phoneInput = document.getElementById('phone');
    
    // Блокируем ввод букв на уровне клавиш
    phoneInput.addEventListener('keydown', function(e) {
        // Разрешаем: backspace, delete, tab, escape, enter, стрелки
        if ([46, 8, 9, 27, 13, 37, 39, 38, 40].indexOf(e.keyCode) !== -1 ||
            (e.keyCode === 65 && e.ctrlKey === true) ||
            (e.keyCode === 67 && e.ctrlKey === true) ||
            (e.keyCode === 86 && e.ctrlKey === true) ||
            (e.keyCode === 88 && e.ctrlKey === true)) {
            return;
        }
        
        // Разрешаем только цифры (48-57 на основной клавиатуре, 96-105 на цифровой)
        if (!((e.keyCode >= 48 && e.keyCode <= 57) || 
              (e.keyCode >= 96 && e.keyCode <= 105))) {
            e.preventDefault();
        }
    });
    
    // Форматирование телефона
    phoneInput.addEventListener('input', function(e) {
        // Оставляем только цифры
        let value = e.target.value.replace(/\D/g, '');
        
        // Ограничиваем до 11 цифр
        if (value.length > 11) {
            value = value.substring(0, 11);
        }
        
        // Убираем первую 7 или 8
        if (value.length > 0) {
            if (value[0] === '7' || value[0] === '8') {
                value = value.substring(1);
            }
            
            // Форматируем
            let formattedValue = '+7';
            
            if (value.length > 0) {
                formattedValue += ' (' + value.substring(0, 3);
            }
            if (value.length >= 3) {
                formattedValue += ') ' + value.substring(3, 6);
            }
            if (value.length >= 6) {
                formattedValue += '-' + value.substring(6, 8);
            }
            if (value.length >= 8) {
                formattedValue += '-' + value.substring(8, 10);
            }
            
            e.target.value = formattedValue;
        }
    });
    
    // Запрет вставки нецифровых символов
    phoneInput.addEventListener('paste', function(e) {
        e.preventDefault();
        const pastedText = (e.clipboardData || window.clipboardData).getData('text');
        const digitsOnly = pastedText.replace(/\D/g, '').substring(0, 11);
        
        if (digitsOnly.length > 0) {
            let value = digitsOnly;
            if (value[0] === '7' || value[0] === '8') {
                value = value.substring(1);
            }
            
            let formattedValue = '+7';
            if (value.length > 0) formattedValue += ' (' + value.substring(0, 3);
            if (value.length >= 3) formattedValue += ') ' + value.substring(3, 6);
            if (value.length >= 6) formattedValue += '-' + value.substring(6, 8);
            if (value.length >= 8) formattedValue += '-' + value.substring(8, 10);
            
            e.target.value = formattedValue;
        }
    });
    
    // ===== ВАЛИДАЦИЯ =====
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    function validatePhone(phone) {
        const digits = phone.replace(/\D/g, '');
        return digits.length === 11;
    }
    
    async function checkUsername(username) {
        try {
            const response = await fetch(`/api/users/check-username/?username=${username}`);
            const data = await response.json();
            return data.exists;
        } catch (error) {
            console.error('Error checking username:', error);
            return false;
        }
    }
    
    // Очистка ошибок при вводе
    const inputs = form.querySelectorAll('.form-input');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            const errorElement = document.getElementById(this.id + 'Error');
            if (errorElement) {
                errorElement.textContent = '';
                errorElement.classList.remove('success');
            }
        });
    });
    
    // ===== ОТПРАВКА ФОРМЫ =====
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        let isValid = true;
        
        const username = document.getElementById('username').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const passwordConfirm = document.getElementById('password_confirm').value;
        
        console.log('Отправка формы с ролью:', selectedRole);
        
        // Сброс ошибок
        document.querySelectorAll('.error-message').forEach(el => {
            el.textContent = '';
            el.classList.remove('success');
        });
        
        // Проверка логина
        if (username.length < 3) {
            document.getElementById('usernameError').textContent = 'Логин должен содержать минимум 3 символа';
            isValid = false;
        } else {
            const usernameExists = await checkUsername(username);
            if (usernameExists) {
                document.getElementById('usernameError').textContent = 'Пользователь с таким логином уже существует';
                isValid = false;
            } else {
                document.getElementById('usernameError').classList.add('success');
            }
        }
        
        // Проверка телефона
        if (!validatePhone(phone)) {
            document.getElementById('phoneError').textContent = 'Введите корректный номер телефона';
            isValid = false;
        }
        
        // Проверка email
        if (!validateEmail(email)) {
            document.getElementById('emailError').textContent = 'Введите корректный email';
            isValid = false;
        }
        
        // Проверка пароля
        if (password.length < 8) {
            document.getElementById('passwordError').textContent = 'Пароль должен содержать минимум 8 символов';
            isValid = false;
        }
        
        // Проверка совпадения паролей
        if (password !== passwordConfirm) {
            document.getElementById('passwordConfirmError').textContent = 'Пароли не совпадают';
            isValid = false;
        } else if (password.length >= 8) {
            document.getElementById('passwordConfirmError').textContent = 'Пароли совпадают';
            document.getElementById('passwordConfirmError').classList.add('success');
        }
        
        if (isValid) {
            const submitBtn = form.querySelector('.btn-register-submit');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Регистрация...';
            submitBtn.disabled = true;
            
            try {
                const requestData = {
                    username: username,
                    phone: phone,
                    email: email,
                    password: password,
                    password_confirm: passwordConfirm,
                    role: selectedRole
                };
                
                console.log('Отправляем данные:', requestData);
                
                const response = await fetch('/api/users/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData)
                });
                
                const data = await response.json();
                console.log('Ответ сервера:', data);
                
                if (response.ok && data.token) {
                    // Сохраняем токен
                    localStorage.setItem('auth_token', data.token);
                    
                    // Сохраняем роль (берем из ответа сервера, чтобы быть уверенным)
                    localStorage.setItem('user_role', data.user.role);

                    // ЛОГИКА РЕДИРЕКТА
                    if (data.user.role === 'executor') {
                        // Если Исполнитель -> ведем на профиль
                        window.location.href = '/executor-profile/';
                    } else {
                        // Если Заказчик -> ведем на главную
                        window.location.href = '/';
                    }
                } else {
                    // ... остальной код обработки ошибок
                    alert('Ошибка регистрации: ' + (data.error || JSON.stringify(data)));
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Произошла ошибка. Попробуйте позже.');
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        }
    });
    
    // ===== ПЕРЕКЛЮЧЕНИЕ ВИДИМОСТИ ПАРОЛЯ =====
    function setupPasswordToggle(toggleId, inputId) {
        const toggle = document.getElementById(toggleId);
        const input = document.getElementById(inputId);
        
        if (toggle && input) {
            const eyeOpen = toggle.querySelector('.eye-open');
            const eyeClosed = toggle.querySelector('.eye-closed');
            
            toggle.addEventListener('click', function() {
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);
                
                if (type === 'text') {
                    eyeOpen.style.display = 'none';
                    eyeClosed.style.display = 'block';
                } else {
                    eyeOpen.style.display = 'block';
                    eyeClosed.style.display = 'none';
                }
            });
        }
    }
    
    setupPasswordToggle('togglePassword', 'password');
    setupPasswordToggle('togglePasswordConfirm', 'password_confirm');
});