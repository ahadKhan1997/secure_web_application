# Project Name: eSIM & SIM Swap Self-Service Portal


## 1. System Overview & Scope:

    This portal is a multi-tired web application, which is designed to allow subscribers to request SIM swaps and manage eSIM prfiles securely. It also provides the admin with auditing and oversight capabilities to avoid SIM swapping fraud.


## 2. Functional Requirements & Access Control (RBAC):

    Two roles: Support Admin & Standard Subscriber
    ![alt text](/assets/functional_requirements.png)

## 3. Security Requirements:

    SR-01: Secure Authntication & Passwod Hashing
        - Requirement       : 
                                User credentials must be protected from offline cracking, brute-force and GPU-side channel attacks.
        - Specification     : 
                                Hashing passwords before storing them to DB. Passwords should never be logged or store in memory.
        - Validation Crieria: 
                                DB "users" table should contain hashed password strings.
    SR-02: Cross-Site Request Forgery (CSRF) Defence
        - Requirement       : 
                                All state changing operations should be immue to CSRF attacks.
        - Specification     : 
                                APIs must implement a Double-Submit Cookie pattern or custom anti-CSRF token verification. State  changing APIs should validate request header token matches encrypted session token.
        - Validaion Criteria: 
                                Automated tests sending state-changing requests without the valid CSRF token header receive an HTTP 403 Forbidden response
    SR-03: HTTP Security Headers & Transport Security
        - Requirement       : 
                                The application must mitigate client-side cross-site scripting (XSS), clickjacking, and transport eavesdropping.
        - Specification     : 
                                FastAPI custom middleware must append mandatory HTTP headers on all API responses.
        - Validation Crieria: 
                                Response inspection via browser developer tools confirms presence and syntax of all 4 security headers.
    SR-04: Role-Based Authorization & BOLA/IDOR Prevention
        - Requirement       : 
                                Users must only access or modify records tied to their own authenticated session, and Admin endpoints must enforce role checks.
        - Specification     : 
                                Every API route must utilize FastAPI Dependencies (Depends(get_current_user)) to evaluate user identity and role claims. Resource lookups (e.g., /api/v1/swap-requests/{request_id}) must explicitly check that request.user_id == current_user.id unless the current_user role is Admin.
        - Validation Crieria: 
                                A Standard Subscriber attempting to access another subscriber’s resource ID receives an HTTP 403 Forbidden or HTTP 404 Not Found response.
    SR-05: Injection Mitigation & Data Integrity
        - Requirement       : 
                                All database interactions must be immune to SQL Injection (SQLi) attacks.
        - Specification     : 
                                SQL interactions must be handled exclusively through SQLAlchemy ORM parameterized queries. Dynamic string concatenation or raw SQL formatting (e.g., f"SELECT * FROM users WHERE id = '{user_id}'") is strictly prohibited.
        - Validation Crieria: 
                                SAST scan with Ruff (ruff check --select S) passes with 0 findings under rule S608 (SQL injection checks).

