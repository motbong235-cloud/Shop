# -*- coding: utf-8 -*-
"""
Kairozen Premium Account Shop Bot — CLASSIC (bot ធម្មតា, គ្មាន Mini App) [v16]
----------------------------------
លក់ account premium (ChatGPT, Netflix, Spotify, Office365, Canva ...) តាម Telegram
- Stock គ្រប់គ្រងតាមឯកសារ .txt (មួយបន្ទាត់ = account មួយ)
- ប្រព័ន្ធ Wallet (deposit លុយចូល -> ទិញអីវ៉ាន់ចេញ)
- KHQR deposit តាម CamRapidPay + auto-polling (ឬ QR ដោយដៃ បើគ្មាន Bakong ID)
- Admin panel ក្នុង Telegram ទាំងស្រុង (reply keyboard + inline button, គ្មាន Mini App)
- Premium Emoji System (ស្រេចចិត្ត, /setupemoji, ត្រូវការ Telegram Premium)

ត្រូវការ Environment Variables:
  BOT_TOKEN            - Telegram Bot Token
  ADMIN_ID             - Telegram user id របស់ admin (លេខ)
  CAMRAPIDPAY_API_KEY  - API key របស់ CamRapidPay (ចាំបាច់សម្រាប់ deposit តាម Bakong KHQR)
  CAMRAPID_CREATE_URL / CAMRAPID_CHECK_URL / PUBLIC_BASE_URL - កំណត់ webhook_url សម្រាប់ CamRapidPay

ចំណាំ (v15 — Classic): កំណែនេះកែចេញពី v14 ដោយ (1) លុប Mini App (miniapp.html, web_app
  button, /api/* Flask routes, initData verification, review/promo system) ព្រោះឥឡូវ
  ប្រើ bot តាម reply keyboard + inline button ធម្មតាទាំងស្រុង — /start ឥឡូវបង្ហាញម៉ឺនុយពេញ
  (reply keyboard) ផ្ទាល់មិនចាំបាច់ចុចចូល Mini App ទៀតទេ។ (2) លុប ប្រព័ន្ធ ណែនាំមិត្ត
  (Referral: referred_by/ref_count/ref_earned/credit_referral_commission/REFERRAL_PERCENT)
  និង ជាវ Bot ផ្ទាល់ខ្លួន (Subscriber clone deploy engine: SUBS_FILE, deploy_subscriber_bot,
  /subscribe, /activatesub, /stopsub, /subs, /setrentalprice) ទាំងស្រុង ព្រោះលែងប្រើហើយ។
  មុខងារផ្សេងទៀត (wallet, deposit KHQR/QR ដោយដៃ, stock, broadcast, premium emoji) នៅតែ
  ដំណើរការដូចដើមទាំងអស់។

ចំណាំ (v16): បន្ថែម product ប្រភេទ "📧 Email (Admin ដាក់ដោយដៃ)" ជាជម្រើសទី ២ ក្នុងពេល
  ➕ Product ថ្មី (ក្រៅពី 📦 Stock file auto ដូចមុន)។ ប្រភេទនេះមិនប្រើ stock .txt ទេ —
  user ទិញរួច ត្រូវផ្ញើ email គេផ្ទាល់ជូន bot, admin ទទួលសារជូនដំណឹងភ្លាមៗ (ជាមួយ
  ប៊ូតុង ✅ រួចរាល់ / ❌ បដិសេធ), ដាក់ Premium/Invite ចូល email នោះដោយដៃ រួចចុច
  '✅ រួចរាល់' ដើម្បីជូនដំណឹងទៅ user ស្វ័យប្រវត្តិ (ឬចុច '❌ បដិសេធ' ដើម្បីសងលុយត្រឡប់
  ចូល wallet វិញ)។ Order ទាំងនេះរក្សាទុកក្នុង pending_email_orders.json ដាច់ដោយឡែក។
  បន្ថែម: product នីមួយៗឥឡូវអាចមាន 🖼 រូបភាព និង 📝 Description (កំណត់ពេលបន្ថែម
  product ថ្មី ជំហានទី ៥-៦, ឬកែពេលក្រោយតាម ✏️ កែ Product -> 🖼 កែ រូបភាព / 📝 កែ
  Description)។ ពេល user ចុចមើល product ណាមួយក្នុងហាង bot នឹងបង្ហាញរូបភាព (បើមាន)
  + description + តម្លៃ + ស្តុក ជាមុនសិន រួចមានប៊ូតុង '✅ ទិញឥឡូវ' ដើម្បីបន្ត។
"""

import os
import re
import io
import html
import json
import time
import hashlib
import threading
import requests
import telebot
from telebot import types

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
CAMRAPIDPAY_API_KEY = os.environ.get("CAMRAPIDPAY_API_KEY", "")
CAMRAPID_CREATE = os.environ.get("CAMRAPID_CREATE_URL", "https://pay.camrapidpay.com/api/v1/khqr/create-payments")
CAMRAPID_CHECK = os.environ.get("CAMRAPID_CHECK_URL", "https://pay.camrapidpay.com/check-transaction-api")
# Render ដាក់ RENDER_EXTERNAL_URL ស្វ័យប្រវត្តិ (ឧ. https://your-app.onrender.com)។
# បើគ្មាន អាចកំណត់ PUBLIC_BASE_URL ដោយដៃ។ ត្រូវការសម្រាប់ webhook_url ដែល CamRapidPay តម្រូវ។
PUBLIC_BASE_URL = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("PUBLIC_BASE_URL", "")
CAMRAPID_WEBHOOK_URL = os.environ.get(
    "CAMRAPID_WEBHOOK_URL",
    f"{PUBLIC_BASE_URL.rstrip('/')}/camrapid-webhook" if PUBLIC_BASE_URL else "",
)
STORE_NAME = os.environ.get("STORE_NAME", "Kairozen Store")  # ឈ្មោះហាង — hardcode ជា default តែអាច override តាម env
# ID របស់ channel/group ដែលចង់ឲ្យ bot ផ្ញើសារជូនដំណឹងស្វ័យប្រវត្តិ ពេលមាន deposit
# ឬ order ជោគជ័យ។ ដាក់ hardcode ត្រង់នេះផ្ទាល់ (negative number ឧ. -1001234567890
# សម្រាប់ channel/supergroup) — អាចដាក់ច្រើនក្នុងមួយ list បាន ១ សម្រាប់ channel ១ សម្រាប់ group។
# ចាំបាច់: bot ត្រូវជា admin (មាន permission ផ្ញើសារ) នៅក្នុង channel/group នោះជាមុនសិន។
_NOTIFY_CHAT_IDS_ENV = os.environ.get("NOTIFY_CHAT_IDS")
if _NOTIFY_CHAT_IDS_ENV is not None:
    NOTIFY_CHAT_IDS = [
        int(x.strip()) for x in _NOTIFY_CHAT_IDS_ENV.split(",") if x.strip()
    ]
else:
    NOTIFY_CHAT_IDS = [
        # -1001234567890,   # <- ដាក់ ID channel/group នៅទីនេះ បើមាន
    ]

# ពេលស្តុក product មួយធ្លាក់មកដល់ចំនួននេះ ឬតិចជាងនេះ (ប៉ុន្តែមិនទាន់អស់ស្រុង) bot នឹងផ្ញើសារ
# ជូនដំណឹងទៅ user គ្រប់គ្នា ដើម្បីជំរុញឲ្យទិញឲ្យឆាប់មុនអស់ស្តុក (មួយដងក្នុងមួយជុំស្តុក —
# reset ស្វ័យប្រវត្តិពេល admin បញ្ចូល stock ថ្មី)។ អាចកែបានតាម Env Var LOW_STOCK_THRESHOLD
LOW_STOCK_THRESHOLD = int(os.environ.get("LOW_STOCK_THRESHOLD", "3"))

# ត្រូវការ Render Persistent Disk mount នៅ path នេះ (Render Dashboard -> service
# -> Disks -> Add Disk -> Mount Path = /var/data) បើមិនដូច្នេះទេ data នៅតែបាត់ពេល
# deploy ដដែល ព្រោះ local filesystem ធម្មតារបស់ Render ជា ephemeral (reset រាល់
# deploy)។ អាចប្តូរ path តាមចិត្តតាម env var DATA_DIR បើចង់ mount ត្រង់ផ្សេង។
DATA_DIR = os.environ.get("DATA_DIR", "/var/data")
try:
    os.makedirs(DATA_DIR, exist_ok=True)
except PermissionError:
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
STOCK_DIR = os.path.join(DATA_DIR, "stock")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
EMOJI_FILE = os.path.join(DATA_DIR, "premium_emoji.json")
# ករណីហាង/subscriber គ្មាន Bakong ID ផ្ទាល់ខ្លួន (គ្មាន CAMRAPIDPAY_API_KEY) — deposit នឹងប្រើ
# QR ផ្ទាល់ខ្លួនដែល admin កំណត់ដោយដៃ (មិនមែន QR របស់ហាងមេ) រួច user ត្រូវផ្ញើវិក័យប័ត្រ/screenshot
# មកឲ្យ admin ត្រួតពិនិត្យ + បញ្ចូលលុយឲ្យដោយដៃ (មិនមែន auto-detect ដូច Bakong ទេ)
PAYMENT_CONFIG_FILE = os.path.join(DATA_DIR, "payment_config.json")
PENDING_DEPOSITS_FILE = os.path.join(DATA_DIR, "pending_deposits.json")
# ករណី product ប្រភេទ "email" (មិនមែនចែក account ពី stock file ទេ) — pending
# រហូតដល់ admin ដាក់ Premium ចូល email របស់ user ដោយផ្ទាល់ រួចចុច 'រួចរាល់'
PENDING_EMAIL_ORDERS_FILE = os.path.join(DATA_DIR, "pending_email_orders.json")
os.makedirs(STOCK_DIR, exist_ok=True)


def notify_admin_error(context, exception):
    """ផ្ញើសារ error ទៅ ADMIN_ID ដោយផ្ទាល់ (មិនចាំបាច់ NOTIFY_CHAT_IDS) ពេលមាន
    unhandled exception កើតឡើងកន្លែងណាមួយក្នុង bot — ជួយ admin ដឹងភ្លាមៗ មិនចាំបាច់
    មើល Render logs ចាំម្តងៗទេ។ បរាជ័យស្ងាត់ៗបើផ្ញើមិនចេញ (ឧ. admin block bot)"""
    if not ADMIN_ID:
        return
    err_text = f"{type(exception).__name__}: {exception}"
    # error ធម្មតា មិនប៉ះពាល់ (ឧ. ចុច button ២ដងលឿន, edit message ដដែល) —
    # គ្រាន់តែ log ចោល កុំរំខាន admin ដោយមិនចាំបាច់
    _BENIGN_MARKERS = (
        "message is not modified",
        "query is too old",
        "message to edit not found",
        "message can't be edited",
        "bot was blocked by the user",
        "user is deactivated",
    )
    if any(m in err_text.lower() for m in _BENIGN_MARKERS):
        return
    try:
        if len(err_text) > 500:
            err_text = err_text[:500] + "…"
        bot.send_message(
            ADMIN_ID,
            f"🚨 <b>Bot Error</b>\n"
            f"📍 កន្លែង: <code>{html.escape(context)}</code>\n"
            f"⚠️ <code>{html.escape(err_text)}</code>",
        )
    except Exception:
        pass


class _LoggingExceptionHandler(telebot.ExceptionHandler):
    """បើគ្មាន handler នេះ pyTelegramBotAPI នឹងលេប exception ចោលស្ងាត់ៗ ពេល handler
    ណាមួយ crash — user ចុច button ហើយគ្មានអ្វីកើតឡើងសោះ គ្មាន log អោយឃើញមូលហេតុ។
    handler នេះធ្វើឲ្យ error print ចេញ terminal/Render logs ជានិច្ច ហើយ bot បន្តដំណើរការ
    ធម្មតាសម្រាប់ update បន្ទាប់ — ព្រមទាំងជូនដំណឹងទៅ admin ដោយស្វ័យប្រវត្តិ។"""
    def handle(self, exception):
        import traceback
        print("[UNHANDLED EXCEPTION]", flush=True)
        traceback.print_exc()
        notify_admin_error("message/callback handler", exception)
        return True


bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML", exception_handler=_LoggingExceptionHandler())


def public_user_label(user):
    """label សម្រាប់បង្ហាញជាសាធារណៈក្នុង channel/group — ប្រើ @username បើមាន
    ឬ first_name បើគ្មាន username (កុំបង្ហាញ user id ពេញលេញជាសាធារណៈ)"""
    if not user:
        return "User"
    username = getattr(user, "username", None)
    if username:
        return f"@{username}"
    return getattr(user, "first_name", None) or "User"


def notify_public(text):
    """ផ្ញើសារទៅ channel/group ទាំងអស់ (hardcode + admin-added តាម /setnotify) — ឧ. deposit/order ជោគជ័យ"""
    chat_ids = get_notify_chat_ids()
    if not chat_ids:
        return
    for cid in chat_ids:
        try:
            bot.send_message(cid, text)
        except Exception as e:
            print(f"[notify_public] failed to send to {cid}: {e}", flush=True)


def resolve_icon(icon):
    """Icon ជា emoji glyph ធម្មតា (admin វាយបញ្ចូលផ្ទាល់ពេលបន្ថែម product) — return
    default 📦 បើគ្មាន icon កំណត់"""
    return icon or "📦"


# ------------------------------------------------------------------
# PREMIUM EMOJI SYSTEM (Bot API 9.4+, ត្រូវការ Telegram Premium)
# ------------------------------------------------------------------
# admin ភ្ជាប់ custom_emoji_id មួយ ទៅនឹង glyph unicode មួយ (ឧ. ✅) ដងតែម្តង
# ចាប់ពីនោះ glyph នេះនៅត្រង់ណាក៏ដោយ (ប៊ូតុង ឬ អត្ថបទសារ) នឹងបង្ហាញ icon premium
# ដោយស្វ័យប្រវត្តិ — emoji ធម្មតានៅតែមាន មិនត្រូវជំនួសទេ។
EMOJI_CATEGORIES = [
    ("✅", "✅ ជោគជ័យ / ទិញ / បញ្ជាក់"),
    ("❌", "❌ បោះបង់ / លុប / អស់ស្តុក"),
    ("🔙", "🔙 ត្រឡប់ក្រោយ"),
    ("➕", "➕ បន្ថែម"),
    ("➖", "➖ បន្ថយ (ចំនួន)"),
    ("📦", "📦 ផលិតផល"),
    ("📊", "📊 ស្ថិតិ"),
    ("💰", "💰 កាបូបលុយ"),
    ("💵", "💵 តម្លៃ/ប្រាក់"),
    ("💳", "💳 ការទូទាត់"),
    ("🛒", "🛒 ទិញ Account"),
    ("🛍", "🛍 ការទិញ"),
    ("📥", "📥 Stock"),
    ("🗑", "🗑 លុប"),
    ("🔑", "🔑 Account/Key"),
    ("🔖", "🔖 លេខយោង Ref"),
    ("⏳", "⏳ កំពុងរង់ចាំ"),
    ("⌛", "⌛ ផុតកំណត់"),
    ("⚠️", "⚠️ ប្រុងប្រយ័ត្ន"),
    ("🚨", "🚨 បន្ទាន់ (Admin alert)"),
    ("🚫", "🚫 បដិសេធ/បិទ"),
    ("🔔", "🔔 ជូនដំណឹង"),
    ("📢", "📢 Broadcast"),
    ("📨", "📨 សំណើ/សារ"),
    ("🔁", "🔁 ព្យាយាមម្តងទៀត"),
    ("☎️", "☎️ ទំនាក់ទំនង"),
    ("👉", "👉 ចង្អុលបង្ហាញ"),
    ("👋", "👋 សួស្តី"),
    ("👥", "👥 អ្នកប្រើប្រាស់"),
    ("🏠", "🏠 ម៉ឺនុយចម្បង"),
    ("⚡", "⚡ ទូទាត់ភ្លាមៗ (KHQR)"),
    ("📱", "📱 ស្កេន QR"),
    ("🎭", "🎭 Setup Emoji"),
    ("✏️", "✏️ កែ/បញ្ចូលព័ត៌មាន"),
    ("🎉", "🎉 អបអរ/Bonus"),
    ("👤", "👤 អ្នកប្រើប្រាស់ម្នាក់"),
    ("📈", "📈 ស្ថិតិលក់ដាច់ / តម្លៃឡើង"),
    ("📉", "📉 តម្លៃចុះ / បញ្ចុះតម្លៃ"),
    ("📭", "📭 អស់ស្តុក (empty)"),
    ("ℹ️", "ℹ️ ព័ត៌មាន"),
    ("🔎", "🔎 ស្វែងរក/Debug"),
    ("✨", "✨ ការណែនាំ/Tips"),
    ("🙏", "🙏 អរគុណ"),
    ("🤖", "🤖 ChatGPT (icon product)"),
    ("🎬", "🎬 Netflix (icon product)"),
    ("🎧", "🎧 Spotify (icon product)"),
    ("📘", "📘 Office 365 (icon product)"),
    ("🎨", "🎨 Canva (icon product)"),
    ("🏦", "🏦 ធនាគារ/ABA"),
    ("★", "★ Premium badge"),
    ("🖼", "🖼 QR / រូបភាព"),
    ("📋", "📋 ព័ត៌មានគណនី"),
    ("📖", "📖 មុខងារ/ម៉ឺនុយ"),
    ("💬", "💬 សារ/ចុចប៊ូតុង"),
    ("📧", "📧 Email (Delivery)"),
    ("📝", "📝 Description"),
    ("📸", "📸 Screenshot/Receipt"),
    ("📍", "📍 កន្លែង (Log/Context)"),
    ("🔄", "🔄 Refresh ម៉ឺនុយ"),
    ("🔗", "🔗 តំណ/Link"),
    ("📮", "📮 Delivery Label"),
    ("📌", "📌 ការណែនាំ (Pin)"),
]


def get_emoji_map():
    return _load(EMOJI_FILE, {})


def save_emoji_map(m):
    _save(EMOJI_FILE, m)


def premium_text(text):
    """ជំនួស glyph ធម្មតា (ឧ. ✅) ដោយ HTML <tg-emoji> tag បើមាន custom_emoji_id
    កំណត់ទុករួច។ ប្រើ placeholder token ជាមុនសិន រួច replace ត្រឡប់ជា HTML នៅចុងក្រោយតែម្តង
    ដើម្បីកុំឲ្យវគ្គបន្ទាប់ replace ត្រូវលើ tag ដែលបានបញ្ចូលរួច (ជៀសវាង nested/broken tag)។"""
    if not text:
        return text
    m = get_emoji_map()
    if not m:
        return text
    items = sorted(m.items(), key=lambda kv: len(kv[0]), reverse=True)
    placeholders = {}
    for i, (glyph, info) in enumerate(items):
        icon_id = info.get("custom_emoji_id")
        if not icon_id or not glyph or glyph not in text:
            continue
        token = f"\x00PE{i}\x00"
        text = text.replace(glyph, token)
        placeholders[token] = f'<tg-emoji emoji-id="{icon_id}">{glyph}</tg-emoji>'
    for token, tag_html in placeholders.items():
        text = text.replace(token, tag_html)
    return text


