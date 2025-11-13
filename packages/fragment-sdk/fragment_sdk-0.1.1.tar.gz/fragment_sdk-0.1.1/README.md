<div align="center">
	<img src="https://raw.githubusercontent.com/whicencer/fragment-sdk/refs/heads/main/logo.png"  alt="Library Logo"  width="100"  height="100">
	<h1  style="margin-top: 24px;">Fragment SDK</h1>
	<div>
		<a href="https://t.me/fragmentsdk">News</a> |
		<a href="https://t.me/fragmentsdk_chat">Telegram Chat</a> |
		<a href="https://t.me/whicencer">Contact developer</a>
	</div>
</div>

---

## 📚 Introduction

**Unofficial Python client for [Fragment](https://fragment.com)** — buy Telegram goods (Stars, Premium, TON) via Fragment

> ⚠️ This library is not affiliated with Telegram or Fragment.  
> Use at your own risk.

## 🚀 Features

> Currently, the library only supports one feature, as it is still under development. The remaining features will be implemented in the very next update.

- Purchase Telegram Stars

-  ~~Purchase Telegram Premium~~

-  ~~Top up Telegram Ads (TON) balance~~

## 📦 Usage

```bash
pip3 install fragment-sdk
```

**Before you start coding, make sure you have:**
- TON wallet (*v4r2* or *v5r1*)
- Fragment account with KYC. Auth cookies string
- [Tonapi.io](https://tonapi.io/) API key

To get auth cookies use [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) extension (Header string).

#### ⭐ Purchase Stars example:  
```py
from fragment_sdk import FragmentClient
from fragment_sdk.wallet import WalletClient
import asyncio

async def main():
  wallet = WalletClient(
    tonapi_key="TONAPI_KEY",
    mnemonic="WORD1 WORD2 WORD3 ...",
    version='v5r1' # v5r1 by default (v4r2 supported)
  )
  fragment = FragmentClient(
    cookies="FRAGMENT_COOKIES_STRING", # Cookies in Header string format.
    wallet=wallet
  )
  
  response = await fragment.stars.buy_stars(username="whicencer", quantity=50)
  
  error = response.error
  tx_hash = response.data
  return tx_hash, error

asyncio.run(main())
```

## 💖 Support the Project
**💎 TON Donations:** `UQCaKFm1d4CavB2aqZK1ypHFaAMIgpAz2D58hDyrT7RITfl2`  
**🌟 Star the repo: it really helps others discover the library**
