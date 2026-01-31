# 🚀 GitHub Desktop Push Guide

## ✅ Pre-Push Checklist

**IMPORTANT:** Your `.gitignore` file will protect these from being uploaded:
- ✅ `.env` file (contains API keys)
- ✅ Database file (`crypto_investigation.db`)
- ✅ `node_modules/` folder
- ✅ Python cache files
- ✅ Large dataset files (Elliptic CSVs)

---

## 📋 Step-by-Step: Push to GitHub Desktop

### **1. Open GitHub Desktop**
- Launch the GitHub Desktop app

### **2. Add Your Repository**
**If this is a NEW project (first time):**
- Click **File → Add Local Repository**
- OR click **File → Create Repository**
- Browse to: `C:\Users\simpl\Desktop\CyberProject`

**If already added:**
- Your repository should appear in the left sidebar

### **3. Review Changes**
You'll see all changed files on the left:

**✅ SAFE to commit:**
- `README.md`
- `backend/app.py`, `backend/models.py`, etc.
- `frontend/src/**` files
- `.gitignore` (just created)
- `demo_addresses.txt`
- `start_project.bat`, `setup_dependencies.bat`

**❌ Should NOT appear (protected by .gitignore):**
- `backend/.env` 
- `crypto_investigation.db`
- `node_modules/`
- `__pycache__/`

### **4. Commit Your Changes**
1. **Summary field** (top): `Initial commit - Crypto Investigation Tool`
2. **Description** (optional):
   ```
   - Multi-source risk assessment platform
   - Bitcoin & Ethereum transaction data
   - 737K address database
   - React frontend + Flask backend
   ```
3. Click **Commit to main**

### **5. Publish to GitHub**
1. Click the **Publish repository** button (top right)
2. **Name:** `CyberProject` or `crypto-investigation-tool`
3. **Description:** "Cryptocurrency address risk assessment platform"
4. **Keep code private:** ✅ Check this box (IMPORTANT)
5. Click **Publish Repository**

### **6. Verify**
Go to GitHub.com and check your repository:
- `.env` should NOT be there ✅
- `.gitignore` should be there ✅
- Database should NOT be there ✅

---

## 🔒 Security Verification

**After pushing, verify these are NOT on GitHub:**

Run this command to check what's being tracked:
```bash
cd CyberProject
git ls-files | findstr /i "env db"
```

**Expected output:** Nothing (or just .env.example if you create one)

**If .env appears:**
```bash
git rm --cached backend/.env
git commit -m "Remove .env from tracking"
git push
```

---

## 🎯 Future Pushes

After the initial push, whenever you make changes:

1. **Open GitHub Desktop**
2. **You'll see changes automatically**
3. **Write commit message**: e.g., "Fixed Chainabuse API", "Added Elliptic dataset"
4. **Click Commit to main**
5. **Click Push origin** (top right)

---

## ⚠️ Important Notes

### **Never commit these:**
- API keys (`.env` files)
- Database files (`.db`, `.sqlite`)
- Large CSVs (>100MB)
- Personal/sensitive data

### **Safe to share:**
- Source code (`.py`, `.jsx`, `.js`)
- Configuration templates (`.env.example`)
- Documentation (`README.md`)
- Batch scripts (`.bat`)

---

## 📦 Recommended: Create .env.example

Create a template for others (without real keys):

**File:** `backend/.env.example`
```env
# Chainabuse API Key
CHAINABUSE_API_KEY=your_chainabuse_key_here

# Etherscan API Key
ETHERSCAN_API_KEY=your_etherscan_key_here
```

This shows what keys are needed without exposing yours!

---

## ✅ You're Ready!

Follow the steps above and your project will be safely on GitHub with all sensitive files excluded!
