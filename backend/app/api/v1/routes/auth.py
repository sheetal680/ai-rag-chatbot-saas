from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.user import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.services.auth_service import get_user_by_id, login_user, register_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201, summary="Create a new account")
async def register(data: UserCreate) -> TokenResponse:
    try:
        return await register_user(data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/login", response_model=TokenResponse, summary="Sign in and receive a token")
async def login(data: LoginRequest) -> TokenResponse:
    try:
        return await login_user(data.email, data.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.get("/me", response_model=UserResponse, summary="Return the authenticated user's profile")
async def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    user = await get_user_by_id(current_user["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.post("/logout", status_code=204, summary="Sign out (client-side token deletion)")
async def logout() -> None:
    # JWT is stateless — actual invalidation requires a token blocklist.
    # For MVP, the client simply deletes the stored token.
    return None
