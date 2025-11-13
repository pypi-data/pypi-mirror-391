from typing import Optional, Any, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup
import re
import json
from requests.exceptions import HTTPError

from .methods import FragmentMethod
from .wallet import WalletClient
from .utils.http_request import http_request
from .errors import (
  FragmentInitError,
  FragmentAPIError,
  FragmentDataSetupError
)

@dataclass
class _Context:
  base_url: str
  cookies: str
  wallet: WalletClient
  ton_rate: Optional[float] = None

class FragmentClient:
  """Client for Fragment API.
  
    Automatically fetches session data during initialization.
  """
  
  def __init__(
    self,
    cookies: str,
    wallet: WalletClient
  ) -> None:
    if cookies is None or wallet is None:
      raise FragmentInitError('cookies and wallet cannot be None')
    
    self._ctx = _Context(base_url='https://fragment.com', cookies=cookies, wallet=wallet)
    self._setup_client_data()
  
  @property
  def stars(self) -> "FragmentStarsAPI":
    from .stars import FragmentStarsAPI
    return FragmentStarsAPI(self)
  
  def _setup_client_data(self) -> None:
    try:
      response = http_request(self._ctx.base_url, method='GET', cookies=self._ctx.cookies)
      html_content = response.text
      
      soup = BeautifulSoup(html_content, 'html.parser')
      script_tags = soup.find_all('script')
      
      if match := re.search(r'ajInit\(({.+?})\);', html_content):
        json_str = match.group(1)
        json_obj = json.loads(json_str)
        api_url = json_obj.get('apiUrl')
        self._ctx.base_url = self._ctx.base_url + api_url
        
        if state := json_obj.get('state'):
          self._ctx.ton_rate = state.get('tonRate')
    except HTTPError as error:
      raise FragmentDataSetupError("Error setting up client data.")
  
  def send_fragment_request(self, method: FragmentMethod, body) -> Tuple[Optional[str], Optional[str]]:
    try:
      response = http_request(
        self._ctx.base_url,
        method='POST',
        body={**body, 'method': method.value},
        cookies=self._ctx.cookies
      )
      data = response.json()
      
      if error := data.get('error'):
        return None, error
      
      return data, None
    except HTTPError as error:
      raise FragmentAPIError("Failed to complete Fragment API request.", str(error))
  
  @property
  def base_url(self) -> str:
    return self._ctx.base_url

  @property
  def ton_rate(self) -> Optional[float]:
    return self._ctx.ton_rate