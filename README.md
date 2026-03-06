# Procurefy — Multi-Agent Supply Chain PO Automation

**Cummins Xtern Hackathon 2026** | IU Indianapolis

Procurefy is an AI-powered procurement system that automates purchase order generation for Cummins heavy-duty diesel engine parts. It uses a **4-agent LangGraph pipeline** with **human-in-the-loop** controls, **Model Context Protocol (MCP) servers** for structured data access, and a modern **Next.js** dashboard — enabling supply chain planners to go from demand analysis to approved PO in minutes instead of days.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Pipeline: How It Works](#pipeline-how-it-works)
- [MCP Servers](#mcp-servers)
- [Database Schema](#database-schema)
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Frontend Pages](#frontend-pages)
- [Environment Variables](#environment-variables)
- [Seed Data](#seed-data)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Next.js Frontend                           │
│  Dashboard · Pipeline Wizard · Approvals · Logs · Suppliers     │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────────┐
│                     FastAPI Backend                              │
│         Step-by-step pipeline with human-in-the-loop            │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────┐│
│  │   Demand      │→│  Supplier    │→│  Container   │→│  PO    ││
│  │   Analyst     │  │  Selector   │  │  Optimizer   │  │Compiler││
│  └──────┬───────┘  └──────┬──────┘  └──────┬───────┘  └──┬───┘│
│         │ MCP              │ MCP            │ MCP          │MCP │
└─────────┼──────────────────┼────────────────┼─────────────┼────┘
          ▼                  ▼                ▼             ▼
┌─────────────────┐ ┌───────────────┐ ┌───────────────┐ ┌────────┐
│  ERP Data       │ │ Supplier Data │ │  Logistics    │ │  PO    │
│  MCP Server     │ │ MCP Server    │ │  MCP Server   │ │Mgmt MCP│
└────────┬────────┘ └───────┬───────┘ └───────┬───────┘ └───┬────┘
         └──────────────────┴─────────────────┴─────────────┘
                          Supabase (PostgreSQL)
```

---

## Key Features

- **Multi-Agent AI Pipeline** — 4 specialized LangGraph agents that each handle one step of the procurement process, with LLM-powered rationale and confidence scoring at every stage
- **Human-in-the-Loop** — Planners review and approve results after each agent before proceeding; edit quantities, override supplier selections, and select/deselect specific SKUs between steps
- **Model Context Protocol (MCP)** — 4 dedicated MCP servers expose Supabase data as structured tools, giving agents sandboxed, schema-validated access to ERP, supplier, logistics, and PO data
- **Smart Demand Analysis** — Considers current inventory, safety stock, in-transit quantities, open PO deduplication, MOQ enforcement, demand forecasts, historical sales delta, and 3-level urgency classification (critical / watch / normal)
- **Weighted Supplier Scoring** — Category-specific weighted scoring across quality, delivery performance, lead time, and cost; returns top 3 candidates per SKU with sub-score breakdowns
- **Container Optimization** — First-fit decreasing bin packing across 20ft and 40ft container types with weight/volume utilization calculations and freight cost estimation
- **Full Audit Trail** — Every agent decision is logged to a `decision_log` table with inputs, outputs, confidence scores, and rationale
- **Role-Based Auth** — Supabase Auth with administrator and PO manager roles
- **Responsive Dashboard** — Dark-themed UI with sidebar navigation, real-time status tracking, sortable data tables, and animated landing page

---

## Tech Stack

| Layer           | Technology                                                                         |
| --------------- | ---------------------------------------------------------------------------------- |
| **Frontend**    | Next.js 16, React 19, TypeScript, Tailwind CSS 4, Framer Motion, Recharts, Zustand |
| **Backend**     | Python 3.11+, FastAPI, LangGraph, LangChain                                        |
| **LLM**         | OpenAI GPT-4o-mini (configurable)                                                  |
| **MCP Servers** | TypeScript, `@modelcontextprotocol/sdk`, Zod validation                            |
| **Database**    | Supabase (PostgreSQL) with Row Level Security                                      |
| **Auth**        | Supabase Auth (email/password)                                                     |
| **Transport**   | MCP servers communicate via stdio JSON-RPC subprocess calls                        |

---

## Project Structure

```
xtern/
├── backend/                    # FastAPI backend
│   ├── main.py                 # API server & pipeline endpoints
│   ├── config.py               # Environment loading
│   ├── requirements.txt        # Python dependencies
│   ├── agents/                 # LangGraph agent nodes
│   │   ├── demand_analyst.py   # Agent 1: Demand analysis & net requirements
│   │   ├── supplier_selector.py# Agent 2: Supplier scoring & selection
│   │   ├── container_optimizer.py # Agent 3: Container planning
│   │   ├── po_compiler.py      # Agent 4: Draft PO creation
│   │   └── llm_config.py       # LLM initialization & activity tracking
│   ├── graph/                  # LangGraph pipeline definition
│   │   ├── pipeline.py         # StateGraph with conditional routing
│   │   └── state.py            # PipelineState TypedDict schema
│   └── mcp_client/             # MCP client for calling MCP servers
│       └── client.py           # stdio JSON-RPC subprocess transport
├── frontend/                   # Next.js 16 frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx        # Landing page (ProcureAI hero)
│   │   │   ├── pipeline/       # Pipeline wizard (step-by-step)
│   │   │   ├── approvals/      # PO review & approve/reject
│   │   │   ├── logs/           # Decision audit log viewer
│   │   │   ├── data/           # Inventory & product data tables
│   │   │   ├── suppliers/      # Supplier directory & scoring
│   │   │   ├── agents/         # Agent status dashboard
│   │   │   ├── account/        # User account settings
│   │   │   └── login/          # Authentication page
│   │   ├── lib/
│   │   │   ├── api.ts          # Backend API client
│   │   │   ├── supabase.ts     # Supabase browser client
│   │   │   └── auth.ts         # Auth helpers (sign in/out, roles)
│   │   ├── components/         # Reusable UI components
│   │   └── contexts/           # React context providers (Auth)
│   └── package.json
├── mcp-servers/                # 4 Model Context Protocol servers
│   ├── erp-data-server/        # Products, inventory, forecasts
│   ├── supplier-data-server/   # Suppliers, pricing, scoring
│   ├── logistics-server/       # Container specs, bin packing
│   └── po-management-server/   # PO CRUD, decision logging
├── supabase/
│   └── schema.sql              # Full database schema
├── data/
│   └── seed_data.py            # Realistic Cummins part seed data
├── SETUP.md                    # Detailed setup guide
└── README.md                   # This file
```

---

## Pipeline: How It Works

The pipeline runs **step-by-step** with human review after each agent:

### Step 1 — Demand Analyst

`POST /pipeline/start`

- Fetches **inventory positions** and **demand forecasts** via the ERP MCP server
- Checks for **open/pending POs** to prevent duplicate ordering
- Calculates **net replenishment quantity** per SKU: `net = forecast + safety_stock - available - open_po_qty`
- Enforces **MOQ (Minimum Order Quantity)** floors
- Classifies urgency: **critical** (stock ≤ safety), **watch** (stock ≤ reorder point), **normal**
- Estimates **need-by date** based on days of stock remaining
- Calculates **sales delta %** from historical actuals
- LLM validates calculations and produces confidence score + rationale

**Planner reviews:** Select which SKUs to proceed with, edit quantities.

### Step 2 — Supplier Selector

`POST /pipeline/{run_id}/continue/supplier_selector`

- For each SKU, calls the Supplier MCP server's **`score_suppliers`** tool
- Applies **category-specific weighted scoring**: quality (35%), delivery (25%), cost (25%), lead time (15%)
- Returns **top 3 candidates** per SKU with sub-score breakdowns
- LLM summarizes selection rationale and flags procurement concerns

**Planner reviews:** Override supplier picks from the candidate dropdown, select which SKUs to include.

### Step 3 — Container Optimizer

`POST /pipeline/{run_id}/continue/container_optimizer`

- Fetches **product dimensions** (weight, CBM) from ERP MCP
- Calls Logistics MCP server's **`calculate_container_plan`** tool
- Uses **first-fit decreasing bin packing** across 20ft and 40ft containers
- Outputs TEU count, weight/volume utilization %, and estimated freight cost
- LLM provides rationale on the container plan

**Planner reviews:** Verify container plan and line items before PO creation.

### Step 4 — PO Compiler

`POST /pipeline/{run_id}/continue/po_compiler`

- Assembles all agent outputs into a **draft Purchase Order**
- LLM writes an **executive summary** for the PO
- Saves the PO, line items, and container plan to Supabase via PO Management MCP
- Logs the final decision to the audit trail
- PO enters **draft** status, awaiting human approval

---

## MCP Servers

Each MCP server is a standalone TypeScript process using the `@modelcontextprotocol/sdk` and communicates via **stdio JSON-RPC**:

| Server                   | Port  | Tools                                                                                        |
| ------------------------ | ----- | -------------------------------------------------------------------------------------------- |
| **erp-data-server**      | stdio | `get_products`, `get_inventory`, `get_forecasts`, `ping`                                     |
| **supplier-data-server** | stdio | `get_suppliers`, `get_supplier_products`, `score_suppliers`, `ping`                          |
| **logistics-server**     | stdio | `get_container_specs`, `calculate_container_plan`, `ping`                                    |
| **po-management-server** | stdio | `create_draft_po`, `get_pos`, `update_po_status`, `get_decision_log`, `log_decision`, `ping` |

All servers read from Supabase and are invoked by the Python backend as subprocesses. Input validation is handled by Zod schemas.

---

## Database Schema

The Supabase PostgreSQL database contains 9 tables:

| Table                      | Description                                                                 |
| -------------------------- | --------------------------------------------------------------------------- |
| `products`                 | 60 Cummins diesel engine parts (filters, gaskets, engine parts, electrical) |
| `suppliers`                | 6 suppliers with quality, delivery, lead time, and cost scores              |
| `supplier_products`        | ~195 supplier-product pricing mappings                                      |
| `forecasts`                | 720 monthly demand forecasts (12 months × 60 SKUs)                          |
| `inventory`                | 60 inventory positions with stock, safety stock, reorder points             |
| `container_specs`          | Container types (20ft, 40ft) with weight/volume/cost specs                  |
| `supplier_scoring_weights` | Category-specific scoring weights for supplier selection                    |
| `purchase_orders`          | PO headers with status tracking (draft → approved/rejected)                 |
| `po_line_items`            | PO line items with SKU, supplier, quantity, price, rationale                |
| `decision_log`             | Full audit trail of every agent decision                                    |

Schema definition: [`supabase/schema.sql`](supabase/schema.sql)

---

## Getting Started

### Prerequisites

- **Node.js** 18+
- **Python** 3.11+
- **Supabase** account (free tier): https://supabase.com
- **OpenAI** API key: https://platform.openai.com

### 1. Clone the repository

```bash
git clone <repo-url>
cd xtern
```

### 2. Set up environment variables

Create a `.env` file in the project root:

```env
NEXT_PUBLIC_SUPABASE_URL=https://YOUR-PROJECT-ID.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://YOUR-PROJECT-ID.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### 3. Set up the database

Run the contents of [`supabase/schema.sql`](supabase/schema.sql) in your Supabase Dashboard → SQL Editor.

### 4. Seed the database

```bash
cd data
pip install supabase python-dotenv
python seed_data.py
```

Expected output: 60 products, 6 suppliers, ~195 supplier-products, 720 forecasts, 60 inventory records.

### 5. Build MCP servers

```bash
cd mcp-servers/erp-data-server && npm install && npm run build
cd ../supplier-data-server && npm install && npm run build
cd ../logistics-server && npm install && npm run build
cd ../po-management-server && npm install && npm run build
```

### 6. Install backend dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

### 7. Install frontend dependencies

```bash
cd frontend
npm install
```

---

## Running the Application

### Start the backend

```bash
cd backend
uvicorn main:app --reload
```

Backend runs at: http://localhost:8000

### Start the frontend

```bash
cd frontend
npm run dev
```

Frontend runs at: http://localhost:3000

### Verify setup

```bash
curl http://localhost:8000/health
curl http://localhost:8000/test-supabase
curl http://localhost:8000/test-openai
curl http://localhost:8000/data-summary
```

---

## API Endpoints

| Method | Endpoint                              | Description                      |
| ------ | ------------------------------------- | -------------------------------- |
| `GET`  | `/health`                             | Health check with env status     |
| `GET`  | `/test-supabase`                      | Verify Supabase connection       |
| `GET`  | `/test-openai`                        | Verify OpenAI LLM connection     |
| `GET`  | `/data-summary`                       | Row counts for all seeded tables |
| `GET`  | `/products`                           | List all products                |
| `POST` | `/pipeline/start`                     | Run Demand Analyst (step 1)      |
| `POST` | `/pipeline/{run_id}/continue/{agent}` | Run next agent (steps 2–4)       |
| `POST` | `/pipeline/approve/{po_number}`       | Approve or reject a draft PO     |
| `GET`  | `/pipeline/pos`                       | List purchase orders             |
| `GET`  | `/pipeline/logs`                      | Get decision log entries         |

---

## Frontend Pages

| Route        | Page            | Description                                          |
| ------------ | --------------- | ---------------------------------------------------- |
| `/`          | Landing         | Animated hero page with feature overview             |
| `/login`     | Login           | Email/password authentication                        |
| `/pipeline`  | Pipeline Wizard | Step-by-step pipeline execution with review gates    |
| `/approvals` | Approvals       | Review, approve, or reject draft POs                 |
| `/logs`      | Decision Log    | Filterable audit trail of all agent decisions        |
| `/data`      | Data Explorer   | Inventory positions and product catalog with sorting |
| `/suppliers` | Suppliers       | Supplier directory with score breakdowns             |
| `/agents`    | Agent Status    | Overview of all 4 AI agents and their configuration  |
| `/account`   | Account         | User profile and settings                            |

---

## Environment Variables

| Variable                        | Required | Description                                    |
| ------------------------------- | -------- | ---------------------------------------------- |
| `NEXT_PUBLIC_SUPABASE_URL`      | Yes      | Supabase project URL                           |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes      | Supabase anonymous key (frontend)              |
| `SUPABASE_SERVICE_ROLE_KEY`     | Yes      | Supabase service role key (backend + MCP)      |
| `OPENAI_API_KEY`                | Yes      | OpenAI API key for GPT-4o-mini                 |
| `OPENAI_MODEL`                  | No       | LLM model name (default: `gpt-4o-mini`)        |
| `NEXT_PUBLIC_BACKEND_URL`       | No       | Backend URL (default: `http://localhost:8000`) |

---

## Seed Data

The seed script ([`data/seed_data.py`](data/seed_data.py)) generates realistic Cummins heavy-duty diesel engine supply chain data:

- **60 products** across 4 categories: filters (15), gaskets (15), engine parts (15), electrical (15)
- **6 suppliers** with varied quality/delivery/cost profiles and regional diversity
- **~195 supplier-product mappings** with category-appropriate pricing
- **720 demand forecasts** (12 months × 60 SKUs) with seasonal variation
- **60 inventory records** with realistic stock levels calibrated to trigger replenishment
- **Container specs** for 20ft and 40ft standard containers
- **Category scoring weights** tuned per product category

All values are modeled after real Cummins ISX15, ISB6.7, QSK60, and X15 platform parts with accurate weights, volumes, prices, and MOQs.
