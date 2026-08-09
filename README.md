# GhostFrame Chat v2 // Vex

**Real conversational AI for ethical hacking research.**
No OpenAI API. No Ollama. Self-hosted open-source LLM on Railway.

## What This Is

A chat app where you type anything and **Vex** (your fictional netrunner AI) replies naturally — like ChatGPT, but:
- Runs a real **Qwen2.5-0.5B-Instruct** transformer model (500M params)
- Searches **TryHackMe, OWASP, PortSwigger, CVE, GitHub** before answering
- Uses **terminal tools** (`lynx`, `whois`, `dig`, `curl`) to extract intel
- **Validates code syntax** in its own replies before sending them to you
- **No API keys** — pure Python, open-source, self-hosted

## Architecture

```
┌─────────────┐      HTTP/JSON      ┌──────────────────────────────┐
│ Android APK │ ◄─────────────────► │ Railway.app Backend          │
│ (Kivy Chat) │                     │ • Qwen 0.5B AI (llama-cpp)   │
│             │                     │ • RAG search (5+ sites)      │
│ [You]       │                     │ • Terminal tools (lynx/dig)  │
│ how does    │                     │ • Code validator (AST/black) │
│ XSS work?   │                     │ • Vex persona (system prompt)│
│             │                     │                              │
│ [Vex]       │                     │ Fallback mode if RAM < 512MB │
│ XSS is...   │                     │ (still fully functional)     │
└─────────────┘                     └──────────────────────────────┘
```

**Backend and APK are completely separate.**
You deploy the backend to Railway, get the public URL, paste it into the APK code, then build the APK in UserLAnd.

## How It Works

1. **You type** in the APK chat: *"teach me XSS and give me a scanner"*
2. **Backend receives** your message
3. **RAG Engine** searches PortSwigger, OWASP, TryHackMe, CVE, GitHub
4. **Terminal Tools** enhance data:
   - `lynx -dump` converts messy HTML to clean text
   - `whois` / `dig` run if you mention a domain
   - `curl` fetches pages that block bots
5. **AI Brain** loads context + Vex persona → generates natural reply
6. **Code Validator** scans the reply for ```python blocks, fixes syntax errors, replaces bad code with clean code
7. **Reply streams back** to your APK as a chat bubble from Vex

## File Structure

```
ghostframe-chat-v2/
├── backend/              # Deploy to Railway
│   ├── main.py           # FastAPI chat endpoint
│   ├── Dockerfile        # Terminal tools + model download
│   ├── requirements.txt
│   ├── railway.json
│   └── core/
│       ├── llm_engine.py     # Qwen 0.5B inference
│       ├── rag_engine.py     # Multi-site scraper + terminal tools
│       ├── code_validator.py # AST + py_compile + black
│       └── persona.py        # Vex system prompt + fallback
├── frontend/             # Build to APK
│   ├── main.py           # Kivy chat UI
│   └── buildozer.spec
├── scripts/
│   ├── setup_userland.sh   # UserLAnd env setup
│   └── build_apk.sh        # APK compiler script
└── README.md
```

## Step 1: Deploy Backend to Railway

```bash
cd ghostframe-chat-v2/backend
git init
git add .
git commit -m "GhostFrame v2 backend"
git branch -M main
git remote add origin https://github.com/YOURNAME/ghostframe-backend.git
git push -u origin main
```

Then:
1. Go to railway.com → New Project → Deploy from GitHub
2. Select your repo
3. Railway reads Dockerfile, installs terminal tools, downloads AI model
4. First deploy: ~10-15 mins (model download + build)
5. Go to Settings → Networking → Generate Domain
6. Copy your public URL: `https://ghostframe-xxx.up.railway.app`

## Step 2: Connect APK to Backend

Open `frontend/main.py` and replace:

```python
BACKEND_URL = "https://your-app.up.railway.app"
```

with your actual Railway URL.

## Step 3: UserLAnd Setup (Android)

Install UserLAnd from Play Store, create an Ubuntu container.

```bash
# Inside UserLAnd Ubuntu
cd /sdcard/Download
unzip ghostframe-chat-v2.zip
cd ghostframe-chat-v2
bash scripts/setup_userland.sh
```

This installs: Python, JDK, build tools, Buildozer, Kivy.

## Step 4: Build the APK

```bash
# Still inside UserLAnd Ubuntu
bash scripts/build_apk.sh
```

**First build:** 20-40 minutes (downloads Android SDK/NDK).
**After:** ~2 minutes.

Your APK: `~/ghostframe-apk/bin/ghostframe-2.0-*.apk`

Copy to phone:
```bash
cp ~/ghostframe-apk/bin/*.apk /sdcard/Download/
```

Then install from your Downloads app.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Health + AI load status |
| `GET /health` | Detailed health check |
| `POST /chat` | Main chat endpoint — send `{"message": "..."}` |

## Terminal Tools on Backend

These are installed in the Railway container to help the AI gather better intel:

| Tool | Purpose |
|------|---------|
| `lynx -dump` | Convert HTML → clean plain text (beats scrapers) |
| `curl -L` | Fetch pages with redirect following |
| `whois` | Domain registration intel |
| `dig +short` | DNS records, IP lookups |
| `host` | DNS resolution |

## Customizing Vex

Edit `backend/core/persona.py`:

```python
self.name = "Zero"  # Change name
```

Or modify the system prompt string to change personality, tone, slang, etc.

## Fallback Mode

If Railway's 512MB free tier can't load the 280MB AI model, the backend automatically switches to **fallback mode**:
- Still searches all 5+ sites
- Still uses terminal tools
- Still validates code syntax
- Vex still replies in-character using templates
- **Fully functional** — just without the AI generating prose

To enable full AI mode, upgrade Railway to a paid tier (1GB+ RAM).

## Disclaimer

**For educational and authorized testing only.**
All code templates include safety comments. Only use on systems you own or have explicit written permission to test.

## License

MIT — hack responsibly.
