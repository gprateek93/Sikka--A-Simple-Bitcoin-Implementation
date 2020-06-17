from hashlib import sha256
from Crypto.PublicKey import RSA

def generate_hash(data):
    data = data.encode('utf-8')
    message = sha256(data)
    message = message.hexdigest()
    return message

def generate_key():
    keyPair = RSA.generate(bits=2048)
    return keyPair

def sign_message(message, keyPair):
    hash = int.from_bytes(sha256(message.encode()).digest(),byteorder = "big")
    signature = pow(hash, keyPair.d, keyPair.n)
    return signature

def verify_message(message, public_key, signature):
    hash = int.from_bytes(sha256(message.encode()).digest(), byteorder = "big")
    hashFromSignature = pow(signature, public_key.e, public_key.n)
    return hash == hashFromSignature

