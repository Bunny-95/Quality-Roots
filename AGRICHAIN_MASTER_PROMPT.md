# 🌿 AGRICHAIN — MASTER BUILD PROMPT FOR WINDSURF
> Feed this entire file to Windsurf as your first prompt.
> Windsurf must ask the user before making any assumption it is unsure about.

---

## 🧠 YOUR ROLE
You are a senior full-stack AI engineer. Your job is to build **AgriChain** — a complete, production-ready web application from scratch, following this specification exactly. 

**IMPORTANT RULES:**
- If you are unsure about ANY detail, STOP and ask the user before proceeding.
- Build one module at a time and confirm it works before moving on.
- Never leave placeholder code — every function must be implemented.
- Install all required packages automatically.
- After each major module, summarize what was built and what is next.

---

## 📓 MEMORY & PROGRESS LOGGING SYSTEM (MANDATORY)

This is your most critical responsibility. You have a limited context window and WILL forget things across sessions. To prevent this, you MUST maintain a live progress log file at all times.

### The Log File
Create and maintain a file called `AGRICHAIN_BUILD_LOG.md` in the project root from the very first step. This is your persistent memory. Every single action you take must be recorded here immediately.

### Log File Format (use exactly this structure):

```markdown
# AgriChain Build Log
_Last updated: [timestamp]_

## ✅ COMPLETED STEPS
| Step | Name | Status | Files Created/Modified | Notes |
|------|------|--------|----------------------|-------|
| 1 | Project Structure | ✅ Done | agrichain/ folder tree | All folders created |
| 2 | Database Models | ✅ Done | backend/database.py, models/*.py | SQLite connected |

## 🔄 CURRENT STEP
**Step: [number] — [name]**
Currently working on: [exact task]
Files open/editing: [list]

## ⏳ REMAINING STEPS
| Step | Name | Depends On |
|------|------|------------|
| 5 | AI Modules | Step 4 (Auth) |
...

## 🐛 ISSUES & DECISIONS LOG
| # | Issue | Decision Made | Step |
|---|-------|---------------|------|
| 1 | SQLite path conflict | Used absolute path via config.py | Step 2 |

## 📦 INSTALLED PACKAGES
### Backend (pip)
- fastapi==0.111.0 ✅
- uvicorn ✅

### Frontend (npm)
- react ✅
- tailwindcss ✅

## 🔑 KEY VALUES & SECRETS
| Key | Value |
|-----|-------|
| Admin email | admin@agrichain.com |
| Admin password | admin123 |
| JWT Secret | agrichain-secret-key-2024 |
| DB path | backend/agrichain.db |
| QR base URL | http://localhost:5173/verify?batch= |
| Backend port | 8000 |
| Frontend port | 5173 |

## 🗂️ FILE REGISTRY (every file ever created)
| File Path | Purpose | Step Created |
|-----------|---------|--------------|
| backend/main.py | FastAPI entry point | Step 1 |
| backend/database.py | SQLAlchemy setup | Step 2 |

## ⚠️ IMPORTANT DECISIONS (things that affect other steps)
- Blockchain blocks stored in SQLite table `blockchain_blocks`
- JWT token stored in localStorage as `agrichain_token`
- All API routes prefixed with `/api`
- QR images saved to `/qr_codes/` folder, served as static files
```

### LOGGING RULES (non-negotiable):
1. **Update the log BEFORE starting any step** — mark it as 🔄 CURRENT
2. **Update the log AFTER finishing any step** — mark it as ✅ COMPLETED
3. **Log every file you create or modify** in the File Registry immediately
4. **Log every decision** — if you choose between two approaches, write why
5. **Log every package installed** with its version
6. **Never delete old log entries** — only add new ones
7. **At the start of EVERY new chat session**, read `AGRICHAIN_BUILD_LOG.md` first and tell the user: "I've read the build log. Last completed step was X. Currently on step Y. Resuming now."
8. **If you ever feel confused** about what was built, read the log before doing anything