def emoji_icon_for(text):
    """រកមើលថាតើ text (ជាធម្មតាជា label ប៊ូតុង) មាន glyph ណាមួយដែលកំណត់ icon រួច
    — return (glyph, custom_emoji_id) ដំបូងដែលរកឃើញ, ឬ (None, None) បើគ្មាន"""
    m = get_emoji_map()
    if not m:
        return None, None
    for glyph in sorted(m.keys(), key=len, reverse=True):
        if glyph and glyph in text:
            icon_id = m[glyph].get("custom_emoji_id")
            if icon_id:
                return glyph, icon_id
    return None, None


def _strip_glyph(text, glyph):
    """លុប glyph ធម្មតាចេញពី label (ព្រោះ icon premium បង្ហាញជំនួសរួចហើយ) — បើលុបហើយ
    label ក្លាយជាទទេ (ឧ. ប៊ូតុងជា glyph តែឯង) រក្សា text ដើមទុក ដើម្បីកុំឲ្យ Telegram
    បដិសេធ button text ទទេ។"""
    cleaned = text.replace(glyph, "", 1)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if cleaned else text


_pbtn_debug = {"last_reason": None, "icon_attempted": 0, "icon_sent": 0, "style_attempted": 0}

# --- Force-inject style/icon_custom_emoji_id ចូល JSON ជានិច្ច ---
# មូលហេតុ: pyTelegramBotAPI version ខ្លះ *ទទួល* style=/icon_custom_emoji_id= ក្នុង
# constructor បាន (គ្មាន TypeError) ប៉ុន្តែ to_dict()/to_dic() របស់ class មិនទាន់ដឹងថា
# ត្រូវដាក់ field ថ្មីនេះចូល JSON ផ្ញើទៅ Telegram ដែរ — លទ្ធផលគឺ button ផ្ញើចេញដោយជោគជ័យ
# (គ្មាន error) ប៉ុន្តែ Telegram មិនដែលឃើញ style សោះ ដូច្នេះមិនបង្ហាញពណ៌។ ដើម្បីជៀសវាង
# បញ្ហានេះទាំងស្រុង យើង monkey-patch to_dict/to_dic ថែមមួយជាន់ ដើម្បីបង្ខំចាក់ field ទាំងនេះ
# ចូល dict ជានិច្ច បើ button object មាន attribute _pbtn_style/_pbtn_icon_id ដែលយើងកំណត់ដោយផ្ទាល់
# (មិនអាស្រ័យលើថាតើ constructor ឬ to_dict ដើមស្គាល់ field នេះឬអត់ទេ)។
# អនុវត្តលើ *ទាំង 2 ប្រភេទ button*: InlineKeyboardButton (ប៊ូតុងភ្ជាប់នឹងសារ) និង
# KeyboardButton (ប៊ូតុងម៉ឺនុយខាងក្រោមអេក្រង់ — reply keyboard ដែលមាននៅជាប់ជានិច្ច)។
def _patch_button_serialize(cls):
    for _m in ("to_dict", "to_dic"):
        if hasattr(cls, _m):
            _orig = getattr(cls, _m)

            def _make_patched(orig):
                def _patched(self):
                    d = orig(self)
                    extra_style = getattr(self, "_pbtn_style", None)
                    extra_icon = getattr(self, "_pbtn_icon_id", None)
                    if extra_style and not d.get("style"):
                        d["style"] = extra_style
                    if extra_icon and not d.get("icon_custom_emoji_id"):
                        d["icon_custom_emoji_id"] = extra_icon
                    return d
                return _patched

            setattr(cls, _m, _make_patched(_orig))


_patch_button_serialize(types.InlineKeyboardButton)
_patch_button_serialize(types.KeyboardButton)


def _build_styled_button(cls, text, style, icon_id, clean_text, use_text, **kw):
    try:
        btn = cls(use_text, **kw)
    except TypeError as e:
        _pbtn_debug["last_reason"] = f"TypeError លើ constructor មូលដ្ឋាន ({cls.__name__}): {e}"
        print(f"[pbtn] {_pbtn_debug['last_reason']}", flush=True)
        return cls(text, **kw)
    if style:
        btn._pbtn_style = style
        _pbtn_debug["style_attempted"] += 1
    if icon_id:
        btn._pbtn_icon_id = icon_id
        _pbtn_debug["icon_attempted"] += 1
        _pbtn_debug["icon_sent"] += 1
        _pbtn_debug["last_reason"] = "ok (force-injected)"
    return btn


def pbtn(text, callback_data=None, style=None, url=None, **kw):
    """InlineKeyboardButton (ប៊ូតុងភ្ជាប់នឹងសារ) ជាមួយ icon premium (បើមាន) + style ពណ៌
    (Bot API 9.4: success/danger/primary)។ បង្ខំដាក់ style/icon_custom_emoji_id ចូល JSON
    ជានិច្ច (មើល _patch_button_serialize ខាងលើ)។"""
    glyph, icon_id = emoji_icon_for(text)
    clean_text = _strip_glyph(text, glyph) if glyph else text
    use_text = clean_text if icon_id else text
    return _build_styled_button(
        types.InlineKeyboardButton, text, style, icon_id, clean_text, use_text,
        callback_data=callback_data, url=url, **kw,
    )


def kbtn(text, style=None, **kw):
    """KeyboardButton (ប៊ូតុងម៉ឺនុយខាងក្រោមអេក្រង់ — reply keyboard ដែលនៅជាប់ជានិច្ច) ជាមួយ
    icon premium (បើមាន) + style ពណ៌ ដូច pbtn() ដែរ តែសម្រាប់ ReplyKeyboardMarkup ជំនួសឲ្យ
    InlineKeyboardMarkup។ ប្រើ kb.add(kbtn(BTN_SHOP, style=\"success\")) ជំនួស kb.add(BTN_SHOP)។"""
    glyph, icon_id = emoji_icon_for(text)
    clean_text = _strip_glyph(text, glyph) if glyph else text
    use_text = clean_text if icon_id else text
    return _build_styled_button(
        types.KeyboardButton, text, style, icon_id, clean_text, use_text, **kw,
    )


@bot.message_handler(commands=["checkemoji"])
def cmd_checkemoji(message):
    """Diagnostic command សម្រាប់ admin — មើលថាហេតុអ្វី icon premium មិនបង្ហាញលើ button។"""
    if not is_admin(message.from_user.id):
        return
    tb_version = getattr(telebot, "__version__", "មិនស្គាល់")
    m = get_emoji_map()
    lines = [
        "🔎 <b>Checkemoji Diagnostic</b>",
        f"📦 pyTelegramBotAPI version: <code>{tb_version}</code>",
        f"🎭 Glyph ដែលបានកំណត់ icon premium: {len(m)}",
        f"🔁 pbtn() ព្យាយាមភ្ជាប់ icon: {_pbtn_debug['icon_attempted']} ដង, ជោគជ័យ (library level): {_pbtn_debug['icon_sent']} ដង",
        f"🎨 pbtn() ព្យាយាមភ្ជាប់ style ពណ៌: {_pbtn_debug['style_attempted']} ដង (បង្ខំចាក់ចូល JSON ដោយ to_dict monkey-patch)",
        f"📝 មូលហេតុចុងក្រោយ: <code>{html.escape(str(_pbtn_debug['last_reason']))}</code>",
        "",
        "⚠️ <b>លក្ខខណ្ឌចាំបាច់ពី Telegram (server-side, code នេះមិនអាចត្រួតពិនិត្យបាន):</b>",
        "• គណនីដែល <b>បង្កើត bot តាម @BotFather</b> (bot owner) ត្រូវមាន Telegram Premium សកម្ម — "
        "មិនមែន admin ដែលចុច /setupemoji ទេ (បើ 2 នាក់ខុសគ្នា)",
        "• ឬ bot បានទិញ username បន្ថែមតាម Fragment",
        "• Icon លើ button បង្ហាញតែក្នុងសារដែល bot ផ្ញើផ្ទាល់ទៅ private/group/supergroup ប៉ុណ្ណោះ",
        "• library ចាស់ (TypeError ខាងលើ) → <code>pip install -U pyTelegramBotAPI</code> រួច deploy ម្តងទៀត",
        "",
        "🎨 <b>ចំណាំ៖</b> ពណ៌ button (<code>style</code>: primary/success/danger) មិនតម្រូវ Telegram "
        "Premium ទេ — ត្រូវការតែ library ថ្មីគ្រប់គ្រាន់ និង Telegram app ថ្មីរបស់ user ប៉ុណ្ណោះ។",
    ]
    bot.reply_to(message, "\n".join(lines))


def norm_label(text):
    """ត្រឡប់ text ដូចគ្នានឹងអ្វីដែល pbtn() ពិតជាផ្ញើទៅ Telegram (បើ glyph មាន premium
    icon រួច នឹងលុប glyph ធម្មតាចេញ ដូច _strip_glyph ធ្វើ)។ ត្រូវប្រើ function នេះទាំងសងខាង
    ពេលប្រៀបធៀប m.text == BTN_XXX ដើម្បីកុំឲ្យ button ដាច់ការងារពេលកំណត់ premium emoji ថ្មី។"""
    if not text:
        return text
    glyph, icon_id = emoji_icon_for(text)
    if glyph and icon_id:
        return _strip_glyph(text, glyph)
    return text


# --- Auto-apply premium_text() លើសារគ្រប់ប្រភេទដែល bot ផ្ញើ ---
# Monkey-patch send_message / reply_to / edit_message_text / edit_message_caption /
# send_photo/video/document(caption) ដើម្បីកុំបំបែក code ចាស់ៗនៅកន្លែងផ្សេងទៀត — គ្រប់
# bot.send_message(...) ដែលមានស្រាប់ នៅតែដំណើរការធម្មតា ប៉ុន្តែ glyph ណាដែលកំណត់ icon
# premium រួច នឹងបង្ហាញស្វ័យប្រវត្តិ។
_orig_send_message = bot.send_message
_orig_reply_to = bot.reply_to
_orig_edit_message_text = bot.edit_message_text
_orig_edit_message_caption = bot.edit_message_caption
_orig_send_photo = bot.send_photo
_orig_send_video = bot.send_video
_orig_send_document = bot.send_document


def _is_entity_parse_error(exc):
    """រកមើលថាតើ exception នេះទាក់ទងនឹង tg-emoji/entity ដែរឬអត់ (ឧ. "can't parse
    entities" ឬ "ENTITY_TEXT_INVALID" ព្រោះ custom_emoji_id លែងមាន) — ករណីណាក៏ដោយ
    គួរតែ retry ដោយអត្ថបទធម្មតា (គ្មាន premium_text/tg-emoji tag) ជាជាងឲ្យសារបាត់សោះ។"""
    msg = str(exc).lower()
    return "entit" in msg


def _patched_send_message(chat_id, text=None, *args, **kwargs):
    try:
        return _orig_send_message(chat_id, premium_text(text), *args, **kwargs)
    except Exception as e:
        if _is_entity_parse_error(e):
            print(f"[premium_text] entity parse failed, retrying plain text: {e}", flush=True)
            return _orig_send_message(chat_id, text, *args, **kwargs)
        raise


def _patched_reply_to(message, text=None, *args, **kwargs):
    try:
        return _orig_reply_to(message, premium_text(text), *args, **kwargs)
    except Exception as e:
        if _is_entity_parse_error(e):
            print(f"[premium_text] entity parse failed, retrying plain text: {e}", flush=True)
            return _orig_reply_to(message, text, *args, **kwargs)
        raise


def _patched_edit_message_text(text=None, *args, **kwargs):
    try:
        return _orig_edit_message_text(premium_text(text), *args, **kwargs)
    except Exception as e:
        if _is_entity_parse_error(e):
            print(f"[premium_text] entity parse failed, retrying plain text: {e}", flush=True)
            return _orig_edit_message_text(text, *args, **kwargs)
        raise


def _patched_edit_message_caption(caption=None, *args, **kwargs):
    try:
        return _orig_edit_message_caption(premium_text(caption), *args, **kwargs)
    except Exception as e:
        if _is_entity_parse_error(e):
            print(f"[premium_text] entity parse failed, retrying plain caption: {e}", flush=True)
            return _orig_edit_message_caption(caption, *args, **kwargs)
        raise


def _patched_send_photo(chat_id, photo, caption=None, *args, **kwargs):
    try:
        return _orig_send_photo(chat_id, photo, premium_text(caption), *args, **kwargs)
    except Exception as e:
        if _is_entity_parse_error(e):
            print(f"[premium_text] entity parse failed, retrying plain caption: {e}", flush=True)
            return _orig_send_photo(chat_id, photo, caption, *args, **kwargs)
        raise


def _patched_send_video(chat_id, video, caption=None, *args, **kwargs):
    try:
        return _orig_send_video(chat_id, video, premium_text(caption), *args, **kwargs)
    except Exception as e:
        if _is_entity_parse_error(e):
            print(f"[premium_text] entity parse failed, retrying plain caption: {e}", flush=True)
            return _orig_send_video(chat_id, video, caption, *args, **kwargs)
        raise


def _patched_send_document(chat_id, document, caption=None, *args, **kwargs):
    try:
        return _orig_send_document(chat_id, document, premium_text(caption), *args, **kwargs)
    except Exception as e:
        if _is_entity_parse_error(e):
            print(f"[premium_text] entity parse failed, retrying plain caption: {e}", flush=True)
            return _orig_send_document(chat_id, document, caption, *args, **kwargs)
        raise


bot.send_message = _patched_send_message
bot.reply_to = _patched_reply_to
bot.edit_message_text = _patched_edit_message_text
bot.edit_message_caption = _patched_edit_message_caption
bot.send_photo = _patched_send_photo
bot.send_video = _patched_send_video
bot.send_document = _patched_send_document


def all_emoji_categories():
    """បញ្ជីពេញលេញសម្រាប់ setup: category base (✅❌🔙...) បូក icon របស់ផលិតផលនីមួយៗ
    ដែលមានក្នុងហាង — ដូច្នេះ admin អាចដាក់ Premium Emoji ទៅ icon ផលិតផលនីមួយៗបានដែរ។"""
    cats = list(EMOJI_CATEGORIES)
    seen = {g for g, _ in cats}
    for key, p in load_products().items():
        icon = resolve_icon(p.get("icon", "📦"))
        if icon and icon not in seen:
            cats.append((icon, f"{icon} Icon ផលិតផល: {p.get('name', key)}"))
            seen.add(icon)
    return cats


def _encode_glyph(glyph):
    return glyph.encode("utf-8").hex()


def _decode_glyph(hex_str):
    return bytes.fromhex(hex_str).decode("utf-8")


def emoji_setup_kb():
    m = get_emoji_map()
    kb = types.InlineKeyboardMarkup(row_width=1)
    for glyph, label in all_emoji_categories():
        mark = "✅" if glyph in m else "⬜"
        kb.add(pbtn(f"{mark} {label}", callback_data=f"emoji_pick_{_encode_glyph(glyph)}", style="primary"))
    kb.add(pbtn("🔙 ត្រឡប់ក្រោយ", callback_data="emoji_close", style="primary"))
    return kb


@bot.message_handler(commands=["setupemoji"])
def cmd_setupemoji(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(
        message.chat.id,
        "🎭 <b>Setup Premium Emoji</b>\n\n"
        "ជ្រើសរើសប្រភេទខាងក្រោម (រួមទាំង icon ផលិតផលនីមួយៗ) រួចផ្ញើ Premium Emoji ពិត "
        "(ត្រូវការ Telegram Premium)\nដើម្បីភ្ជាប់ icon នោះទៅគ្រប់ប៊ូតុង/សារដែលមាន glyph ធម្មតានេះ "
        "— ស្តុកមានទើបប៊ូតុងបង្ហាញ icon premium ដូចក្នុងឧទាហរណ៍។\n\n"
        "✅ អនុវត្តលើ <b>ប៊ូតុងគ្រប់ប្រភេទ</b>៖ ទាំង Inline button (ភ្ជាប់នឹងសារ) និង "
        "Reply Keyboard (ម៉ឺនុយខាងក្រោមអេក្រង់ដូចជា 🛒 ទិញ Account, 💰 Wallet ។ល។) ដោយស្វ័យប្រវត្តិ — "
        "កំណត់ម្តងគ្រប់កន្លែងទាំងអស់។\n"
        "⚠️ ចំណាំ៖ Reply Keyboard ដែលកំពុងបើកនៅលើអេក្រង់ user រួចហើយ នឹងបង្ហាញ icon ថ្មី "
        "តែពេល bot ផ្ញើម៉ឺនុយនោះម្តងទៀត (ឧ. user ចុច /start ម្តងទៀត)។",
        reply_markup=emoji_setup_kb(),
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("emoji_"))
def emoji_setup_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id)
        return
    data = call.data
    chat_id = call.message.chat.id

    if data == "emoji_close":
        bot.edit_message_text("🎭 បិទ Setup Emoji។ ប្រើ /setupemoji ម្តងទៀតបើត្រូវការ។", chat_id, call.message.message_id)

    elif data.startswith("emoji_pick_"):
        glyph = _decode_glyph(data[len("emoji_pick_"):])
        label = next((l for g, l in all_emoji_categories() if g == glyph), f"Icon {glyph}")
        msg = bot.send_message(
            chat_id,
            f"📨 សូមផ្ញើ <b>Premium Emoji ពិត</b> សម្រាប់ប្រភេទ:\n{label}\n\n"
            f"(ត្រូវជា custom emoji ពិតៗ ដែលអ្នកមាន Telegram Premium ចុចផ្ញើ មិនមែន emoji ធម្មតាទេ)",
        )
        bot.register_next_step_handler(msg, emoji_capture_step, glyph, label)

    elif data.startswith("emoji_clear_"):
        glyph = _decode_glyph(data[len("emoji_clear_"):])
        label = next((l for g, l in all_emoji_categories() if g == glyph), f"Icon {glyph}")
        m = get_emoji_map()
        m.pop(glyph, None)
        save_emoji_map(m)
        bot.edit_message_text(
            f"🗑 លុប icon premium សម្រាប់ {label} រួចហើយ។",
            chat_id, call.message.message_id, reply_markup=emoji_setup_kb(),
        )

    bot.answer_callback_query(call.id)


