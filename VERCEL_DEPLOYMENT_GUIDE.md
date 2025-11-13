# 🚀 Vercel Deployment Guide - Bitcoin Trading System

## 📋 Overview

This guide explains how to deploy your Bitcoin trading system using:
- **Frontend** → Vercel (React app)
- **Backend** → Railway/Render (FastAPI + WebSocket)

## 🎯 Why This Split?

- **Vercel** is perfect for static/serverless frontends but has limited WebSocket support
- **Railway/Render** are better for long-running servers with WebSocket connections
- This setup gives you the best of both worlds!

---

## Part 1: Deploy Backend to Railway (Recommended)

### **Step 1: Create Railway Account**

1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Connect your GitHub account

### **Step 2: Deploy Backend**

1. Click "New Project"
2. Choose "Deploy from GitHub repo"
3. Select: `IliyaMar22/btc_position_check_fetch`
4. Railway will auto-detect Python

### **Step 3: Configure Backend**

Add these environment variables in Railway:
```
PORT=8123
```

Railway will automatically:
- Install dependencies from `requirements_backend_api.txt`
- Run `python3 btc_trading_api.py`
- Provide a public URL like: `https://your-app.railway.app`

### **Step 4: Get Your Backend URL**

After deployment, Railway provides:
- **HTTP URL**: `https://your-app-xxx.railway.app`
- **WebSocket**: `wss://your-app-xxx.railway.app/ws`

Save these URLs! You'll need them for the frontend.

---

## Part 2: Deploy Frontend to Vercel

### **Step 1: Install Vercel CLI**

```bash
npm install -g vercel
```

### **Step 2: Login to Vercel**

```bash
vercel login
```

### **Step 3: Configure Environment Variables**

Create a file `.env.production` in `btc-trading-frontend/`:

```bash
cd btc-trading-frontend
cat > .env.production << EOF
REACT_APP_API_URL=https://your-app-xxx.railway.app
REACT_APP_WS_URL=wss://your-app-xxx.railway.app/ws
EOF
```

**Replace** `your-app-xxx.railway.app` with your actual Railway URL!

### **Step 4: Deploy to Vercel**

From the `btc-trading-frontend` directory:

```bash
cd btc-trading-frontend
vercel --prod
```

Follow the prompts:
- **Set up and deploy?** → Yes
- **Which scope?** → Your account
- **Link to existing project?** → No
- **Project name?** → `btc-trading-dashboard` (or any name)
- **Directory?** → `./` (current directory)
- **Override settings?** → No

Vercel will:
1. Build your React app
2. Deploy to their CDN
3. Provide a URL like: `https://btc-trading-dashboard.vercel.app`

---

## Part 3: Alternative - Deploy Frontend via Vercel Dashboard

### **Step 1: Go to Vercel Dashboard**

