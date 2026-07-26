@app.get("/me")
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_profile(update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = auth_service.update_user(db, current_user, full_name=update.full_name, email=update.email)
    return UserResponse.model_validate(updated)
