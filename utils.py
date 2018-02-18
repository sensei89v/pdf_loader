import random
import hashlib

def create_salt(length=12):
    ALLOWED_CHARS = '0123456789QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm'
    random_gen = random.SystemRandom()
    return ''.join([random_gen.choice(ALLOWED_CHARS) for i in range(0, length)])

def hash_password(salt, password):
    decrtpted_str = salt + password
    decoded_str = decrtpted_str.encode()
    digest = hashlib.md5(decoded_str).hexdigest()
    return salt + ":" + digest

def check_password(password, hashed_password):
    salt = hashed_password.split(':')[0]
    return hash_password(salt, password) == hashed_password