### SESSION START PROTOCOL
At the start of every new Windsurf session, you MUST say:
> "📖 Reading AGRICHAIN_BUILD_LOG.md..."
> Then summarize: last completed step, current step, any open issues, and what you'll do next.
> Ask the user: "Should I continue from where we left off?"

### SESSION END PROTOCOL
Before ending any session or if the user says "stop" / "take a break", you MUST:
1. Update the log with current status
2. List the next 3 things to do in the next session
3. Say: "✅ Log updated. Next session I will: [list 3 things]. Safe to close Windsurf."

---

## 📦 PROJECT OVERVIEW

**AgriChain** is an AI-enabled, simulated-blockchain-based smart agricultural supply chain provenance system for specialty products (spices, coffee, tea, millets, organic crops).

It enables:
- Farmers to register crops and batches
- AI to grade quality, detect fraud, and forecast demand/price
- A simulated blockchain to store tamper-proof records
- QR codes for consumer verification
- Dashboards for Farmers, Admins, and Consumers

---

## 🗂️ FULL FOLDER STRUCTURE

Build the project with this exact structure:

```
agrichain/
├── backend/
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Config & constants
│   ├── database.py               # SQLite setup with SQLAlchemy
│   ├── blockchain/
│   │   ├── __init__.py
│   │   ├── chain.py              # Simulated blockchain (SHA-256 linked blocks)
│   │   └── models.py             # Block data models
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── quality_grader.py     # CNN-based quality grading (simulated with sklearn)
│   │   ├── fraud_detector.py     # Isolation Forest anomaly detection
│   │   └── demand_forecaster.py  # LSTM demand & price prediction
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py               # Login / Register / JWT
│   │   ├── farmer.py             # Farmer endpoints
│   │   ├── admin.py              # Admin endpoints
│   │   ├── consumer.py           # Consumer / QR endpoints
│   │   ├── blockchain_routes.py  # View chain, verify block
│   │   └── ai_routes.py          # AI prediction endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── batch.py
│   │   └── supply_chain.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── qr_generator.py       # QR code generation
│   │   ├── security.py           # JWT, password hashing
│   │   └── seed_data.py          # Seed realistic demo data on startup
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── index.css             # Global styles + CSS variables
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── QRScanner.jsx
│   │   │   ├── BlockchainViewer.jsx
│   │   │   ├── AIInsightCard.jsx
│   │   │   ├── ProductTimeline.jsx
│   │   │   ├── StatCard.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── pages/
│   │   │   ├── Landing.jsx        # Public landing page
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── FarmerDashboard.jsx
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── ConsumerVerify.jsx # QR scan + product journey
│   │   │   ├── AddBatch.jsx
│   │   │   ├── BlockchainExplorer.jsx
│   │   │   └── AIAnalytics.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── hooks/
│   │   │   └── useApi.js
│   │   └── utils/
│   │       └── api.js             # Axios instance
│
├── qr_codes/                      # Generated QR code images (served statically)
├── README.md
└── run.sh                         # Single command to start everything
```

---

## ⚙️ TECH STACK

### Backend
| Layer | Technology |
|---|---|
| Framework | FastAPI (Python) |
| Database | SQLite + SQLAlchemy ORM |
| Auth | JWT (python-jose) + bcrypt |
| Blockchain | Custom Python SHA-256 linked chain (no real chain) |
| AI - Quality | Scikit-learn RandomForest (simulates CNN grading) |
| AI - Fraud | Scikit-learn Isolation Forest |
| AI - Forecast | Scikit-learn + numpy (simulates LSTM forecasting) |
| QR Codes | `qrcode` + `Pillow` |
| CORS | FastAPI CORS middleware |

### Frontend
| Layer | Technology |
|---|---|
| Framework | React 18 + Vite |
| Styling | Tailwind CSS |
| Routing | React Router v6 |
| HTTP | Axios |
| Charts | Recharts |
| Icons | Lucide React |
| QR Scan | `html5-qrcode` |
| Animations | Framer Motion |

