start postgres server:
    net start postgresql-x64-17

stop postgres server
    net stop postgresql-x64-17

start backend:
    cd backend
    .\venv\Scripts\Activate.ps1
    uvicorn app.main:app --reload

start frontend:
    cd frontend
    npm start

credntials:
    subscriber:
        username: subscriber@telecom.com
        password: UserPassword123!
    admin:
        username: admin@telecom.com
        password: AdminPassword123!

backend SAST scan:
    ruff check --select S app/

frontend SAST scan:
    npx eslint src/ --ext .js,.jsx
    npx eslint src/ --ext .js,.jsx; if ($LASTEXITCODE -eq 0) { Write-Host "ESLint SAST Audit Passed: 0 Errors, 0 Warnings" -ForegroundColor Green }

backend DAST scan:
    while server is running:
    pytest -v tests/test_dast_security.py

frontend DAST scan:
    while both frontend and backend servers are running
    node --test tests/dast_frontend.test.mjs