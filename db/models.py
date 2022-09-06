from sqlalchemy import TIMESTAMP, BigInteger, Column, String, Boolean
from datetime import datetime
from db.base import Base


class User(Base):
    __tablename__ = 'users'
    user_id = Column(BigInteger, primary_key=True)
    user_name = Column(String(32), nullable = True)
    pub_key = Column(String(250), unique = False, nullable = False, default = "0")
    ip = Column(String(20), unique = False, nullable = False, default = "0")
    created_at = Column(TIMESTAMP, default = datetime.now())
    updated_at = Column(TIMESTAMP, default = datetime.now())
    is_baned = Column(Boolean, default = False)
    is_pay = Column(Boolean, default = True)