def emoji_capture_step(message, glyph, label):
    if not is_admin(message.from_user.id):
        return
    entities = message.entities or []
    ce = next((e for e in entities if e.type == "custom_emoji"), None)
    if not ce:
        kb = types.InlineKeyboardMarkup()
        kb.add(pbtn("🔁 ព្យាយាមម្តងទៀត", callback_data=f"emoji_pick_{_encode_glyph(glyph)}", style="primary"))
        kb.add(pbtn("🔙 ត្រឡប់ក្រោយ", callback_data="emoji_close", style="primary"))
        bot.send_message(
            message.chat.id,
            "❌ រកមិនឃើញ Premium Emoji ក្នុងសារនេះទេ។\nសូមផ្ញើ Premium Emoji ពិត (មិនមែន emoji ធម្មតា) ម្តងទៀត:",
            reply_markup=kb,
        )
        return
    emoji_char = message.text[ce.offset: ce.offset + ce.length]
    m = get_emoji_map()
    m[glyph] = {"custom_emoji_id": ce.custom_emoji_id, "emoji": emoji_char}
    save_emoji_map(m)
    bot.send_message(
        message.chat.id,
        f"✅ <b>{label}</b>\n\nបានភ្ជាប់ Premium Emoji {emoji_char} ទៅ glyph <code>{glyph}</code> រួចហើយ។\n"
        f"ចាប់ពីនេះទៅ គ្រប់ប៊ូតុង/សារណាដែលមាន {glyph} នឹងបង្ហាញ icon premium ថែមទៀត "
        f"(ទាំង Inline button និង Reply Keyboard ម៉ឺនុយខាងក្រោមអេក្រង់)។",
        reply_markup=emoji_setup_kb(),
    )
    # បើ glyph នេះប្រើក្នុង Reply Keyboard (ម៉ឺនុយខាងក្រោមអេក្រង់) ផ្ញើ preview ថ្មីភ្លាមៗ
    # ដើម្បីឲ្យ admin ឃើញលទ្ធផលដោយផ្ទាល់ (Telegram មិន auto-refresh keyboard ចាស់ដែលកំពុងបើកស្រាប់ទេ)
    reply_btn_texts = [
        BTN_SHOP, BTN_WALLET, BTN_DEPOSIT, BTN_ORDERS, BTN_PROFILE, BTN_HELP,
        ADMIN_BTN_STATS, ADMIN_BTN_ADDPRODUCT, ADMIN_BTN_ADDSTOCK, ADMIN_BTN_DELSTOCK,
        ADMIN_BTN_DELPRODUCT, ADMIN_BTN_EDITPRODUCT, ADMIN_BTN_MSGUSER, ADMIN_BTN_BROADCAST,
        ADMIN_BTN_EMOJI, ADMIN_BTN_SETQR,
    ]
    if any(glyph in t for t in reply_btn_texts):
        bot.send_message(
            message.chat.id,
            "🔄 ម៉ឺនុយខាងក្រោមអេក្រង់ (Reply Keyboard) ត្រូវបាន refresh ថ្មី — សូមមើលខាងក្រោម៖",
            reply_markup=reply_kb_for(message.from_user.id),
        )


# ------------------------------------------------------------------
# STORAGE HELPERS
# ------------------------------------------------------------------
_lock = threading.RLock()  # RLock ព្រោះកូដមានច្រើនកន្លែងហៅ save_products()/save_users()
# ពីខាងក្នុង "with _lock:" រួចស្រាប់ — Lock ធម្មតានឹង deadlock ខ្លួនឯង


def _load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def _save(path, data):
    """សរសេរឯកសារ JSON ដោយសុវត្ថិភាព៖ សរសេរទៅ temp file ជាមុន រួច os.replace() ត្រឡប់
    ទៅឈ្មោះពិត (atomic rename) ដើម្បីជៀសវាងឯកសារខូច/ទទេ បើសរសេរ ២ ដំណាលគ្នា។"""
    with _lock:
        tmp_path = f"{path}.tmp{os.getpid()}"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)


def load_users():
    return _load(USERS_FILE, {})


def save_users(d):
    _save(USERS_FILE, d)


def load_products():
    # default product catalogue - admin អាចកែ/បន្ថែមតាម ➕ Product ថ្មី
    default = {
        "chatgpt": {"name": "ChatGPT Plus 1 Month", "price": 8.0, "icon": "🤖"},
        "netflix": {"name": "Netflix Premium 1 Month", "price": 5.0, "icon": "🎬"},
        "spotify": {"name": "Spotify Premium 1 Month", "price": 3.0, "icon": "🎧"},
        "office365": {"name": "Office 365 1 Year", "price": 10.0, "icon": "📘"},
        "canva": {"name": "Canva Pro 1 Month", "price": 4.0, "icon": "🎨"},
    }
    return _load(PRODUCTS_FILE, default)


def save_products(d):
    _save(PRODUCTS_FILE, d)


def load_orders():
    return _load(ORDERS_FILE, [])


def save_orders(d):
    _save(ORDERS_FILE, d)


# ------------------------------------------------------------------
# ------------------------------------------------------------------
# MANUAL QR DEPOSIT (សម្រាប់ហាង/subscriber ដែលគ្មាន Bakong ID ផ្ទាល់ខ្លួន)
# ------------------------------------------------------------------
def load_payment_config():
    return _load(PAYMENT_CONFIG_FILE, {"manual_qr_file_id": None, "manual_qr_note": ""})


def save_payment_config(d):
    _save(PAYMENT_CONFIG_FILE, d)


def get_manual_qr():
    cfg = load_payment_config()
    return cfg.get("manual_qr_file_id"), cfg.get("manual_qr_note") or ""


def set_manual_qr(file_id, note=None):
    with _lock:
        cfg = load_payment_config()
        cfg["manual_qr_file_id"] = file_id
        if note is not None:
            cfg["manual_qr_note"] = note
        save_payment_config(cfg)
        return cfg


NOTIFY_CONFIG_FILE = os.path.join(DATA_DIR, "notify_config.json")


def load_notify_config():
    return _load(NOTIFY_CONFIG_FILE, {"chat_ids": []})


def save_notify_config(d):
    _save(NOTIFY_CONFIG_FILE, d)


def get_notify_chat_ids():
    """សរុប NOTIFY_CHAT_IDS ពី env var (hardcode) + channel/group ដែល admin បាន /setnotify
    បន្ថែមតាម bot ផ្ទាល់ (ដកស្ទួនចេញ)។"""
    cfg = load_notify_config()
    ids = list(NOTIFY_CHAT_IDS) + [c for c in cfg.get("chat_ids", []) if c not in NOTIFY_CHAT_IDS]
    return ids


def add_notify_chat_id(chat_id):
    with _lock:
        cfg = load_notify_config()
        ids = cfg.get("chat_ids", [])
        if chat_id not in ids:
            ids.append(chat_id)
        cfg["chat_ids"] = ids
        save_notify_config(cfg)
        return ids


def remove_notify_chat_id(chat_id):
    with _lock:
        cfg = load_notify_config()
        ids = [c for c in cfg.get("chat_ids", []) if c != chat_id]
        cfg["chat_ids"] = ids
        save_notify_config(cfg)
        return ids


def has_auto_bakong():
    """True បើហាងនេះមាន Bakong auto-payment (CAMRAPIDPAY_API_KEY កំណត់ហើយ)"""
    return bool(CAMRAPIDPAY_API_KEY)


def load_pending_deposits():
    return _load(PENDING_DEPOSITS_FILE, {})


def save_pending_deposits(d):
    _save(PENDING_DEPOSITS_FILE, d)


