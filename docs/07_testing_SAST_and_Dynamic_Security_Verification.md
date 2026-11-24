# Testing: SAST & Dynamic Security Verification
**Frameworks:** Ruff (Backend SAST) / ESLint + `eslint-plugin-security` (Frontend SAST) / Pytest + HTTPX (Backend DAST) / Node Test Runner (Frontend DAST) / GitHub Actions CI  

## 1. Security Testing Architecture & Directory Layout
```text
secure_web_application/
├── .github/
│   └── workflows/
│       └── sast-ci.yml                 # Automated Full-Stack SAST & DAST CI/CD Pipeline
├── backend/
│   ├── pyproject.toml                  # Ruff SAST rule configuration (flake8-bandit 'S' rules)
│   ├── requirements.txt                # Includes ruff, pytest, and httpx security testing tools
│   └── tests/
│       └── test_dast_security.py       # Automated Backend DAST exploit & header test suite
└── frontend/
    ├── .eslintrc.js                    # ESLint + eslint-plugin-security configuration
    └── tests/
        └── dast_frontend.test.mjs      # Automated Frontend DAST runtime & CORS probe suite
```

### Security Testing File Purpose Matrix
| File Path | Testing Layer & Role | Key Security Controls Verified |
| :--- | :--- | :--- |
| `backend/pyproject.toml` | Backend SAST Configuration | Enforces `flake8-bandit` (`S`), `flake8-bugbear` (`B`), `Pyflakes` (`F`), and `pycodestyle` (`E`) rules across `app/`. |
| `frontend/.eslintrc.js` | Frontend SAST Configuration | Enforces `react/no-danger`, `react/jsx-no-target-blank`, `security/detect-unsafe-regex`, and `security/detect-object-injection`. |
| `backend/tests/test_dast_security.py` | Backend Automated DAST | Executes live HTTP exploit simulations against FastAPI (`SQLi`, `CSRF bypass`, `RBAC escalation`, `BOLA/IDOR`, and `HTTP security headers`). |
| `frontend/tests/dast_frontend.test.mjs` | Frontend Automated DAST | Probes live React SPA (`localhost:3000`) and API preflight policies for stack trace leaks, `.env`/`.git` exposure, reflected XSS, and strict CORS origins. |
| `.github/workflows/sast-ci.yml` | Automated DevSecOps CI/CD | Runs Ruff SAST, ESLint SAST, spins up a live PostgreSQL 15 container, boots both servers, and executes Pytest + Node DAST on every push/PR. |

---

## 2. Static Application Security Testing (SAST)
### Backend Static Analysis (Ruff)
Ruff inspects the FastAPI codebase (`backend/app/`) against `flake8-bandit` (`S`) security rules to detect hardcoded secrets (`S105`), raw SQL string formatting (`S608`), and insecure cryptographic primitives.

```powershell
# Run from backend/ with virtual environment active
ruff check --select S app/
```

* **Verification Result:** `All checks passed!` — Confirms all secrets are loaded via environment variables (`os.getenv`) with secure runtime fallbacks (`secrets.token_hex(32)`), passwords use Argon2id, and database queries rely exclusively on parameterized SQLAlchemy ORM expressions.

### Frontend Static Analysis (ESLint)
ESLint paired with `eslint-plugin-security` and `eslint-plugin-react` audits JSX components (`frontend/src/`) for DOM-based XSS vectors, reverse tabnabbing, and prototype/object injection sinks.

```powershell
# Run from frontend/
npx eslint src/ --ext .js,.jsx
```

#### SAST Vulnerability Catch & Remediation Log
To validate rule enforcement prior to CI/CD integration, intentional anti-patterns were temporarily introduced into `frontend/src/App.jsx`, detected by ESLint, and remediated:

| Rule ID | Severity | Vulnerability Pattern Tested | Remediation Applied |
| :--- | :--- | :--- | :--- |
| `react/no-danger` | Error | `dangerouslySetInnerHTML={{ __html: reason }}` | Replaced with standard JSX expression interpolation (`{reason}`), enforcing React automatic HTML entity escaping. |
| `react/jsx-no-target-blank` | Error | `<a href="..." target="_blank">` without `rel` | Removed unguarded external anchor / enforced `rel="noopener noreferrer"` to prevent reverse tabnabbing. |
| `security/detect-object-injection` | Warning | Dynamic bracket lookup (`configMap[swapType]`) | Replaced bracket notation with explicit conditional/safe property access on validated enum values. |

* **Post-Remediation Result:** `npx eslint src/ --ext .js,.jsx` exits with code `0` (0 errors, 0 warnings).

---

## 3. Automated Dynamic Application Security Testing (DAST)
### Backend Automated DAST Suite (`pytest` + `httpx`)
With PostgreSQL running on port `5432` and FastAPI running on `http://127.0.0.1:8000`, execute the live dynamic exploit suite from `backend/`:

```powershell
pytest -v tests/test_dast_security.py
```

