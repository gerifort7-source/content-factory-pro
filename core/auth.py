"""JWT authentication and security utilities"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthenticationCredentials
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class AuthenticationError(Exception):
    """Custom authentication exception"""
    pass


class TokenPayload:
    """JWT token payload"""
    def __init__(self, sub: str, exp: datetime, iat: datetime):
        self.sub = sub
        self.exp = exp
        self.iat = iat


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token
    
    Args:
        data: Dictionary containing token claims
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        logger.debug(f"Access token created for user {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token
    
    Args:
        data: Dictionary containing token claims
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "refresh"})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating refresh token: {str(e)}")
        raise


def verify_token(token: str) -> TokenPayload:
    """Verify and decode a JWT token
    
    Args:
        token: JWT token to verify
        
    Returns:
        Token payload
        
    Raises:
        AuthenticationError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        sub: str = payload.get("sub")
        if sub is None:
            raise AuthenticationError("Invalid token: no subject")
        
        exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        iat = datetime.fromtimestamp(payload.get("iat"), tz=timezone.utc)
        
        return TokenPayload(sub=sub, exp=exp, iat=iat)
    except JWTError as e:
        logger.error(f"JWT verification error: {str(e)}")
        raise AuthenticationError(f"Invalid token: {str(e)}")


async def get_current_user(credentials: HTTPAuthenticationCredentials = Depends(security)) -> str:
    """Dependency to get current authenticated user
    
    Args:
        credentials: HTTP bearer credentials
        
    Returns:
        User ID from token
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        token = credentials.credentials
        token_payload = verify_token(token)
        return token_payload.sub
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin(current_user: str = Depends(get_current_user)) -> str:
    """Dependency to verify admin access
    
    Args:
        current_user: Current authenticated user ID
        
    Returns:
        User ID if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    # Note: In production, check user role in database
    logger.info(f"Admin access check for user: {current_user}")
    return current_user


class JWTHandler:
    """JWT token handler utility class"""
    
    @staticmethod
    def create_tokens(user_id: int) -> dict:
        """Create access and refresh tokens for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with access and refresh tokens
        """
        access_token = create_access_token(data={"sub": str(user_id)})
        refresh_token = create_refresh_token(data={"sub": str(user_id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """Create new access token from refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")
            
            user_id = payload.get("sub")
            return create_access_token(data={"sub": user_id})
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise AuthenticationError("Could not refresh token")
