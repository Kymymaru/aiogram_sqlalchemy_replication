from sqlalchemy import Column, Integer, BigInteger, String
from bot.database.models.base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(BigInteger, primary_key=True, unique=True)
    name = Column(String(255))

    def __repr__(self):
        return f'<User>: user_id=[{self.user_id}], name=[{self.name}]'
