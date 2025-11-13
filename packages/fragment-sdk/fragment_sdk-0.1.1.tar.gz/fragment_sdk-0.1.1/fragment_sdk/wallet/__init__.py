import base64
from tonutils.client import TonapiClient
from tonutils.wallet.messages import TransferMessage
from typing import Optional, Any
from ..errors import WalletVersionError

NANO = 1_000_000_000

class WalletClient:
  def __init__(self, tonapi_key, mnemonic, version: str = 'v5r1', is_testnet=False):
    self.api_key = tonapi_key
    self.is_testnet = is_testnet
    self._client = TonapiClient(api_key=self.api_key, is_testnet=self.is_testnet, rps=1)

    if version == 'v5r1':
      from tonutils.wallet import WalletV5R1
      self._wallet, _, _, _ = WalletV5R1.from_mnemonic(
        client=self._client,
        mnemonic=mnemonic
      )
    elif version == 'v4r2':
      from tonutils.wallet import WalletV4R2
      self._wallet, _, _, _ = WalletV4R2.from_mnemonic(
        client=self._client,
        mnemonic=mnemonic
      )
    else:
      raise WalletVersionError("Wrong wallet version specified. Use only v5r1 or v4r2")
  
  @property
  def address(self) -> str:
    """
      Returns user-friendly, non-bouncable wallet address
    """
    return self._wallet.address.to_str(True, True, False)
  
  async def get_balance(self) -> float:
    return await self._wallet.balance()
  
  def get_wallet_data(self) -> dict[str, Any]:
    """
      Returns object that is needed to create a purchase transaction
    """
    boc = self._wallet.state_init.serialize().to_boc()
    return {
      "address": self.address,
      "chain": "-239",
      "walletStateInit": base64.b64encode(boc).decode(),
      "publicKey": self._wallet.public_key.hex()
    }
  
  def _decode_payload(self, payload: str) -> str:
    from tonutils.utils import Slice, Cell
    
    missing_padding = len(payload) % 4
    if missing_padding:
      payload += "=" * (4 - missing_padding)
    
    boc_bytes = base64.b64decode(payload)
    
    cell = Cell.one_from_boc(boc_bytes)
    cs = cell.begin_parse()
    
    op = cs.load_uint(32)
    comment = cs.load_string()
    return comment
  
  async def process_transaction(self, destination: str, amount: str, body: str) -> Optional[str]:
    if not self._wallet:
      raise ValueError("Wallet not connected.")
    
    body = self._decode_payload(body)
    try:
      messages = [
        TransferMessage(
          destination=destination,
          amount=int(amount) / NANO,
          body=body
        )
      ]
      tx_hash = await self._wallet.batch_transfer_messages(messages=messages)
      return tx_hash
    except Exception as error:
      raise Exception(error)