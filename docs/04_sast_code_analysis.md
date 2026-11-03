# 1. Target Engines:
## Backend: Ruff
    Ruff enforces rulesets from flake8-bandit under S rule group to detect:
    - unparameterized DB queries
    - hardcoded secrets
    - weak cryptographic primitives
    - unsafe network listeners

    Tool Config:
    --------------------------------------------------------------------
        [tool.ruff]
        target-verison = "py311"
        line-length = 88

        [tool.ruff.lint]
        select = [
            "E",    # code style errors
            "F",    # logic errors
            "B",    # design flaws
            "S"     # security checks
        ]

        [tool.ruff.lint.per-file-ignores]
        "tests/*" = ["S101"]    # allow assert statement inside test files
    --------------------------------------------------------------------

    Security Rules & Detection Scope:

        ==================================================================
        Rule ID         Category            Detection Scope
        ==================================================================
        S105/S106       Hardcoded Creds     Flags hardcoded passwords, API
                                            secrets and connection strings

        S303/S304       Weak Cryptography   Detects legacy hash algos or
                                            broken PRNG implementations

        S608            SQL Injection       Detects raw SQL string format-
                                            -ting inside query strings

        S104            Insecure Binding    Flags sockets or servers lis-
                                            -tening on public interfaces

        S110            Error Suppression   try-except-pass blocks that
                                            hide underlying execution
                                            failures
        =================================================================

## Fronend: ESLint
    ESLint with eslint-plugin-security and eslint-plugin-react analyzes the react app. It checks:
    - DOM based Cross-Site Scripting (XSS)
    - dangerous DOM property assinment
    - insecure opbject injection

    Tool Config:
    --------------------------------------------------------------------

        module.exports = {
            env: {
                browser: true,
                es2021: true
            },
            extends: [
                'eslint:recommended',
                'plugin:react/recommended',
                'plugin:security/recommended',
            ],
            plugins: ['react', 'security'],
            rules: {
              'security/detect-object-injection': 'warn',
              'security/detect-non-literal-require': 'error',
              'security/detect-unsafe-regex': 'error',
              'react/no-danger': 'error',
              'react/jsx-no-target-blank': 'error',
            },
            settings: {
                react: {
                  version: 'detect',
                },
            }
        }
    --------------------------------------------------------------------

    Security Rules & Detection Scope:

        ==================================================================
        Rule ID             Category            Detection Scope
        ==================================================================
        react/no-           DOM-based XSS       Rejects use of 
        danger                                  dangerouslySetInnerHTML

        security/detect-    Obj. Injection      Warns against access obj
        object-injection                        propertie using unsaniti-
                                                -zed user keys

        react/jsx-no-       Reverse Tabnabbing  Enforces rel="noopener
        target-blank                                          noreferrer"
                                                on external link tags(
                                                    target="_blank")

        security/detect     ReDoS               Flags regex vulnerable
        -unsafe-regex                           to catastrophic backtra-
                                                -cking
        =================================================================
     

# 2. Code Review Findings & Remediation Log

    ==================================================================================================================================================================
    Finding ID  Scope       Rule ID         Vulnerable Code Pattern Identified                              Refactored Secure Implementation
    ==================================================================================================================================================================
    SAST-01     Backend     S105            Hardcoded JWT signing key:                                      Moved key to environment variable: 
                                            JWT_SECRET = "super_secret_key_123"                             JWT_SECRET = os.getenv("JWT_SECRET_KEY")

    SAST-02     Backend     S608            Direct string interpolation in SQL lookup:                      Parameterized lookup using SQLAlchemy: 
                                            db.execute(f"SELECT * FROM users WHERE email='{email}'")        db.query(User).filter(User.email == email).first()

    SAST-03     Backend     S303            Legacy password hashing attempt:                                Upgraded to memory-hard hashing: 
                                            hashlib.sha256(password.encode()).hexdigest()                   ph.hash(password) (Argon2id)

    SAST-04     Frontend    react/no-       Direct HTML insertion:                                          Standard React JSX escaping: <div>{userNote}</div>
                            danger          <div dangerouslySetInnerHTML={{ __html: userNote }} /> 
    
    SAST-05     Frontend    jsx-no-         Link without window isolation:                                  Isolated link:
                            target-blank    <a href={docUrl} target="_blank">Help</a>                       <a href={docUrl} target="_blank" 
                                                                                                            rel="noopener noreferrer">Help</a>

    SAST-06     Frontend    detect-object   Dynamic object key lookup:                                      Key whitelist check before lookup to ensure key is valid
                            -injection      const val = settings[userInputKey]
    ==================================================================================================================================================================


# 3. Automated CI/CD Pipeline

    =============================================================================================================================

            name: Full-Stack SAST Security Audit

            on:
              push:
                branches: [ "main", "develop" ]
              pull_request:
                branches: [ "main" ]

            jobs:
              backend_sast:
                name: Backend SAST (Ruff)
                runs-on: ubuntu-latest
                steps:
                  - name: Checkout Repository
                    uses: actions/checkout@v4

                  - name: Set up Python
                    uses: actions/setup-python@v5
                    with:
                      python-version: "3.11"

                  - name: Install Ruff
                    run: pip install ruff

                  - name: Run Backend Security Scan
                    run: ruff check --select S app/
              frontend_sast:
                name: Frontend SAST (ESLint)
                runs-on: ubuntu-latest
                steps:
                  - name: Checkout Repository
                    uses: actions/checkout@v4

                  - name: Set up Node.js
                    uses: actions/setup-node@v4
                    with:
                      node-version: "20"
                      cache: "npm"
                      cache-dependency-path: "frontend/package-lock.json"

                  - name: Install Frontend Dependencies
                    run: |
                      cd frontend
                      npm ci
                      
                  - name: Run Frontend Security Scan
                    run: |
                      cd frontend
                      npx eslint src/ --ext .js,.jsx,.ts,.tsx

    =============================================================================================================================
