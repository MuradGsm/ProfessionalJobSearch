import pytest
from pydantic import ValidationError
from app.schemas.user_schema import UserRequest, UserRole, UserResponse, UserProfile, UserUpdate, ChangePasswordRequest
from datetime import datetime

class TestUserRequest:
    def test_valid_user_request(self):
        valid_data = {
            "name": "John Doe",
            "role": "candidate", 
            "email": "john@example.com",
            "password": "Password123"
        }
        
        user = UserRequest(**valid_data)
        
        assert user.name == "John Doe"
        assert user.role == UserRole.candidate
        assert user.email == "john@example.com"
        assert user.password == "Password123"
    
    def test_name_too_short(self):
        invalid_data = {
            "name": "A", 
            "role": "candidate",
            "email": "john@example.com", 
            "password": "Password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('name',)
        assert 'at least 2 characters' in error['msg']

    def test_password_missing_uppercase(self):

        invalid_data = {
            "name": "John Doe",
            "role": "candidate", 
            "email": "john@example.com",
            "password": "password123"  
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('password',)
        assert 'uppercase letter' in error['msg']
    
    @pytest.mark.parametrize("role", ["candidate", "employer"])
    def test_valid_roles(self, role):
        valid_data = {
            "name": "John Doe",
            "role": role,
            "email": "john@example.com", 
            "password": "Password123"
        }
        
        user = UserRequest(**valid_data)
        assert user.role.value == role


class TestUserResponse:
    
    def test_valid_user_response(self):
        now = datetime.utcnow()
        valid_data = {
            "id": 1,
            "name": "John Doe",
            "role": "candidate",
            "email": "john@example.com",
            "is_admin": False,
            "is_active": True,
            "email_verified": False,
            "company_id": None,
            "last_login": None,
            "created_at": now,
            "updated_at": now
        }
        
        user = UserResponse(**valid_data)
        
        assert user.id == 1
        assert user.name == "John Doe"
        assert user.role == UserRole.candidate
        assert user.email == "john@example.com"
        assert user.is_admin == False
        assert user.is_active == True
        assert user.email_verified == False
        assert user.company_id is None
        assert user.last_login is None
        assert user.created_at == now
        assert user.updated_at == now

    def test_user_response_with_optional_fields(self):
        now = datetime.utcnow()
        last_login = datetime(2024, 1, 15, 10, 30, 0)
        
        data_with_optionals = {
            "id": 2,
            "name": "Jane Smith",
            "role": "employer",
            "email": "jane@company.com",
            "is_admin": True,
            "is_active": True,
            "email_verified": True,
            "company_id": 42,
            "last_login": last_login,
            "created_at": now,
            "updated_at": now
        }
        
        user = UserResponse(**data_with_optionals)
        
        assert user.id == 2
        assert user.role == UserRole.employer
        assert user.is_admin == True
        assert user.email_verified == True
        assert user.company_id == 42
        assert user.last_login == last_login

    def test_user_response_default_values(self):
        now = datetime.utcnow()
        minimal_data = {
            "id": 3,
            "name": "Test User",
            "role": "candidate",
            "email": "test@example.com",
            "created_at": now,
            "updated_at": now
        }
        
        user = UserResponse(**minimal_data)
        
        assert user.is_admin == False  # default
        assert user.is_active == True  # default
        assert user.email_verified == False  # default
        assert user.company_id is None  # Optional field
        assert user.last_login is None  # Optional field

    def test_user_response_invalid_id(self):
        """Тест: ID должен быть integer"""
        now = datetime.utcnow()
        invalid_data = {
            "id": "not_integer",
            "name": "Test User",
            "role": "candidate",
            "email": "test@example.com",
            "created_at": now,
            "updated_at": now
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('id',)
        assert 'int' in error['type']

    def test_user_response_invalid_email(self):
        now = datetime.utcnow()
        invalid_data = {
            "id": 1,
            "name": "Test User", 
            "role": "candidate",
            "email": "invalid-email", 
            "created_at": now,
            "updated_at": now
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('email',)

    def test_user_response_invalid_role(self):
        now = datetime.utcnow()
        invalid_data = {
            "id": 1,
            "name": "Test User",
            "role": "invalid_role",
            "email": "test@example.com",
            "created_at": now,
            "updated_at": now
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('role',)

    @pytest.mark.parametrize("role", ["candidate", "employer"])
    def test_user_response_valid_roles(self, role):
        now = datetime.utcnow()
        data = {
            "id": 1,
            "name": "Test User",
            "role": role,
            "email": "test@example.com", 
            "created_at": now,
            "updated_at": now
        }
        
        user = UserResponse(**data)
        assert user.role.value == role

    def test_user_response_serialization(self):
        now = datetime.utcnow()
        data = {
            "id": 1,
            "name": "Test User",
            "role": "candidate",
            "email": "test@example.com",
            "created_at": now,
            "updated_at": now
        }
        
        user = UserResponse(**data)
        
        user_dict = user.model_dump()
        assert isinstance(user_dict, dict)
        assert user_dict["id"] == 1
        assert user_dict["name"] == "Test User"
        assert user_dict["role"] == "candidate"
        
        user_json = user.model_dump_json()
        assert isinstance(user_json, str)
        assert '"id":1' in user_json

    def test_user_response_from_attributes_simulation(self):
        class MockORMUser:
            def __init__(self):
                self.id = 1
                self.name = "ORM User"
                self.role = "employer"
                self.email = "orm@example.com"
                self.is_admin = False
                self.is_active = True
                self.email_verified = True
                self.company_id = 10
                self.last_login = datetime.utcnow()
                self.created_at = datetime.utcnow()
                self.updated_at = datetime.utcnow()
        
        orm_user = MockORMUser()
        
        user_response = UserResponse.model_validate(orm_user)
        
        assert user_response.id == 1
        assert user_response.name == "ORM User"
        assert user_response.role == UserRole.employer
        assert user_response.company_id == 10


class TestUserProfile:
    def test_valid_user_profile(self):
        now = datetime.utcnow()
        valid_data = {
            'id': 1,
            'name': 'murad',
            'email': 'email@email.com',
            'role': 'employer',
            'is_admin': False,
            'is_active': True,
            'email_verified': True,  
            'two_factor_enabled': True,
            'company_id': None,
            'company_name': None,
            'last_login': None,
            'created_at': now,
            'updated_at': now,
            'total_applications': 5,
            'total_resumes': 2,
            'unread_notifications': 3,
            'unread_messages': 1
        }

        user = UserProfile(**valid_data)

        assert user.id == 1
        assert user.name == 'murad'
        assert user.email == 'email@email.com'
        assert user.role == UserRole.employer
        assert user.is_admin == False
        assert user.is_active == True
        assert user.email_verified == True 
        assert user.two_factor_enabled == True
        assert user.company_id is None
        assert user.company_name is None
        assert user.created_at == now
        assert user.updated_at == now
        assert user.total_applications == 5
        assert user.total_resumes == 2
        assert user.unread_notifications == 3
        assert user.unread_messages == 1

    def test_user_profile_default_statistics(self):
        now = datetime.utcnow()
        minimal_data = {
            'id': 1,
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'candidate',
            'is_admin': False,
            'is_active': True,
            'email_verified': False,
            'two_factor_enabled': False,
            'created_at': now,
            'updated_at': now
        }

        user = UserProfile(**minimal_data)

        assert user.total_applications == 0
        assert user.total_resumes == 0
        assert user.unread_notifications == 0
        assert user.unread_messages == 0


class TestUserUpdate:
    
    def test_valid_user_update_all_fields(self):
        valid_data = {
            "name": "Updated Name",
            "email": "updated@example.com"
        }
        
        user_update = UserUpdate(**valid_data)
        
        assert user_update.name == "Updated Name"
        assert user_update.email == "updated@example.com"
    
    def test_valid_user_update_partial(self):
        partial_data = {
            "name": "Only Name Updated"
        }
        
        user_update = UserUpdate(**partial_data)
        
        assert user_update.name == "Only Name Updated"
        assert user_update.email is None  
    
    def test_valid_user_update_email_only(self):
        partial_data = {
            "email": "newemail@example.com"
        }
        
        user_update = UserUpdate(**partial_data)
        
        assert user_update.name is None  
        assert user_update.email == "newemail@example.com"
    
    def test_empty_user_update(self):
        """Тест пустого обновления - все поля Optional"""
        empty_data = {}
        
        user_update = UserUpdate(**empty_data)
        
        assert user_update.name is None
        assert user_update.email is None
    
    def test_name_validation_strips_whitespace(self):
        data_with_spaces = {
            "name": "  John Doe  " 
        }
        
        user_update = UserUpdate(**data_with_spaces)
        
        assert user_update.name == "John Doe"
    
    def test_name_validation_only_spaces(self):
        invalid_data = {
            "name": "  " 
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('name',)
        assert 'Name cannot be empty' in error['msg']


    def test_name_too_short_field_validation(self):
        invalid_data = {
            "name": "A" 
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('name',)
        assert 'at least 2 characters' in error['msg']
    
    def test_name_too_long_field_validation(self):
        invalid_data = {
            "name": "A" * 101  
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('name',)
        assert 'at most 100 characters' in error['msg']
    
    def test_email_validation_invalid_format(self):
        invalid_data = {
            "email": "invalid-email-format"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('email',)
    
    @pytest.mark.parametrize("valid_email", [
        "test@example.com",
        "user.name@domain.org",
        "user+tag@example.co.uk",
        "123@numbers.com"
    ])
    def test_valid_email_formats(self, valid_email):
        data = {
            "email": valid_email
        }
        
        user_update = UserUpdate(**data)
        assert user_update.email == valid_email
    
    @pytest.mark.parametrize("invalid_email", [
        "notanemail",
        "@domain.com",
        "user@",
        "user space@domain.com",
        "user..double@domain.com"
    ])
    def test_invalid_email_formats(self, invalid_email):
        data = {
            "email": invalid_email
        }
        
        with pytest.raises(ValidationError):
            UserUpdate(**data)
    
    def test_name_validation_preserves_internal_spaces(self):

        data = {
            "name": "  John   Doe  Smith  " 
        }
        
        user_update = UserUpdate(**data)
        assert user_update.name == "John   Doe  Smith"
    
    def test_name_validation_none_value(self):
        data = {
            "name": None
        }

        user_update = UserUpdate(**data)
        assert user_update.name is None
    
    def test_serialization_with_none_values(self):
        data = {
            "name": "Test User"
        }
        
        user_update = UserUpdate(**data)
        
        serialized = user_update.model_dump()
        assert serialized["name"] == "Test User"
        assert serialized["email"] is None
        

        serialized_exclude_none = user_update.model_dump(exclude_none=True)
        assert "name" in serialized_exclude_none
        assert "email" not in serialized_exclude_none


class TestChangePasswordRequest:

    def test_valid_change_password_all_fields(self):
        valid_data = {
            'current_password': 'current',
            'new_password': 'Aze12321',
            'confirm_password': 'Aze12321'
        }

        change = ChangePasswordRequest(**valid_data)

        assert change.current_password == 'current'
        assert change.new_password == 'Aze12321'
        assert change.confirm_password == 'Aze12321'

    def test_current_password_invalid_format(self):
        invalid_data = {
            'current_password': '', 
            'new_password': 'Aze12321',
            'confirm_password': 'Aze12321'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('current_password',)  
        assert 'at least 1 character' in error['msg'] 

    def test_new_password_invalid_format(self):
        invalid_data = {
            'current_password': 'current',
            'new_password': 'Aze123',
            'confirm_password': 'Aze12321'
        }

        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(**invalid_data)

        error = exc_info.value.errors()[0]
        assert error['loc'] == ('new_password',)
        assert 'at least 8 character' in error['msg']
    
    def test_confirm_password_invalid_format(self):
        invalid_data = {
            'current_password': 'current',
            'new_password': 'Aze12321',
            'confirm_password': 'Aze123'
        }

        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(**invalid_data)

        error = exc_info.value.errors()[0]
        assert error['loc'] == ('confirm_password',)
        assert 'at least 8 character' in error['msg']


    def test_new_password_upprecase(self):
        invalid_data = {
            'current_password': 'current',
            'new_password': 'aze12321',
            'confirm_password': 'aze12321'
        }

        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('new_password',)
        assert 'uppercase letter' in error['msg']
    
    def test_new_password_lowercase(self):
        invalid_data = {
            'current_password': 'current',
            'new_password': 'AZE12321',
            'confirm_password': 'AZE12321'
        }

        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('new_password',)
        assert 'lowercase letter' in error['msg']
    
    def test_new_password_isdigite(self):
        invalid_data = {
            'current_password': 'current',
            'new_password': 'AzePassword',
            'confirm_password': 'AzePassword'
        }

        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(**invalid_data)
        
        error = exc_info.value.errors()[0]
        assert error['loc'] == ('new_password',)
        assert 'digit' in error['msg']
    
    def test_confir_and_new_password_match(self):
        invalid_data = {
            'current_password': 'current',
            'new_password': 'AzePassword123',
            'confirm_password': 'AzePassword321'
        }

        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(**invalid_data)

        error = exc_info.value.errors()[0]
        assert error['loc'] == ('confirm_password',)
        assert 'Passwords do not match' in error['msg']