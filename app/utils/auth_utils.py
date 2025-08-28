import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app
from app import db
from app.models import User

class AuthUtils:
    """
    utility class for generating and verifying JWT tokens
    """
    @staticmethod
    def generate_token(user_id, expires_in=3600):
        payload = {
            "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
            "iat": datetime.now(timezone.utc),
            "sub": str(user_id)
        }
        return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")
    
    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            return int(payload["sub"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.DecodeError:
            return None
        except jwt.InvalidTokenError:
            return None
        
    @staticmethod
    def get_user_from_token(token):
        user_id = AuthUtils.verify_token(token)
        if user_id:
            return db.session.get(User, user_id)
        return None
