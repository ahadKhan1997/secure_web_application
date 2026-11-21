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