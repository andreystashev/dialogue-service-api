import datetime

from sqlalchemy import Boolean, Column, DateTime, Text

from .base import Base
from .mixin import AbstractModel, UserMixinModel


class JwtToken(Base, AbstractModel, UserMixinModel):
    __tablename__ = "jwt_token"
    token = Column(Text, nullable=False)
    expires = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Token id={self.id!r}, token={self.token!r}, is_active={self.is_active!r}, expires={self.expires!r} >"
