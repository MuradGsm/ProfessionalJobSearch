from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy import Enum 

class UserRole(str, Enum):
    candidate = "candidate"
    employer = "employer"

class User(Base):
    id: Mapped[pk_int]
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"