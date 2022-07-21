
from sqlalchemy import TIMESTAMP, BigInteger, Column, String, Boolean
from datetime import datetime
from .base import Base


class User(Base):
    __tablename__ = 'users'
    user_id = Column(BigInteger, primary_key=True)
    user_name = Column(String(32), nullable = True) # может быть VARCHAR
    full_name = Column(String(250), nullable = True)
    pub_key = Column(String(250), unique = True, nullable = False, default = "0")
    ip = Column(String(20), unique = True, nullable = False, default = "0")
    created_at = Column(TIMESTAMP, default = datetime.now())
    updated_at = Column(TIMESTAMP, default = datetime.now())
    is_baned = Column(Boolean, default = False)

    def __str__(self) -> str:
        return f"<User:{self.user_id}>"
