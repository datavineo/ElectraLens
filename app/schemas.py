from pydantic import BaseModel
from typing import Optional


class VoterBase(BaseModel):
    name: str
    age: Optional[int]
    gender: Optional[str]
    constituency: Optional[str]
    booth_no: Optional[str]
    address: Optional[str]
    vote: Optional[bool] = False


class VoterCreate(VoterBase):
    pass


class VoterUpdate(BaseModel):
    name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    constituency: Optional[str]
    booth_no: Optional[str]
    address: Optional[str]
    vote: Optional[bool]


class VoterOut(VoterBase):
    id: int

    class Config:
        orm_mode = True
