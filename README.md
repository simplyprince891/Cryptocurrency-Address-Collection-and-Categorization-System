# 🔍 Crypto Investigation Tool

A comprehensive cryptocurrency address risk assessment platform that combines multiple data sources to identify fraudulent wallets, mixers, and suspicious activity.

---

## 🚀 Features

### ✅ **Working Features**

#### **Multi-Source Risk Assessment**
- **Local Database** - 737K+ labeled addresses (scams, ransomware, threats)
- **Blockchain APIs** - Real-time transaction data
  - Bitcoin: Blockchain.com API (FREE, no key needed)
  - Ethereum: Etherscan V2 API (FREE tier, API key required)
- **Chainabuse Integration** - Community-reported scams (with caching)
- **Elliptic Dataset** - 200K+ Bitcoin transaction labels (illicit/licit classification)

#### **Smart Risk Analysis**
- **Behavioral Pattern Detection**
  - Mixing patterns (many small transactions)
  - New wallet fraud (<30 days + high volume)
  - Tumbler patterns (high throughput, low balance)
  - Exit scam detection (emptied after receiving funds)
- **Dynamic Weight Normalization** - Dataset-only addresses get full 100% weight
- **Multi-Factor Scoring** - Combines dataset, behavioral, Chainabuse, and wallet type

#### **Transaction Analytics**
- Transaction count
- Wallet age (in days)
- Current balance
- Total received/sent amounts
- First/last transaction dates

#### **Modern UI**
- Real-time address classification
- Risk visualization with color-coded scores (0-100)
- Transaction metrics display
- Data source tracking
- Responsive design

---

## 📦 Setup

### **Prerequisites**
- Python 3.8+
- Node.js 16+
- npm

### **Installation**

1. **Clone/Download the project**
```bash
cd CyberProject
```

2. **Install dependencies**
```bash
setup_dependencies.bat
```

3. **Configure API keys** (Edit `backend/.env`):
```env
CHAINABUSE_API_KEY=your_chainabuse_key_here
ETHERSCAN_API_KEY=your_etherscan_key_here
```

4. **Run database migration** (adds transaction analytics columns):
```bash
run_migration.bat
```

5. **Start the application**:
```bash
start_project.bat
```

**Access:**
- Frontend: http://localhost:5173
- Backend: http://127.0.0.1:5000

---

## 🎯 How to Use

### **Search Addresses**

**Bitcoin Addresses (Working):**
```
1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s
```
- Shows transaction data, behavioral risk, mixing patterns

**Ethereum Addresses (Working):**
```
0x00000000219ab540356cBB839Cbe05303d7705Fa
```
- Shows transaction count, wallet age, balance

**Addresses from Local Dataset:**
- Any address in `backend/dataset.csv`
- Now properly shows 100/100 risk for critical threats

### **Demo Addresses**
See `demo_addresses.txt` for 20+ curated test addresses organized by risk level.

---

## 🏗️ Architecture

### **Backend** (`/backend`)
- **Flask API** - REST endpoints
- **SQLAlchemy** - Database ORM
- **Services:**
  - `blockchain_api.py` - Blockchain.com + Etherscan V2 integration
  - `elliptic_dataset.py` - Bitcoin transaction label lookup
  - `risk_engine.py` - Multi-source risk calculation
  - `chainabuse.py` - Scam report aggregation

### **Frontend** (`/frontend`)
- **React + Vite** - Modern UI framework
- **Components:**
  - `RiskCard.jsx` - Risk visualization with transaction metrics
  - `ReportsList.jsx` - Abuse report display
  - `NetworkGraph.jsx` - (Future: Transaction network visualization)

---

## 📊 Risk Scoring

### **Weights**
- **Dataset:** 45% (or 100% if only source available)
- **Behavioral:** 30%
- **Chainabuse:** 15%
- **Wallet Type:** 10%

### **Risk Levels**
- **0-30:** Clean (green)
- **31-70:** Medium Risk (orange)
- **71-100:** Critical Risk (red)

---

## ✅ What's Working

| Feature | Status | Notes |
|---------|--------|-------|
| Bitcoin transaction data | ✅ Working | Blockchain.com API |
| Ethereum transaction data | ✅ Working | Etherscan V2 with chainid |
| Dataset risk scoring | ✅ Working | Smart weight normalization |
| Behavioral analysis | ✅ Working | Mixer/fraud detection |
| Frontend metrics display | ✅ Working | Shows tx count, age, balance |
| Chainabuse API calls | ✅ Working | Caching implemented |
| Database migration | ✅ Working | New columns added |

