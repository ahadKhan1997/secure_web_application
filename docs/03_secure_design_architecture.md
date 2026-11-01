
## Target Tech Stack:
    - Python 3.13 (Fast API)
    - React (PrimeReact)
    - PostgreSQL

## 1. DB Schema & Data Models:
    Schema contains three tables primarily:
        - uers
        - sim_swap_requests
        - audit_logs
    Tables use index lookups on queried column, foreign key constraints and ENUM data type for status fields.
    
    ![alt text](/assets/design/database_schema.png)

## 2. Core Security Controls Implementation
    Password Hashing:
        Passwords are hashed uing Argon2id. Plaintext passwords are never stored or printed in logs

        -----------------------------------------------------------------------------------------
        FUNCTION HashPassword(plain_password_string):
            CONFIGURE Argon2id with parameters:
                time_cost = 3 iterations
                memory_cost = 64 MB (65536 KB)
                parallelism = 4 threads
                salt_length = 16 bytes

            GENERATE unique random salt
            COMPUTE hash value for plain_password_string using configured Argon2id
            RETURN encoded string containing algorithm details, parameters, salt, and hash

        FUNCTION VerifyPassword(input_password, stored_hash_string):
            PARSE stored_hash_string to extract algorithm parameters and salt
            COMPUTE hash of input_password using extracted parameters and salt
            IF computed_hash MATCHES stored_hash_string THEN
                RETURN True
            ELSE
                RETURN False
            END IF
        -----------------------------------------------------------------------------------------
    
    Anti-CSRF Middleware:
        State chaing API calls require a double-submit cookie structure. The middleware checks that the value in X-CSRF-Token request header matches the token stored in the HTTP-only session cookie.

        -----------------------------------------------------------------------------------------
        MIDDLEWARE VerifyCSRFToken(incoming_request):
            IF incoming_request.method IS ONE OF ["GET", "HEAD", "OPTIONS"]:
                ALLOW request to proceed to next handler
            END IF

            IF incoming_request.path IS EQUAL TO "/api/v1/auth/login":
                ALLOW request to proceed (authentication endpoints issue tokens)
            END IF

            EXTRACT cookie_token FROM incoming_request.cookies["csrf_token"]
            EXTRACT header_token FROM incoming_request.headers["X-CSRF-Token"]

            IF cookie_token IS MISSING OR header_token IS MISSING:
                REJECT request WITH HTTP Status 403 Forbidden ("CSRF token missing")
            END IF

            IF cookie_token DOES NOT EQUAL header_token:
                REJECT request WITH HTTP Status 403 Forbidden ("CSRF token mismatch")
            END IF

            ALLOW request to proceed to next handler
        -------------------------------------------------------------------------------------------
    
    HTTP Security Headers Middleware:
        Security headers are attached to every outgoing response to restrict browser behavior, prevent frame embedding and enforce HTTPS connections.

        -------------------------------------------------------------------------------------------
        MIDDLEWARE InjectSecurityHeaders(incoming_request):
            EXECUTE request and CAPTURE outgoing_response

            SET outgoing_response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            SET outgoing_response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none';       frame-ancestors 'none';"
            SET outgoing_response.headers["X-Frame-Options"] = "DENY"
            SET outgoing_response.headers["X-Content-Type-Options"] = "nosniff"
            SET outgoing_response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

            RETURN outgoing_response
        ----------------------------------------------------------------------------------------------
    
    Authorization & Resource Ownership Dependencies:
        Role-Based Access Control (RBAC) and resource ownership validation are enforced via FastAPI dependencies to prevent Broken Object Level Authorization (BOLA)

        ----------------------------------------------------------------------------------------------
        FUNCTION AuthenticateToken(bearer_token):
            DECODE bearer_token using system secret key
            EXTRACT user_id and role from token payload
            IF token is invalid OR token is expired THEN
                RAISE HTTP 401 Unauthorized
            END IF

            FETCH user_record FROM database WHERE id == user_id
            IF user_record is NULL OR user_record.is_active IS False THEN
                RAISE HTTP 401 Unauthorized
            END IF

            RETURN user_record

        FUNCTION AuthorizeSwapAccess(swap_request_id, authenticated_user):
            FETCH swap_record FROM database WHERE id == swap_request_id
            IF swap_record IS NULL THEN
                RAISE HTTP 404 Not Found
            END IF

            -- Allow access if caller owns the object OR possesses Admin privileges
            IF swap_record.user_id EQUALS authenticated_user.id OR authenticated_user.role EQUALS "admin":
                RETURN swap_record
            ELSE:
                RAISE HTTP 403 Forbidden ("Access denied to requested resource")
            END IF
        -------------------------------------------------------------------------------------------------

## 3. Directory Layout & Module Organization

        -------------------------------------------------------------------------------------------------
        secure_web_application/
        ├── app/
        │   ├── api/
        │   │   ├── dependencies/       # Authentication & authorization logic
        │   │   └── v1/
        │   │       ├── auth/           # Session management & credential endpoints
        │   │       ├── swap_requests/  # SIM Swap handling logic
        │   │       └── users/          # Subscriber account endpoints
        │   ├── core/
        │   │   ├── config/             # System runtime parameters
        │   │   └── security/           # Hashing algorithms & JWT signing logic
        │   ├── db/
        │   │   ├── connection/         # Database engine pool
        │   │   └── models/             # Database ORM entity definitions
        │   ├── middleware/
        │   │   ├── csrf/               # Double-submit token evaluation logic
        │   │   └── headers/            # Security header response modifier
        │   └── schemas/                # Input validation & output formatting rules
        ├── frontend/                   # Client application
        │   └── src/
        │       ├── components/         # Shared PrimeReact interface inputs
        │       ├── pages/              # Subscriber & Admin dashboard views
        │       └── services/           # HTTP API client configuration
        ├── docs/                       # SSDLC Documentation Files
        │   ├── 01_secure_requirements_gathering.md
        │   ├── 02_threat_model_stride.md
        │   ├── 03_secure_design_architecture.md
        |   └── assets/
        |       ├── design/
        |       |   └── database_schema.png
        |       ├── functional_requirements.png
        |       ├── stride_threat_identification_matrix.png
        |       └── threat_model_verification_strategy.png
        ├── pyproject.toml              # Ruff static analyzer rules
        └── README.md                   # System operational guide
        ----------------------------------------------------------------------------------------------------