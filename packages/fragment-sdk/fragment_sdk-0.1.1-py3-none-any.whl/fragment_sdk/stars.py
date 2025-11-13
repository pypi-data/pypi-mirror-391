from typing import Tuple, Optional, Any
import re
from .client import FragmentClient
from .methods import FragmentMethod
from .errors import StarsOperationError, FragmentAPIError
from .models.stars import (
  ApiResult,
  InitBuyStarsResponseData,
  BuyStarsTransaction,
  BuyStarsTxMessage,
  SearchRecipientResponseData
)

class FragmentStarsAPI:
  def __init__(self, client: FragmentClient) -> None:
    self._client = client
    self._wallet = self._client._ctx.wallet
  
  def _initBuyStarsRequest(self, recipient_id, quantity) -> ApiResult[InitBuyStarsResponseData]:
    try:
      data, error = self._client.send_fragment_request(
        method=FragmentMethod.INIT_BUY_STARS,
        body={ 'recipient': recipient_id, 'quantity': quantity }
      )
      
      if error:
        return ApiResult.fail(f'Failed to initialize Stars purchase: {error}')
      
      return ApiResult.ok(
        data=InitBuyStarsResponseData(
          req_id=str(data["req_id"]),
          to_bot=bool(data["to_bot"]),
          amount=str(data["amount"]),
        )
      )
    except FragmentAPIError as error:
      raise StarsOperationError(f"Failed to initialize Stars purchase: {error}")
  
  def _getBuyStarsLink(self, account, req_id) -> ApiResult[BuyStarsTransaction]:
    try:
      data, error = self._client.send_fragment_request(
        method=FragmentMethod.GET_BUY_STARS_LINK,
        body={
          'account': account,
          'transaction': '1',
          'id': req_id,
          'show_sender': '0'
        }
      )
      
      if error:
        return ApiResult.fail(f'Failed to obtain Stars purchase link:{error}')
      
      if transaction := data.get('transaction'):
        transaction.pop('from', None)
      
      transaction_messages = transaction.get('messages')
      messages = [
        BuyStarsTxMessage(
          address=item.get('address'),
          amount=item.get('amount'),
          payload=item.get('payload')
        )
        for item in transaction_messages
      ]
      
      return ApiResult.ok(
        data=BuyStarsTransaction(
          validUntil=transaction.get('validUntil'),
          messages=messages
        )
      )
    except FragmentAPIError as error:
      raise StarsOperationError(f"Failed to obtain Stars purchase link: {error}")
  
  def search_stars_recipient(self, recipient_username) -> ApiResult[SearchRecipientResponseData]:
    try:
      data, error = self._client.send_fragment_request(
        method=FragmentMethod.SEARCH_STARS_RECIPIENT,
        body={
          'query': recipient_username,
          'quantity': '',
        }
      )
      
      if error:
        return ApiResult.fail(f"Failed to obtain Stars recipient: {error}")
      
      if found := data.get('found'):
        photo = found.get('photo')
        match = re.search(r'src=["\'](.*?)["\']', photo or '')
        photo_src = match.group(1) if match else None
      
      return ApiResult.ok(
        data=SearchRecipientResponseData(
          recipient_id=found.get('recipient'),
          name=found.get('name'),
          photo_url=photo_src
        )
      )
    except FragmentAPIError as error:
      raise StarsOperationError(f"Failed to obtain Stars recipient: {error}")
  
  def create_stars_transaction(self, recipient_id, quantity, wallet_account) -> ApiResult[BuyStarsTransaction]:
    try:
      init_data = self._initBuyStarsRequest(
        recipient_id=recipient_id,
        quantity=quantity
      )
      
      if init_data.error:
        return ApiResult.fail(init_data.error)
      
      buy_transaction = self._getBuyStarsLink(
        account=wallet_account,
        req_id=init_data.data.req_id
      )
      
      if buy_transaction.error:
        return ApiResult.fail(buy_transaction.error)
      
      return ApiResult.ok(data=buy_transaction.data)
    except StarsOperationError:
      raise
  
  async def buy_stars(self, username: str, quantity: int) -> ApiResult[str]:
    try:
      recipient = self.search_stars_recipient(recipient_username=username)
      if recipient.error:
        return ApiResult.fail(recipient.error)
      wallet_account = self._wallet.get_wallet_data()
      transaction = self.create_stars_transaction(recipient_id=recipient.data.recipient_id, quantity=quantity, wallet_account=wallet_account)
      
      if transaction.error:
        return ApiResult.fail(transaction.error)

      transaction_msg = transaction.data.messages[0]
      tx_hash = await self._wallet.process_transaction(
        destination=transaction_msg.address,
        amount=transaction_msg.amount,
        body=transaction_msg.payload
      )
      
      return ApiResult.ok(data=tx_hash)
    except StarsOperationError:
      raise