def create_pending_deposit(dep_id, uid, amount, ref_disp):
    with _lock:
        deps = load_pending_deposits()
        deps[dep_id] = {
            "uid": uid,
            "amount": amount,
            "ref": ref_disp,
            "status": "pending",  # pending | approved | rejected
            "receipt_file_id": None,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_pending_deposits(deps)
        return deps[dep_id]


def get_pending_deposit(dep_id):
    deps = load_pending_deposits()
    return deps.get(dep_id)


def update_pending_deposit(dep_id, **fields):
    with _lock:
        deps = load_pending_deposits()
        rec = deps.get(dep_id)
        if not rec:
            return None
        rec.update(fields)
        deps[dep_id] = rec
        save_pending_deposits(deps)
        return rec


# ------------------------------------------------------------------
# EMAIL-DELIVERY ORDERS (product ប្រភេទ "email" — admin ដាក់ premium ដោយដៃ
# លើ email ផ្ទាល់ខ្លួនរបស់ user ខ្លួនឯង ជំនួសឲ្យការចែក account ពី stock file)
# ------------------------------------------------------------------
def load_pending_email_orders():
    return _load(PENDING_EMAIL_ORDERS_FILE, {})


def save_pending_email_orders(d):
    _save(PENDING_EMAIL_ORDERS_FILE, d)


def create_pending_email_order(order_id, uid, product_key, product_name, price, email):
    with _lock:
        orders = load_pending_email_orders()
        orders[order_id] = {
            "uid": uid,
            "product_key": product_key,
            "product": product_name,
            "price": price,
            "email": email,
            "status": "pending",  # pending | done | rejected
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_pending_email_orders(orders)
        return orders[order_id]


def get_pending_email_order(order_id):
    orders = load_pending_email_orders()
    return orders.get(order_id)


def update_pending_email_order(order_id, **fields):
    with _lock:
        orders = load_pending_email_orders()
        rec = orders.get(order_id)
        if not rec:
            return None
        rec.update(fields)
        orders[order_id] = rec
        save_pending_email_orders(orders)
        return rec


def get_user(uid):
    users = load_users()
    uid = str(uid)
    if uid not in users:
        users[uid] = {
            "balance": 0.0,
            "orders": 0,
            "joined_at": time.strftime("%Y-%m-%d"),
            "first_name": None,
            "last_name": None,
            "username": None,
            "last_seen": None,
        }
        save_users(users)
    return users[uid]


def touch_user_profile(uid, first_name=None, last_name=None, username=None):
    with _lock:
        users = load_users()
        uid = str(uid)
        if uid not in users:
            users[uid] = {
                "balance": 0.0, "orders": 0, "joined_at": time.strftime("%Y-%m-%d"),
                "first_name": None, "last_name": None, "username": None, "last_seen": None,
            }
        u = users[uid]
        if first_name is not None:
            u["first_name"] = first_name
        if last_name is not None:
            u["last_name"] = last_name
        if username is not None:
            u["username"] = username
        u["last_seen"] = time.strftime("%Y-%m-%d %H:%M:%S")
        if not u.get("joined_at"):
            u["joined_at"] = time.strftime("%Y-%m-%d")
        save_users(users)
        return u


def update_balance(uid, delta):
    with _lock:
        users = load_users()
        uid = str(uid)
        if uid not in users:
            users[uid] = {"balance": 0.0, "orders": 0}
        users[uid]["balance"] = round(users[uid]["balance"] + delta, 2)
        save_users(users)
        return users[uid]["balance"]


def stock_path(product_key):
    return os.path.join(STOCK_DIR, f"{product_key}.txt")


def stock_count(product_key):
    p = stock_path(product_key)
    if not os.path.exists(p):
        return 0
    with open(p, "r", encoding="utf-8") as f:
        return len([l for l in f if l.strip()])


def pop_stock_item(product_key):
    with _lock:
        p = stock_path(product_key)
        if not os.path.exists(p):
            return None
        with open(p, "r", encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        if not lines:
            return None
        item = lines[0].strip()
        remaining = lines[1:]
        with open(p, "w", encoding="utf-8") as f:
            f.writelines(remaining)
        return item


def push_stock_items(product_key, items):
    p = stock_path(product_key)
    with _lock:
        with open(p, "a", encoding="utf-8") as f:
            for it in items:
                it = it.strip()
                if it:
                    f.write(it + "\n")


def pop_stock_items(product_key, qty):
    items = []
    for _ in range(qty):
        it = pop_stock_item(product_key)
        if not it:
            break
        items.append(it)
    return items


def peek_stock_items(product_key, limit=None):
    p = stock_path(product_key)
    if not os.path.exists(p):
        return []
    with open(p, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    if limit:
        return lines[:limit]
    return lines


def remove_stock_items_by_indices(product_key, indices):
    with _lock:
        p = stock_path(product_key)
        if not os.path.exists(p):
            return [], 0
        with open(p, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        idx_set = {i for i in indices if 1 <= i <= len(lines)}
        removed = [lines[i - 1] for i in sorted(idx_set)]
        kept = [lines[i] for i in range(len(lines)) if (i + 1) not in idx_set]
        with open(p, "w", encoding="utf-8") as f:
            for it in kept:
                f.write(it + "\n")
        return removed, len(kept)


def clear_stock_items(product_key):
    with _lock:
        p = stock_path(product_key)
        count = stock_count(product_key)
        if os.path.exists(p):
            with open(p, "w", encoding="utf-8") as f:
                f.write("")
        return count


# ------------------------------------------------------------------
# CAMRAPIDPAY (KHQR) INTEGRATION
# ------------------------------------------------------------------
_http = requests.Session()
_http.mount("https://", requests.adapters.HTTPAdapter(
    max_retries=requests.adapters.Retry(total=2, backoff_factor=0.5)
))


_last_camrapid_error = ""


def camrapid_create(amount, reference, _attempt=1):
    global _last_camrapid_error
    if not CAMRAPIDPAY_API_KEY:
        _last_camrapid_error = "CAMRAPIDPAY_API_KEY មិនបានកំណត់ក្នុង Render environment variables"
        print(f"[camrapid_create] {_last_camrapid_error}", flush=True)
        return None
    if not CAMRAPID_WEBHOOK_URL:
        _last_camrapid_error = (
            "CAMRAPID_WEBHOOK_URL/PUBLIC_BASE_URL មិនបានកំណត់ — CamRapidPay តម្រូវ webhook_url"
        )
        print(f"[camrapid_create] {_last_camrapid_error}", flush=True)
        return None
    try:
        r = _http.post(
            CAMRAPID_CREATE,
            json={
                "api_key": CAMRAPIDPAY_API_KEY,
                "amount": round(float(amount), 2),
                "reference": reference,
                "webhook_url": CAMRAPID_WEBHOOK_URL,
            },
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=20,
        )
        try:
            data = r.json()
        except Exception:
            _last_camrapid_error = f"HTTP {r.status_code} (non-JSON): {r.text[:300]}"
            print(f"[camrapid_create] {_last_camrapid_error}", flush=True)
            if r.status_code >= 500 and _attempt < 2:
                time.sleep(1.5)
                return camrapid_create(amount, reference, _attempt=2)
            return None
        if data.get("success"):
            return data
        _last_camrapid_error = f"HTTP {r.status_code}: {data}"
        print(f"[camrapid_create] failed: {_last_camrapid_error}", flush=True)
        if r.status_code >= 500 and _attempt < 2:
            time.sleep(1.5)
            return camrapid_create(amount, reference, _attempt=2)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        _last_camrapid_error = f"{type(e).__name__}: {e}"
        print(f"[camrapid_create] transient error: {_last_camrapid_error}", flush=True)
        if _attempt < 2:
            time.sleep(1.5)
            return camrapid_create(amount, reference, _attempt=2)
    except Exception as e:
        _last_camrapid_error = f"{type(e).__name__}: {e}"
        print(f"[camrapid_create] error: {_last_camrapid_error}", flush=True)
    return None


def camrapid_check(reference):
    try:
        r = _http.get(
            CAMRAPID_CHECK,
            params={"api_key": CAMRAPIDPAY_API_KEY, "reference": reference},
            headers={"Accept": "application/json"},
            timeout=10,
        )
        data = r.json()
        return bool(data.get("success")) and data.get("status", "").lower() in ("success", "paid")
    except Exception as e:
        print(f"[camrapid_check] error: {e}")
    return False


# ------------------------------------------------------------------
# KHQR CARD GENERATOR (styled card, requires: pip install qrcode Pillow numpy)
# ------------------------------------------------------------------
_CARD_NAVY = (13, 18, 38)
_CARD_NAVY2 = (30, 27, 75)
_CARD_RED = (229, 29, 39)
_CARD_WHITE = (255, 255, 255)
_CARD_SUBTITLE = (191, 196, 234)
_CARD_GRAY = (104, 110, 128)
_CARD_MUTED = (139, 140, 144)
_CARD_GOLD = (245, 197, 66)
_CARD_VIOLET = (124, 92, 255)
_CARD_PANEL = (250, 250, 252)

_FONT_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/system/fonts/Roboto-Regular.ttf",
    "/data/data/com.termux/files/usr/share/fonts/DejaVuSans.ttf",
]
_FONT_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/system/fonts/Roboto-Bold.ttf",
    "/data/data/com.termux/files/usr/share/fonts/DejaVuSans-Bold.ttf",
]


def _card_font(size, bold=False):
    from PIL import ImageFont
    for path in (_FONT_BOLD if bold else _FONT_REG):
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _tw(draw, text, font):
    return draw.textbbox((0, 0), text, font=font)[2]


def _cx_text(draw, cx, y, text, font, fill):
    draw.text((cx - _tw(draw, text, font) / 2, y), text, font=font, fill=fill)


def _vgrad(draw, box, top_color, bottom_color):
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / h
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=(r, g, b))


def _qr_matrix(data):
    import numpy as np
    import qrcode as _qrcode
    qr = _qrcode.QRCode(border=0, error_correction=_qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(data)
    qr.make(fit=True)
    m = qr.get_matrix()
    return np.array([[0 if c else 255 for c in row] for row in m], dtype=np.uint8)


def _qr_img(data, box_px):
    from PIL import Image, ImageDraw
    matrix = _qr_matrix(data)
    n = matrix.shape[0]
    mod = max(1, box_px // n)
    img = Image.new("RGB", (mod * n, mod * n), _CARD_PANEL)
    draw = ImageDraw.Draw(img)
    for ry in range(n):
        for rx in range(n):
            if matrix[ry, rx] == 0:
                x0, y0 = rx * mod, ry * mod
                draw.rectangle([x0, y0, x0 + mod - 1, y0 + mod - 1], fill=_CARD_NAVY)
    return img.resize((box_px, box_px), Image.LANCZOS)


def build_qr_image(qr_string, amount=None, ref=None, label=None, subtitle=None, expires_min=5, width=720):
    """បង្កើត branded KHQR card (Bakong-style) → BytesIO (PNG)។ Fallback ទៅ QR ធម្មតាបើមានបញ្ហា។"""
    from PIL import Image, ImageDraw
    try:
        W = width
        HEADER_H = int(W * 0.30)
        SIDE_PAD = int(W * 0.13)
        QR_BOX = W - 2 * SIDE_PAD
        QR_PAD = int(QR_BOX * 0.09)
        OVERLAP = int(W * 0.10)

        f_title = _card_font(int(W * 0.052), bold=True)
        f_sub = _card_font(int(W * 0.026))
        f_name = _card_font(int(W * 0.042), bold=True)
        f_label = _card_font(int(W * 0.024))
        f_amt = _card_font(int(W * 0.062), bold=True)
        f_small = _card_font(int(W * 0.0205))
        f_badge = _card_font(int(W * 0.0195), bold=True)

        qr_card_top = HEADER_H - OVERLAP
        qr_card_bottom = qr_card_top + QR_BOX
        content_top = qr_card_bottom + int(W * 0.05)

        amt_h = int(f_amt.size * 1.5)
        gap1, gap2 = int(W * 0.022), int(W * 0.035)
        bottom_pad = int(W * 0.05)

        H = (content_top + int(W * 0.065) + int(W * 0.04) + gap1 + amt_h + gap2
             + int(W * 0.03) + int(W * 0.03) + int(W * 0.03) + int(W * 0.03) + bottom_pad)

        img = Image.new("RGB", (W, H), _CARD_WHITE)
        draw = ImageDraw.Draw(img)
        cx = W // 2
        pad = int(W * 0.06)

        _vgrad(draw, [0, 0, W, HEADER_H], _CARD_NAVY, _CARD_NAVY2)

        ring_r = int(W * 0.32)
        ring_cx, ring_cy = W - int(W * 0.05), int(W * 0.02)
        draw.ellipse([ring_cx - ring_r, ring_cy - ring_r, ring_cx + ring_r, ring_cy + ring_r],
                     outline=(255, 255, 255), width=1)

        draw.text((pad, int(W * 0.045)), "KHQR", font=f_title, fill=_CARD_WHITE)
        draw.text((pad, int(W * 0.045) + f_title.size + int(W * 0.010)),
                  "Cambodian QR Payment · Bakong", font=f_sub, fill=_CARD_SUBTITLE)

        badge_txt = "★ PREMIUM"
        bw = _tw(draw, badge_txt, f_badge)
        bpad_x, bpad_y = int(W * 0.020), int(W * 0.011)
        bx1 = W - pad
        bx0 = bx1 - bw - bpad_x * 2
        by0 = int(W * 0.045)
        by1 = by0 + f_badge.size + bpad_y * 2
        draw.rounded_rectangle([bx0, by0, bx1, by1], radius=(by1 - by0) // 2, fill=_CARD_GOLD)
        draw.text((bx0 + bpad_x, by0 + bpad_y - int(W * 0.003)), badge_txt, font=f_badge, fill=_CARD_NAVY)

        r = int(W * 0.045)
        panel_box = [SIDE_PAD, qr_card_top, SIDE_PAD + QR_BOX, qr_card_bottom]
        shadow_off = int(W * 0.012)
        draw.rounded_rectangle(
            [panel_box[0] + shadow_off, panel_box[1] + shadow_off,
             panel_box[2] + shadow_off, panel_box[3] + shadow_off],
            radius=r, fill=(225, 227, 235))
        draw.rounded_rectangle(panel_box, radius=r, fill=_CARD_WHITE)

        qr_px = QR_BOX - 2 * QR_PAD
        qr_pil = _qr_img(qr_string, qr_px)
        img.paste(qr_pil, (SIDE_PAD + QR_PAD, qr_card_top + QR_PAD))

        bl = int(W * 0.055)
        bt = max(3, int(W * 0.007))
        bo = int(W * 0.018)
        x0, y0, x1, y1 = panel_box
        corners = [
            ((x0 + bo, y0 + bo + bl), (x0 + bo, y0 + bo), (x0 + bo + bl, y0 + bo)),
            ((x1 - bo - bl, y0 + bo), (x1 - bo, y0 + bo), (x1 - bo, y0 + bo + bl)),
            ((x0 + bo, y1 - bo - bl), (x0 + bo, y1 - bo), (x0 + bo + bl, y1 - bo)),
            ((x1 - bo - bl, y1 - bo), (x1 - bo, y1 - bo), (x1 - bo, y1 - bo - bl)),
        ]
        for pts in corners:
            draw.line(pts, fill=_CARD_VIOLET, width=bt, joint="curve")

        y = content_top
        store_label = label or STORE_NAME
        _cx_text(draw, cx, y, store_label, f_name, _CARD_NAVY)
        y += int(W * 0.065)
        _cx_text(draw, cx, y, subtitle or STORE_NAME, f_label, _CARD_GRAY)
        y += int(W * 0.04) + gap1

        if amount is not None:
            amt_str = f"${float(amount):.2f}"
            banner_box = [pad, y, W - pad, y + amt_h]
            draw.rounded_rectangle(banner_box, radius=int(W * 0.02), fill=(243, 241, 255))
            draw.rounded_rectangle(banner_box, radius=int(W * 0.02), outline=_CARD_VIOLET, width=2)
            _cx_text(draw, cx, y + (amt_h - f_amt.size) // 2 - int(W * 0.010), amt_str, f_amt, _CARD_NAVY2)
            y += amt_h + gap2

        if ref:
            _cx_text(draw, cx, y, f"Ref: {ref}", f_small, _CARD_MUTED)
            y += int(W * 0.03)
        if expires_min:
            _cx_text(draw, cx, y, f"Expires in {expires_min} minutes", f_small, _CARD_RED)
            y += int(W * 0.03)
        _cx_text(draw, cx, y, "Scan with any Bakong-member app", f_small, _CARD_MUTED)
        y += int(W * 0.03)
        _cx_text(draw, cx, y, "ABA · ACLEDA · Wing", f_small, _CARD_MUTED)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        buf.name = "khqr_card.png"
        return buf

    except Exception as e:
        print(f"[build_qr_image] {e}")
        try:
            import qrcode as _qrcode
            qr = _qrcode.QRCode(box_size=8, border=2, error_correction=_qrcode.constants.ERROR_CORRECT_M)
            qr.add_data(qr_string)
            qr.make(fit=True)
            pil = qr.make_image(fill_color=(10, 34, 64), back_color="white").convert("RGB")
            buf = io.BytesIO()
            pil.save(buf, format="PNG")
            buf.seek(0)
            buf.name = "khqr.png"
            return buf
        except Exception:
            return None


def poll_deposit(uid, chat_id, amount, reference, user_label=None, max_minutes=5, checker=None):
    try:
        checker = checker or camrapid_check
        deadline = time.time() + max_minutes * 60
        while time.time() < deadline:
            if checker(reference):
                new_balance = update_balance(uid, amount)
                try:
                    bot.send_message(
                        chat_id,
                        f"✅ ការទូទាត់ជោគជ័យ! បញ្ចូល <b>${amount:.2f}</b> ចូល wallet។\n"
                        f"💰 សមតុល្យថ្មី: <b>${new_balance:.2f}</b>\n\n"
                        f"🙏 អរគុណដែលទុកចិត្ត {STORE_NAME}!",
                    )
                except Exception:
                    pass
                notify_public(
                    f"💰 <b>Deposit ជោគជ័យ!</b>\n"
                    f"👤 {user_label or 'User'} (ID: <code>{uid}</code>)\n"
                    f"💵 ${amount:.2f}"
                )
                return
            time.sleep(8)
        try:
            bot.send_message(chat_id, "⌛ QR ផុតកំណត់ ឬមិនទាន់ទូទាត់។ សូមព្យាយាមម្តងទៀត /deposit")
        except Exception:
            pass
    except Exception as e:
        print(f"[poll_deposit] {e}", flush=True)
        notify_admin_error(f"poll_deposit (uid={uid}, amount={amount})", e)


# ------------------------------------------------------------------
# UI HELPERS
# ------------------------------------------------------------------
_bot_username_cache = None


def get_bot_username():
    global _bot_username_cache
    if _bot_username_cache:
        return _bot_username_cache
    try:
        _bot_username_cache = bot.get_me().username
    except Exception:
        _bot_username_cache = None
    return _bot_username_cache


def is_admin(uid):
    return uid == ADMIN_ID


def main_menu_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        pbtn("🛒 ទិញ Account", callback_data="menu_shop", style="success"),
        pbtn("💰 Wallet", callback_data="menu_wallet", style="primary"),
    )
    kb.add(
        pbtn("📦 ការកម្មង់របស់ខ្ញុំ", callback_data="menu_orders", style="primary"),
        pbtn("☎️ ទំនាក់ទំនង Admin", url="tg://user?id=%d" % ADMIN_ID, style="primary"),
    )
    return kb


def products_kb():
    products = load_products()
    kb = types.InlineKeyboardMarkup(row_width=1)
    for key, p in products.items():
        icon = resolve_icon(p.get("icon", "📦"))
        # product ប្រភេទ "email" គ្មាន stock file ទេ (admin ដាក់ដោយដៃម្តងម្នាក់ៗ) —
        # ចាត់ទុកជាមានស្តុកជានិច្ច មិនត្រូវ check stock_count ទេ
        is_email_type = p.get("delivery_type") == "email"
        left = None if is_email_type else stock_count(key)
        if is_email_type or left > 0:
            label = f"{icon} {p['name'].upper()} - ${p['price']:.2f}"
        else:
            label = f"× {icon} {p['name'].upper()} - អស់ស្តុក"
        # ចុចមើលបានជានិច្ច (មិនថាអស់ស្តុក ឬ balance អ្វីទេ) — ព័ត៌មាន photo/price/description
        # ត្រូវឲ្យ user ឃើញបានគ្រប់ពេល, ការ check ស្តុក/balance ធ្វើតែពេលចុច "✅ ទិញឥឡូវ" ប៉ុណ្ណោះ
        btn = pbtn(label, callback_data=f"buyopt_{key}", style="success" if (is_email_type or left > 0) else "danger")
        kb.add(btn)
    kb.add(pbtn("🔙 ត្រឡប់ក្រោយ", callback_data="back_main", style="primary"))
    return kb


def qty_pick_kb(key, qty, max_qty, unit_price):
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        pbtn("➖", callback_data=f"qtymin_{key}_{qty}", style="danger"),
        pbtn(f"{qty} ដុំ", callback_data="noop", style="primary"),
        pbtn("➕", callback_data=f"qtyplus_{key}_{qty}", style="success"),
    )
    kb.add(pbtn(f"✅ ទិញពី Wallet — សរុប ${unit_price * qty:.2f}", callback_data=f"qtyok_{key}_{qty}", style="success"))
    kb.add(pbtn("🔙 ត្រឡប់ក្រោយ", callback_data="menu_shop", style="primary"))
    return kb


def _safe_edit_or_send(call, text, reply_markup):
    """ព្យាយាម edit សារដើម (menu_shop list) ជាអត្ថបទថ្មី — បើ edit មិនកើត (ឧ. សារដើម
    ជារូបភាព ដែល Telegram មិនអនុញ្ញាតឲ្យប្តូរទៅជាអត្ថបទបានទេ) នោះផ្ញើសារថ្មីជំនួសវិញ"""
    chat_id = call.message.chat.id
    try:
        bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=reply_markup)
    except Exception:
        bot.send_message(chat_id, text, reply_markup=reply_markup)


def show_product_detail(call, product_key):
    """បង្ហាញព័ត៌មានលម្អិត product (រូបភាព + description) មុននឹង user ចុចទិញ"""
    chat_id = call.message.chat.id
    products = load_products()
    p = products.get(product_key)
    if not p:
        bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
        return
    icon = resolve_icon(p.get("icon", "📦"))
    is_email_type = p.get("delivery_type") == "email"
    description = (p.get("description") or "").strip()
    out_of_stock = (not is_email_type) and stock_count(product_key) <= 0
    sold = p.get("sold", 0)

    lines = [f"{icon} <b>{p['name']}</b>", ""]
    lines.append(f"💵 Price: <b>${p['price']:.2f}</b>")
    if is_email_type:
        lines.append("📧 Delivery: Email")
    elif out_of_stock:
        lines.append("➕ Stock: អស់ស្តុក")
    else:
        lines.append(f"➕ Stock: {stock_count(product_key)} accounts")
    lines.append(f"📊 Sold: {sold} accounts")
    if description:
        lines.append("")
        lines.append("📝 <b>Description:</b>")
        lines.append(f"<blockquote>{html.escape(description)}</blockquote>")
    caption = "\n".join(lines)

    kb = types.InlineKeyboardMarkup(row_width=1)
    if out_of_stock:
        kb.add(pbtn("❌ អស់ស្តុក — ទាក់ទង Admin", callback_data=f"nostock_{product_key}", style="danger"))
    else:
        kb.add(pbtn("✅ ទិញឥឡូវ", callback_data=f"buydetailok_{product_key}", style="success"))
    kb.add(pbtn("🔙 ត្រឡប់ក្រោយ", callback_data="menu_shop", style="primary"))

    photo_file_id = p.get("photo_file_id")
    if photo_file_id:
        bot.answer_callback_query(call.id)
        try:
            bot.send_photo(chat_id, photo_file_id, caption=caption, reply_markup=kb)
        except Exception as e:
            print(f"[show_product_detail] send_photo failed: {e}", flush=True)
            bot.send_message(chat_id, caption, reply_markup=kb)
    else:
        _safe_edit_or_send(call, caption, kb)


def show_qty_picker(call, product_key, qty):
    chat_id = call.message.chat.id
    products = load_products()
    if product_key not in products:
        bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
        return
    p = products[product_key]
    max_qty = stock_count(product_key)
    if max_qty <= 0:
        bot.answer_callback_query(call.id, f"❌ {p['name']} អស់ស្តុកហើយ សូមទាក់ទង Admin", show_alert=True)
        return
    qty = max(1, min(qty, max_qty))
    icon = resolve_icon(p.get("icon", "📦"))
    sold = p.get("sold", 0)
    text = (
        f"{icon} <b>{p['name']}</b>\n💵 តម្លៃឯកតា: ${p['price']:.2f}\n📦 ស្តុកនៅសល់: {max_qty}\n📈 លក់រួច: {sold} accounts\n\n"
        f"សូមជ្រើសរើសចំនួនដែលចង់ទិញ:"
    )
    _safe_edit_or_send(call, text, qty_pick_kb(product_key, qty, max_qty, p["price"]))


def deposit_amount_kb():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(pbtn("✏️ បញ្ចូលចំនួនលុយ", callback_data="dep_custom", style="primary"))
    kb.add(pbtn("🔙 ត្រឡប់ក្រោយ", callback_data="back_main", style="primary"))
    return kb


DEPOSIT_MIN_AMOUNT = 0.1


def _deposit_custom_amount_step(message, from_user):
    chat_id = message.chat.id
    raw = (message.text or "").strip().replace("$", "").replace(",", "")
    try:
        amount = round(float(raw), 2)
    except (TypeError, ValueError):
        bot.send_message(chat_id, "❌ សូមវាយបញ្ចូលជាលេខ (ឧ. 0.5 ឬ 3.25)។ ចុច /deposit ដើម្បីព្យាយាមម្តងទៀត")
        return
    if amount < DEPOSIT_MIN_AMOUNT:
        bot.send_message(
            chat_id,
            f"❌ ចំនួនតិចជាងអប្បបរមា (${DEPOSIT_MIN_AMOUNT:.2f})។ ចុច /deposit ដើម្បីព្យាយាមម្តងទៀត",
        )
        return
    handle_deposit(from_user.id, chat_id, amount, from_user)


# --- Reply Keyboard (ប៊ូតុងខាងក្រោមអេក្រង់, នៅជាប់ជានិច្ច) ---
BTN_SHOP = "🛒 ទិញ Account"
BTN_WALLET = "💰 Wallet"
BTN_DEPOSIT = "➕ បញ្ចូលលុយ"
BTN_ORDERS = "📦 ការកម្មង់"
BTN_PROFILE = "👤 ប្រវត្តិរូប"
BTN_HELP = "☎️ ជួយខ្ញុំផង"
ADMIN_BTN_STATS = "📊 ស្ថិតិ"
ADMIN_BTN_ADDPRODUCT = "➕ Product ថ្មី"
ADMIN_BTN_ADDSTOCK = "📥 Stock ថ្មី"
ADMIN_BTN_DELSTOCK = "🗑 លុប Stock"
ADMIN_BTN_DELPRODUCT = "🗑 លុប Product"
ADMIN_BTN_EDITPRODUCT = "✏️ កែ Product"
ADMIN_BTN_MSGUSER = "📨 ផ្ញើសារទៅ User"
ADMIN_BTN_BROADCAST = "📢 ផ្ញើសារទៅគ្រប់គ្នា"
ADMIN_BTN_EMOJI = "🎭 Setup Emoji"
ADMIN_BTN_SETQR = "🖼 កំណត់ QR ទូទាត់ដោយដៃ"
ADMIN_BTN_SETNOTIFY = "🔔 កំណត់ Channel ជូនដំណឹង"


def reply_kb_for(uid):
    """ម៉ឺនុយ reply keyboard ពេញលេញ (ធម្មតា, គ្មាន Mini App) — user ធម្មតាឃើញប៊ូតុងសំខាន់ៗ,
    admin (ADMIN_ID) ឃើញប៊ូតុងគ្រប់គ្រងបន្ថែម។ ប៊ូតុងម៉ឺនុយខាងក្រោមអេក្រង់ (ReplyKeyboard) —
    ប្រើ kbtn() ជំនួស string ធម្មតា ដើម្បីអាចដាក់ពណ៌ (Bot API 9.4)។"""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(kbtn(BTN_SHOP, style="success"))
    kb.add(kbtn(BTN_WALLET, style="primary"), kbtn(BTN_DEPOSIT, style="success"))
    kb.add(kbtn(BTN_ORDERS, style="primary"), kbtn(BTN_PROFILE, style="primary"))
    kb.add(kbtn(BTN_HELP, style="primary"))
    if is_admin(uid):
        kb.add(kbtn(ADMIN_BTN_STATS, style="primary"), kbtn(ADMIN_BTN_ADDPRODUCT, style="success"))
        kb.add(kbtn(ADMIN_BTN_ADDSTOCK, style="success"), kbtn(ADMIN_BTN_DELSTOCK, style="danger"))
        kb.add(kbtn(ADMIN_BTN_DELPRODUCT, style="danger"), kbtn(ADMIN_BTN_EDITPRODUCT, style="primary"))
        kb.add(kbtn(ADMIN_BTN_MSGUSER, style="primary"), kbtn(ADMIN_BTN_BROADCAST, style="primary"))
        kb.add(kbtn(ADMIN_BTN_EMOJI, style="primary"), kbtn(ADMIN_BTN_SETQR, style="primary"))
        kb.add(kbtn(ADMIN_BTN_SETNOTIFY, style="primary"))
    return kb


# ------------------------------------------------------------------
# USER COMMANDS
# ------------------------------------------------------------------
@bot.message_handler(commands=["start"])
def cmd_start(message):
    get_user(message.from_user.id)
    touch_user_profile(
        message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=getattr(message.from_user, "last_name", None),
        username=getattr(message.from_user, "username", None),
    )
    first_name = message.from_user.first_name or "មិត្ត"
    u = get_user(message.from_user.id)
    username = getattr(message.from_user, "username", None)
    username_line = f"@{username}" if username else "—"
    text = (
        f"👋 ជម្រាបសួរ {first_name}! សូមស្វាគមន៍មកកាន់ {STORE_NAME}! 🎉\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"📋 <b>ព័ត៌មានគណនី</b>\n"
        f"├ ID: <code>{message.from_user.id}</code>\n"
        f"├ Username: {username_line}\n"
        f"└ ទឹកប្រាក់: ${u['balance']:.2f}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"📖 <b>មុខងារ</b>\n"
        f"├ 🛒 ទិញ Account\n"
        f"├ ➕ បញ្ចូលលុយ\n"
        f"├ 📦 ការកម្មង់\n"
        f"└ 👤 ប្រវត្តិរូប\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💬 ចុចប៊ូតុងខាងក្រោមដើម្បីប្រើប្រាស់!"
    )
    bot.send_message(message.chat.id, text, reply_markup=reply_kb_for(message.from_user.id))


@bot.message_handler(commands=["wallet"])
def cmd_wallet(message):
    u = get_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"💰 សមតុល្យបច្ចុប្បន្ន: <b>${u['balance']:.2f}</b>\n"
        f"ការកម្មង់សរុប: {u['orders']}\n\n"
        f"ចង់បញ្ចូលលុយ? ចុច /deposit",
    )


@bot.message_handler(commands=["deposit"])
def cmd_deposit(message):
    bot.send_message(
        message.chat.id,
        "សូមជ្រើសរើសចំនួនទឹកប្រាក់ដែលចង់បញ្ចូល (USD):",
        reply_markup=deposit_amount_kb(),
    )


@bot.message_handler(commands=["orders"])
def cmd_orders(message):
    orders = load_orders()
    mine = [o for o in orders if o["uid"] == message.from_user.id]
    if not mine:
        bot.send_message(message.chat.id, "អ្នកមិនទាន់មានការកម្មង់ណាមួយទេ។")
        return
    lines = []
    for o in mine[-10:]:
        lines.append(f"• {o['product']} - ${o['price']:.2f} - {o['time']}")
    bot.send_message(message.chat.id, "📦 ការកម្មង់ចុងក្រោយ:\n" + "\n".join(lines))


# ------------------------------------------------------------------
# REPLY KEYBOARD TEXT HANDLERS
# ------------------------------------------------------------------
@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(BTN_SHOP))
def reply_shop(message):
    bot.send_message(
        message.chat.id, "🛒 ជ្រើសរើស account ដែលអ្នកចង់ទិញ:",
        reply_markup=products_kb(),
    )


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(BTN_WALLET))
def reply_wallet(message):
    u = get_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"💰 សមតុល្យបច្ចុប្បន្ន: <b>${u['balance']:.2f}</b>\nការកម្មង់សរុប: {u['orders']}",
    )


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(BTN_DEPOSIT))
def reply_deposit(message):
    bot.send_message(message.chat.id, "សូមជ្រើសរើសចំនួនទឹកប្រាក់ដែលចង់បញ្ចូល (USD):", reply_markup=deposit_amount_kb())


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(BTN_ORDERS))
def reply_orders(message):
    orders = load_orders()
    mine = [o for o in orders if o["uid"] == message.from_user.id]
    if not mine:
        bot.send_message(message.chat.id, "អ្នកមិនទាន់មានការកម្មង់ណាមួយទេ។")
        return
    lines = [f"• {o['product']} - ${o['price']:.2f} - {o['time']}" for o in mine[-10:]]
    bot.send_message(message.chat.id, "📦 ការកម្មង់ចុងក្រោយ:\n" + "\n".join(lines))


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(BTN_PROFILE))
def reply_profile(message):
    u = get_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"👤 <b>ប្រវត្តិរូបរបស់អ្នក</b>\nID: <code>{message.from_user.id}</code>\n"
        f"💰 សមតុល្យ: ${u.get('balance', 0.0):.2f}\nការកម្មង់: {u.get('orders', 0)}",
    )


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(BTN_HELP))
def reply_help(message):
    bot.send_message(
        message.chat.id,
        "☎️ ទំនាក់ទំនង Admin បានផ្ទាល់ខាងក្រោម ឬចុច /start ដើម្បីមើលម៉ឺនុយម្តងទៀត:",
        reply_markup=main_menu_kb(),
    )


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(ADMIN_BTN_STATS))
def reply_admin_stats(message):
    if is_admin(message.from_user.id):
        cmd_stats(message)


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(ADMIN_BTN_ADDPRODUCT))
def reply_admin_addproduct(message):
    if is_admin(message.from_user.id):
        cmd_addproduct(message)


