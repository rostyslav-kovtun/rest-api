from fastapi import APIRouter, HTTPException, status, Depends
from models import UserCreate, UserLogin, Token, RefreshTokenRequest, UserResponse
from user_repository import user_repository
from password_utils import verify_password
from auth import create_access_token, create_refresh_token, verify_token, get_current_active_user

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    try:
        user = await user_repository.create_user(user_data)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка при створенні користувача"
        )

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    user = await user_repository.get_user_by_username(user_credentials.username)
    
    # Перевіряємо чи існує користувач і чи правильний пароль
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний username або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неактивний користувач"
        )

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(token_request: RefreshTokenRequest):
    username = await verify_token(token_request.refresh_token, "refresh")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалідний refresh токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repository.get_user_by_username(username)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Користувач не знайдений або неактивний",
        )

    new_access_token = create_access_token(data={"sub": user.username})
    
    return Token(
        access_token=new_access_token,
        refresh_token=token_request.refresh_token,
        token_type="bearer"
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )