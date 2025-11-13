# 🚀 Bitcoin Position Check & Fetch - Real-Time Trading System

A professional, full-stack Bitcoin trading analysis system with real-time multi-timeframe position recommendations, interactive charts, and comprehensive technical analysis.

![Bitcoin Trading](https://img.shields.io/badge/Bitcoin-Trading-orange)
![React](https://img.shields.io/badge/React-18.3.1-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-blue)

## 🌟 Features

### **Real-Time Analysis**
- ⚡ **WebSocket Updates** - Live data every 60 seconds
- 📊 **5 Timeframes** - 15min, 1h, 4h, 1d, 1w analysis
- 🎯 **Position Recommendations** - BUY, SELL, or HOLD with confidence scores
- 😱 **Fear & Greed Index** - Market sentiment integration

### **Advanced Technical Analysis**
- 📈 **20+ Indicators** - EMA, SMA, RSI, MACD, ADX, Stochastic, etc.
- 📐 **Fibonacci Retracements** - Key support/resistance levels
- 🎯 **Support & Resistance** - Auto-detected price levels
- 💹 **Bollinger Bands** - Volatility analysis
- 📊 **Volume Analysis** - OBV and volume ratios

### **Modern Web Interface**
- 🎨 **Beautiful UI** - Modern, responsive design with TailwindCSS
- 📱 **Fully Responsive** - Works on mobile, tablet, and desktop
- 📊 **Interactive Charts** - Real-time price charts with Recharts
- 🔄 **Auto-Refresh** - No manual reloading needed
- 🌐 **WebSocket** - Instant updates

### **Trade Management**
- 🎯 **Entry Points** - Exact entry prices
- 🛡️ **Stop Loss** - ATR-based risk management
- 💰 **Take Profit** - 3 levels (TP1, TP2, TP3)
- 📊 **Risk:Reward** - Calculated ratios
- 📈 **Position Sizing** - Recommended allocation

## 🚀 Quick Start

### **One-Command Launch**

```bash
git clone https://github.com/IliyaMar22/btc_position_check_fetch.git
cd btc_position_check_fetch
./start_fullstack.sh
```

Then open: **http://localhost:3124**

### **Manual Setup**

#### **1. Install Dependencies**

**Backend:**
```bash
pip3 install fastapi uvicorn websockets pandas numpy requests
```

**Frontend:**
```bash
cd btc-trading-frontend
npm install
```

#### **2. Start Backend (Terminal 1)**

```bash
python3 btc_trading_api.py
```

Backend will run on: **http://localhost:8123**

#### **3. Start Frontend (Terminal 2)**

```bash
cd btc-trading-frontend
PORT=3124 npm start
```

Frontend will run on: **http://localhost:3124**

## 📊 What You'll See

### **Dashboard Overview**

1. **Header**
   - Live Bitcoin price
   - WebSocket connection status (🟢 = connected)
   - Last update timestamp
   - Manual refresh button

2. **Fear & Greed Widget**
   - Current market sentiment (0-100)
   - Visual gauge with color coding
   - Buy/sell recommendations
   - Contrarian signals

3. **Summary Cards**
   - Best signal across all timeframes
   - Buy/Sell/Hold signal counts
   - Quick overview grid

4. **Position Cards (5x)**
   - **15-Minute**: Day trading signals
   - **1-Hour**: Swing trading (⭐ usually best)
   - **4-Hour**: Position trading
   - **1-Day**: Long-term analysis
   - **1-Week**: Investment/DCA strategy

5. **Interactive Charts**
   - Price action with indicators
   - Entry/exit markers
   - Support/resistance lines
   - Hover for details

## 🎯 Position Scoring System

Each position is scored from -20 to +20 based on:

- **Trend Analysis** (±3 points)
- **RSI Momentum** (±3 points)
- **MACD Signals** (±2 points)
- **Support/Resistance** (±2 points)
- **Fear & Greed** (±3 points)
- **Volume** (±1 point)
- **Fibonacci Levels** (±1 point)
- **Other indicators** (±5 points)

### **Score Interpretation:**
- **≥8**: 🟢 STRONG BUY
- **5-7**: 🟢 BUY
- **2-4**: 🟡 WEAK BUY
- **-1 to 1**: ⚪ HOLD
- **-5 to -2**: 🟠 WEAK SELL
- **≤-5**: 🔴 SELL

## 🏗️ Tech Stack

### **Backend**
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **WebSockets** - Real-time communication
- **Pandas/NumPy** - Data processing
- **CCXT** - Binance API integration

### **Frontend**
- **React 18** - UI library
- **TypeScript** - Type safety
- **TailwindCSS** - Utility-first CSS
- **Recharts** - Chart library
- **Axios** - HTTP client
- **React Icons** - Icon library

## 📁 Project Structure

```
btc_position_check_fetch/
├── Backend
│   ├── btc_trading_api.py                    # FastAPI server
│   ├── multi_timeframe_position_analyzer.py  # Position analysis
│   ├── advanced_technical_analysis.py        # Technical indicators
│   ├── multi_source_data_fetcher.py          # Data fetching
│   ├── fear_greed_index.py                   # Fear & Greed
│   └── requirements_backend_api.txt          # Python dependencies
│
├── Frontend
│   └── btc-trading-frontend/
│       ├── src/
│       │   ├── components/                   # React components
│       │   ├── App.tsx                       # Main app
│       │   └── ...
│       └── package.json                      # Node dependencies
│
├── Documentation
│   ├── README_FULLSTACK.md                   # Complete guide
│   ├── FULLSTACK_SETUP_GUIDE.md              # Setup instructions
│   ├── MULTI_TIMEFRAME_GUIDE.md              # Analysis guide
│   └── QUICK_START_POSITIONS.md              # Quick reference
│
└── Scripts
    └── start_fullstack.sh                     # One-click launcher
```

## 🌐 API Endpoints

### **REST API**
- `GET /api/positions` - Get all position suggestions
- `GET /api/fear-greed` - Get Fear & Greed Index
- `GET /api/current-price` - Get current BTC price
- `GET /api/position/{timeframe}` - Get specific timeframe
- `GET /api/health` - Health check

### **WebSocket**
- `ws://localhost:8123/ws` - Real-time updates

**API Documentation:** http://localhost:8123/docs

## 📚 Documentation

- **[Complete Setup Guide](FULLSTACK_SETUP_GUIDE.md)** - Detailed installation
- **[Multi-Timeframe Guide](MULTI_TIMEFRAME_GUIDE.md)** - Position analysis
- **[Quick Start](QUICK_START_POSITIONS.md)** - Quick reference
- **[Full Stack README](README_FULLSTACK.md)** - Comprehensive docs

## 🎨 Screenshots

### Desktop View
Full dashboard with all features, side-by-side charts, real-time updates.

### Mobile View
Single-column layout, touch-friendly, all features available.

## 🔧 Configuration

### **Change Ports**

Edit `btc_trading_api.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8123)  # Backend port
```

Edit `btc-trading-frontend/src/App.tsx`:
```typescript
const API_BASE_URL = 'http://localhost:8123';  // API URL
const WS_URL = 'ws://localhost:8123/ws';        // WebSocket URL
```

Set frontend port:
```bash
PORT=3124 npm start
```

## 📈 Usage Tips

### **For Day Traders (15m-1h)**
- Focus on 15-minute and 1-hour timeframes
- Use tight stop losses
- Take profits quickly at TP1/TP2

### **For Swing Traders (1h-4h)**
- Focus on 1-hour and 4-hour timeframes
- Use medium stop losses
- Hold for TP2/TP3

### **For Long-term Investors (1d-1w)**
- Focus on daily and weekly timeframes
- Use DCA (Dollar Cost Averaging)
- Accumulate during extreme fear

## ⚠️ Disclaimer

**This system is for educational and informational purposes only.**

- Not financial advice
- Always DYOR (Do Your Own Research)
- Never invest more than you can afford to lose
- Past performance ≠ future results
- Crypto trading carries significant risk

## 🤝 Contributing

This is a personal project, but feel free to fork and customize!

## 📄 License

Educational use only. Not for commercial distribution.

## 🎉 Features Checklist

- [x] Real-time WebSocket updates
- [x] Multi-timeframe analysis (5 timeframes)
- [x] 20+ technical indicators
- [x] Fear & Greed Index integration
- [x] Interactive charts
- [x] Responsive design
- [x] Trade recommendations
- [x] Risk management
- [x] Position tracking
- [x] TradingView Pine Script export
- [x] Multi-source data fetching
- [x] Support/Resistance detection
- [x] Fibonacci retracements

## 🚂 Deployment to Production

### **Deploy Everything to Railway** (Recommended)

Deploy the entire full-stack application to Railway in **5 minutes**!

**Full guide:** See **[RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)**

**Quick steps:**
1. ✅ Push code to GitHub (already done!)
2. 🚂 Go to https://railway.app and sign in
3. 🎯 Create new project from GitHub repo
4. ⏳ Wait 2-3 minutes for auto-build
5. 🎉 Done! Your app is live!

**What Railway does automatically:**
- Installs Python dependencies
- Installs Node.js dependencies
- Builds React frontend
- Starts FastAPI backend
- Serves everything on one domain
- Provides HTTPS + WebSocket support

**Benefits:**
- ✅ One platform (simpler than separate hosting)
- ✅ No CORS issues (same domain)
- ✅ WebSocket support (persistent connections)
- ✅ Auto-deploy from GitHub
- ✅ Cost-effective (~$5-10/month)

**Your deployed URLs:**
```
🌍 Main App:     https://your-app.railway.app
📊 Dashboard:    https://your-app.railway.app/
📡 API Docs:     https://your-app.railway.app/docs
🔌 WebSocket:    wss://your-app.railway.app/ws
```

## 🚀 Getting Help

For issues or questions:
1. Check the [troubleshooting guide](FULLSTACK_SETUP_GUIDE.md#troubleshooting)
2. Review the [API documentation](http://localhost:8123/docs)
3. Check browser console for errors
4. Review backend logs
5. See [Railway Deployment Guide](RAILWAY_DEPLOYMENT_GUIDE.md) for production issues

---

<div align="center">

**Made with ❤️ for Bitcoin traders**

**Happy Trading! 🎯📈💰**

[⬆ Back to Top](#-bitcoin-position-check--fetch---real-time-trading-system)

</div>