def admin_product_pick_kb(prefix, empty_stock_only=False):
    products = load_products()
    kb = types.InlineKeyboardMarkup(row_width=1)
    for key, p in products.items():
        icon = resolve_icon(p.get("icon", "📦"))
        left = stock_count(key)
        sold = p.get("sold", 0)
        label = f"{icon} {p['name']} ({left} នៅសល់ / លក់ {sold})"
        kb.add(pbtn(label, callback_data=f"{prefix}_{key}", style="primary"))
    if not products:
        kb.add(pbtn("(មិនទាន់មាន product ណាមួយ)", callback_data="noop", style="primary"))
    kb.add(pbtn("🔙 បោះបង់", callback_data="admcancel", style="danger"))
    return kb


def admin_delete_confirm_kb(key):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        pbtn("✅ បាទ/ចាស លុប", callback_data=f"admdelyes_{key}", style="danger"),
        pbtn("🔙 បោះបង់", callback_data="admcancel", style="danger"),
    )
    return kb


def admin_edit_field_kb(key):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        pbtn("✏️ កែ ឈ្មោះ", callback_data=f"admeditname_{key}", style="primary"),
        pbtn("💵 កែ តម្លៃ", callback_data=f"admeditprice_{key}", style="primary"),
        pbtn("🖼 កែ រូបភាព", callback_data=f"admeditphoto_{key}", style="primary"),
        pbtn("📝 កែ Description", callback_data=f"admeditdesc_{key}", style="primary"),
        pbtn("🔙 បោះបង់", callback_data="admcancel", style="danger"),
    )
    return kb


def editproduct_step_name(message, key):
    if not is_admin(message.from_user.id):
        return
    new_name = (message.text or "").strip()
    if not new_name:
        msg = bot.send_message(message.chat.id, "❌ ឈ្មោះមិនអាចទទេបានទេ។ សូមផ្ញើម្តងទៀត:")
        bot.register_next_step_handler(msg, editproduct_step_name, key)
        return
    products = load_products()
    if key not in products:
        bot.reply_to(message, "❌ Product មិនត្រឹមត្រូវ (ប្រហែលជាត្រូវបានលុបទៅហើយ)")
        return
    old_name = products[key]["name"]
    products[key]["name"] = new_name
    save_products(products)
    bot.reply_to(message, f"✅ បានប្តូរឈ្មោះពី '{old_name}' ទៅ '{new_name}' រួចហើយ")


def editproduct_step_price(message, key):
    if not is_admin(message.from_user.id):
        return
    try:
        new_price = float((message.text or "").strip())
        if new_price <= 0:
            raise ValueError
    except Exception:
        msg = bot.send_message(message.chat.id, "❌ តម្លៃត្រូវជាលេខវិជ្ជមាន (ឧ. 5.5)។ សូមផ្ញើម្តងទៀត:")
        bot.register_next_step_handler(msg, editproduct_step_price, key)
        return
    products = load_products()
    if key not in products:
        bot.reply_to(message, "❌ Product មិនត្រឹមត្រូវ (ប្រហែលជាត្រូវបានលុបទៅហើយ)")
        return
    old_price = products[key]["price"]
    products[key]["price"] = new_price
    save_products(products)
    bot.reply_to(message, f"✅ បានប្តូរតម្លៃពី ${old_price:.2f} ទៅ ${new_price:.2f} រួចហើយ")
    if new_price != old_price:
        sent, failed = broadcast_price_change(key, old_price, new_price)
        bot.send_message(message.chat.id, f"📢 ជូនដំណឹងតម្លៃថ្មីទៅ user {sent} នាក់ ({failed} បរាជ័យ)")


def editproduct_step_photo(message, key):
    if not is_admin(message.from_user.id):
        return
    if not message.photo:
        if (message.text or "").strip().lower() in ("skip", "-", "remove", "clear"):
            products = load_products()
            if key not in products:
                bot.reply_to(message, "❌ Product មិនត្រឹមត្រូវ (ប្រហែលជាត្រូវបានលុបទៅហើយ)")
                return
            products[key]["photo_file_id"] = None
            save_products(products)
            bot.reply_to(message, "✅ បានលុបរូបភាពរបស់ product នេះចេញរួចហើយ")
            return
        msg = bot.send_message(
            message.chat.id,
            "❌ សូមផ្ញើជា <b>រូបភាព (Photo)</b>, ឬវាយ <code>skip</code> ដើម្បីលុបរូបភាពចេញ សូមព្យាយាមម្តងទៀត:",
        )
        bot.register_next_step_handler(msg, editproduct_step_photo, key)
        return
    products = load_products()
    if key not in products:
        bot.reply_to(message, "❌ Product មិនត្រឹមត្រូវ (ប្រហែលជាត្រូវបានលុបទៅហើយ)")
        return
    products[key]["photo_file_id"] = message.photo[-1].file_id
    save_products(products)
    bot.reply_to(message, "✅ បានប្តូររូបភាព product នេះរួចហើយ")


def editproduct_step_description(message, key):
    if not is_admin(message.from_user.id):
        return
    text = (message.text or "").strip()
    products = load_products()
    if key not in products:
        bot.reply_to(message, "❌ Product មិនត្រឹមត្រូវ (ប្រហែលជាត្រូវបានលុបទៅហើយ)")
        return
    if text.lower() in ("skip", "-", "remove", "clear"):
        products[key]["description"] = ""
        save_products(products)
        bot.reply_to(message, "✅ បានលុប description របស់ product នេះចេញរួចហើយ")
        return
    products[key]["description"] = text[:900]
    save_products(products)
    bot.reply_to(message, "✅ បានប្តូរ description របស់ product នេះរួចហើយ")


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(ADMIN_BTN_ADDSTOCK))
def reply_admin_addstock(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(
        message.chat.id,
        "📥 <b>Stock ថ្មី</b>\n\nជ្រើសរើស product ដែលចង់បញ្ចូល stock:",
        reply_markup=admin_product_pick_kb("admaddstock"),
    )


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(ADMIN_BTN_DELSTOCK))
def reply_admin_delstock(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(
        message.chat.id,
        "🗑 <b>លុប Stock</b>\n\nជ្រើសរើស product ដែលចង់លុប stock ចេញ:",
        reply_markup=admin_product_pick_kb("admdelstock"),
    )


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(ADMIN_BTN_DELPRODUCT))
def reply_admin_delproduct(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(
        message.chat.id,
        "🗑 <b>លុប Product</b>\n\nជ្រើសរើស product ដែលចង់លុប (នឹងលុបទាំង stock ដែលនៅសល់ផងដែរ):",
        reply_markup=admin_product_pick_kb("admdel"),
    )


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(ADMIN_BTN_EDITPRODUCT))
def reply_admin_editproduct(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(
        message.chat.id,
        "✏️ <b>កែ Product</b>\n\nជ្រើសរើស product ដែលចង់កែ ឈ្មោះ/តម្លៃ:",
        reply_markup=admin_product_pick_kb("admedit"),
    )


@bot.message_handler(commands=["msguser"])
def cmd_msguser(message):
    if not is_admin(message.from_user.id):
        return
    msg = bot.send_message(
        message.chat.id,
        "📨 <b>ផ្ញើសារទៅ User</b>\n\nសូមផ្ញើ user_id ដែលចង់ផ្ញើសារទៅ (លេខ):",
    )
    bot.register_next_step_handler(msg, msguser_step_id)


def msguser_step_id(message):
    if not is_admin(message.from_user.id):
        return
    try:
        target_uid = int(message.text.strip())
    except Exception:
        msg = bot.send_message(message.chat.id, "❌ user_id ត្រូវជាលេខ។ សូមផ្ញើម្តងទៀត:")
        bot.register_next_step_handler(msg, msguser_step_id)
        return
    msg = bot.send_message(
        message.chat.id,
        f"📨 សូមផ្ញើមាតិកាសារដែលចង់ផ្ញើទៅ user <code>{target_uid}</code>:",
    )
    bot.register_next_step_handler(msg, msguser_step_text, target_uid)


def msguser_step_text(message, target_uid):
    if not is_admin(message.from_user.id):
        return
    text = message.text
    try:
        bot.send_message(target_uid, f"📨 <b>សារពី Admin</b>\n\n{text}")
        bot.reply_to(message, f"✅ បានផ្ញើសារទៅ user {target_uid} ជោគជ័យ")
    except Exception as e:
        bot.reply_to(message, f"❌ បរាជ័យ ផ្ញើមិនចេញ: {e}")


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(ADMIN_BTN_MSGUSER))
def reply_admin_msguser(message):
    if is_admin(message.from_user.id):
        cmd_msguser(message)


def broadcast_step_content(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    uids = list(users.keys())
    total = len(uids)
    status = bot.send_message(message.chat.id, f"⏳ កំពុងផ្ញើ... 0/{total}")

    sent, failed = 0, 0
    for i, uid_str in enumerate(uids, start=1):
        try:
            target_uid = int(uid_str)
        except Exception:
            failed += 1
            continue
        try:
            if message.content_type == "text":
                bot.send_message(target_uid, f"📢 <b>សារពី Admin</b>\n\n{message.text}")
            elif message.content_type == "photo":
                bot.send_photo(target_uid, message.photo[-1].file_id, caption=message.caption or "")
            elif message.content_type == "video":
                bot.send_video(target_uid, message.video.file_id, caption=message.caption or "")
            elif message.content_type == "document":
                bot.send_document(target_uid, message.document.file_id, caption=message.caption or "")
            else:
                bot.forward_message(target_uid, message.chat.id, message.message_id)
            sent += 1
        except Exception:
            failed += 1
        time.sleep(0.05)
        if i % 20 == 0 or i == total:
            try:
                bot.edit_message_text(
                    f"⏳ កំពុងផ្ញើ... {i}/{total} (✅ {sent} / ❌ {failed})",
                    message.chat.id,
                    status.message_id,
                )
            except Exception:
                pass

    bot.send_message(
        message.chat.id,
        f"✅ <b>ផ្ញើសារបញ្ចប់</b>\n\nសរុប: {total}\nជោគជ័យ: {sent}\nបរាជ័យ: {failed}",
    )


@bot.message_handler(commands=["broadcast"])
def cmd_broadcast(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, text = message.text.split(" ", 1)
    except Exception:
        msg = bot.send_message(
            message.chat.id,
            "📢 <b>ផ្ញើសារទៅគ្រប់គ្នា</b>\n\nសូមផ្ញើអត្ថបទ/រូបភាព/video ដែលចង់ Broadcast:",
        )
        bot.register_next_step_handler(msg, broadcast_step_content)
        return
    users = load_users()
    sent, failed = 0, 0
    for uid in users:
        try:
            bot.send_message(int(uid), f"📢 <b>សេចក្តីជូនដំណឹង</b>\n\n{text}")
            sent += 1
        except Exception:
            failed += 1
    bot.reply_to(message, f"✅ ផ្ញើជោគជ័យ {sent} នាក់ ({failed} បរាជ័យ)")


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(ADMIN_BTN_BROADCAST))
def reply_admin_broadcast(message):
    if is_admin(message.from_user.id):
        cmd_broadcast(message)


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(ADMIN_BTN_EMOJI))
def reply_admin_emoji(message):
    if is_admin(message.from_user.id):
        cmd_setupemoji(message)