---

## 🔗 SIMULATED BLOCKCHAIN (IMPLEMENT FULLY)

Build a **pure Python** simulated blockchain in `backend/blockchain/chain.py`.

### Block Structure:
```python
class Block:
    index: int
    timestamp: str
    data: dict          # The supply chain event data
    previous_hash: str
    hash: str           # SHA-256 of all above fields
    nonce: int          # Simple proof of work (find hash starting with "00")
```

### Chain Rules:
- Genesis block is created automatically on startup
- Every supply chain event (batch created, quality checked, shipped, received, sold) adds a new block
- Chain integrity is verifiable — expose a `/blockchain/verify` endpoint that validates all hashes
- Blocks are persisted to SQLite so they survive server restarts
- Expose endpoints: `GET /blockchain/chain`, `GET /blockchain/block/{index}`, `GET /blockchain/verify`

---

## 🤖 AI MODULES (IMPLEMENT ALL THREE FULLY)

### 1. Quality Grader (`ai/quality_grader.py`)
**Goal:** Grade a product batch as Grade A / Grade B / Grade C based on attributes.

**Input features** (farmer provides when creating batch):
- `moisture_level` (float, 0–100)
- `color_score` (float, 0–10)
- `aroma_score` (float, 0–10)
- `defect_percentage` (float, 0–100)
- `weight_per_unit` (float, grams)
- `product_type` (string: spice/coffee/tea/millet/organic)

**Implementation:**
- Train a `RandomForestClassifier` on **synthetic generated training data** (generate 500 samples in code)
- Synthetic labels: Grade A = high scores + low defects, Grade C = opposite
- Return: `{ grade: "A", confidence: 0.92, recommendations: ["Reduce moisture to <12%"] }`
- Save/load trained model with `joblib`
- Also return a quality score (0–100)

### 2. Fraud Detector (`ai/fraud_detector.py`)
**Goal:** Detect anomalous/suspicious supply chain transactions.

**Input features:**
- `price_per_kg` (float)
- `quantity_kg` (float)
- `transit_days` (int)
- `temperature_reported` (float)
- `location_jump_km` (float)
- `time_since_last_event_hours` (float)

**Implementation:**
- Use `IsolationForest` from scikit-learn
- Fit on synthetic normal transaction data (300 samples)
- Return: `{ is_anomaly: true/false, anomaly_score: -0.34, risk_level: "HIGH/MEDIUM/LOW", flags: ["Unusual price spike", "Impossible transit speed"] }`
- Expose `POST /ai/detect-fraud` endpoint

### 3. Demand Forecaster (`ai/demand_forecaster.py`)
**Goal:** Forecast next 7-day demand and recommended price per product type.

**Input:**
- `product_type` (string)
- `historical_prices` (list of 30 floats — past 30 days prices)
- `historical_demand` (list of 30 floats — past 30 days demand)
- `season` (string: summer/monsoon/winter/spring)

**Implementation:**
- Use `numpy` + polynomial regression to simulate LSTM-style forecasting
- Generate realistic synthetic time series for 5 product types
- Return: `{ forecast_7_days: [102, 105, 98, ...], recommended_price: 145.50, trend: "RISING", confidence: 0.87 }`
- Expose `POST /ai/forecast` endpoint

---

## 🗃️ DATABASE MODELS

### User
```
id, name, email, password_hash, role (farmer/admin/consumer), 
phone, location, created_at, is_active
```

### Product
```
id, name, type (spice/coffee/tea/millet/organic), 
description, origin_state, farmer_id, created_at
```

### Batch
```
id, batch_code (unique), product_id, farmer_id,
quantity_kg, harvest_date, moisture_level, color_score, 
aroma_score, defect_percentage, weight_per_unit,
grade (A/B/C), quality_score, qr_code_path,
blockchain_block_index, created_at, status
```