1. Visit [vercel.com](https://vercel.com)
2. Click "Add New" → "Project"
3. Import from GitHub: `IliyaMar22/btc_position_check_fetch`

### **Step 2: Configure Project**

- **Framework Preset**: Create React App
- **Root Directory**: `btc-trading-frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `build`

### **Step 3: Add Environment Variables**

In Vercel dashboard, add:
```
REACT_APP_API_URL = https://your-app-xxx.railway.app
REACT_APP_WS_URL = wss://your-app-xxx.railway.app/ws
```

### **Step 4: Deploy**

Click "Deploy" and wait 2-3 minutes!

---

## Part 4: Update Backend CORS Settings

Your backend needs to allow requests from Vercel.

Edit `btc_trading_api.py` and update CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3124",
        "http://localhost:3000",
        "https://btc-trading-dashboard.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then push to GitHub and Railway will auto-deploy the update!

---

## 📊 Testing Your Deployment

### **Frontend (Vercel)**
Visit: `https://btc-trading-dashboard.vercel.app`

You should see:
- ✅ Loading screen
- ✅ Dashboard with position cards
- ✅ Live price updates
- ✅ WebSocket connection (green dot)

### **Backend (Railway)**
Visit: `https://your-app-xxx.railway.app/docs`

You should see:
- ✅ FastAPI documentation
- ✅ API endpoints
- ✅ WebSocket endpoint

### **Test WebSocket**
In browser console:
```javascript
const ws = new WebSocket('wss://your-app-xxx.railway.app/ws');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (e) => console.log('Data:', JSON.parse(e.data));
```

---

## 🔧 Configuration Summary

### **Frontend Environment Variables (Vercel)**
```
REACT_APP_API_URL=https://your-backend.railway.app
REACT_APP_WS_URL=wss://your-backend.railway.app/ws
```

### **Backend Environment Variables (Railway)**
```
PORT=8123
```

### **Config File** (`btc-trading-frontend/src/config.ts`)
```typescript
export const API_CONFIG = {
  API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8123',
  WS_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8123/ws',
};
```

---

## 🚀 Deployment Workflow

### **For Updates:**

1. **Update Code Locally**
   ```bash
   git add .
   git commit -m "Update: description"
   git push origin main
   ```

2. **Railway Auto-Deploys Backend**
   - Watches GitHub repo
   - Auto-deploys on push
   - Takes 1-2 minutes

3. **Vercel Auto-Deploys Frontend**
   - Watches GitHub repo
   - Auto-deploys on push
   - Takes 2-3 minutes

### **Manual Deployment:**

**Frontend Only:**
```bash
cd btc-trading-frontend
vercel --prod
```

**Backend:**
Railway auto-deploys, or use Railway CLI:
```bash
railway up
```

---

## 💡 Alternative Backend Hosting Options

### **Option 1: Railway** (Recommended)
- ✅ Easy setup
- ✅ Auto-deploy from GitHub
- ✅ WebSocket support
- ✅ Free tier available
- 💰 ~$5/month after free tier

### **Option 2: Render**
- ✅ WebSocket support
- ✅ Auto-deploy
- ✅ Free tier (sleeps after inactivity)
- 💰 $7/month for always-on

### **Option 3: Heroku**
- ✅ Reliable
- ✅ WebSocket support
- 💰 ~$7/month (no free tier anymore)

### **Option 4: DigitalOcean App Platform**
- ✅ Full control
- ✅ WebSocket support
- 💰 $5/month

### **Option 5: AWS/Azure/GCP**
- ✅ Most powerful
- ⚠️ More complex setup
- 💰 Pay as you go

---

## 📁 Repository Structure for Deployment

```
btc_position_check_fetch/
├── btc-trading-frontend/          ← Vercel deploys this
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vercel.json                ← Vercel config
│   └── .env.production            ← Production env vars
│
├── btc_trading_api.py             ← Railway deploys this
├── requirements_backend_api.txt   ← Backend dependencies
└── railway.json                   ← (optional) Railway config
```

---

## 🔍 Troubleshooting

### **Frontend shows "Cannot connect to backend"**

**Check:**
1. Is backend running? Visit backend URL in browser
2. Are environment variables set correctly in Vercel?
3. Is CORS configured on backend?
4. Check browser console for errors

**Fix:**
```bash
# Rebuild frontend with correct env vars
cd btc-trading-frontend
vercel --prod
```

### **WebSocket not connecting**

**Check:**
1. Use `wss://` not `ws://` for production
2. Backend logs for WebSocket errors
3. Browser console for connection errors

**Fix:**
Update `REACT_APP_WS_URL` to use `wss://`

### **Backend crashes or restarts**

**Check:**
1. Railway logs: `railway logs`
2. Memory usage (upgrade plan if needed)
3. Python dependencies installed correctly

### **CORS Errors**

**Fix:**
Add your Vercel URL to backend CORS settings:
```python
allow_origins=["https://your-app.vercel.app", "https://*.vercel.app"]
```

---

## 📊 Cost Estimate

### **Free Tier (Perfect for Testing)**
- **Vercel**: Free (100GB bandwidth/month)
- **Railway**: $5 free credit/month
- **Total**: Free for light usage!

### **Paid (For Production)**
- **Vercel**: Free for frontend
- **Railway**: ~$5-10/month for backend
- **Total**: ~$5-10/month

### **Custom Domain (Optional)**
- **Domain**: $10-15/year
- **SSL**: Free (Vercel & Railway provide)

---

## 🎉 Success Checklist

- [ ] Backend deployed to Railway
- [ ] Backend URL obtained
- [ ] Frontend configured with backend URL
- [ ] Frontend deployed to Vercel
- [ ] CORS configured on backend
- [ ] WebSocket connection working
- [ ] Position data loading correctly
- [ ] Real-time updates functioning
- [ ] Mobile responsive
- [ ] Custom domain added (optional)

---

## 🌐 Final URLs

After deployment, you'll have:

**Production:**
- Frontend: `https://btc-trading-dashboard.vercel.app`
- Backend: `https://your-app-xxx.railway.app`
- API Docs: `https://your-app-xxx.railway.app/docs`

**Development:**
- Frontend: `http://localhost:3124`
- Backend: `http://localhost:8123`

---

## 🚀 Quick Deployment Commands

```bash
# 1. Deploy backend (Railway CLI)
railway login
railway init
railway up

# 2. Deploy frontend (Vercel CLI)
cd btc-trading-frontend
vercel --prod

# 3. Update and redeploy both
git add .
git commit -m "Update"
git push origin main
# Both auto-deploy!
```

---

## 📝 Need Help?

1. **Vercel Docs**: https://vercel.com/docs
2. **Railway Docs**: https://docs.railway.app
3. **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
4. **React Deployment**: https://create-react-app.dev/docs/deployment/

---

**Your Bitcoin trading system is ready for the world! 🚀📈**

