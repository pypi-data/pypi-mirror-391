import jwt
from datetime import datetime, timedelta
from models.model import Model
import src.properties as properties

class Authentication:
    @staticmethod
    def get_token(user: Model):
        if not user._user:
            raise Exception("[Auth] The provided model is not a user")
        
        payload: dict = user.__dict__
        payload["exp"] = datetime.now() + timedelta(hours=1)

        return jwt.encode(payload, properties.SECRET_KEY, algorithm="HS256")
    
    @staticmethod 
    def verify_token(token: str):
        try:
            return jwt.decode(token, properties.SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            raise Exception("[Auth] Invalid token")
        except jwt.ExpiredSignatureError:
            raise Exception("[Auth] Token expired")
        
    @staticmethod
    def verify_password(password: str, db_password: str):
        return password.strip() == db_password.strip()