# ------------------------------------------------------------------
# CALLBACK HANDLERS
# ------------------------------------------------------------------
@bot.callback_query_handler(func=lambda c: not c.data.startswith("emoji_"))
def callback_router(call):
    data = call.data
    uid = call.from_user.id
    chat_id = call.message.chat.id

    if data == "menu_shop":
        bot.edit_message_text(
            "🛒 ជ្រើសរើស account ដែលអ្នកចង់ទិញ:",
            chat_id, call.message.message_id, reply_markup=products_kb(),
        )

    elif data == "menu_wallet":
        u = get_user(uid)
        bot.edit_message_text(
            f"💰 សមតុល្យបច្ចុប្បន្ន: <b>${u['balance']:.2f}</b>\n\nចង់បញ្ចូលលុយ?",
            chat_id, call.message.message_id, reply_markup=deposit_amount_kb(),
        )

    elif data == "menu_orders":
        orders = load_orders()
        mine = [o for o in orders if o["uid"] == uid]
        if not mine:
            bot.answer_callback_query(call.id, "អ្នកមិនទាន់មានការកម្មង់ណាមួយទេ", show_alert=True)
            return
        lines = [f"• {o['product']} - ${o['price']:.2f} - {o['time']}" for o in mine[-10:]]
        bot.edit_message_text(
            "📦 ការកម្មង់ចុងក្រោយ:\n" + "\n".join(lines),
            chat_id, call.message.message_id, reply_markup=main_menu_kb(),
        )

    elif data == "back_main":
        bot.edit_message_text(
            "🏠 ម៉ឺនុយចម្បង:", chat_id, call.message.message_id, reply_markup=main_menu_kb(),
        )

    elif data.startswith("buyopt_"):
        product_key = data.split("_", 1)[1]
        show_product_detail(call, product_key)

    elif data.startswith("buydetailok_"):
        product_key = data[len("buydetailok_"):]
        products = load_products()
        product = products.get(product_key)
        if product and product.get("delivery_type") == "email":
            start_buy_email_flow(call, product_key)
        else:
            show_qty_picker(call, product_key, 1)

    elif data.startswith("qtymin_"):
        key, qty_s = data[len("qtymin_"):].rsplit("_", 1)
        show_qty_picker(call, key, int(qty_s) - 1)

    elif data.startswith("qtyplus_"):
        key, qty_s = data[len("qtyplus_"):].rsplit("_", 1)
        show_qty_picker(call, key, int(qty_s) + 1)

    elif data.startswith("qtyok_"):
        key, qty_s = data[len("qtyok_"):].rsplit("_", 1)
        handle_buy_wallet(call, key, int(qty_s))

    elif data.startswith("nostock_"):
        product_key = data.split("_", 1)[1]
        products = load_products()
        name = products.get(product_key, {}).get("name", "Product")
        bot.answer_callback_query(call.id, f"❌ {name} អស់ស្តុកហើយ សូមទាក់ទង Admin", show_alert=True)
        return

    elif data == "dep_custom":
        msg = bot.send_message(
            chat_id,
            "✏️ សូមវាយបញ្ចូលចំនួនទឹកប្រាក់ដែលអ្នកចង់ដាក់ (USD)\n"
            "អប្បបរមា <b>$0.1</b> — ឧទាហរណ៍: 0.5 ឬ 3.25",
        )
        bot.register_next_step_handler(msg, _deposit_custom_amount_step, call.from_user)

    elif data.startswith("paym_bkq_"):
        amount = float(data[len("paym_bkq_"):])
        handle_deposit(uid, chat_id, amount, call.from_user, call=call)

    elif data.startswith("dep_"):
        amount = float(data.split("_", 1)[1])
        handle_deposit(uid, chat_id, amount, call.from_user, call=call)

    elif data.startswith("depapprove_"):
        if not is_admin(uid):
            return
        dep_id = data[len("depapprove_"):]
        _handle_deposit_approve(call, dep_id)

    elif data.startswith("depreject_"):
        if not is_admin(uid):
            return
        dep_id = data[len("depreject_"):]
        _handle_deposit_reject(call, dep_id)

    elif data.startswith("emailordone_"):
        if not is_admin(uid):
            return
        order_id = data[len("emailordone_"):]
        _handle_email_order_done(call, order_id)

    elif data.startswith("emailorreject_"):
        if not is_admin(uid):
            return
        order_id = data[len("emailorreject_"):]
        _handle_email_order_reject(call, order_id)

    elif data == "admcancel":
        bot.edit_message_text("🚫 បានបោះបង់។", chat_id, call.message.message_id)

    elif data == "noop":
        pass

    elif data.startswith("admaddstock_"):
        if not is_admin(uid):
            return
        key = data.split("_", 1)[1]
        products = load_products()
        if key not in products:
            bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
            return
        bot.edit_message_text(
            f"📥 សូមផ្ញើ account list សំរាប់ '{products[key]['name']}'\n(មួយបន្ទាត់ = account មួយ)",
            chat_id, call.message.message_id,
        )
        bot.register_next_step_handler(call.message, process_addstock, key)

    elif data.startswith("admdelstock_"):
        if not is_admin(uid):
            return
        key = data.split("_", 1)[1]
        products = load_products()
        if key not in products:
            bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
            return
        total = stock_count(key)
        if total == 0:
            bot.edit_message_text(
                f"📭 '{products[key]['name']}' គ្មាន stock សល់ទេ។",
                chat_id, call.message.message_id,
            )
            bot.answer_callback_query(call.id)
            return
        preview = peek_stock_items(key, limit=30)
        lines = [f"{i+1}. <code>{html.escape(it)}</code>" for i, it in enumerate(preview)]
        more_note = f"\n… និងមាន {total - len(preview)} ទៀត (មិនបានបង្ហាញ)" if total > len(preview) else ""
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(pbtn("🗑 លុបទាំងអស់ (Clear All)", callback_data=f"admclearstockconfirm_{key}", style="danger"))
        kb.add(pbtn("🔙 បោះបង់", callback_data="admcancel", style="danger"))
        msg = bot.edit_message_text(
            f"🗑 <b>លុប Stock — {products[key]['name']}</b> (សរុប {total})\n\n"
            + "\n".join(lines) + more_note +
            "\n\nសូមវាយបញ្ចូល <b>លេខ</b> ដែលចង់លុប (ឧ. <code>1,3,5</code>) រួចផ្ញើមក "
            "ឬចុច 🗑 លុបទាំងអស់ខាងក្រោម:",
            chat_id, call.message.message_id,
            reply_markup=kb,
        )
        bot.register_next_step_handler(msg, process_delstock_indices, key)

    elif data.startswith("admclearstockconfirm_"):
        if not is_admin(uid):
            return
        key = data.split("_", 1)[1]
        products = load_products()
        if key not in products:
            bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
            return
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            pbtn("✅ បាទ/ចាស លុបទាំងអស់", callback_data=f"admclearstockyes_{key}", style="danger"),
            pbtn("🔙 បោះបង់", callback_data="admcancel", style="danger"),
        )
        bot.edit_message_text(
            f"⚠️ តើអ្នកប្រាកដថាចង់លុប stock ទាំង {stock_count(key)} account "
            f"របស់ '{products[key]['name']}' ចោលទាំងអស់មែនទេ? (មិនអាចដកមកវិញបានទេ)",
            chat_id, call.message.message_id,
            reply_markup=kb,
        )

    elif data.startswith("admclearstockyes_"):
        if not is_admin(uid):
            return
        key = data.split("_", 1)[1]
        products = load_products()
        if key not in products:
            bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
            return
        removed = clear_stock_items(key)
        bot.edit_message_text(
            f"✅ បានលុប stock ទាំង {removed} account របស់ '{products[key]['name']}' រួចហើយ\n"
            f"📊 ស្តុកសល់: {stock_count(key)}",
            chat_id, call.message.message_id,
        )

    elif data.startswith("admdelyes_"):
        if not is_admin(uid):
            return
        key = data.split("_", 1)[1]
        products = load_products()
        if key not in products:
            bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
            return
        name = products[key]["name"]
        left = stock_count(key)
        del products[key]
        save_products(products)
        sp = stock_path(key)
        if os.path.exists(sp):
            os.remove(sp)
        bot.edit_message_text(
            f"✅ បានលុប product '{name}' (key: <code>{key}</code>) រួចហើយ\n"
            f"🗑 Stock ដែលបានលុបទាំង {left} account",
            chat_id, call.message.message_id,
        )

    elif data.startswith("admedit_"):
        if not is_admin(uid):
            return
        key = data.split("_", 1)[1]
        products = load_products()
        if key not in products:
            bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
            return
        p = products[key]
        bot.edit_message_text(
            f"✏️ <b>{resolve_icon(p.get('icon','📦'))} {p['name']}</b> (តម្លៃបច្ចុប្បន្ន: ${p['price']:.2f})\n\n"
            f"ជ្រើសរើសអ្វីដែលចង់កែ:",
            chat_id, call.message.message_id,
            reply_markup=admin_edit_field_kb(key),
        )

    elif data.startswith("admeditname_"):
        if not is_admin(uid):
            return
        key = data.split("_", 1)[1]
        products = load_products()
        if key not in products:
            bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
            return
        bot.edit_message_text(
            f"✏️ ឈ្មោះបច្ចុប្បន្ន: <b>{products[key]['name']}</b>\n\nសូមផ្ញើឈ្មោះថ្មី:",
            chat_id, call.message.message_id,
        )
        bot.register_next_step_handler(call.message, editproduct_step_name, key)

    elif data.startswith("admeditprice_"):
        if not is_admin(uid):
            return
        key = data.split("_", 1)[1]
        products = load_products()
        if key not in products:
            bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
            return
        bot.edit_message_text(
            f"✏️ តម្លៃបច្ចុប្បន្ន: <b>${products[key]['price']:.2f}</b>\n\nសូមផ្ញើតម្លៃថ្មី (ឧ. 5.5):",
            chat_id, call.message.message_id,
        )
        bot.register_next_step_handler(call.message, editproduct_step_price, key)

    elif data.startswith("admeditphoto_"):
        if not is_admin(uid):
            return
        key = data.split("_", 1)[1]
        products = load_products()
        if key not in products:
            bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
            return
        bot.send_message(
            chat_id,
            "🖼 សូមផ្ញើ <b>រូបភាព (Photo)</b> ថ្មីសម្រាប់ product នេះ\n"
            "ឬវាយ <code>skip</code> ដើម្បីលុបរូបភាពបច្ចុប្បន្នចេញ:",
        )
        bot.register_next_step_handler(call.message, editproduct_step_photo, key)

    elif data.startswith("admeditdesc_"):
        if not is_admin(uid):
            return
        key = data.split("_", 1)[1]
        products = load_products()
        if key not in products:
            bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
            return
        cur_desc = products[key].get("description") or "— គ្មាន"
        bot.send_message(
            chat_id,
            f"📝 Description បច្ចុប្បន្ន: {html.escape(cur_desc)}\n\n"
            f"សូមផ្ញើ description ថ្មី ឬវាយ <code>skip</code> ដើម្បីលុបចេញ:",
        )
        bot.register_next_step_handler(call.message, editproduct_step_description, key)

    elif data.startswith("admdel_"):
        if not is_admin(uid):
            return
        key = data.split("_", 1)[1]
        products = load_products()
        if key not in products:
            bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
            return
        p = products[key]
        bot.edit_message_text(
            f"⚠️ តើអ្នកប្រាកដថាចង់លុប <b>{resolve_icon(p.get('icon','📦'))} {p['name']}</b> (key: <code>{key}</code>)?\n"
            f"ស្តុកនៅសល់ {stock_count(key)} account នឹងត្រូវលុបចោលផងដែរ។",
            chat_id, call.message.message_id,
            reply_markup=admin_delete_confirm_kb(key),
        )

    bot.answer_callback_query(call.id)


def handle_buy_wallet(call, product_key, qty=1):
    uid = call.from_user.id
    chat_id = call.message.chat.id
    products = load_products()
    if product_key not in products:
        bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
        return

    product = products[product_key]
    unit_price = product["price"]
    qty = max(1, qty)
    total_price = round(unit_price * qty, 2)

    if stock_count(product_key) < qty:
        bot.answer_callback_query(call.id, f"❌ ស្តុកមានតែ {stock_count(product_key)} មិនគ្រប់ {qty}", show_alert=True)
        return

    user = get_user(uid)
    if user["balance"] < total_price:
        bot.answer_callback_query(
            call.id,
            f"❌ សមតុល្យមិនគ្រប់គ្រាន់ (${user['balance']:.2f}/${total_price:.2f}). សូម /deposit មុន",
            show_alert=True,
        )
        return

    items = pop_stock_items(product_key, qty)
    if len(items) < qty:
        push_stock_items(product_key, items)
        bot.answer_callback_query(call.id, "❌ ស្តុកអស់ភ្លាមៗ សូមព្យាយាមម្តងទៀត", show_alert=True)
        return

    update_balance(uid, -total_price)
    orders = load_orders()
    orders.append({
        "uid": uid,
        "product": product["name"],
        "price": total_price,
        "qty": qty,
        "time": time.strftime("%Y-%m-%d %H:%M"),
    })
    save_orders(orders)

    products[product_key]["sold"] = products[product_key].get("sold", 0) + qty
    save_products(products)

    users = load_users()
    users[str(uid)]["orders"] = users[str(uid)].get("orders", 0) + qty
    save_users(users)

    accounts_text = "\n".join(f"{i+1}. <code>{html.escape(it)}</code>" for i, it in enumerate(items))
    bot.send_message(
        chat_id,
        f"✅ ការទិញជោគជ័យ!\n\n"
        f"🛍️ Product: <b>{product['name']}</b> × {qty}\n"
        f"💵 សរុប: ${total_price:.2f}\n\n"
        f"🔑 <b>Account របស់អ្នក:</b>\n{accounts_text}",
    )

    if ADMIN_ID:
        try:
            bot.send_message(
                ADMIN_ID,
                f"🔔 លក់ថ្មី: {product['name']} × {qty} (${total_price:.2f}) ដល់ user {uid}\n"
                f"ស្តុកនៅសល់: {stock_count(product_key)}",
            )
            if stock_count(product_key) <= 2:
                bot.send_message(ADMIN_ID, f"⚠️ ស្តុក {product['name']} ជិតអស់! ({stock_count(product_key)} នៅសល់)")
        except Exception:
            pass

    notify_public(
        f"🛍️ <b>ការកម្មង់ថ្មី!</b>\n"
        f"{product.get('icon', '📦')} {product['name']} × {qty}\n"
        f"💵 ${total_price:.2f}\n"
        f"👤 {public_user_label(call.from_user)}"
    )

    left_after = stock_count(product_key)
    if 0 < left_after <= LOW_STOCK_THRESHOLD:
        products2 = load_products()
        if product_key in products2 and not products2[product_key].get("low_stock_alerted"):
            products2[product_key]["low_stock_alerted"] = True
            save_products(products2)
            try:
                broadcast_low_stock(product_key, left_after)
            except Exception as e:
                print(f"[broadcast_low_stock] failed: {e}", flush=True)


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def start_buy_email_flow(call, product_key):
    """ចាប់ផ្ដើមការទិញ product ប្រភេទ 'email' — សួរ email របស់ user ជាមុនសិន
    មុននឹងកាត់លុយ (kiểm balance មុន ដើម្បីកុំឲ្យសួរ email ចោលឥតប្រយោជន៍)"""
    uid = call.from_user.id
    chat_id = call.message.chat.id
    products = load_products()
    product = products.get(product_key)
    if not product:
        bot.answer_callback_query(call.id, "❌ Product មិនត្រឹមត្រូវ", show_alert=True)
        return
    price = product["price"]
    user = get_user(uid)
    if user["balance"] < price:
        bot.answer_callback_query(
            call.id,
            f"❌ សមតុល្យមិនគ្រប់គ្រាន់ (${user['balance']:.2f}/${price:.2f}). សូម /deposit មុន",
            show_alert=True,
        )
        return
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        chat_id,
        f"📧 <b>{resolve_icon(product.get('icon'))} {product['name']}</b> — ${price:.2f}\n\n"
        f"សូមផ្ញើ <b>Email</b> គណនីរបស់អ្នក ដែលចង់ឲ្យ Admin ដាក់ Premium ចូល "
        f"(ឧ. <code>example@gmail.com</code>)\n\n"
        f"⚠️ សូមប្រាកដថា Email ត្រឹមត្រូវ — Admin នឹងដាក់ Premium ដោយផ្ទាល់លើ email នេះ។",
    )
    bot.register_next_step_handler(msg, buy_email_step_address, product_key)


def buy_email_step_address(message, product_key):
    if not message.from_user:
        return
    uid = message.from_user.id
    chat_id = message.chat.id
    email = (message.text or "").strip()
    if not _EMAIL_RE.match(email):
        msg = bot.send_message(
            chat_id, "❌ Email មិនត្រឹមត្រូវទេ សូមផ្ញើម្តងទៀត (ឧ. <code>example@gmail.com</code>):"
        )
        bot.register_next_step_handler(msg, buy_email_step_address, product_key)
        return

    products = load_products()
    product = products.get(product_key)
    if not product:
        bot.send_message(chat_id, "❌ Product នេះលែងមានទៀតហើយ")
        return
    price = product["price"]
    user = get_user(uid)
    if user["balance"] < price:
        bot.send_message(
            chat_id,
            f"❌ សមតុល្យមិនគ្រប់គ្រាន់ (${user['balance']:.2f}/${price:.2f}). សូម /deposit មុន រួចទិញម្តងទៀត",
        )
        return

    update_balance(uid, -price)
    order_id = f"EM{uid}{int(time.time())}"[:60]
    create_pending_email_order(order_id, uid, product_key, product["name"], price, email)

    bot.send_message(
        chat_id,
        f"✅ បានទទួល Email របស់អ្នករួចហើយ!\n\n"
        f"🛍️ Product: <b>{product['name']}</b>\n"
        f"💵 តម្លៃ: ${price:.2f} (កាត់ចេញពី Wallet រួច)\n"
        f"📧 Email: <code>{html.escape(email)}</code>\n\n"
        f"⏳ សូមរង់ចាំ Admin ដាក់ Premium ចូល Email នេះ (មិនយូរប៉ុន្មាន) — "
        f"bot នឹងជូនដំណឹងទៅអ្នកភ្លាមៗពេលរួចរាល់។",
    )

    admin_kb = types.InlineKeyboardMarkup(row_width=1)
    admin_kb.add(
        pbtn("✅ រួចរាល់ (Done)", callback_data=f"emailordone_{order_id}", style="success"),
        pbtn("❌ បដិសេធ (Refund)", callback_data=f"emailorreject_{order_id}", style="danger"),
    )
    if ADMIN_ID:
        try:
            bot.send_message(
                ADMIN_ID,
                f"📧 <b>Order Email ថ្មី — ត្រូវការដាក់ Premium ដោយដៃ</b>\n\n"
                f"🛍️ Product: <b>{product['name']}</b>\n"
                f"💵 តម្លៃ: ${price:.2f}\n"
                f"👤 User: {public_user_label(message.from_user)} (<code>{uid}</code>)\n"
                f"📧 Email: <code>{html.escape(email)}</code>\n\n"
                f"👉 សូមដាក់ Premium/Invite លើ email នេះឲ្យរួច រួចចុច '✅ រួចរាល់' ដើម្បីជូនដំណឹង user។",
                reply_markup=admin_kb,
            )
        except Exception as e:
            print(f"[buy_email_step_address] failed to notify admin: {e}", flush=True)


def _handle_email_order_done(call, order_id):
    rec = get_pending_email_order(order_id)
    if not rec:
        bot.answer_callback_query(call.id, "❌ រកមិនឃើញ order នេះទេ", show_alert=True)
        return
    if rec.get("status") != "pending":
        bot.answer_callback_query(call.id, f"ℹ️ Order នេះត្រូវបានដោះស្រាយរួចហើយ ({rec.get('status')})", show_alert=True)
        return
    uid = rec["uid"]
    update_pending_email_order(order_id, status="done")

    orders = load_orders()
    orders.append({
        "uid": uid,
        "product": rec["product"],
        "price": rec["price"],
        "qty": 1,
        "time": time.strftime("%Y-%m-%d %H:%M"),
        "delivery_type": "email",
        "email": rec["email"],
    })
    save_orders(orders)

    products = load_products()
    if rec["product_key"] in products:
        products[rec["product_key"]]["sold"] = products[rec["product_key"]].get("sold", 0) + 1
        save_products(products)

    users = load_users()
    if str(uid) in users:
        users[str(uid)]["orders"] = users[str(uid)].get("orders", 0) + 1
        save_users(users)

    try:
        bot.send_message(
            uid,
            f"✅ <b>Premium ត្រូវបានដាក់រួចរាល់!</b>\n\n"
            f"🛍️ Product: <b>{rec['product']}</b>\n"
            f"📧 Email: <code>{html.escape(rec['email'])}</code>\n\n"
            f"🙏 សូមពិនិត្យ email/app របស់អ្នក។ អរគុណដែលទុកចិត្ត {STORE_NAME}!",
        )
    except Exception:
        pass

    notify_public(
        f"📧 <b>Order Email ជោគជ័យ!</b>\n{rec['product']} — ${rec['price']:.2f}\n👤 User ID: <code>{uid}</code>"
    )
    bot.answer_callback_query(call.id, "✅ បានបញ្ជាក់ ហើយជូនដំណឹងទៅ user រួចរាល់")
    try:
        base_text = call.message.caption or call.message.text or ""
        new_text = base_text + "\n\n✅ <b>រួចរាល់ហើយ</b>"
        if call.message.content_type == "text":
            bot.edit_message_text(new_text, chat_id=call.message.chat.id, message_id=call.message.message_id)
        else:
            bot.edit_message_caption(new_text, chat_id=call.message.chat.id, message_id=call.message.message_id)
    except Exception:
        pass


