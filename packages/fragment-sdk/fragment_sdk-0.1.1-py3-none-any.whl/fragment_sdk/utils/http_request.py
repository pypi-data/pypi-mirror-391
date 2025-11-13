import requests

def http_request(url, method='GET', body=None, cookies=None):
  method = method.upper()
  
  headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cookie": cookies
  }
  
  response = None
  try:
    if method == "GET":
      response = requests.get(url, headers=headers)
    elif method == "POST":
      response = requests.post(url, data=body, headers=headers)
    else:
      raise ValueError('Only POST and GET methods!')
  except requests.exceptions.HTTPError as error:
    raise
  return response