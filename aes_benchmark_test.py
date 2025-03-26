from crypto.benchmarked_aes import BenchmarkedAES as AES

key = b'ThisIs16BytesKey'
plaintext = "Hello, World!"

aes = AES(key)

cipher = aes.encrypt(plaintext)
decipher = aes.decrypt(cipher)

print('Cipher: ', cipher)
print('Decipher: ', decipher)

block_count = aes.get_block_count()
round_timings = aes.get_round_timings()


print('Block count: ', block_count)

print('Round time:')
for time in round_timings:
    print(time * 1000)