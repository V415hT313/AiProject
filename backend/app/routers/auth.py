import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import auth, config, crud, models, schemas
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("aiproject")


@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username is already taken")
    return crud.create_user(db, user)


@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user is None or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = auth.create_access_token(user_id=db_user.id, username=db_user.username)
    return schemas.Token(access_token=access_token)


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user=Depends(auth.get_current_user)):
    return current_user


GENERIC_FORGOT_PASSWORD_RESPONSE = {
    "detail": "If that account exists, a password reset email has been sent."
}


@router.post("/forgot-password")
def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, request.username)
    if db_user is not None:
        reset_token = crud.create_password_reset_token(db, db_user.id)
        reset_link = f"{config.FRONTEND_URL}/?reset_token={reset_token.token}"
        try:
            auth.send_password_reset_email(db_user.username, reset_link)
        except Exception:
            logger.exception("Failed to send password reset email to %s", db_user.username)

    # Always return the same response, whether or not the account exists,
    # so this endpoint can't be used to enumerate registered usernames.
    return GENERIC_FORGOT_PASSWORD_RESPONSE


@router.post("/reset-password")
def reset_password(request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_token = crud.get_valid_reset_token(db, request.token)
    if reset_token is None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")

    user = db.get(models.User, reset_token.user_id)
    crud.update_user_password(db, user, request.new_password)
    crud.mark_reset_token_used(db, reset_token)
    return {"detail": "Password has been reset. You can now log in with your new password."}
