from app.schemas.user_schema import UserResponse, UserProfile

def map_user_to_response(user: "User") -> UserResponse:
    """Преобразуем SQLAlchemy User в Pydantic UserResponse"""
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        is_admin=user.is_admin,
        is_active=user.is_active,
        email_verified=user.email_verified,
        company_id=user.get_company_id(),
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

def map_user_to_profile(user: "User") -> UserProfile:
    """Преобразуем SQLAlchemy User в Pydantic UserProfile"""
    company_name = None
    if user.owned_company:
        company_name = user.owned_company.name
    elif user.company_membership and getattr(user.company_membership, 'company', None):
        company_name = user.company_membership.company.name

    # Заглушки для статистики
    return UserProfile(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        is_admin=user.is_admin,
        is_active=user.is_active,
        email_verified=user.email_verified,
        two_factor_enabled=user.two_factor_enabled,
        company_id=user.get_company_id(),
        company_name=company_name,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
        total_applications=0,
        total_resumes=0,
        unread_notifications=0,
        unread_messages=0
    )
