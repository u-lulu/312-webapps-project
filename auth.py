import hashlib
from flask import request


# Function used to hash an auth token
def hash_auth_token(token: bytes):
    # Convert the input data to bytes
    hash_result = hashlib.sha256(token).digest()
    return hash_result


# Function used to check if a user is auth
def is_authenticated(db_collection):
    if request.cookies.get("Authentication-token", None) is not None:
        # Lookup the token in my cookie header, hash it and attempt to find it in my database
        hash_token = hash_auth_token(request.cookies["Authentication-token"].encode())
        valid_user = db_collection.find_one({"Hashed authentication token": hash_token}, {"_id": 0})
        # If the token is valid then the user is valid
        if valid_user:
            return valid_user
        else:
            return False
    else:
        print("Token not found")
        return False


# Retrieve User
def retrieve_user(db_collection):
    valid_user = is_authenticated(db_collection)
    if valid_user is not False:
        return valid_user["user"]
    else:
        return "Guest"

