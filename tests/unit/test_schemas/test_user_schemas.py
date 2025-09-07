import pytest
from pydantic import ValidationError
from app.schemas.user_schema import UserRequest, UserRole

class TestUserRequest:
    """Unit тесты для UserRequest схемы"""
    
    def test_valid_user_request(self):
        """Тест с корректными данными"""
        valid_data = {
            "name": "John Doe",
            "role": "candidate", 
            "email": "john@example.com",
            "password": "Password123"
        }
        
        # Создаем объект - не должно быть ошибок
        user = UserRequest(**valid_data)
        
        # Проверяем что данные сохранились правильно
        assert user.name == "John Doe"
        assert user.role == UserRole.candidate
        assert user.email == "john@example.com"
        assert user.password == "Password123"
    
    # НЕГАТИВНЫЙ ТЕСТ - невалидное имя
    def test_name_too_short(self):
        """Тест: имя короче 2 символов должно вызывать ошибку"""
        invalid_data = {
            "name": "A",  # Слишком короткое
            "role": "candidate",
            "email": "john@example.com", 
            "password": "Password123"
        }
        
        # Ожидаем ValidationError
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(**invalid_data)
        
        # Проверяем что ошибка именно в поле name
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('name',)
        assert 'at least 2 characters' in error['msg']
    
    # ТЕСТ КАСТОМНОГО ВАЛИДАТОРА
    def test_password_missing_uppercase(self):
        """Тест: пароль без заглавных букв должен вызывать ошибку"""
        invalid_data = {
            "name": "John Doe",
            "role": "candidate", 
            "email": "john@example.com",
            "password": "password123"  # Нет заглавных букв
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('password',)
        assert 'uppercase letter' in error['msg']
    
    # ПАРАМЕТРИЗОВАННЫЙ ТЕСТ для разных ролей
    @pytest.mark.parametrize("role", ["candidate", "employer"])
    def test_valid_roles(self, role):
        """Тест: проверяем что обе роли валидны"""
        valid_data = {
            "name": "John Doe",
            "role": role,
            "email": "john@example.com", 
            "password": "Password123"
        }
        
        user = UserRequest(**valid_data)
        assert user.role.value == role