### SupplyChainEvent
```
id, batch_id, event_type (CREATED/QUALITY_CHECKED/DISPATCHED/
IN_TRANSIT/RECEIVED_DISTRIBUTOR/RECEIVED_RETAILER/SOLD),
actor_name, actor_role, location, notes, timestamp,
blockchain_block_index, fraud_score, is_flagged
```

### BlockchainBlock
```
id, index, timestamp, data_json, previous_hash, hash, nonce
```

---

## 🔐 AUTH & ROLES

### Three roles:
1. **farmer** — can add products, batches, view own dashboard
2. **admin** — can view all users, all batches, all blockchain, all AI insights
3. **consumer** — can scan QR and view product journey (no login required for QR scan)

### Auth flow:
- `POST /auth/register` — register with role
- `POST /auth/login` — returns JWT token
- `GET /auth/me` — returns current user
- All farmer/admin routes protected with JWT middleware
- Consumer QR route is public

---

## 📡 ALL API ENDPOINTS

```
AUTH
POST   /auth/register
POST   /auth/login
GET    /auth/me

FARMER
GET    /farmer/dashboard          # Stats: total batches, avg grade, revenue
POST   /farmer/products           # Add new product
GET    /farmer/products           # List own products
POST   /farmer/batches            # Create batch (triggers QR + AI grading + blockchain)
GET    /farmer/batches            # List own batches
GET    /farmer/batches/{id}       # Batch detail

ADMIN
GET    /admin/dashboard           # All stats
GET    /admin/users               # All users
GET    /admin/batches             # All batches
GET    /admin/flagged             # Fraud-flagged events
GET    /admin/reports             # Download report (JSON)

CONSUMER (PUBLIC)
GET    /consumer/verify/{batch_code}   # Full product journey for QR scan

BLOCKCHAIN
GET    /blockchain/chain               # Full chain
GET    /blockchain/block/{index}       # Single block
GET    /blockchain/verify              # Verify chain integrity

AI
POST   /ai/grade-quality               # Grade a batch
POST   /ai/detect-fraud                # Fraud detection
POST   /ai/forecast                    # Demand forecast
GET    /ai/insights/{product_type}     # Pre-computed insights for product type

SUPPLY CHAIN
POST   /supply/event                   # Add supply chain event (distributor/retailer updates)
GET    /supply/batch/{batch_code}      # Full timeline for a batch

QR
GET    /qr/{batch_code}                # Return QR code image
```

---

## 🎨 FRONTEND DESIGN — AGRI THEMED (IMPLEMENT BEAUTIFULLY)

### Color Palette (define as CSS variables):
```css
:root {
  --green-primary: #2D6A4F;     /* Deep forest green */
  --green-secondary: #40916C;   /* Medium green */
  --green-accent: #74C69D;      /* Fresh mint green */
  --green-light: #B7E4C7;       /* Pale leaf green */
  --green-xlight: #D8F3DC;      /* Background tint */
  --amber: #F4A261;             /* Warm harvest amber */
  --amber-dark: #E76F51;        /* Deep terracotta */
  --earth: #8B5E3C;             /* Rich soil brown */
  --cream: #FEFAE0;             /* Warm off-white */
  --text-dark: #1B1B1B;
  --text-mid: #4A4A4A;
  --text-light: #888888;
}
```

### Typography:
- **Headings:** `'Playfair Display'` from Google Fonts (elegant, natural)
- **Body:** `'DM Sans'` from Google Fonts (clean, modern)

### Design System:
- Cards: `rounded-2xl`, soft shadow, `bg-white` with green top border accent (4px)
- Buttons: Primary = `bg-green-primary` with hover lift effect, Secondary = outlined green
- Navbar: Deep green (`#2D6A4F`) with leaf logo SVG icon and white text
- Sidebar: `#1B4332` dark green with active states in `#40916C`
- Data tables: Alternating `green-xlight` rows
- Grade badges: A = green pill, B = amber pill, C = red pill
- Charts (Recharts): Use green gradient fills
- Background: `#F0FAF4` (very subtle green tint)

