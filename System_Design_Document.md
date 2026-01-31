# Cryptocurrency Address Collection and Categorization System for Cybercrime Investigation

## Abstract

The proliferation of cryptocurrencies has facilitated a new wave of cybercrime, enabling illicit actors to conduct financial transactions with relative anonymity. Law enforcement agencies face significant challenges in tracing funds and identifying perpetrators due to the pseudo-anonymous nature of blockchain technology. This project proposes a "Cryptocurrency Address Collection and Categorization System," a centralized platform designed to assist cyber-forensics investigators. The system automates the collection of cryptocurrency wallet addresses from diverse sources, analyzes transaction patterns, and categorizes wallets based on their likelihood of involvement in criminal activities such as ransomware, darknet markets, and money laundering. By integrating blockchain APIs, OSINT feeds, and heuristic-based risk scoring, the system provides actionable intelligence to speed up investigations and support anti-money laundering (AML) efforts.

---

## 1. Problem Definition & Objectives

### 1.1 Problem Statement
Cryptocurrencies like Bitcoin and Ethereum operate on decentralized ledgers where user identities are masked by cryptographic addresses. While transactions are public, linking an address to a real-world entity is difficult. Cybercriminals exploit this anonymity for:
- **Ransomware payments:** Extorting victims for encrypted data keys.
- **Darknet Marketplaces:** Buying/selling illegal goods.
- **Money Laundering:** Using mixers and tumbling services to obscure the trail of funds.
- **Ponzi Schemes & Fraud:** Deceiving investors.

Manual tracing of these transactions is time-consuming and often futile without advanced analytical tools. Investigators lack a unified system to aggregate data from multiple blockchains and intelligence sources.

### 1.2 Objectives
The primary goals of this system are:
1.  **Automated Data Collection:** scraping and fetching wallet addresses from blockchain explorers, social media, specialized forums, and public blacklists.
2.  **Address Categorization:** Classifying addresses into categories (e.g., Exchange, Mixer, Ransomware, User) to understand their nature.
3.  **Risk Assessment:** Assigning risk scores to addresses based on transaction history and associations.
4.  **Investigative Support:** Providing a visual dashboard for investigators to search addresses, view transaction graphs, and generate forensic reports.

---

## 2. System Architecture

### 2.1 High-Level Architecture
The system follows a modular microservices-inspired architecture comprising four main layers:

1.  **Data Collection Layer:** Interfaces with external data sources (Blockchain nodes/APIs, OSINT feeds). It runs scheduled tasks to fetch new blocks and harvest flagged addresses.
2.  **Processing & Analysis Layer:** The core engine that processes raw data. It includes the Feature Extraction Module, Risk Scoring Engine, and Graph Analysis algorithms.
3.  **Storage Layer:** A hybrid database approach.
    - **Relational Database (PostgreSQL):** For user data, reports, and structured address metadata.
    - **Graph Database (Neo4j) or Document Store (MongoDB):** For storing complex transaction relationships and unstructured logs.
4.  **Presentation Layer (UI):** A web-based dashboard for investigators to interact with the system, visualize data, and export reports.

### 2.2 Core Components
-   **Blockchain Data Fetcher:** Connects to APIs (e.g., Etherscan, Blockchair) to retrieve transaction details.
-   **OSINT Scraper:** Monitors sites like Reddit, Twitter, and BitcoinTalk for user-reported scam addresses.
-   **Categorization Engine:** Applies rules and ML models to label addresses.
-   **Transaction Graph/Network Analyzer:** Builds a network of funds flow to identify clusters.
-   **API Gateway:** Manages requests between the frontend dashboard and backend services.

---

## 3. Modules & Functionalities

### 3.1 Address Collection Module
-   **Input:** APIs, Web Scrapers, Log files.
-   **Function:** Continuously ingests data. It supports extracting addresses from text using Regex patterns (e.g., `^[13][a-km-zA-Z0-9]{25,34}$` for Bitcoin).
-   **Blacklist Integration:** Syncs with public databases like CryptoScamDB and OFAC sanctions lists.

### 3.2 Transaction Monitoring Module
-   **Function:** Tracks incoming/outgoing transactions for flagged addresses in real-time.
-   **Alerts:** Triggers notifications when a high-risk address moves a large sum of funds.

