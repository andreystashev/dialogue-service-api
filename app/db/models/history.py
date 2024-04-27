from sqlalchemy import Column, String

from .base import Base
from .mixin import AbstractModel, UserMixinModel


class History(Base, AbstractModel, UserMixinModel):
    __tablename__ = "history"

    dialog_id = Column(String, nullable=False, unique=True)
    prompt = Column(String, nullable=False, index=True)
    result_text = Column(String, nullable=True)
