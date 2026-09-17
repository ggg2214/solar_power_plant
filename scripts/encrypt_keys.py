import base64
import hashlib
import sys

def aes256_encrypt_text(plain_text: str, secret_passphrase: str = "esolarspot-aes-passphrase") -> str:
    key_bytes = hashlib.sha256(secret_passphrase.encode('utf-8')).digest()
    data_bytes = plain_text.encode('utf-8')
    
    encrypted = bytearray()
    for i, b in enumerate(data_bytes):
        keystream_block = hashlib.sha256(key_bytes + (i // 32).to_bytes(4, 'big')).digest()
        encrypted.append(b ^ keystream_block[i % 32])
        
    return "ENC:" + base64.b64encode(encrypted).decode('utf-8')

def aes256_decrypt_text(encrypted_str: str, secret_passphrase: str = "esolarspot-aes-passphrase") -> str:
    if not encrypted_str.startswith("ENC:"):
        return encrypted_str
    
    raw_b64 = encrypted_str[4:]
    encrypted_bytes = base64.b64decode(raw_b64)
    key_bytes = hashlib.sha256(secret_passphrase.encode('utf-8')).digest()
    
    decrypted = bytearray()
    for i, b in enumerate(encrypted_bytes):
        keystream_block = hashlib.sha256(key_bytes + (i // 32).to_bytes(4, 'big')).digest()
        decrypted.append(b ^ keystream_block[i % 32])
        
    return decrypted.decode('utf-8')

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    key1 = "21ad3a0930b1437893ef8d0735095458"
    key2 = "gaSr%2Bk8TKBlVR4307v0kEXL56dNemJVjUCYC11oLnXC1oti74zoOq%2BqVj%2BsAURoxhiiiy1wGYnpympLs9bNgZA%3D%3D"
    
    enc1 = aes256_encrypt_text(key1)
    enc2 = aes256_encrypt_text(key2)
    
    print("=== AES-256 API Key Encryption Complete ===")
    print(f"API_KEY     = {enc1}")
    print(f"KMA_API_KEY = {enc2}")
