from dataclasses import dataclass, asdict
from typing import List, Any, Generic, Optional, TypeVar

T = TypeVar("T")

class BaseResponseModel:
  def to_dict(self) -> dict[str, Any]:
    return asdict(self)

@dataclass(slots=True)
class ApiResult(Generic[T]):
  success: bool
  data: Optional[T] = None
  error: Optional[str] = None
  
  @classmethod
  def ok(cls, data: T) -> "ApiResult[T]":
    return cls(success=True, data=data)

  @classmethod
  def fail(cls, error: str) -> "ApiResult[T]":
    return cls(success=False, error=error)

  def __bool__(self) -> bool:
    return self.success

@dataclass
class InitBuyStarsResponseData(BaseResponseModel):
  req_id: str
  to_bot: bool
  amount: str

@dataclass
class BuyStarsTxMessage(BaseResponseModel):
  address: str
  amount: str
  payload: str
@dataclass
class BuyStarsTransaction(BaseResponseModel):
  validUntil: int
  messages: List[BuyStarsTxMessage]

@dataclass
class SearchRecipientResponseData(BaseResponseModel):
  recipient_id: str
  name: str
  photo_url: str | None