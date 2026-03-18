# NexChat — Flask Web App

A WhatsApp-style 2-user private chat app built with Python + Flask.

---

## 📁 File Structure

```
nexchat/
├── app.py               ← Flask backend
├── requirements.txt     ← Dependencies
├── Procfile             ← For Railway / Render hosting
├── templates/
│   └── index.html       ← Full frontend (single page)
└── nexchat.db           ← Auto-created SQLite database
```

---

## 💻 Run Locally on Windows

**Step 1 — Install Python**
Download Python 3.10+ from https://python.org (check "Add to PATH" during install)

**Step 2 — Open a terminal in the nexchat folder**
```
cd path\to\nexchat
```

**Step 3 — Install dependencies**
```
pip install -r requirements.txt
```

**Step 4 — Run the app**
```
python app.py
```

**Step 5 — Open in browser**
```
http://localhost:5000
```

Open in two different browser windows (or browsers) to chat as both users.

---

## 🔑 Login Credentials

| Username | Password  |
|----------|-----------|
| Alice    | alice123  |
| Bob      | bob123    |

To change these: open `app.py`, find the `init_db()` function, and edit the `users` list.
Then delete `nexchat.db` and restart the app.

---

## ☁️ Free Hosting — Railway (Recommended)

Railway is the easiest free host for Flask apps.

**Step 1 — Create accounts**
- GitHub: https://github.com (free)
- Railway: https://railway.app (free, login with GitHub)

**Step 2 — Push to GitHub**
```bash
git init
git add .
git commit -m "initial commit"
# Create a new repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/nexchat.git
git push -u origin main
```

**Step 3 — Deploy on Railway**
1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your nexchat repository
4. Railway auto-detects the Procfile and deploys
5. Click "Generate Domain" under Settings → Networking
6. Your app is live at `https://nexchat-xxx.up.railway.app`

**Step 4 — Set SECRET_KEY (optional but recommended)**
In Railway → Variables, add:
```
SECRET_KEY = any-random-string-you-choose
```

---

## ☁️ Free Hosting — Render (Alternative)

1. Push code to GitHub (same as above)
2. Go to https://render.com → New Web Service
3. Connect your GitHub repo
4. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Deploy — get a free `.onrender.com` URL

---

## ☁️ Free Hosting — PythonAnywhere (No GitHub needed)

1. Sign up at https://pythonanywhere.com (free)
2. Go to Dashboard → Files → Upload nexchat folder files
3. Open a Bash console:
   ```bash
   pip3 install flask gunicorn --user
   ```
4. Go to Web tab → Add a new web app
5. Choose Flask, Python 3.10
6. Set source code path to `/home/YOURUSERNAME/nexchat`
7. In WSGI config file, point to `app:app`
8. Reload → your app is live at `YOURUSERNAME.pythonanywhere.com`

---

## ⚠️ Important Notes

- **SQLite on hosted platforms**: The database file (`nexchat.db`) resets every time Railway/Render redeploys. For persistent storage, upgrade to PostgreSQL (Railway provides one free). For now, this is fine for testing.
- **Two users at once**: Both Alice and Bob can be logged in simultaneously from different devices/browsers.
- **Clear history**: Click ⋮ → "Clear Chat History" — deletes all messages for both users.

---

## ✨ Features

- 🔐 Username + password login (SHA-256 hashed)  
- ✓ Sent / ✓✓ Delivered / ✓✓ Read ticks (blue when read)  
- 🟢 Online / last seen status  
- 🗑 Clear chat history with confirmation  
- 🚪 Logout and switch users  
- 📱 Mobile-friendly WhatsApp-style dark UI  
- ⚡ Auto-refreshes every 1.5 seconds  
