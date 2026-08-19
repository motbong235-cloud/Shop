# Premium Shop Bot — Deploy លើ Render

## Files
- `premium_shop_bot_v15.py` — កូដ bot ចម្បង (រត់ដោយ `python premium_shop_bot_v15.py`)
- `requirements.txt` — library ដែលត្រូវការ
- `render.yaml` — Blueprint សម្រាប់ deploy ស្វ័យប្រវត្តិ (New + → Blueprint → ភ្ជាប់ repo នេះ)

## ជំហាន Deploy

1. **Push code** ទាំងអស់ (3 files ខាងលើ) ចូល GitHub repo ថ្មី
2. លើ Render Dashboard → **New +** → **Blueprint** → ជ្រើសរើស repo នេះ (Render នឹងអាន `render.yaml` ស្វ័យប្រវត្តិ ព្រមទាំងបង្កើត Persistent Disk `/var/data` ជូន)
3. Render នឹងសួរឲ្យបំពេញ Environment Variables ខាងក្រោម (ចាំបាច់):
   - `BOT_TOKEN` — Token ពី @BotFather
   - `ADMIN_ID` — Telegram user id របស់អ្នក (លេខ)
   - `CAMRAPIDPAY_API_KEY` — API key CamRapidPay (បើមាន Bakong ID ផ្ទាល់ខ្លួន — បើគ្មាន អាចទុកទទេ ហើយប្រើ QR ដោយដៃ `/setqr` ជំនួសវិញ)
4. ចុច **Apply** — Render នឹង build + deploy ភ្លាមៗ

## Environment Variables ស្រេចចិត្តបន្ថែម (មិនចាំបាច់)
- `STORE_NAME` — ឈ្មោះហាង (default: Kairozen Store)
- `REFERRAL_PERCENT` — % commission referral (default: 5)
- `LOW_STOCK_THRESHOLD` — ចំនួន stock ត្រូវជូនដំណឹងជិតអស់ (default: 3)
- `BOT_RENTAL_PER_DAY` — តម្លៃជួល Bot ក្នុងមួយថ្ងៃ (default: 0.15)
- `NOTIFY_CHAT_IDS` — channel/group id (comma-separated) ដែលចង់ឲ្យ bot ផ្ញើសារជូនដំណឹងសាធារណៈ
- `PUBLIC_BASE_URL` — ជាធម្មតា Render ដាក់ `RENDER_EXTERNAL_URL` ជូនស្វ័យប្រវត្តិ មិនចាំបាច់កំណត់ដោយដៃ

## ចម្លង Data ចាស់ (បើផ្លាស់ពី server ចាស់)
Data (users.json, products.json, stock/*.txt ។ល។) ស្ថិតនៅ `/var/data` លើ server ចាស់។
ត្រូវទាញ file ទាំងនោះចេញពី Persistent Disk ចាស់ (Render Shell ឬ SCP) រួចដាក់ត្រង់
`/var/data` របស់ service ថ្មី **មុននឹង** bot ចាប់ផ្តើមដំណើរការលើកដំបូង។

## ពិនិត្យក្រោយ deploy
- `/start` លើ bot Telegram — ត្រូវឃើញម៉ឺនុយ reply keyboard ពេញលេញ
- `/stats` (admin) — ត្រួតពិនិត្យស្ថិតិ user/stock
- `/setqr` (admin) — កំណត់ QR ទូទាត់ដោយដៃ បើគ្មាន Bakong ID
- `/setupemoji` (admin) — ភ្ជាប់ Premium Emoji (ស្រេចចិត្ត, ត្រូវការ Telegram Premium)