| Test Case ID | Test Function | Live Attack Payload / Probe | Expected & Verified Outcome |
| :--- | :--- | :--- | :--- |
| **DAST-01** | `test_dast_01_sqli_login_bypass` | Submits `username="' OR '1'='1' --"` to `POST /api/v1/auth/login`. | `401 Unauthorized` (`Incorrect email or password`); SQLAlchemy treats payload as a literal parameter. |
| **DAST-02** | `test_dast_02_csrf_missing_header_blocked` | Sends authenticated `POST /api/v1/swap-requests` with valid JWT and session cookie, omitting `X-CSRF-Token`. | `403 Forbidden` (`CSRF token verification failed.`); Double-Submit Cookie middleware blocks request. |
| **DAST-03** | `test_dast_03_rbac_admin_endpoint_blocked` | Queries `GET /api/v1/admin/swap-requests` using a standard `subscriber` role JWT. | `403 Forbidden` (`Admin privileges required.`); `require_admin` RBAC dependency rejects privilege escalation. |
| **DAST-04** | `test_dast_04_bola_idor_unauthorized_object_access` | Creates a swap request as an authenticated subscriber, then queries `GET /api/v1/swap-requests/{id}` without owner authorization. | `401 Unauthorized` / `403 Forbidden`; prevents unauthorized object enumeration (BOLA/IDOR). |
| **DAST-05** | `test_dast_05_security_headers_enforced` | Inspects HTTP response headers returned by `GET /openapi.json`. | `200 OK` containing `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, and `Content-Security-Policy`. |

### Frontend Automated DAST Suite (`node --test`)
With both React (`http://localhost:3000`) and FastAPI (`http://127.0.0.1:8000`) running locally, execute the runtime SPA security suite from `frontend/`:

```powershell
node --test tests/dast_frontend.test.mjs
```

| Test Case ID | Probe Description | Expected & Verified Outcome |
| :--- | :--- | :--- |
| **FE-DAST-01** | Live SPA entry rendering & stack trace leak check (`GET /`). | `200 OK` with `<div id="root"></div>` present and zero server tracebacks exposed. |
| **FE-DAST-02** | Sensitive file exposure probe (`/.env`, `/.env.local`, `/.git/config`). | No environment secrets (`DB_PASSWORD`) or Git configuration (`[core]`) served by the dev/static server. |
| **FE-DAST-03** | Reflected XSS probe via URL query parameter (`/?q=<script>alert("xss")</script>`). | Unescaped `<script>` payload is never reflected in the rendered HTML response. |
| **FE-DAST-04** | Cross-Origin Resource Sharing (`OPTIONS`) preflight validation. | Permits `http://localhost:3000` and blocks untrusted origins (`http://evil-phishing-site.com`). |

---

## 4. Continuous DevSecOps Pipeline (GitHub Actions)
The workflow `.github/workflows/sast-ci.yml` (**Full-Stack SAST & DAST Security Audit**) triggers automatically on every `push` to `main`/`develop` and every `pull_request` targeting `main`:

1. **`backend_sast`:** Installs Ruff on `ubuntu-latest` and runs `ruff check --select S app/`.
2. **`frontend_sast`:** Installs Node.js 20 dependencies and runs `npx eslint src/ --ext .js,.jsx`.
3. **`dast_security_audit` (runs after both SAST jobs pass):**
   * Spins up an isolated `postgres:15` service container with health checks.
   * Initializes SQLAlchemy tables and seeds test accounts (`subscriber@telecom.com` and `admin@telecom.com`) with Argon2id hashes.
   * Launches Uvicorn (`127.0.0.1:8000`) and React (`localhost:3000`) in the background, waits for readiness via `wait-on`, and executes both `pytest -v tests/test_dast_security.py` (5/5 passed) and `node --test tests/dast_frontend.test.mjs` (4/4 passed).

---

## 5. OWASP Top 10 Verification Summary
| OWASP Top 10 Category | Implemented Mitigation | Verification Method | Status |
| :--- | :--- | :--- | :--- |
| **A01: Broken Access Control** | JWT role claims (`require_admin`), BOLA owner ID verification, and Double-Submit Anti-CSRF middleware. | `DAST-02`, `DAST-03`, `DAST-04` | Verified |
| **A02: Cryptographic Failures** | Argon2id password hashing (`m=65536, t=3, p=4`), HS256 JWT signing, environment-injected secrets. | Ruff `S105`, DB Inspection | Verified |
| **A03: Injection (SQLi & XSS)** | SQLAlchemy ORM parameterized queries, Pydantic input validation, React JSX auto-escaping. | Ruff `S608`, ESLint `react/no-danger`, `DAST-01`, `FE-DAST-03` | Verified |
| **A05: Security Misconfiguration** | Strict CORS origin whitelist, CSP, HSTS, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`. | `DAST-05`, `FE-DAST-02`, `FE-DAST-04` | Verified |