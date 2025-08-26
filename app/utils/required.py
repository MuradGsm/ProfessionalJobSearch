from fastapi import Depends, HTTPException, status
from app.schemas.user_schema import UserResponse
from app.auth.deps import get_current_user

async def admin_required(current_user: UserResponse = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin access required')
    return current_user
    

async def candidate_required(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    if current_user.role != 'candidate':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Candidate access required')
    return current_user

async def employer_required(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    if current_user.role != 'employer':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Employer access required')
    return current_user