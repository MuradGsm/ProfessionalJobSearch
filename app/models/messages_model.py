from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Index
 
class Message(Base):
    id: Mapped[pk_int]
    chat_id: Mapped[str] = mapped_column(String(100), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    recipient: Mapped["User"] = relationship("User", foreign_keys=[recipient_id], back_populates="received_messages")

    __table_args__ = (
        Index('idx_message_chat', 'chat_id'),
        Index('idx_message_sender', 'sender_id'),
        Index('idx_message_recipient', 'recipient_id'),
        Index('idx_message_unread', 'recipient_id', 'is_read'),
        Index('idx_message_created', 'created_at'),
    )

    @staticmethod
    def generate_chat_id(user1_id: int, user2_id: int) -> str:
        """Generate consistent chat_id for two users"""
        sorted_ids = sorted([user1_id, user2_id])
        return f"chat_{sorted_ids[0]}_{sorted_ids[1]}"

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, chat_id={self.chat_id}, sender_id={self.sender_id})>"