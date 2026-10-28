# Kairozen Store — Telegram Bot + Mini App

Premium digital-products store: **Telegram Bot** + **Telegram Mini App**.

## Structure
- `premium_shop_bot_v16.py` — Bot + Flask API + Mini App host
- `miniapp/` — Mini App frontend (HTML/CSS/JS)
- `assets/welcome_banner.png` — `/start` banner
- `render.yaml` — Render deploy

## `/start` (strict)
Exactly **one** message:
1. Banner image
2. Welcome caption (Khmer + EN)
3. Single button **Open Mini App** (`web_app`)

## Env
| Key | Required | Note |
|-----|----------|------|
| `BOT_TOKEN` | yes | BotFather |
| `ADMIN_ID` | yes | Your Telegram id |
| `WEBAPP_URL` | yes for Mini App | `https://YOUR.onrender.com` |
| `STORE_NAME` | no | default Kairozen Store |
| `DATA_DIR` | no | default `/var/data` |

## Deploy (Render)
1. Push this repo
2. Blueprint / Web service, start: `python premium_shop_bot_v16.py`
3. Set env vars; Persistent Disk → `/var/data`
4. After deploy set `WEBAPP_URL` to the service URL (HTTPS)
5. BotFather → Bot Settings → Menu Button / Web App optional

## Mini App routes
- `/miniapp/` — UI
- `/api/mini/bootstrap` — products + user (initData verified)
- `/api/mini/order` — create pending order (server-side price)
- `/api/mini/order/<id>` — status

## Payment note
KHQR real payment uses existing ABA / CamRapid logic in the bot when keys are set.
Mini App checkout creates **pending_payment** orders; DEMO QR is shown until provider keys are configured — never marks Paid from a client click alone.

## Local
```bash
pip install -r requirements.txt
export BOT_TOKEN=... ADMIN_ID=... WEBAPP_URL=http://127.0.0.1:8080
python premium_shop_bot_v16.py
```
