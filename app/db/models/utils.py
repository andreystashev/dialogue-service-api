from .history import History
from .jwt_token import JwtToken
from .user import User


def get_models() -> list:
    return [
        History,
        JwtToken,
        User,
    ]


from .base import Base  # noqa: E402


metadata = Base.metadata