### Animations (Framer Motion):
- Page transitions: fade + slide up on mount
- Cards: stagger entrance (each card 0.1s delay)
- Stats: count-up animation on number display
- Blockchain blocks: slide in from right when new block added
- QR verification: scan line animation

---

## 📄 PAGE SPECIFICATIONS

### 1. Landing Page (`/`)
- Full-screen hero with animated grain texture overlay
- Headline: "From Farm to Table — Verified, Trusted, Transparent"
- 3 feature cards: Blockchain Security / AI Quality / QR Verification
- Animated supply chain flow diagram (SVG arrows: Farmer → AI → Blockchain → QR → Consumer)
- CTA buttons: "Register as Farmer" and "Verify a Product"
- Footer with tagline

### 2. Farmer Dashboard (`/farmer`)
Stats row:
- Total Batches | Grade A % | Avg Quality Score | Flagged Batches
Below:
- Recent Batches table with grade badges and blockchain status
- 7-day demand forecast chart (Recharts LineChart) — pulled from AI endpoint
- Quick action buttons: "+ Add Batch", "View Blockchain"

### 3. Add Batch Page (`/farmer/add-batch`)
Multi-step form (3 steps):
- Step 1: Product details (select product, harvest date, quantity)
- Step 2: Quality attributes (sliders for moisture, color, aroma, defect %)
- Step 3: Review + Submit
On submit:
- Call `POST /farmer/batches`
- Backend: AI grades it → Blockchain records it → QR generated
- Show success screen with generated QR code (downloadable)
- Show AI grade result with animated grade reveal

### 4. Admin Dashboard (`/admin`)
- Full stat overview (total users, batches, fraud flags, chain length)
- User management table with role badges
- Fraud-flagged events list with risk indicators
- Blockchain status: chain length, last block hash, verified ✓
- AI insights tab: aggregate quality by product type (bar chart)

### 5. Consumer Verify Page (`/verify`)
- QR code scanner (camera, using html5-qrcode)
- OR manual batch code entry
- On verification: beautiful product journey timeline
  - Each event shown as a vertical timeline card
  - Blockchain verification badge shown (✓ Verified on Chain)
  - Grade badge and quality score
  - Farm origin map placeholder (with farm name + state)
  - Fraud-free indicator

### 6. Blockchain Explorer (`/blockchain`)
- Chain stats: total blocks, genesis hash, last block time
- Block cards in a horizontal scroll OR vertical list
- Each block shows: Index, Timestamp, Hash (truncated), Previous Hash, Data summary
- "Verify Chain" button → calls `/blockchain/verify` → shows animated ✓

### 7. AI Analytics Page (`/ai`)
- Quality grade distribution (PieChart by product type)
- Fraud detection heatmap-style table
- Demand forecast for all 5 product types (multi-line chart)
- Manual test panel: enter product attributes → get live AI grade

---

## 🧩 COMPONENT SPECIFICATIONS

### `ProductTimeline.jsx`
Vertical timeline showing supply chain events.
Each node: colored dot + event name + location + actor + timestamp + blockchain index.
Colors: CREATED=green, IN_TRANSIT=amber, RECEIVED=blue, SOLD=purple.

### `BlockchainViewer.jsx`
Horizontal scrollable blockchain visualization.
Each block = card with: index badge, truncated hash, previous hash connector arrow, timestamp.
"Genesis" block styled differently (gold border).

### `AIInsightCard.jsx`
Card showing AI result with: grade pill, confidence bar, recommendations list, product icon.

### `QRScanner.jsx`
Camera QR scanner using `html5-qrcode`. Shows scan frame animation.
On success, redirect to `/verify?batch={code}`.

### `StatCard.jsx`
Metric card with: icon, label, value (count-up), trend arrow (up/down).

---

## 🌱 SEED DATA (auto-generate on startup)

In `utils/seed_data.py`, auto-generate on first run:

**Users:**
- 3 farmers (Ravi Kumar - Karnataka, Priya Nair - Kerala, Arjun Patel - Gujarat)
- 1 admin (admin@agrichain.com / admin123)