def _handle_email_order_reject(call, order_id):
    rec = get_pending_email_order(order_id)
    if not rec:
        bot.answer_callback_query(call.id, "❌ រកមិនឃើញ order នេះទេ", show_alert=True)
        return
    if rec.get("status") != "pending":
        bot.answer_callback_query(call.id, f"ℹ️ Order នេះត្រូវបានដោះស្រាយរួចហើយ ({rec.get('status')})", show_alert=True)
        return
    uid = rec["uid"]
    price = rec["price"]
    update_pending_email_order(order_id, status="rejected")
    new_balance = update_balance(uid, price)  # សងលុយត្រឡប់ចូល wallet វិញ
    try:
        bot.send_message(
            uid,
            f"❌ ការកម្មង់ <b>{rec['product']}</b> (Email: <code>{html.escape(rec['email'])}</code>) "
            f"មិនអាចដំណើរការបានទេ។\n"
            f"💰 លុយ ${price:.2f} ត្រូវបានសងត្រឡប់ចូល Wallet វិញ (សមតុល្យថ្មី: ${new_balance:.2f})\n\n"
            f"សូមទាក់ទង Admin ប្រសិនបើមានចម្ងល់។",
        )
    except Exception:
        pass
    bot.answer_callback_query(call.id, "❌ បានបដិសេធ ហើយសងលុយត្រឡប់ជូន user រួចរាល់")
    try:
        base_text = call.message.caption or call.message.text or ""
        new_text = base_text + "\n\n❌ <b>បានបដិសេធ + សងលុយ</b>"
        if call.message.content_type == "text":
            bot.edit_message_text(new_text, chat_id=call.message.chat.id, message_id=call.message.message_id)
        else:
            bot.edit_message_caption(new_text, chat_id=call.message.chat.id, message_id=call.message.message_id)
    except Exception:
        pass


def handle_deposit(uid, chat_id, amount, user_obj, call=None):
    """• បើហាងនេះមាន Bakong ID ផ្ទាល់ខ្លួន (CAMRAPIDPAY_API_KEY កំណត់ហើយ) → auto KHQR + auto-detect
    • បើអត់មាន → ប្រើ QR ផ្ទាល់ខ្លួនដែល admin កំណត់ដោយដៃ + ឲ្យ user ផ្ញើវិក័យប័ត្រមកផ្ទៀងផ្ទាត់ដោយដៃ"""
    if not has_auto_bakong():
        handle_deposit_manual(uid, chat_id, amount, user_obj, call=call)
        return
    _handle_deposit_auto(uid, chat_id, amount, user_obj, call=call)


def _handle_deposit_auto(uid, chat_id, amount, user_obj, call=None):
    def _fail(err_text):
        if call:
            bot.answer_callback_query(call.id, err_text, show_alert=True)
        retry_kb = types.InlineKeyboardMarkup()
        retry_kb.add(pbtn(
            "🔁 ព្យាយាមម្តងទៀត", callback_data=f"paym_bkq_{amount}", style="primary"
        ))
        bot.send_message(chat_id, f"{err_text}\n\nសូមព្យាយាមម្តងទៀត បើ error នៅតែកើតឡើង ជា server ខាង gateway ខ្លួនឯងគាំង (មិនមែនកូដឯង)។", reply_markup=retry_kb)

    ref = f"KZDEP{uid}{int(time.time())}"[:50]
    ref_disp = f"DEP-{hashlib.md5(ref.encode()).hexdigest()[:8].upper()}"

    caption = (
        f"💰 Deposit <b>${amount:.2f}</b>\n💳 វិធីទូទាត់: <b>Bakong KHQR</b>\n🔖 <code>{ref_disp}</code>\n\n"
        f"📱 សូម Scan QR ខាងក្រោម (ឬចុចប៊ូតុងទំព័រទូទាត់) ដើម្បីបញ្ចូលលុយចូល Wallet\n"
        f"✅ ប្រព័ន្ធនឹង detect ស្វ័យប្រវត្តិ\n⏳ QR ផុតកំណត់ក្នុង ~5-10 នាទី"
    )

    data = camrapid_create(amount, ref)
    if not data:
        _fail(f"❌ មិនអាចបង្កើត QR បានទេ (Bakong KHQR)\n\nមូលហេតុ:\n{_last_camrapid_error[:180]}")
        return

    qr_string = data.get("qr_code", "")
    payment_url = data.get("payment_url", "")

    kb = None
    if payment_url:
        kb = types.InlineKeyboardMarkup()
        kb.add(pbtn("🔗 បើកទំព័រទូទាត់", url=payment_url, style="primary"))

    img_buf = build_qr_image(
        qr_string, amount=amount, ref=ref_disp,
        label="Wallet Top-Up", subtitle=f"{STORE_NAME} · Bakong KHQR",
    ) if qr_string else None
    photo = img_buf or None

    if photo:
        bot.send_photo(chat_id, photo, caption=caption, reply_markup=kb)
    elif payment_url:
        bot.send_message(chat_id, caption, reply_markup=kb)
    else:
        _fail("❌ គ្មានទិន្នន័យ QR ត្រឡប់មកទេ សូមព្យាយាមម្តងទៀត")
        return

    t = threading.Thread(
        target=poll_deposit,
        args=(uid, chat_id, amount, ref, public_user_label(user_obj)),
        kwargs={"checker": camrapid_check},
        daemon=True,
    )
    t.start()


def handle_deposit_manual(uid, chat_id, amount, user_obj, call=None):
    qr_file_id, qr_note = get_manual_qr()
    if not qr_file_id:
        text = (
            "⚠️ ហាងនេះមិនទាន់កំណត់ QR ទូទាត់ដោយដៃនៅឡើយទេ។\n"
            "សូមទាក់ទង Admin ដើម្បីដាក់លុយចូល Wallet ជូន។"
        )
        if call:
            bot.answer_callback_query(call.id, text, show_alert=True)
        else:
            bot.send_message(chat_id, text)
        try:
            bot.send_message(
                ADMIN_ID,
                f"🚨 <b>User ព្យាយាមដាក់លុយ ${amount:.2f} តែអ្នកមិនទាន់កំណត់ QR ទូទាត់ដោយដៃទេ!</b>\n"
                f"👤 {public_user_label(user_obj)} (<code>{uid}</code>)\n\n"
                f"សូមចុច 🖼 កំណត់ QR ទូទាត់ ដើម្បីកំណត់ QR របស់អ្នកជាមុនសិន។",
            )
        except Exception:
            pass
        return

    ref = f"KZDEP{uid}{int(time.time())}"[:50]
    ref_disp = f"DEP-{hashlib.md5(ref.encode()).hexdigest()[:8].upper()}"
    dep_id = ref_disp

    create_pending_deposit(dep_id, uid, amount, ref_disp)

    note_line = f"\nℹ️ {html.escape(qr_note)}\n" if qr_note else ""
    caption = (
        f"💰 Deposit <b>${amount:.2f}</b>\n💳 វិធីទូទាត់: <b>QR ផ្ទាល់ខ្លួនរបស់ហាង</b>\n🔖 <code>{ref_disp}</code>\n"
        f"{note_line}\n"
        f"📱 សូម Scan QR ខាងក្រោម ហើយផ្ទេរប្រាក់ <b>${amount:.2f}</b>\n"
        f"📸 <b>ផ្ញើ screenshot វិក័យប័ត្រ (receipt) ត្រឡប់មកវិញនៅសារបន្ទាប់</b> ដើម្បីឲ្យ Admin ត្រួតពិនិត្យ ហើយបញ្ចូលលុយចូល Wallet ជូន\n"
        f"⏳ ការបញ្ចូលលុយនឹងចំណាយពេលបន្តិច ព្រោះត្រូវផ្ទៀងផ្ទាត់ដោយ Admin ដោយផ្ទាល់ (មិនមែន auto ដូច Bakong ទេ)"
    )
    msg = bot.send_photo(chat_id, qr_file_id, caption=caption)
    bot.register_next_step_handler(msg, _deposit_receipt_step, uid, chat_id, amount, dep_id, user_obj)


def _deposit_receipt_step(message, uid, chat_id, amount, dep_id, user_obj):
    rec = get_pending_deposit(dep_id)
    if not rec or rec.get("status") != "pending":
        bot.send_message(chat_id, "❌ សំណើដាក់លុយនេះលែងមានសុពលភាពទៀតហើយ សូម /deposit ម្តងទៀត")
        return
    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    if not file_id:
        msg = bot.send_message(
            chat_id,
            "📸 សូមផ្ញើជា <b>រូបភាព (Photo/Screenshot)</b> នៃវិក័យប័ត្រ ដែលបញ្ជាក់ថាបានទូទាត់រួច សូមផ្ញើម្តងទៀត:",
        )
        bot.register_next_step_handler(msg, _deposit_receipt_step, uid, chat_id, amount, dep_id, user_obj)
        return

    update_pending_deposit(dep_id, receipt_file_id=file_id)
    bot.send_message(
        chat_id,
        "✅ បានទទួលវិក័យប័ត្ររបស់អ្នករួចហើយ។ សូមរង់ចាំ Admin ត្រួតពិនិត្យ ហើយបញ្ចូលលុយចូល Wallet ជូន (មិនយូរប៉ុន្មាន)។",
    )

    admin_kb = types.InlineKeyboardMarkup(row_width=2)
    admin_kb.add(
        pbtn(f"✅ បញ្ជាក់ +${amount:.2f}", callback_data=f"depapprove_{dep_id}", style="success"),
        pbtn("❌ បដិសេធ", callback_data=f"depreject_{dep_id}", style="danger"),
    )
    try:
        bot.send_photo(
            ADMIN_ID,
            file_id,
            caption=(
                f"📨 <b>វិក័យប័ត្រ Deposit ថ្មី</b>\n"
                f"👤 {public_user_label(user_obj)} (<code>{uid}</code>)\n"
                f"💵 ចំនួន: <b>${amount:.2f}</b>\n"
                f"🔖 <code>{rec.get('ref')}</code>\n\n"
                f"សូមផ្ទៀងផ្ទាត់ថាបានទទួលប្រាក់ពិតមុននឹងចុច 'បញ្ជាក់'។"
            ),
            reply_markup=admin_kb,
        )
    except Exception as e:
        print(f"[_deposit_receipt_step] failed to notify admin: {e}", flush=True)


def _handle_deposit_approve(call, dep_id):
    rec = get_pending_deposit(dep_id)
    if not rec:
        bot.answer_callback_query(call.id, "❌ រកមិនឃើញសំណើនេះទេ", show_alert=True)
        return
    if rec.get("status") != "pending":
        bot.answer_callback_query(call.id, f"ℹ️ សំណើនេះត្រូវបានដោះស្រាយរួចហើយ ({rec.get('status')})", show_alert=True)
        return
    uid = rec["uid"]
    amount = rec["amount"]
    new_balance = update_balance(uid, amount)
    update_pending_deposit(dep_id, status="approved")
    try:
        bot.send_message(
            uid,
            f"✅ ការទូទាត់ត្រូវបានបញ្ជាក់! បញ្ចូល <b>${amount:.2f}</b> ចូល wallet។\n"
            f"💰 សមតុល្យថ្មី: <b>${new_balance:.2f}</b>\n\n"
            f"🙏 អរគុណដែលទុកចិត្ត {STORE_NAME}!",
        )
    except Exception:
        pass
    notify_public(f"💰 <b>Deposit ជោគជ័យ!</b>\n👤 User ID: <code>{uid}</code>\n💵 ${amount:.2f}")
    bot.answer_callback_query(call.id, "✅ បានបញ្ជាក់ ហើយបញ្ចូលលុយចូល Wallet ជូនរួចរាល់")
    try:
        new_caption = (call.message.caption or "") + "\n\n✅ <b>បានបញ្ជាក់រួចរាល់</b>"
        bot.edit_message_caption(new_caption, chat_id=call.message.chat.id, message_id=call.message.message_id)
    except Exception:
        pass


def _handle_deposit_reject(call, dep_id):
    rec = get_pending_deposit(dep_id)
    if not rec:
        bot.answer_callback_query(call.id, "❌ រកមិនឃើញសំណើនេះទេ", show_alert=True)
        return
    if rec.get("status") != "pending":
        bot.answer_callback_query(call.id, f"ℹ️ សំណើនេះត្រូវបានដោះស្រាយរួចហើយ ({rec.get('status')})", show_alert=True)
        return
    uid = rec["uid"]
    amount = rec["amount"]
    update_pending_deposit(dep_id, status="rejected")
    try:
        bot.send_message(
            uid,
            f"❌ វិក័យប័ត្រ Deposit ${amount:.2f} របស់អ្នកមិនត្រូវបានបញ្ជាក់ទេ។\n"
            f"សូមទាក់ទង Admin ប្រសិនបើអ្នកគិតថាមានកំហុស ឬសាកល្បង /deposit ម្តងទៀត",
        )
    except Exception:
        pass
    bot.answer_callback_query(call.id, "❌ បានបដិសេធសំណើនេះ")
    try:
        new_caption = (call.message.caption or "") + "\n\n❌ <b>បានបដិសេធ</b>"
        bot.edit_message_caption(new_caption, chat_id=call.message.chat.id, message_id=call.message.message_id)
    except Exception:
        pass


# ------------------------------------------------------------------
# ADMIN COMMANDS
# ------------------------------------------------------------------
def slugify_key(name):
    key = name.strip().lower()
    key = re.sub(r"[^a-z0-9]+", "_", key)
    key = key.strip("_")
    return key or "product"


def unique_key(base_key, products):
    if base_key not in products:
        return base_key
    i = 2
    while f"{base_key}_{i}" in products:
        i += 1
    return f"{base_key}_{i}"


@bot.message_handler(commands=["addproduct"])
def cmd_addproduct(message):
    if not is_admin(message.from_user.id):
        return
    msg = bot.send_message(
        message.chat.id,
        "🆕 <b>បន្ថែម Product ថ្មី</b>\n\n1️⃣ សូមវាយ <b>ឈ្មោះ Product</b> ឧ. <code>Disney+ 1 Month</code>",
    )
    bot.register_next_step_handler(msg, addproduct_step_name)


def addproduct_step_name(message):
    if not is_admin(message.from_user.id):
        return
    name = message.text.strip()
    if not name:
        msg = bot.reply_to(message, "❌ ឈ្មោះមិនត្រឹមត្រូវ សូមវាយម្តងទៀត:")
        bot.register_next_step_handler(msg, addproduct_step_name)
        return
    products = load_products()
    key = unique_key(slugify_key(name), products)
    msg = bot.reply_to(
        message,
        f"🔑 key auto-generate: <code>{key}</code>\n\n"
        f"2️⃣ សូមវាយ <b>តម្លៃ</b> (ជាលេខ, USD) ឧ. <code>6</code>",
    )
    bot.register_next_step_handler(msg, addproduct_step_price, key, name)


def addproduct_step_price(message, key, name):
    if not is_admin(message.from_user.id):
        return
    try:
        price = float(message.text.strip())
    except ValueError:
        msg = bot.reply_to(message, "❌ តម្លៃត្រូវជាលេខ (ឧ. 6 ឬ 6.5) សូមវាយម្តងទៀត:")
        bot.register_next_step_handler(msg, addproduct_step_price, key, name)
        return
    msg = bot.reply_to(
        message,
        "3️⃣ សូមផ្ញើ <b>icon/emoji</b> សម្រាប់ app នេះ (ឧ. 🎬)\nឬវាយ <code>skip</code> ដើម្បីប្រើ 📦 លំនាំដើម",
    )
    bot.register_next_step_handler(msg, addproduct_step_icon, key, name, price)


def addproduct_step_icon(message, key, name, price):
    if not is_admin(message.from_user.id):
        return
    icon = message.text.strip()
    if icon.lower() == "skip" or not icon:
        icon = "📦"
    msg = bot.reply_to(
        message,
        "4️⃣ សូមជ្រើសរើស <b>របៀបប្រគល់ (Delivery)</b> សម្រាប់ product នេះ:\n\n"
        "<b>1</b> — 📦 Stock file (auto) — bot ប្រគល់ account ពី stock .txt ភ្លាមៗ ពេល user ទិញ\n"
        "<b>2</b> — 📧 Email (admin ដាក់ដោយដៃ) — user ផ្ញើ email គេផ្ទាល់មកឲ្យ bot, "
        "អ្នកដាក់ Premium/Invite ចូល email នោះផ្ទាល់ រួចចុច '✅ រួចរាល់' ដើម្បីជូនដំណឹង user\n\n"
        "សូមវាយ <code>1</code> ឬ <code>2</code>:",
    )
    bot.register_next_step_handler(msg, addproduct_step_delivery, key, name, price, icon)


def addproduct_step_delivery(message, key, name, price, icon):
    if not is_admin(message.from_user.id):
        return
    choice = message.text.strip()
    if choice not in ("1", "2"):
        msg = bot.reply_to(message, "❌ សូមវាយ <code>1</code> ឬ <code>2</code> តែប៉ុណ្ណោះ:")
        bot.register_next_step_handler(msg, addproduct_step_delivery, key, name, price, icon)
        return
    delivery_type = "stock" if choice == "1" else "email"
    msg = bot.reply_to(
        message,
        "5️⃣ សូមផ្ញើ <b>រូបភាព (Photo)</b> សម្រាប់ product នេះ (បង្ហាញឲ្យ user ឃើញពេលចុចមើល)\n"
        "ឬវាយ <code>skip</code> ដើម្បីរំលង (គ្មានរូបភាព):",
    )
    bot.register_next_step_handler(msg, addproduct_step_photo, key, name, price, icon, delivery_type)


def addproduct_step_photo(message, key, name, price, icon, delivery_type):
    if not is_admin(message.from_user.id):
        return
    photo_file_id = None
    if message.photo:
        photo_file_id = message.photo[-1].file_id
    elif (message.text or "").strip().lower() == "skip":
        photo_file_id = None
    else:
        msg = bot.reply_to(
            message,
            "❌ សូមផ្ញើជា <b>រូបភាព (Photo)</b> ឬវាយ <code>skip</code> ដើម្បីរំលង សូមព្យាយាមម្តងទៀត:",
        )
        bot.register_next_step_handler(msg, addproduct_step_photo, key, name, price, icon, delivery_type)
        return
    msg = bot.send_message(
        message.chat.id,
        "6️⃣ សូមវាយ <b>ការពិពណ៌នា (Description)</b> សម្រាប់ product នេះ (បង្ហាញឲ្យ user ឃើញ)\n"
        "ឬវាយ <code>skip</code> ដើម្បីរំលង (គ្មាន description):",
    )
    bot.register_next_step_handler(msg, addproduct_step_description, key, name, price, icon, delivery_type, photo_file_id)


