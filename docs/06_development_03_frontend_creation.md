# Frontend
**Framework:** React 18+ / PrimeReact / Axios / Tailwind CSS / Node.js  

## 1. Project Directory & Architecture Layout
```text
frontend/
├── public/
│   └── index.html                # HTML5 root template & DOM entry point
├── src/
│   ├── services/
│   │   └── api.js                # Centralized Axios client & anti-CSRF/JWT interceptors
│   ├── App.jsx                   # Primary UI view, state management & RBAC views
│   └── index.js                  # React DOM rendering root & global style imports
├── package.json                  # Node dependency manifest & build scripts
└── package-lock.json             # Exact dependency tree lockfile
```

## 2. File Directory & Code Purpose Matrix
| File Path | Component Purpose & Core Responsibilities | Key Security & Technical Mechanisms |
| :--- | :--- | :--- |
| `public/index.html` | HTML5 foundational document mounting the React virtual DOM tree into `<div id="root">`. | Sets secure viewport constraints, UTF-8 charset declarations, and responsive meta tags. |
| `src/index.js` | Application bootstrap script mounting `<App />` via React 18 `createRoot` concurrent renderer. | Imports PrimeReact component theme stylesheets and wraps application in `React.StrictMode` for lifecycle auditing. |
| `src/services/api.js` | Centralized API communication module configuring Axios instance defaults (`baseURL: 'http://127.0.0.1:8000/api/v1'`). | • **Automated CSRF Injection:** Intercepts outgoing requests and attaches `X-CSRF-Token` headers extracted from `csrf_token` cookie/state.<br>• **Bearer Token Handling:** Automatically includes `Authorization: Bearer <token>` for authenticated routes.<br>• **Credentials Mode:** Enforces `withCredentials: true` to support HTTP-Only/SameSite cookie transmission. |
| `src/App.jsx` | Single-page application router and primary user dashboard container supporting Subscriber and Admin personas. | • **Client-Side RBAC:** Dynamically renders Subscriber forms vs. Global Admin Request Queues based on decoded JWT claims.<br>• **Input Validation:** Enforces strict regex validation on E.164 phone numbers (`^\+353[0-9]{8,9}$`) and 19-digit ICCID values before dispatching network payloads.<br>• **XSS Mitigation:** Relies on React's auto-escaping JSX engine to prevent DOM-based XSS attacks when displaying user inputs. |
| `package.json` | Project manifest declaring core build scripts (`start`, `build`) and runtime UI libraries. | Pins exact major versions for `react`, `react-dom`, `react-scripts`, `primereact`, `primeicons`, `axios`, and `tailwindcss`. |

## 3. Environment Setup & Dependency Installation
### Step 1: Navigate to Frontend Workspace
Open a terminal in the project root and navigate to the `frontend/` directory:

```powershell
# Windows (PowerShell / CMD) or macOS / Linux
cd frontend
```

### Step 2: Install Node Dependencies
Install all required UI components, styling libraries, and HTTP clients:

```powershell
npm install
```

> **Note (`react-scripts` missing error):** If `react-scripts` is not recognized, explicitly install it into `node_modules`:
> ```powershell
> npm install react-scripts --save
> ```

## 4. Security Configuration & Interceptor Setup
### 1. Centralized Axios Interceptor Configuration (`src/services/api.js`)
The API service ensures every state-modifying request (`POST`, `PUT`, `DELETE`) includes both a Bearer token and an anti-CSRF token:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  const csrfToken = localStorage.getItem('csrf_token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (csrfToken && ['post', 'put', 'delete', 'patch'].includes(config.method.toLowerCase())) {
    config.headers['X-CSRF-Token'] = csrfToken;
  }
  return config;
}, (error) => Promise.reject(error));

export default api;
```

## 5. Launching & Testing the Client
### Start React Development Server
Ensure the FastAPI Uvicorn backend is running on `http://127.0.0.1:8000`, then execute in your `frontend/` directory:

```powershell
npm start
```

### UI Verification Steps
1. **Subscriber Journey (`http://localhost:3000`)**:
   * Log in with Subscriber credentials (`subscriber@telecom.com` / `UserPassword123!`).
   * Submit a valid SIM swap request (e.g., Phone: `+353871234567`, ICCID: `8935300000000000001`).
   * Verify instant update in the **My SIM Swap History** PrimeReact DataTable.
2. **Support Admin Journey**:
   * Click **Logout** and log in as `admin@telecom.com` (`AdminPassword123!`).
   * Verify the interface switches to the **Global SIM Swap Request Queue**, displaying requests across all users with status transition controls (`Approve` / `Reject`).