**Products:**
- Coorg Coffee, Kerala Black Pepper, Assam Green Tea, Rajasthan Bajra, Organic Turmeric

**Batches:** 10 batches (2 per farmer, mixed grades)

**Supply Chain Events:** Full journey for each batch (CREATED → QUALITY_CHECKED → DISPATCHED → IN_TRANSIT → RECEIVED_DISTRIBUTOR → RECEIVED_RETAILER)

**Blockchain:** All 60+ events recorded as blocks

**AI Data:** Pre-run grading and fraud detection on all batches

---

## 🔧 SETUP & RUN

### `requirements.txt`
```
fastapi==0.111.0
uvicorn==0.30.1
sqlalchemy==2.0.30
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
qrcode[pil]==7.4.2
Pillow==10.3.0
scikit-learn==1.5.0
numpy==1.26.4
joblib==1.4.2
pydantic==2.7.1
aiofiles==23.2.1
```

### `run.sh`
```bash
#!/bin/bash
echo "🌿 Starting AgriChain..."

# Backend
cd backend
pip install -r requirements.txt -q
uvicorn main:app --reload --port 8000 &

# Frontend
cd ../frontend
npm install -q
npm run dev &

echo "✅ AgriChain running!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
wait
```

### `backend/main.py` must:
- Include CORS for `http://localhost:5173`
- Mount `/qr_codes` as static files
- Call `seed_data.run_seed()` on startup if DB is empty
- Include all routers with `/api` prefix

---

## ✅ BUILD ORDER (Follow this sequence)

Build and verify each step before moving to the next:

```
Step 1:  Project folder structure + git init
Step 2:  Backend database models + SQLAlchemy setup
Step 3:  Simulated blockchain module (chain.py) + tests
Step 4:  Auth system (register/login/JWT)
Step 5:  AI modules (quality grader → fraud detector → forecaster)
Step 6:  QR code generator utility
Step 7:  All API routes (farmer, admin, consumer, blockchain, ai)
Step 8:  Seed data generator + run it
Step 9:  Frontend project setup (Vite + React + Tailwind + fonts)
Step 10: Global styles + design system (CSS variables, typography)
Step 11: Auth pages (Login, Register) with animations
Step 12: Landing page (hero, features, flow diagram)
Step 13: Farmer Dashboard + Add Batch form
Step 14: Consumer Verify page + QR scanner
Step 15: Admin Dashboard
Step 16: Blockchain Explorer page
Step 17: AI Analytics page
Step 18: Final integration test + run.sh
```

---

## ⚠️ IMPORTANT INSTRUCTIONS FOR WINDSURF

1. **Ask before assuming** — If any requirement is unclear, stop and ask the user.
2. **No placeholder code** — Every function must be fully implemented.
3. **Test as you build** — After each backend module, verify the endpoint works.
4. **Keep AI models deterministic** — Use `random_state=42` everywhere so results are reproducible.
5. **QR codes** — Must encode the full consumer verify URL: `http://localhost:5173/verify?batch={batch_code}`
6. **Blockchain persistence** — Blocks MUST be saved to SQLite, not just in-memory.
7. **Frontend must be adaptive** — Mobile-first, responsive at all breakpoints.
8. **Error handling** — All API endpoints must return proper HTTP status codes and error messages.
9. **Loading states** — All frontend API calls must show loading spinners.
10. **Console logs** — Add descriptive console logs in backend for all major operations.

---

## 🚀 START COMMAND

**Say this to Windsurf to begin:**

> "Please read the full AGRICHAIN_MASTER_PROMPT.md file I've shared. Then start building the project from Step 1. After completing each step, tell me what was built and what's coming next. Ask me if you need any clarification before making assumptions."

---

*Built for: AgriChain — AI + Blockchain Agricultural Provenance System*
*Stack: FastAPI + React + SQLite + Simulated Blockchain + Scikit-learn AI*
*Theme: Agri-green vibrant dashboard*
