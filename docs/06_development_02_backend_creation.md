# Backend
**Framework:** Python 3.11+ / FastAPI / SQLAlchemy ORM / PostgreSQL  

## 1. Project Directory & Architecture Layout
```text
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                 # Dependency Injection (Auth, JWT, RBAC)
│   │   └── v1/
│   │       └── endpoints.py        # REST API endpoints & route handlers
│   ├── core/
│   │   └── security.py             # Argon2id hashing & JWT generation
│   ├── db/
│   │   └── session.py              # SQLAlchemy engine & PostgreSQL connection
│   ├── middleware/
│   │   └── security_middleware.py  # CSP, HSTS & Double-Submit Anti-CSRF
│   ├── models/
│   │   └── entities.py             # SQLAlchemy ORM models & Enum definitions
│   └── main.py                     # FastAPI application entrypoint & CORS config
├── requirements.txt                # Python package dependency manifest
└── seed_passwords.py               # Database seeding script for Argon2id hashes
```

## 2. File Directory & Code Purpose Matrix
| File Path | Component Purpose & Core Responsibilities | Key Security & Technical Mechanisms |
| :--- | :--- | :--- |
| `app/main.py` | FastAPI application initialization, CORS policy declaration, middleware registration, and API router inclusion. | Enforces strict CORS origins (`http://localhost:3000`), mounts global security middleware, and initializes Uvicorn worker settings. |
| `app/db/session.py` | Initializes the database connection pool using SQLAlchemy's `create_engine` and provides DB session lifecycle hooks (`get_db`). | Utilizes `urllib.parse.quote_plus` to safely handle special characters (e.g., `@`) in database passwords; enforces connection pre-pinging. |
| `app/models/entities.py` | Defines ORM mappings (`User`, `SimSwapRequest`) matching PostgreSQL DDL tables and PostgreSQL `ENUM` types. | Uses `values_callable` lambda functions on Enum columns to seamlessly map database string values (`subscriber`, `admin`) to Python Enums. |
| `app/core/security.py` | Cryptographic utilities for password hashing and stateless token issuance. | Uses `argon2-cffi` ($m=65536, t=3, p=4$) for memory-hard password verification and `python-jose` for HS256 JWT signature creation. |
| `app/middleware/security_middleware.py` | ASGI HTTP middleware stack intercepting incoming web requests and outgoing HTTP responses. | • `SecurityHeadersMiddleware`: Injects HSTS, CSP (with dynamic Swagger `/docs` exemptions), `X-Frame-Options: DENY`, and `X-Content-Type-Options: nosniff`.<br>• `CSRFProtectionMiddleware`: Validates `X-CSRF-Token` headers against session cookies on state-changing methods (`POST`, `PUT`, `DELETE`). |
| `app/api/deps.py` | Reusable FastAPI dependency functions for authentication and authorization. | Intercepts HTTP Authorization headers, validates JWT integrity, extracts identity claims (`sub`), and enforces Role-Based Access Control (`require_admin`). |
| `app/api/v1/endpoints.py` | Business logic endpoints for Subscriber and Support Admin workflows. | Handles login, SIM swap submission, personal request listing, individual ID lookups with BOLA/IDOR protection checks, and global admin queues. |
| `seed_passwords.py` | Maintenance script for resetting test account password hashes in PostgreSQL. | Fetches raw passwords (`AdminPassword123!`, `UserPassword123!`), converts them to valid Argon2id hash strings, and commits changes to the database. |
| `requirements.txt` | Package lock specification for backend runtime and static security auditing. | Pinpoints versions for FastAPI, Uvicorn, SQLAlchemy, `psycopg2-binary`, `argon2-cffi`, `python-jose`, and Ruff. |


## 3. Environment Setup & Dependency Installation
### Step 1: Create Python Virtual Environment
Open a terminal in the `backend/` directory:

```powershell
# Windows (PowerShell)
python -m venv venv

# macOS / Linux
python3 -m venv venv
```

### Step 2: Activate Virtual Environment
```powershell
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

> **Note (PowerShell Execution Policy Error):** If PowerShell blocks script execution, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

### Step 3: Install Required Packages
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. PostgreSQL Database Configuration
### 1. Special Character Handling in Connection String
If your PostgreSQL master password contains reserved characters like `@`, ensure `app/db/session.py` uses `quote_plus`:

```python
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine

RAW_PASSWORD = os.getenv("DB_PASSWORD", "YourPasswordWith@Here")
ENCODED_PASSWORD = quote_plus(RAW_PASSWORD)

DATABASE_URL = f"postgresql+psycopg2://postgres:{ENCODED_PASSWORD}@127.0.0.1:5432/telecom_db"
```
### 2. Password Hash Seeding
Run the seeding script to populate PostgreSQL with valid Argon2id password hashes for testing:

```powershell
python seed_passwords.py
```

Expected Output:
```text
Admin hash updated: $argon2id$v=19$m=65536,t=3,p=4$...
Subscriber hash updated: $argon2id$v=19$m=65536,t=3,p=4$...
Database password hashes updated successfully!
```

## 5. Launching & Testing the Server
### Start Server via Uvicorn
Make sure your terminal is inside the `backend/` directory (where `app/` is located):

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Endpoint Verification & Documentation
1. Navigate to `http://127.0.0.1:8000/docs` in your browser.
2. Test **`POST /api/v1/auth/login`**:
   * **Username**: `subscriber@telecom.com`
   * **Password**: `UserPassword123!`
3. Verify that the server returns `200 OK` with `access_token`, `csrf_token`, and role `subscriber`.