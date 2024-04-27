import random
import string


class DomainException(Exception):
    status_code: int = 400
    error_details: str = "unknown domain error"
    error_code: int = 0

    def to_dict(self) -> dict:
        return {
            "status_code": self.status_code,
            "error_details": self.error_details,
            "error_code": self.error_code,
        }

    def uniq_id(self, length: int = 10):
        return "".join(random.choice(string.ascii_lowercase) for _ in range(length))
