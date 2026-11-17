# app/models/entities.py

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class UserRole(str, enum.Enum):
    SUBSCRIBER = "subscriber"
    ADMIN = "admin"

class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class SwapType(str, enum.Enum):
    PHYSICAL_TO_ESIM = "physical_to_esim"
    ESIM_REPLACEMENT = "esim_replacement"
    DEVICE_CHANGE = "device_change"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    role = Column(
        Enum(UserRole, values_callable=lambda x: [e.value for e in x]), 
        default=UserRole.SUBSCRIBER, 
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    swap_requests = relationship("SimSwapRequest", back_populates="user", foreign_keys="SimSwapRequest.user_id")

class SimSwapRequest(Base):
    __tablename__ = "sim_swap_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_msisdn = Column(String(20), nullable=False)
    current_iccid = Column(String(22), nullable=False)
    new_iccid = Column(String(22), nullable=True)
    reason = Column(Text, nullable=False)
    swap_type = Column(
        Enum(SwapType, values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    status = Column(
        Enum(RequestStatus, values_callable=lambda x: [e.value for e in x]), 
        default=RequestStatus.PENDING, 
        nullable=False
    )
    admin_notes = Column(Text, nullable=True)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="swap_requests", foreign_keys=[user_id])