# BizGuru — Business-only Telegram Bot

## Step 1: Telegram Bot Token lo (agar nahi hai)
1. Telegram me `@BotFather` ko search karo, chat kholo
2. `/newbot` bhejo
3. Bot ka naam do (jaise: BizGuru)
4. Username do jo `bot` se end ho (jaise: bizguru_helper_bot)
5. Tumhe ek TOKEN milega, isse copy karke rakho — kisi se share mat karna

## Step 2: Gemini API Key lo (FREE)
1. https://aistudio.google.com/apikey pe jao
2. Google account se login karo
3. "Create API Key" pe click karo — credit card nahi chahiye
4. Key copy kar lo

## Step 3: Railway pe FREE deploy karo
1. https://railway.app pe jaake GitHub se signup karo
2. Is poore folder (`business_bot`) ko GitHub pe ek naya repo bana ke upload karo
   - GitHub.com pe "New repository" > naam do > "uploading an existing file" se ye saare files daal do
3. Railway pe "New Project" > "Deploy from GitHub repo" > apna repo select karo
4. Railway automatically Procfile dekh ke bot ko chalu kar dega
5. Railway project ke "Variables" tab me jaake ye 2 environment variables add karo:
   - `TELEGRAM_TOKEN` = tumhara BotFather wala token
   - `GEMINI_API_KEY` = tumhari Gemini key
6. Deploy hone do (1-2 min lagega), fir Telegram me apne bot ko `/start` bhejo

Railway free tier me $5 free credit milta hai monthly jo ek chhote bot ke liye kaafi hai.

## Step 4 (Alternative): Apne computer pe chalao
```bash
pip install -r requirements.txt
export TELEGRAM_TOKEN="tumhara_token"
export GEMINI_API_KEY="tumhari_key"
python bot.py
```
(Windows me `export` ki jagah `set` use karo)
Note: computer band karoge toh bot bhi band ho jayega — 24/7 ke liye Railway/Render better hai.

## Bot Commands
- `/start` — welcome message
- `/idea` — turant ek business idea suggest karwao
- `/reset` — chat history clear karo, fresh baat shuru karo
- Normal message — kuch bhi business-related poochho, bot reply karega

## Customize karna ho
`bot.py` file me `SYSTEM_PROMPT` variable edit karke bot ka tone, rules, ya focus area badal sakte ho.
