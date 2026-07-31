from app.utils.security import hash_password, verify_password

hashed = hash_password("admin123")

print(hashed)

print(verify_password("admin123", hashed))

print(verify_password("wrongpassword", hashed))