### 3.3 Feature Extraction Module
Extracts behavioral features for analysis:
-   **Volume:** Total ETH/BTC received/sent.
-   **Frequency:** Transactions per day/hour.
-   **Lifetime:** Time between first and last transaction.
-   **Fan-out/Fan-in:** Many inputs to one output (agglomeration) or one input to many outputs (distribution).

### 3.4 Address Categorization Module
Classifies wallets into:
-   **Exchange/Service:** High volume, high frequency, known cold/hot wallets.
-   **Mixer/Tumbler:** Complex transaction graphs designed to obfuscate links.
-   **Darknet Market:** Associated with known marketplace addresses.
-   **Ransomware:** Addresses linked to malware campaigns.
-   **Personal/Private:** Low volume, distinct patterns.

### 3.5 Risk Scoring Module
Calculates a risk score (0-100) based on:
-   Proximity to known bad actors (hops away from a blacklisted address).
-   Presence in scam databases.
-   Use of mixing services.
*(0 = Safe, 100 = Highly Suspicious/Criminal)*

### 3.6 Search & Investigation Dashboard
-   **Search Bar:** Lookup stats for any specific address.
-   **Visualization:** Interactive node-link diagrams showing fund flow.
-   **Filters:** Filter by time, amount, or currency.

### 3.7 Report Generation Module
-   **Automated Reporting:** Generates PDF/HTML reports summarizing an address's activity, risk score, and known associates for legal proceedings.

---

## 4. Algorithms & Techniques

### 4.1 Heuristic-Based Rules
Simple logic to identify obvious behaviors:
-   *IF* transaction_count > 10,000 *AND* specific_time_pattern = TRUE *THEN* Tag as "Exchange/Service".
-   *IF* address found in "Ransomware_Blacklist" *THEN* Risk_Score = 100.

### 4.2 Graph Analysis (Clustering)
-   **Common Input Ownership Heuristic:** If multiple addresses are used as inputs in a single transaction, they likely belong to the same entity.
-   **Change Address Detection:** Heuristics to identify "change" addresses in UTXO-based blockchains (like Bitcoin) to link them back to the sender.

### 4.3 Machine Learning Classification
-   **Model:** Random Forest or Gradient Boosting (XGBoost).
-   **Training Data:** Labeled dataset of known categories (Exchanges, Miners, Scams).
-   **Features:** Transaction frequency, average amount, idle time, neighbor risk scores.
-   **Output:** Probability distribution over categories.

### 4.4 Anomaly Detection
-   **Isolation Forests:** To detect wallets with unusual spending patterns compared to the norm (potential money laundering).

---

## 5. Data Sources

1.  **Blockchain Explorers/APIs:**
    -   Etherscan (Ethereum)
    -   Blockchain.com (Bitcoin)
    -   Blockchair (Multi-chain)
2.  **OSINT Feeds:**
    -   CryptoScamDB (Community reported scams)
    -   OFAC SDN List (Sanctioned addresses)
    -   BitcoinTalk Forum (Scam accusations)
    -   Twitter/X APIs (Real-time reports)

## 6. Technology Stack

-   **Frontend:** React.js (for dynamic dashboard), D3.js or Cytoscape.js (for graph visualization).
-   **Backend:** Python (Flask/Django) or Node.js (Express). Python is preferred for data analysis capabilities.
-   **Database:** 
    -   **PostgreSQL:** Relational data (Users, Alerts, Reports).
    -   **MongoDB:** Unstructured logs and raw transaction data.
    -   **Neo4j (Optional):** Highly recommended for storing address relationships.
-   **Analysis Libraries:** Pandas, Scikit-learn (ML), NetworkX (Graph theory).
-   **External APIs:** Etherscan API, CoinGecko API (price conversion).

---

## 7. Workflow

1.  **Investigator Input:** The user enters a suspect address or keywords into the system.
2.  **Data Fetching:** The system queries the blockchain to retrieve the address's entire transaction history.
3.  **OSINT Check:** Simultaneously, the address is checked against blacklists and scraped web data.
4.  **Analysis:**
    -   Graph algorithms cluster related addresses.
    -   ML models predict the entity type.
    -   Risk score is computed.
