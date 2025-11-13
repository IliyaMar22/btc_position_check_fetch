# 🚂 Railway Full-Stack Deployment Guide

Deploy your entire Bitcoin Trading System on Railway in **5 minutes**!

---

## 🎯 **Why Railway for Everything?**

✅ **Simpler**: One platform for frontend + backend  
✅ **No CORS Issues**: Everything on same domain  
✅ **WebSocket Support**: Full persistent connection support  
✅ **Auto-Deploy**: Push to GitHub → automatic deployment  
✅ **Cost-Effective**: ~$5-10/month for everything  
✅ **Fast**: Low latency between frontend and backend  

---

## 📋 **Prerequisites**

- GitHub account
- Railway account (sign up at https://railway.app)
- Git installed locally
- Your code pushed to GitHub

---

## 🚀 **Deployment Steps**

### **Step 1: Push Code to GitHub** ✅ (Already Done!)

Your code is already at:
```
https://github.com/IliyaMar22/btc_position_check_fetch
```

### **Step 2: Deploy to Railway** (5 minutes)

1. **Go to Railway**
   ```
   https://railway.app
   ```

2. **Sign in with GitHub**
   - Click "Login" → "Login with GitHub"
   - Authorize Railway

3. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose: `IliyaMar22/btc_position_check_fetch`

4. **Railway Auto-Configures!** 🎉
   - Railway detects Python + Node.js
   - Reads `nixpacks.toml` configuration
   - Automatically:
     - Installs Python dependencies
     - Installs Node.js dependencies
     - Builds React frontend
     - Starts FastAPI backend

5. **Wait for Deployment** (~2-3 minutes)
   - Watch the build logs
   - You'll see:
     ```
     ✓ Installing Python packages...
     ✓ Installing Node.js packages...
     ✓ Building React app...
     ✓ Starting server...
     ✓ Deployment successful!
     ```

6. **Get Your URL**
   - Railway assigns a URL like:
     ```
     https://btc-trading-production.up.railway.app
     ```
   - Click "Generate Domain" if needed

7. **Test It!**
   - Open your URL
   - You should see the Bitcoin Trading Dashboard! 🎉

---

## 🌐 **Your Deployed URLs**

After deployment, you'll have:

```
🌍 Main App:     https://your-app.railway.app
📊 Dashboard:    https://your-app.railway.app/
📡 API Docs:     https://your-app.railway.app/docs
🔌 WebSocket:    wss://your-app.railway.app/ws
💓 Health Check: https://your-app.railway.app/api/health
```

**Everything on ONE domain!** No CORS issues! 🎉

---

## ⚙️ **Configuration**

### **Environment Variables** (Optional)

Railway automatically sets:
- `PORT` - Railway assigns this
- `NODE_ENV` - Set to "production"
- `ENVIRONMENT` - Set to "production"

You can add custom variables in Railway dashboard:
1. Go to your project
2. Click "Variables" tab
3. Add any custom settings

### **What Railway Does Automatically**

1. **Detects Python** → Installs from `requirements_backend_api.txt`
2. **Detects Node.js** → Installs from `package.json`
3. **Builds Frontend** → Runs `npm run build`
4. **Starts Backend** → Runs `python3 btc_trading_api.py`
5. **Serves Both** → Backend serves API + frontend static files

---

## 🔄 **Auto-Deploy Setup**

### **Enable Auto-Deploy from GitHub**

1. In Railway project settings
2. Go to "Deployments" tab
3. Enable "Auto-deploy on push"
4. Select branch (usually `main`)

Now every time you push to GitHub:
```bash
git add .
git commit -m "Update features"
git push
```
→ Railway automatically redeploys! 🚀

---

## 📊 **How It Works**

```
┌─────────────────────────────────────────┐
│         Railway Platform                │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │   Single Deployment                │ │
│  │                                    │ │
│  │  1. Build Phase:                  │ │
│  │     ├── Install Python deps       │ │
│  │     ├── Install Node.js deps      │ │
│  │     └── Build React app           │ │
│  │                                    │ │
│  │  2. Runtime:                      │ │
│  │     ├── FastAPI Server (Port)     │ │
│  │     ├── ├─ /api/*  → Backend     │ │
│  │     ├── ├─ /ws     → WebSocket   │ │
│  │     └── └─ /*      → Frontend    │ │
│  │                                    │ │
│  └────────────────────────────────────┘ │
│                                          │
│  URL: https://your-app.railway.app      │
└─────────────────────────────────────────┘
```

---

## 💰 **Pricing**

Railway uses usage-based pricing:

**Free Tier:**
- $5 free credit per month
- ~500 hours of compute
- Perfect for testing!

**Estimated Monthly Cost:**
- Small app: **$5-10/month**
- Medium traffic: **$10-20/month**
- High traffic: **$20-50/month**

**Much cheaper than separate hosting!**

---

## 🛠️ **Troubleshooting**

### **Build Fails**

**Problem:** Python or Node.js installation fails

**Solution:**
1. Check `nixpacks.toml` is in root directory
2. Check `requirements_backend_api.txt` exists
3. Check `btc-trading-frontend/package.json` exists

### **Frontend Not Showing**

**Problem:** API works but frontend shows 404

**Solution:**
1. Check build logs - did `npm run build` succeed?
2. Check `btc-trading-frontend/build` directory exists
3. Check `btc_trading_api.py` serves static files

### **WebSocket Not Connecting**

**Problem:** WebSocket fails to connect

**Solution:**
1. Check URL uses `wss://` (not `ws://`)
2. Check Railway firewall allows WebSocket
3. Check CORS settings in `btc_trading_api.py`

### **API Returns 500 Error**

**Problem:** Backend crashes on startup

**Solution:**
1. Check Railway logs (click "View Logs")
2. Look for Python errors
3. Check all Python dependencies installed
4. Test locally first: `python3 btc_trading_api.py`

---

## 🔍 **Monitoring**

### **View Logs**

1. Go to Railway dashboard
2. Click your project
3. Click "View Logs"
4. Real-time logs appear!

### **Check Resource Usage**

1. Railway dashboard
2. Click "Metrics" tab
3. See CPU, Memory, Network usage

### **Set Up Alerts**

1. Railway dashboard
2. Click "Settings" → "Notifications"
3. Add email/Slack alerts

---

## 🎨 **Custom Domain** (Optional)

Want `btc-trading.yourdomain.com`?

1. Buy domain (Namecheap, GoDaddy, etc.)
2. Railway dashboard → "Settings" → "Domains"
3. Click "Add Custom Domain"
4. Enter: `btc-trading.yourdomain.com`
5. Add CNAME record to your DNS:
   ```
   CNAME: btc-trading → your-app.railway.app
   ```
6. Wait 5-10 minutes for DNS propagation
7. Railway auto-provisions SSL! 🎉

---

## 📈 **Scaling**

### **Vertical Scaling** (More Power)

Railway automatically scales based on usage:
- More RAM needed? Railway allocates it
- More CPU? Railway provides it
- You only pay for what you use!

### **Horizontal Scaling** (More Instances)

For high traffic:
1. Railway dashboard
2. "Settings" → "Scaling"
3. Increase replicas
4. Railway load-balances automatically

---

## 🔐 **Security**

Railway provides:
- ✅ **HTTPS** - Automatic SSL certificates
- ✅ **Private networking** - Services can communicate privately
- ✅ **Environment variables** - Secure config storage
- ✅ **DDoS protection** - Built-in
- ✅ **Automatic backups** - Daily snapshots

---

## 📚 **Useful Commands**

### **Local Development**

```bash
# Start locally (same ports as before)
./start_fullstack.sh

# Or manually:
# Terminal 1 - Backend
python3 btc_trading_api.py

# Terminal 2 - Frontend
cd btc-trading-frontend
PORT=3124 npm start
```

### **Deploy to Railway**

```bash
# Just push to GitHub!
git add .
git commit -m "Your changes"
git push

# Railway auto-deploys! 🚀
```

### **Check Railway Status**

```bash
# Install Railway CLI (optional)
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Open in browser
railway open
```

---

## 🎯 **Quick Checklist**

Before deploying, ensure:

- [x] Code pushed to GitHub
- [x] `nixpacks.toml` in root directory
- [x] `requirements_backend_api.txt` exists
- [x] `btc-trading-frontend/package.json` exists
- [x] `railway.json` configured
- [x] Frontend config uses relative URLs for production
- [x] Backend serves static files

**All configured! Ready to deploy!** ✅

---

## 🆘 **Need Help?**

**Railway Documentation:**
- https://docs.railway.app

**Railway Discord:**
- https://discord.gg/railway

**Railway Status:**
- https://status.railway.app

---

## 🎉 **Summary**

**What you get:**
1. ✅ Full-stack app on Railway
2. ✅ One simple URL
3. ✅ Automatic HTTPS
4. ✅ WebSocket support
5. ✅ Auto-deploy from GitHub
6. ✅ Real-time logs and monitoring
7. ✅ ~$5-10/month cost

**Deployment time:** **~5 minutes**

**Maintenance effort:** **Minimal** (just push to GitHub)

---

## 🚀 **Ready to Deploy?**

1. Go to: **https://railway.app**
2. Sign in with GitHub
3. Create new project from repo
4. Wait 2-3 minutes
5. **Done!** 🎉

Your Bitcoin Trading System is live! 🚂💰

---

**Questions?** Check the troubleshooting section above or Railway docs!

