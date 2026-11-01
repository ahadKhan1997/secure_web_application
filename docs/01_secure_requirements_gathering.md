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

## 4. Abuse & Misuse Case Scenarios:

+-----------------------------------------------------------------------------------+
|                                 ABUSE CASE MATRIX                                 |
+--------------------------+--------------------------------+-----------------------+
| Threat Scenario          | Adversary Objective            | Technical Mitigation  |
+--------------------------+--------------------------------+-----------------------+
| Unauthorized SIM Swap    | Hijack victim's phone line to  | SR-01, SR-04: Admin   |
| (Account Takeover)       | intercept 2FA SMS codes.       | manual approval flow. |
+--------------------------+--------------------------------+-----------------------+
| CSRF Profile Update      | Force subscriber to change     | SR-02: Double-Submit  |
|                          | email via malicious site link. | Anti-CSRF header check|
+--------------------------+--------------------------------+-----------------------+
| BOLA / IDOR Exploitation | Enumerate swap request IDs     | SR-04: Contextual     |
|                          | to read other users' data.     | owner validation middleware|
+--------------------------+--------------------------------+-----------------------+
| XSS Payload Injection    | Inject script in support chat  | SR-03: CSP header     |
|                          | to steal session cookies.      | & PrimeReact escaping |
+--------------------------+--------------------------------+-----------------------+

    Scenario 1: Malicious SIM Swap Attempt (Account Takeover)
        Legitimate Use Case: Subscriber lost their physical phone and requests a SIM swap to an eSIM on a new device.

        Abuse Case: An attacker submits a SIM swap request using a stolen subscriber ID to redirect incoming SMS multi-factor authentication (MFA) codes to the attacker's device.

        System Safeguard: SIM swap requests trigger a PENDING_APPROVAL status. High-risk requests require Support Admin verification (SR-04), and audit logs record the requesting IP address and timestamp.
    
    Scenario 2: Cross-Site Request Forgery on Profile Updates
        Legitimate Use Case: Subscriber updates their registered billing address via the React UI settings panel.

        Abuse Case: An attacker tricks an authenticated subscriber into clicking an external link hosted on attacker.com that fires an automated POST /api/v1/user/profile request to alter email settings.

        System Safeguard: FastAPI anti-CSRF middleware rejects the request because the cross-origin browser fetch lacks the custom X-CSRF-Token header generated for the subscriber's session (SR-02).


## 5. Security Requirements Traceability Matrix (RTM):
 