def addproduct_step_description(message, key, name, price, icon, delivery_type, photo_file_id):
    if not is_admin(message.from_user.id):
        return
    text = (message.text or "").strip()
    if text.lower() == "skip" or not text:
        description = ""
    else:
        description = text[:900]  # កំណត់កុំឲ្យវែងហួស (Telegram photo caption កំណត់ 1024 តួ)

    products = load_products()
    products[key] = {
        "name": name,
        "price": price,
        "icon": icon,
        "delivery_type": delivery_type,
        "photo_file_id": photo_file_id,
        "description": description,
    }
    save_products(products)
    if delivery_type == "stock":
        if not os.path.exists(stock_path(key)):
            open(stock_path(key), "w").close()
        extra_hint = "👉 ឥឡូវចុចប៊ូតុង 📥 Stock ថ្មី ដើម្បីបញ្ចូល account ចូល stock"
        delivery_label = "📦 Stock file (Auto)"
    else:
        extra_hint = (
            "ℹ️ Product នេះ <b>មិនប្រើ stock file</b> ទេ — user ទិញរួច ផ្ញើ email គេផ្ទាល់ "
            "មកឲ្យ bot, អ្នកនឹងទទួលសារជូនដំណឹងភ្លាមៗ ដើម្បីដាក់ Premium ចូល email នោះដោយដៃ "
            "រួចចុច '✅ រួចរាល់' ដើម្បីជូនដំណឹង user។"
        )
        delivery_label = "📧 Email (Admin ដាក់ដោយដៃ)"

    summary = (
        f"✅ <b>Product បន្ថែមរួចរាល់!</b>\n\n"
        f"{icon} {name}\n"
        f"🔑 key: <code>{key}</code>\n"
        f"💵 តម្លៃ: ${price:.2f}\n"
        f"📮 Delivery: {delivery_label}\n"
        f"🖼 Photo: {'✅ មាន' if photo_file_id else '— គ្មាន'}\n"
        f"📝 Description: {html.escape(description) if description else '— គ្មាន'}\n\n"
        f"{extra_hint}"
    )
    if photo_file_id:
        bot.send_photo(message.chat.id, photo_file_id, caption=summary)
    else:
        bot.send_message(message.chat.id, summary)


@bot.message_handler(commands=["addstock"])
def cmd_addstock(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, key = message.text.split(" ", 1)
        key = key.strip()
        products = load_products()
        if key not in products:
            bot.reply_to(message, "❌ Product key មិនត្រឹមត្រូវ")
            return
        msg = bot.reply_to(message, f"📥 សូមផ្ញើ account list សំរាប់ '{products[key]['name']}'\n(មួយបន្ទាត់ = account មួយ)")
        bot.register_next_step_handler(msg, process_addstock, key)
    except Exception:
        bot.reply_to(message, "ទំរង់ត្រូវជា: /addstock key")


@bot.message_handler(commands=["delstock"])
def cmd_delstock(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, key = message.text.split(" ", 1)
        key = key.strip()
        products = load_products()
        if key not in products:
            bot.reply_to(message, "❌ Product key មិនត្រឹមត្រូវ")
            return
        total = stock_count(key)
        if total == 0:
            bot.reply_to(message, f"📭 '{products[key]['name']}' គ្មាន stock សល់ទេ។")
            return
        preview = peek_stock_items(key, limit=30)
        lines = [f"{i+1}. <code>{html.escape(it)}</code>" for i, it in enumerate(preview)]
        more_note = f"\n… និងមាន {total - len(preview)} ទៀត (មិនបានបង្ហាញ)" if total > len(preview) else ""
        msg = bot.reply_to(
            message,
            f"🗑 <b>លុប Stock — {products[key]['name']}</b> (សរុប {total})\n\n"
            + "\n".join(lines) + more_note +
            "\n\nសូមវាយបញ្ចូល <b>លេខ</b> ដែលចង់លុប (ឧ. <code>1,3,5</code>):",
        )
        bot.register_next_step_handler(msg, process_delstock_indices, key)
    except Exception:
        bot.reply_to(message, "ទំរង់ត្រូវជា: /delstock key")


def broadcast_new_stock(key, added_count):
    products = load_products()
    p = products.get(key)
    if not p or added_count <= 0:
        return 0, 0
    icon = resolve_icon(p.get("icon", "📦"))
    text = (
        f"➕ <b>ស្តុកថ្មីត្រូវបានបន្ថែមសម្រាប់ {p['name']}!</b>\n\n"
        f"📦 ថ្មីបន្ថែម: <b>{added_count} items</b>\n"
        f"📊 សរុបនៅសល់: <b>{stock_count(key)} items</b>\n"
        f"💰 តម្លៃ: <b>${p['price']:.2f}</b>"
    )
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(pbtn(f"{icon} {p['name'].upper()}", callback_data=f"buyopt_{key}", style="success"))
    users = load_users()
    sent, failed = 0, 0
    for uid in users:
        try:
            bot.send_message(int(uid), text, reply_markup=kb)
            sent += 1
        except Exception:
            failed += 1
    return sent, failed


def broadcast_price_change(key, old_price, new_price):
    products = load_products()
    p = products.get(key)
    if not p or new_price == old_price:
        return 0, 0
    icon = resolve_icon(p.get("icon", "📦"))
    if new_price < old_price:
        pct = round((old_price - new_price) / old_price * 100) if old_price else 0
        header = f"📉 <b>បញ្ចុះតម្លៃ! {p['name']} ថោកជាងមុន{f' {pct}%' if pct else ''}!</b>"
        cta = "🎉 ចាប់ឱកាសទិញឥឡូវ មុនតម្លៃឡើងវិញ!"
    else:
        header = f"📈 <b>តម្លៃថ្មី — {p['name']}</b>"
        cta = "ℹ️ តម្លៃត្រូវបានធ្វើបច្ចុប្បន្នភាព។"
    text = (
        f"{header}\n\n"
        f"💵 តម្លៃចាស់: <s>${old_price:.2f}</s>\n"
        f"💰 តម្លៃថ្មី: <b>${new_price:.2f}</b>\n\n"
        f"{cta}"
    )
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(pbtn(f"{icon} {p['name'].upper()} — ${new_price:.2f}", callback_data=f"buyopt_{key}", style="success"))
    users = load_users()
    sent, failed = 0, 0
    for uid in users:
        try:
            bot.send_message(int(uid), text, reply_markup=kb)
            sent += 1
        except Exception:
            failed += 1
    notify_public(
        f"{header}\n💵 <s>${old_price:.2f}</s> → 💰 <b>${new_price:.2f}</b>"
    )
    return sent, failed


def broadcast_low_stock(key, left):
    products = load_products()
    p = products.get(key)
    if not p:
        return 0, 0
    icon = resolve_icon(p.get("icon", "📦"))
    text = (
        f"🚨 <b>ស្តុកជិតអស់ហើយ — {p['name']}!</b>\n\n"
        f"📦 សល់តែ <b>{left} accounts</b> ប៉ុណ្ណោះ\n"
        f"💰 តម្លៃ: <b>${p['price']:.2f}</b>\n\n"
        f"⏳ សូមទិញឲ្យឆាប់មុនអស់ស្តុក!"
    )
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(pbtn(f"{icon} ទិញឥឡូវ — {p['name'].upper()}", callback_data=f"buyopt_{key}", style="success"))
    users = load_users()
    sent, failed = 0, 0
    for uid in users:
        try:
            bot.send_message(int(uid), text, reply_markup=kb)
            sent += 1
        except Exception:
            failed += 1
    notify_public(
        f"🚨 <b>ស្តុកជិតអស់ — {icon} {p['name']}!</b>\nសល់តែ {left} accounts ទៀតប៉ុណ្ណោះ 💵 ${p['price']:.2f}\n⏳ ទិញឲ្យឆាប់!"
    )
    return sent, failed


def process_addstock(message, key):
    if not is_admin(message.from_user.id):
        return
    items = message.text.split("\n")
    added = len([i for i in items if i.strip()])
    push_stock_items(key, items)
    products = load_products()
    if key in products and products[key].get("low_stock_alerted"):
        products[key]["low_stock_alerted"] = False
        save_products(products)
    bot.reply_to(message, f"✅ បន្ថែម {added} accounts ចូល stock '{key}'\n"
                           f"ស្តុករួម: {stock_count(key)}")
    sent, failed = broadcast_new_stock(key, added)
    bot.send_message(message.chat.id, f"📢 ជូនដំណឹងទៅ user {sent} នាក់ ({failed} បរាជ័យ)")


def process_delstock_indices(message, key):
    if not is_admin(message.from_user.id):
        return
    products = load_products()
    if key not in products:
        bot.reply_to(message, "❌ Product មិនត្រឹមត្រូវ (ប្រហែលជាត្រូវបានលុបទៅហើយ)")
        return
    raw = (message.text or "").strip()
    if not raw:
        bot.reply_to(message, "❌ សូមវាយបញ្ចូលលេខ (ឧ. 1,3,5)")
        return
    try:
        indices = [int(x.strip()) for x in raw.replace(" ", "").split(",") if x.strip()]
        if not indices:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "❌ ទំរង់មិនត្រឹមត្រូវ។ សូមវាយជាលេខ ខណ្ឌដោយ , (ឧ. 1,3,5)")
        return
    removed, remaining = remove_stock_items_by_indices(key, indices)
    if not removed:
        bot.reply_to(message, "❌ គ្មាន item ត្រូវនឹងលេខដែលអ្នកបញ្ចូលទេ (ប្រហែលជាលេខហួសព្រំដែន)")
        return
    lines = "\n".join(f"• <code>{html.escape(it)}</code>" for it in removed)
    bot.reply_to(
        message,
        f"✅ បានលុប {len(removed)} account ចេញពី stock '{products[key]['name']}':\n{lines}\n\n"
        f"📊 ស្តុកសល់: {remaining}",
    )


@bot.message_handler(commands=["lastqrerror"])
def cmd_lastqrerror(message):
    if not is_admin(message.from_user.id):
        return
    lines = []
    if _last_camrapid_error:
        lines.append(f"🔎 <b>CamRapidPay error ចុងក្រោយ:</b>\n<code>{html.escape(_last_camrapid_error)}</code>")
    bot.reply_to(message, "\n\n".join(lines) if lines else "✅ មិនទាន់មាន error QR ណាមួយកត់ត្រាទុកនៅឡើយទេ")


@bot.message_handler(commands=["stats"])
def cmd_stats(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    orders = load_orders()
    products = load_products()
    total_balance = sum(u["balance"] for u in users.values())

    lines = [
        "📊 <b>ស្ថិតិទូទៅ</b>",
        f"👥 អ្នកប្រើប្រាស់: {len(users)}",
        f"🛒 ការកម្មង់សរុប: {len(orders)}",
        f"💰 សមតុល្យសរុបក្នុងប្រព័ន្ធ: ${total_balance:.2f}",
        "",
        "📦 ស្តុកបច្ចុប្បន្ន:",
    ]
    for key, p in products.items():
        if p.get("delivery_type") == "email":
            stock_disp = "📧 Email (Unlimited)"
        else:
            stock_disp = f"{stock_count(key)} នៅសល់"
        lines.append(f"  • {p['name']}: {stock_disp} / លក់រួច {p.get('sold', 0)} accounts")
    bot.reply_to(message, "\n".join(lines))


@bot.message_handler(commands=["addbalance"])
def cmd_addbalance(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, payload = message.text.split(" ", 1)
        target_uid, amount = payload.split("|")
        new_balance = update_balance(int(target_uid.strip()), float(amount.strip()))
        bot.reply_to(message, f"✅ បន្ថែម ${amount.strip()} ចូល user {target_uid.strip()} (សមតុល្យថ្មី: ${new_balance:.2f})")
    except Exception:
        bot.reply_to(message, "ទំរង់ត្រូវជា:\n/addbalance user_id|amount\nឧ. /addbalance 123456789|10")


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(ADMIN_BTN_SETQR))
def reply_admin_setqr(message):
    if not is_admin(message.from_user.id):
        return
    _start_setqr_flow(message.chat.id)


@bot.message_handler(commands=["setqr"])
def cmd_setqr(message):
    if not is_admin(message.from_user.id):
        return
    _start_setqr_flow(message.chat.id)


def _start_setqr_flow(chat_id):
    qr_file_id, qr_note = get_manual_qr()
    status = "✅ បច្ចុប្បន្នមាន QR កំណត់រួចហើយ" if qr_file_id else "⚠️ បច្ចុប្បន្នមិនទាន់កំណត់ QR ណាមួយទេ"
    msg = bot.send_message(
        chat_id,
        f"🖼 <b>កំណត់ QR ទូទាត់ដោយដៃ</b>\n{status}\n\n"
        f"ប្រើសម្រាប់ deposit ករណីហាងគ្មាន Bakong ID ផ្ទាល់ខ្លួន (គ្មាន auto-detect) — "
        f"user scan QR នេះ ទូទាត់ រួចផ្ញើ screenshot មកឲ្យអ្នកបញ្ជាក់ដោយដៃ។\n\n"
        f"📸 សូមផ្ញើជា <b>រូបភាព (Photo)</b> នៃ QR ដែលអ្នកចង់ប្រើ (ABA/Wing/ACLEDA... QR អីក៏បាន):",
    )
    bot.register_next_step_handler(msg, admin_setqr_photo_step)


def admin_setqr_photo_step(message):
    if not is_admin(message.from_user.id):
        return
    if not message.photo:
        msg = bot.send_message(message.chat.id, "❌ សូមផ្ញើជា <b>រូបភាព (Photo)</b> នៃ QR មិនមែនឯកសារ/អត្ថបទទេ សូមផ្ញើម្តងទៀត:")
        bot.register_next_step_handler(msg, admin_setqr_photo_step)
        return
    qr_file_id = message.photo[-1].file_id
    msg = bot.send_message(
        message.chat.id,
        "✅ បានទទួលរូបភាព QR រួចហើយ។\n\n"
        "ℹ️ សូមវាយបញ្ចូល <b>ចំណាំបន្ថែម</b> ដែលចង់ឲ្យ user ឃើញរួមជាមួយ QR (ឧ. ឈ្មោះគណនី/លេខទូរស័ព្ទ)\n"
        "ឬវាយ <code>-</code> បើមិនចង់មានចំណាំបន្ថែម:",
    )
    bot.register_next_step_handler(msg, admin_setqr_note_step, qr_file_id)


def admin_setqr_note_step(message, qr_file_id):
    if not is_admin(message.from_user.id):
        return
    note = (message.text or "").strip()
    if note == "-":
        note = ""
    set_manual_qr(qr_file_id, note=note)
    bot.send_message(message.chat.id, "✅ បានកំណត់ QR ទូទាត់ដោយដៃរួចរាល់! User នឹងឃើញ QR នេះពេលចុច ➕ បញ្ចូលលុយ (ករណីគ្មាន Bakong auto-payment)។")


@bot.message_handler(func=lambda m: norm_label(m.text) == norm_label(ADMIN_BTN_SETNOTIFY))
def reply_admin_setnotify(message):
    if not is_admin(message.from_user.id):
        return
    _start_setnotify_flow(message.chat.id)


@bot.message_handler(commands=["setnotify"])
def cmd_setnotify(message):
    if not is_admin(message.from_user.id):
        return
    _start_setnotify_flow(message.chat.id)


def _notify_list_text():
    ids = get_notify_chat_ids()
    if not ids:
        return "⚠️ បច្ចុប្បន្នមិនទាន់មាន channel/group ជូនដំណឹងណាមួយទេ។"
    lines = "\n".join(f"├ <code>{i}</code>" for i in ids)
    return f"✅ បច្ចុប្បន្នមាន {len(ids)} កន្លែងជូនដំណឹង:\n{lines}"


def _start_setnotify_flow(chat_id):
    msg = bot.send_message(
        chat_id,
        f"🔔 <b>កំណត់ Channel/Group ជូនដំណឹង</b>\n{_notify_list_text()}\n\n"
        f"Bot នឹងផ្ញើសារជូនដំណឹងស្វ័យប្រវត្តិទៅទីនេះ ពេលមាន <b>deposit</b> ឬ <b>order</b> ជោគជ័យ។\n\n"
        f"📌 <b>របៀបបន្ថែម:</b> សូម <b>Forward</b> សារណាមួយពី channel/group ដែលអ្នកចង់បន្ថែម មកឲ្យ bot "
        f"(bot ត្រូវជា admin នៅក្នុងទីនោះជាមុនសិន)\n"
        f"🗑 <b>ដកចេញ:</b> វាយបញ្ចូល ID ចាស់ (ឧ. <code>-1001234567890</code>) ដើម្បីលុបចេញ\n"
        f"❌ វាយ <code>-</code> ដើម្បីបោះបង់",
    )
    bot.register_next_step_handler(msg, admin_setnotify_step)


def admin_setnotify_step(message):
    if not is_admin(message.from_user.id):
        return
    if (message.text or "").strip() == "-":
        bot.send_message(message.chat.id, "❌ បានបោះបង់។")
        return
    fwd = getattr(message, "forward_from_chat", None)
    if fwd is not None:
        chat_id = fwd.id
        title = getattr(fwd, "title", None) or str(chat_id)
        add_notify_chat_id(chat_id)
        bot.send_message(
            message.chat.id,
            f"✅ បានបន្ថែម <b>{title}</b> (<code>{chat_id}</code>) ជាកន្លែងជូនដំណឹងរួចរាល់!\n\n{_notify_list_text()}",
        )
        return
    text = (message.text or "").strip()
    try:
        chat_id = int(text)
    except ValueError:
        msg = bot.send_message(
            message.chat.id,
            "❌ មិនត្រឹមត្រូវទេ។ សូម Forward សារពី channel/group ឬវាយបញ្ចូល ID លេខ (ឧ. -1001234567890)។ សូមព្យាយាមម្តងទៀត:",
        )
        bot.register_next_step_handler(msg, admin_setnotify_step)
        return
    ids = get_notify_chat_ids()
    if chat_id in ids:
        remove_notify_chat_id(chat_id)
        bot.send_message(message.chat.id, f"🗑 បានដកចេញ <code>{chat_id}</code> ពីបញ្ជីជូនដំណឹងរួចរាល់!\n\n{_notify_list_text()}")
    else:
        add_notify_chat_id(chat_id)
        bot.send_message(message.chat.id, f"✅ បានបន្ថែម <code>{chat_id}</code> ជាកន្លែងជូនដំណឹងរួចរាល់!\n\n{_notify_list_text()}")


# ------------------------------------------------------------------
# KEEP-ALIVE (Flask, សម្រាប់ deploy លើ Render — binding port ចាំបាច់)
# ------------------------------------------------------------------
def start_keep_alive():
    from flask import Flask, request as flask_request
    app = Flask(__name__)

    @app.route("/")
    def home():
        return f"{STORE_NAME} Bot is running ✅"

    @app.route("/camrapid-webhook", methods=["POST", "GET"])
    def camrapid_webhook():
        # CamRapidPay ហៅ endpoint នេះពេលទូទាត់ជោគជ័យ។ bot ប្រើ polling (camrapid_check)
        # ជាចម្បងរួចហើយ ដូច្នេះទីនេះគ្រាន់តែ log ចោល និង return 200 ដើម្បីបំពេញលក្ខខណ្ឌ webhook_url។
        try:
            print(f"[camrapid_webhook] {flask_request.get_json(silent=True) or flask_request.args}", flush=True)
        except Exception:
            pass
        return {"success": True}, 200

    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080))),
        daemon=True,
    ).start()


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise SystemExit("❌ សូម set environment variable BOT_TOKEN ជាមុនសិន")
    start_keep_alive()
    print("🤖 Bot កំពុងដំណើរការ...")
    while True:
        try:
            bot.infinity_polling(skip_pending=True)
        except Exception as e:
            print(f"[MAIN] infinity_polling crashed: {e}", flush=True)
            notify_admin_error("main polling loop (bot បានផ្អាកបណ្តោះអាសន្ន ហើយកំពុង restart)", e)
            time.sleep(5)
