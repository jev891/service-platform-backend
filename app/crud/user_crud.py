from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import List, Optional
from app.models.user import User


class UserCRUD:
    @staticmethod
    def create_user(
        db: Session,
        mobile_number: str,
        name: str,
        email: Optional[str] = None,
        company_name: Optional[str] = None,
        hashed_password: Optional[str] = None,
        role: Optional[str] = "client",
        location: Optional[str] = None,
    ) -> User:
        """Создать пользователя"""
        #"INVALID_ROLE": {"status_code": 400, "detail": "Invalid role. Choose from ['client', 'executor', 'admin']."},
        #"DUPLICATE_ENTRY": {"status_code": 409, "detail": "Mobile number or email already registered."},
        #"NOT_FOUND": {"status_code": 404, "detail": "User not found."},
        #"UNAUTHORIZED_ACTION": {"status_code": 403, "detail": "Only admins can delete users."},
        try:
            # Validate role
            valid_roles = ["client", "executor", "admin", "pending_admin"]
            if role not in valid_roles:
                raise HTTPException(status_code=400, detail=f"Invalid role. Choose from {valid_roles}")

            new_user = User(
                mobile_number=mobile_number,
                name=name,
                email=email,
                company_name=company_name,
                hashed_password=hashed_password,
                role=role,
                location=location,
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Mobile number or email already registered")

    @staticmethod
    def get_user(db: Session, user_id: Optional[int] = None, mobile_number: Optional[str] = None) -> User:
        """Получить пользователя по ID или номеру телефона"""
        query = db.query(User)
        if user_id:
            user = query.filter(User.id == user_id).first()
            if user:
                return user

        if mobile_number:
            user = query.filter(User.mobile_number == mobile_number).first()
            if user:
                return user
        else:
            raise HTTPException(status_code=400, detail="User ID or Mobile Number is required")
        
        if not user:
            return None

    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        company_name: Optional[str] = None,
        location: Optional[str] = None,
    ) -> User:
        """Обновить пользователя"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if name:
            user.name = name
        if email:
            user.email = email
        if company_name:
            user.company_name = company_name
        if location:
            user.location = location

        try:
            db.commit()
            db.refresh(user)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Email already in use")
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int, requester_role: str):
        """Удалить пользователя (только для админа)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if requester_role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can delete users")
        
        db.delete(user)
        db.commit()
        return {"detail": f"User {user_id} deleted"}

    @staticmethod
    def filter_users_by_role(db: Session, role: str) -> List[User]:
        """Фильтрация пользователей по роли"""
        valid_roles = ["client", "executor", "admin", "pending_admin"]
        if role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role. Choose from {valid_roles}")
        
        users = db.query(User).filter(User.role == role).all()
        if not users:
            raise HTTPException(status_code=404, detail="No users found with this role")
        return users
