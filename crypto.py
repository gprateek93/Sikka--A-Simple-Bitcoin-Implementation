from hashlib import sha256
from Crypto.PublicKey import RSA

def generate_hash(data = ""):
    '''Arguments - data: Type = string, default value = ""
       This function is used to generate a sha256 hash for a given string.'''
    message = sha256(data.encode()).digest()
    return int.from_bytes(message, byteorder = "big")

def generate_key():
    '''This function is used to generate a random RSA public and private key pair.'''
    keyPair = RSA.generate(bits=2048)
    return keyPair

def sign_message(message = "", keyPair = None):
    '''Arguments - message: Type = string, default value = ""
                   keyPair: Type = an RSA key pair object, default value = None
       This function is used to sign the given message  using the RSA private key that can be extracted from the key pair object.'''
    if keyPair == None:
        return None
    hash = generate_hash(message)
    signature = pow(hash, keyPair.d, keyPair.n)
    return signature

def verify_signature(message = "", public_key = None, signature= None):
    '''Arguments - message: Type = string, default value = ""
                   public_key: Type = an RSA public key object, default value = None
                   signature: Type = Byte string, default value = None
       Given a message and a public key this function matches whether the provided signature is valid for the message or not.'''
    if signature == None or public_key == None:
        return False
    hash = generate_hash(message)
    hashFromSignature = pow(signature, public_key.e, public_key.n)
    return hash == hashFromSignature

