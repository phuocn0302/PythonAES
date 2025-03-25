from crypto.aes import AES
from crypto.aes_utils import base64_decode, base64_encode

from Crypto.Cipher import AES as AES_Lib
from Crypto.Util.Padding import pad, unpad

key = b'ThisIs16BytesKey'
plaintext = 'Hello, World! abcdef123456'

## My implement test

aes = AES(key)
cipher = aes.encrypt(plaintext)
decipher = aes.decrypt(cipher)

print('Key: ', key)
print('Plaintext: ', plaintext)
print('Ciphertext: ', cipher)
print('Deciphertext: ', decipher)
print('Match:', plaintext == decipher)

## Test with pycryptodome

padded_plaintext = pad(plaintext.encode(), 16)

lib_aes = AES_Lib.new(key, AES_Lib.MODE_ECB)
lib_cipher = lib_aes.encrypt(padded_plaintext)

lib_decipher = lib_aes.decrypt(lib_cipher)
lib_decipher = unpad(lib_decipher, 16).decode()

lib_cipher = base64_encode(lib_aes.encrypt(padded_plaintext))


print('Lib ciphertext: ',  lib_cipher)
print('Match with custom implement: ', lib_cipher == cipher)
print('Lib deciphertext: ', lib_decipher)
print('Match with custom implement: ', lib_decipher == decipher)

