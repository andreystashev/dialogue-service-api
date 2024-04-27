from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime


class IdentityMixinModel:
    id = Column(BigInteger, primary_key=True, index=True)


class CreatedAtMixinModel:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserMixinModel:
    user_id = Column(BigInteger, nullable=True)


class AbstractModel(IdentityMixinModel, CreatedAtMixinModel):
    pass