5.  **Visualization:** Results are displayed on the dashboard with a visual graph of connections.
6.  **Action:** Investigator exports a PDF report for the case file.

---

## 8. Outputs

1.  **Address Intelligence Profile:** Comprehensive view of an address (Balance, Total Received, First/Last Seen).
2.  **Visual Transaction Graph:** Interactive map showing money flow to/from the target.
3.  **Risk Scorecard:** Quantitative assessment of criminality.
4.  **Forensic Report:** Downloadable document summarizing findings.

---

## 9. Applications

-   **Law Enforcement:** Tracing stolen funds from hacks or scams.
-   **Compliance (Exchanges):** AML checks to prevent accepting dirty funds.
-   **Cybersecurity Researchers:** Analyzing ransomware campaigns (e.g., WannaCry, Conti).
-   **Financial Forensics:** Investigating fraud cases involving crypto assets.

---

## 10. Advantages & Limitations

### 10.1 Advantages
-   **Efficiency:** Automates manual lookups across multiple sites.
-   **Visual Clarity:** Converts complex ledger data into understandable graphs.
-   **Proactive:** Can flag suspicious activity before it is reported by users.

### 10.2 Limitations
-   **Mixing Services:** CoinJoins and mixers can successfully sever the link between sender and receiver, reducing accuracy.
-   **Privacy Coins:** Monero (XMR) and Zcash (ZEC) hide transaction details, making them untraceable by this system.
-   **Off-Chain Transactions:** Transactions on Layer 2 solutions or internal exchange ledgers are not visible on the public blockchain.

---

## 11. Future Enhancements

-   **Multi-Chain Support:** Expanding beyond BTC/ETH to support Solana, Tron, etc.
-   **AI-Based Predictive Analysis:** Predicting where stolen funds will move next based on historical behavior.
-   **Real-Time Monitoring Feed:** A live ticker of large suspicious transactions.
-   **Dark Web Scraper:** specialized module to access .onion sites for new scam addresses.

---

## Appendix A: Sample Database Schema

**Table: Addresses**
| Field | Type | Description |
| :--- | :--- | :--- |
| `address_id` | VARCHAR(64) | Primary Key, Wallet Address |
| `currency` | VARCHAR(10) | BTC, ETH, etc. |
| `risk_score` | FLOAT | 0.0 to 100.0 |
| `category` | VARCHAR(50) | Exchange, Scam, etc. |
| `last_updated` | TIMESTAMP | Last sync time |

**Table: Transactions**
| Field | Type | Description |
| :--- | :--- | :--- |
| `tx_hash` | VARCHAR(64) | Primary Key, Transaction Hash |
| `sender_addr` | VARCHAR(64) | FK to Addresses |
| `receiver_addr` | VARCHAR(64) | FK to Addresses |
| `amount` | DECIMAL | Value transferred |
| `timestamp` | TIMESTAMP | Time of transaction |

**Table: Entity_Labels**
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | INT | PK |
| `address_id` | VARCHAR(64) | FK to Addresses |
| `label` | VARCHAR(100) | e.g., "Binance Hot Wallet", "WannaCry Attacker" |
| `source` | VARCHAR(100) | e.g., "Etherscan", "User Report" |

---

## Appendix B: Use Case Scenarios

**Scenario 1: Ransomware Investigation**
A company is hit by ransomware and pays 5 BTC to an address provided by attackers.
1.  Investigator inputs the attacker's address.
2.  System visualizes the flow of the 5 BTC.
3.  System detects the funds moving to a cluster of addresses identified as a known "Mixing Service".
4.  Report shows the funds are currently obfuscated, but history shows the mixer often outputs to "Exchange X".
5.  Investigator subpoenas "Exchange X" for KYC info on the output addresses.

**Scenario 2: Investment Scam Vetting**
A user reports a suspicious investment platform.
1.  Investigator inputs the deposit address.
2.  System checks OSINT feeds and finds 50+ Twitter mentions linking this address to "MegaYield Scam".
3.  Risk score is set to 95.
4.  System identifies the destination wallet as a personal wallet, not a corporate structure.
5.  Investigator confirms fraud and adds the address to the public blacklist.
