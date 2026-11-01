# Secure Design & STRIDE Threat Modeling

Target Stack: Python FastAPI, React + PrimeReact, PostgreSQL (pgAdmin)

## 1. Data Flow Diagrams (DFD) & Trust Boundaries
Level-0 Context Diagram
    The Level-0 diagram establishes the outer boundary of the system, identifying external actors and high-level interactions across the primary public network trust boundary.

                   +---------------------------------------+
                   |          External Actors              |
                   |  (Subscriber / Support Admin Browser) |
                   +-------------------+-------------------+
                                       |
                                       | HTTPS / TLS 1.3
                                       | Requests + Headers
    =======================================v=======================================
            [ TRUST BOUNDARY 1: PUBLIC INTERNET / CLIENT-SERVER BOUNDARY ]
    ===============================================================================
                                       |
                   +-------------------+-------------------+
                   |   Telecom eSIM & SIM Swap Portal      |
                   |    (FastAPI + PostgreSQL Engine)      |
                   +---------------------------------------+
    
    Level-1 Data Flow Diagram
        The Level-1 diagram decomposes the application into sub-processes, datastores, and explicit internal trust boundaries.

                    [ Subscriber / Support Admin Browser ]
                               |
                               | 1. HTTP Requests (JWT, X-CSRF-Token, Credentials)
                               v
            ===============================================================================
            [ TRUST BOUNDARY 1: UNTRUSTED CLIENT -> FRONTEND APPLICATION ]
            ===============================================================================
                               |
                               | 2. API Call (JSON Payload)
                               v
                    +---------------------+
                    |  1.0 React UI /     |
                    |  PrimeReact View    |
                    +----------+----------+
                               |
                               | 3. REST API Requests over HTTPS
                               v
            ===============================================================================
            [ TRUST BOUNDARY 2: WEB FRONTEND -> FASTAPI APPLICATION SERVER ]
            ===============================================================================
                               |
                               v
                    +---------------------+
                    | 2.0 Security        |---- (Reject missing CSRF / invalid auth)
                    | Middleware          |
                    +----------+----------+
                               |
                               | 4. Processed Request Context
                               v
                    +---------------------+
                    | 3.0 Authorization   |---- (Verify RBAC: Subscriber vs Admin)
                    | & Route Controllers |
                    +----------+----------+
                               |
                               | 5. Parameterized SQL Queries (SQLAlchemy ORM)
                               v
            ===============================================================================
            [ TRUST BOUNDARY 3: FASTAPI SERVER -> POSTGRESQL DATABASE ]
            ===============================================================================
                               |
                               v
                    +---------------------+
                    | D1: PostgreSQL      |
                    | Datastore           |
                    +---------------------+

## 2. STRIDE Threat Identification Matrix
The STRIDE model categorizes potential security threats across all system components and data flows.

    ![alt text](/assets/stride_threat_idendification_matix.png)


## 3. STRIDE Threat Scenarios & Remediation Protocols
Scenario 1: Elevation of Privilege via BOLA/IDOR (Threat Category: E)
    Vulnerability Flow: A logged-in Subscriber changes the URL parameters or API request body from /api/v1/swap-requests/101 to /api/v1/swap-requests/102 to view another user's pending SIM swap request.

    Impact: Exposure of target MSISDN, ICCID, and personal subscriber identifiers.

    Design Control:

    Implement explicit resource ownership validation in the FastAPI controller layer.

    Compare current_user.id against swap_request.user_id. Reject non-matching non-admin access with HTTP 403 Forbidden before   querying details.

    // FastAPI Endpoint Defense Example
    @router.get("/swap-requests/{request_id}", response_model=SwapRequestResponse)
    def get_swap_request(
        request_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        swap_request = crud_swap.get(db, id=request_id)
        if not swap_request:
            raise HTTPException(status_code=404, detail="Request not found")

        # Enforce Owner or Admin Privileges
        if swap_request.user_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized to access this record")

        return swap_request

Scenario 2: Request Tampering & CSRF Attack on SIM Swap Submissions (Threat Category: T)
    Vulnerability Flow: An attacker tricks an authenticated subscriber into opening a malicious site containing an auto-submitting HTML form targeting POST /api/v1/swap-requests.

    Impact: Unauthorized initiation of SIM swap requests leading to potential account takeovers.

    Design Control:

    Double-Submit Cookie Anti-CSRF verification middleware.

    Require a custom HTTP header (X-CSRF-Token) generated on the client that must match the encrypted CSRF cookie token on state-changing requests.

    # Anti-CSRF Middleware Enforcement Concept
    @app.middleware("http")
    def csrf_protection_middleware(request: Request, call_next):
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            csrf_cookie = request.cookies.get("csrf_token")
            csrf_header = request.headers.get("X-CSRF-Token")

            if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF token validation failed"}
                )

        return call_next(request)


## 4. Threat Model Verification Strategy

    ![alt text](/assets/threat_model_verification_strategy.png)
