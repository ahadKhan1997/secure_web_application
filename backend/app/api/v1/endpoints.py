from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import secrets

from app.db.session import get_db
from app.models.entities import User, SimSwapRequest, RequestStatus, SwapType
from app.core.security import verify_password, create_access_token
from app.api.deps import get_current_user, require_admin

router = APIRouter()

# Pydantic Schemas
class SwapRequestCreate(BaseModel):
    target_msisdn: str
    current_iccid: str
    reason: str
    swap_type: SwapType

class SwapRequestResponse(BaseModel):
    id: int
    user_id: int
    target_msisdn: str
    current_iccid: str
    swap_type: SwapType
    status: RequestStatus

    class Config:
        from_attributes = True

# 1. Authentication Endpoint
@router.post("/auth/login")
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    csrf_token = secrets.token_hex(32)
    
    # Set HTTP-Only CSRF Cookie
    response.set_cookie(key="csrf_token", value=csrf_token, httponly=True, samesite="strict")
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "csrf_token": csrf_token,
        "role": user.role.value
    }

# 2. Create SIM Swap (Subscriber)
@router.post("/swap-requests", response_model=SwapRequestResponse, status_code=status.HTTP_201_CREATED)
def create_swap_request(payload: SwapRequestCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_request = SimSwapRequest(
        user_id=current_user.id,
        target_msisdn=payload.target_msisdn,
        current_iccid=payload.current_iccid,
        reason=payload.reason,
        swap_type=payload.swap_type,
        status=RequestStatus.PENDING
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

# 3. Read Personal Requests (Subscriber)
@router.get("/swap-requests/me", response_model=List[SwapRequestResponse])
def get_my_swap_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(SimSwapRequest).filter(SimSwapRequest.user_id == current_user.id).all()

# 4. Read Specific Request with Owner/BOLA Check
@router.get("/swap-requests/{request_id}", response_model=SwapRequestResponse)
def get_swap_request_by_id(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = db.query(SimSwapRequest).filter(SimSwapRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # BOLA Protection Check
    if req.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this request")
    
    return req

# 5. Read All Pending Requests (Admin Only)
@router.get("/admin/swap-requests", response_model=List[SwapRequestResponse])
def get_all_swap_requests(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(SimSwapRequest).all()