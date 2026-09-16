from fastapi import APIRouter, HTTPException, status, Depends
import bcrypt
from datetime import timedelta
from app.schemas.auth import UserSignup, UserResponse, UserLogin, LoginResponse
from app.models.user import UserModel
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    pwd_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserSignup, db=Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available")
        
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    # Hash password
    password_hash = get_password_hash(user_in.password)
    
    # Create user model
    new_user = UserModel(
        full_name=user_in.full_name,
        email=user_in.email,
        password_hash=password_hash
    )
    
    # Insert to db
    result = await db.users.insert_one(new_user.model_dump())
    
    # Prepare response
    return UserResponse(
        id=str(result.inserted_id),
        full_name=new_user.full_name,
        email=new_user.email,
        created_at=new_user.created_at
    )

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(user_credentials: UserLogin, db=Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available")
        
    user = await db.users.find_one({"email": user_credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    if not verify_password(user_credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"])}, expires_delta=access_token_expires
    )
        
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=str(user["_id"]),
            full_name=user["full_name"],
            email=user["email"],
            created_at=user["created_at"]
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    return current_user
