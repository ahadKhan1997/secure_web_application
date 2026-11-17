start postgres server:
    net start postgresql-x64-17

stop postgres server
    net stop postgresql-x64-17

start backend:
    cd backend
    .\venv\Scripts\Activate.ps1
    uvicorn app.main:app --reload

