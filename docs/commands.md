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

backend scan:
    ruff check --select S app/

frontend scan:
    npx eslint src/ --ext .js,.jsx
    npx eslint src/ --ext .js,.jsx; if ($LASTEXITCODE -eq 0) { Write-Host "ESLint SAST Audit Passed: 0 Errors, 0 Warnings" -ForegroundColor Green }