---

## ⚠️ Known Issues

### **Chainabuse Report Display**
- **Issue:** API returns 0 reports even for addresses with reports on website
- **Status:** API endpoint may need adjustment or response parsing fix
- **Workaround:** Chainabuse data is fetched and cached, but reports may not display
- **Next Step:** Debug API response structure (logging added in v1.2)

### **Etherscan Transaction Limits**
- Free tier limited to 10,000 transactions per query
- Very active addresses may not show full history

---

## 🔮 Future Enhancements

### **High Priority**
1. Fix Chainabuse report parsing/display
2. Add support for more chains (BSC, Polygon)
3. Implement transaction graph visualization
4. Add export to PDF/CSV functionality

### **Medium Priority**
5. Enhanced Elliptic dataset integration (currently service exists but not fully integrated)
6. User authentication for report submissions
7. Historical risk tracking
8. Batch address analysis

### **Low Priority**
9. Dark mode toggle
10. Advanced search filters
11. API rate limiting dashboard
12. Community reporting features

---

## 📁 Project Structure

```
CyberProject/
├── backend/
│   ├── services/
│   │   ├── blockchain_api.py       # FREE APIs for tx data
│   │   ├── elliptic_dataset.py     # Bitcoin label lookup
│   │   ├── risk_engine.py          # Multi-source risk calc
│   │   └── chainabuse.py           # Scam reports
│   ├── routes/
│   │   └── api.py                  # Main API endpoints
│   ├── models.py                   # Database models
│   ├── app.py                      # Flask app
│   ├── dataset.csv                 # 737K addresses
│   └── .env                        # API keys
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── RiskCard.jsx
│   │   │   └── ReportsList.jsx
│   │   └── pages/
│   │       └── Investigate.jsx
│   └── package.json
├── demo_addresses.txt              # Test addresses
├── start_project.bat               # One-click launcher
└── README.md                       # This file
```

---

## 🔑 API Keys

### **Required:**
- **ETHERSCAN_API_KEY** - Free tier: https://etherscan.io/apis
  - 5 requests/second, 100K requests/day

### **Optional but Recommended:**
- **CHAINABUSE_API_KEY** - Get from: https://www.chainabuse.com/api

### **Not Required:**
- Blockchain.com (Bitcoin) - No key needed ✅

---

## 🛠️ Development Notes

### **Recent Updates (v1.2)**
- ✅ Fixed Etherscan V2 API integration (added `chainid=1`)
- ✅ Implemented smart risk weight normalization
- ✅ Added transaction metrics to frontend display
- ✅ Enhanced error handling for all APIs
- ✅ Added comprehensive logging for debugging
- ✅ Created database migration for transaction columns

### **Database Schema**
The `addresses` table includes:
- Core fields: address, chain, category, label, risk_score
- Transaction analytics: tx_count, wallet_age_days, balance
- Behavioral flags: is_mixer_pattern, is_high_volume
- Timestamps: first_tx_date, last_tx_date

---

## 📞 Support & Contributing

### **Need Help?**
- Check `demo_addresses.txt` for working test addresses
- Review `walkthrough.md` (in artifacts folder) for detailed implementation notes
- Ensure all dependencies are installed via `setup_dependencies.bat`

### **Common Issues:**
1. **"No such column" error** → Run `run_migration.bat`
2. **Etherscan returns no data** → Check API key in `.env`
3. **Frontend won't start** → Run `npm install` in frontend directory
4. **Backend port conflict** → Check if port 5000 is available

---

## 📝 Version History

**v1.2** (Current)
- Etherscan V2 API support
- Transaction metrics display
- Smart risk normalization
- Enhanced logging

**v1.1**
- Blockchain API integration
- Behavioral risk detection
- Elliptic dataset service

**v1.0**
- Initial release
- Local dataset (737K addresses)
- Basic risk scoring
- React frontend

---

## 📄 License

This project is for educational and research purposes.

---

## 🎯 Quick Start Commands

```bash
# First time setup
setup_dependencies.bat
run_migration.bat

# Daily use
start_project.bat

# Clear Chainabuse cache (if needed for debugging)
cd backend
python clear_cache.py
```

---

**Built with ❤️ for cybersecurity research and fraud prevention**

*Last Updated: January 31, 2026*
