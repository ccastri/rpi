import bcrypt

# Hashing passwords using bcrypt
password1 = "password1"
hashed_password1 = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt())

password2 = "password2"
hashed_password2 = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())

print("Hashed password for ccastri:", hashed_password1.decode('utf-8'))
print("Hashed password for protipark:", hashed_password2.decode('utf-8'))
