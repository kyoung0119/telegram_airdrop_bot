from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime


class User(BaseModel):
    id: int
    name: str
    username: Optional[str] = None
    date: datetime
    balance: int = 0
    withdrawn: int = 0
    invited_by: Optional[int] = None
    invited_users: List[int] = []
    is_admin: bool = False
    is_banned: bool = False
    is_approved: bool = False

    @property
    def mention(self) -> str:
        return f"[{self.name}](tg://user?id={self.id})"

    @property
    def invited_count(self) -> int:
        return len(self.invited_users)

    @property
    def balance_text(self) -> str:
        return f"{self.balance:,} $SCOT"


class Verification(BaseModel):
    id: int
    picture: str
    date: datetime
    user_id: int
    status: Literal["pending", "approved", "rejected"]
