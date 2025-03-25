from .aes_utils import *

class AES:
    def __init__(self, key):
        if isinstance(key, bytes):
            self.key = key
        else:
            self.key = key.encode('utf-8')

        key_len = len(self.key)

        if key_len == 16:
            self.rounds = 10
        elif key_len == 24:
            self.rounds = 12
        elif key_len == 32:
            self.rounds = 14
        else:
            raise ValueError("Key must be 16, 24 or 32 bytes")

        self.round_keys = self.key_expansion(self.key)

    def key_expansion(self, key):
        key = list(key)
        key_len = len(key)
        words_count = 4 * (self.rounds + 1)
        Nk = key_len // 4 # Can be 4, 6 or 8

        words = [0] * words_count

        # Copy key into first words
        for i in range(key_len):
            word_index = i // 4
            byte_position =  i % 4
            shift_amount = 24 - (byte_position * 8)

            if byte_position == 0:
                words[word_index] = 0

            words[word_index] |= key[i] << shift_amount
    
        for i in range(Nk, words_count):
            temp = words[i - 1]

            if i % Nk == 0:
                temp = rot_word(temp)
                temp = sub_word(temp)
                temp = xor_rcon(temp, rcon[(i // Nk) - 1])
            elif key_len > 24 and Nk > 6 and i % Nk == 4: # AES-256 check
                temp = sub_word(temp)
            words[i] = words[i - Nk] ^ temp

        return words
                        
    def encrypt_block(self, block):
        state = [
            [0, 0, 0, 0], 
            [0, 0, 0, 0],
            [0, 0, 0, 0], 
            [0, 0, 0, 0]   
        ]

        for col in range (4):
            for row in range(4):
                state[row][col] = block[col * 4 + row]

        state = add_round_key(state, 0, self.round_keys)

        for round_idx in range(1, self.rounds):
            state = sub_bytes(state)
            state = shift_rows(state)
            state = mix_columns(state)
            state = add_round_key(state, round_idx, self.round_keys)

        state = sub_bytes(state)
        state = shift_rows(state)
        state = add_round_key(state, self.rounds, self.round_keys)

        result = bytearray(16)

        for col in range(4):
            for row in range(4):
                result[col * 4 + row] = state[row][col]

        return result

    def decrypt_block(self, block):
        state = [
            [0, 0, 0, 0], 
            [0, 0, 0, 0],
            [0, 0, 0, 0], 
            [0, 0, 0, 0]   
        ]

        for col in range (4):
            for row in range(4):
                state[row][col] = block[col * 4 + row]

        state = add_round_key(state, self.rounds, self.round_keys)

        for round_idx in range(self.rounds -1 , 0, -1):
            state = inv_shift_rows(state)
            state = inv_sub_bytes(state)
            state = add_round_key(state, round_idx, self.round_keys)
            state = inv_mix_columns(state)


        state = inv_shift_rows(state)
        state = inv_sub_bytes(state)
        state = add_round_key(state, 0, self.round_keys)

        result = bytearray(16)

        for col in range(4):
            for row in range(4):
                result[col + row * 4] = state[col][row]

        return result

    def encrypt(self, plaintext):
        if isinstance(plaintext, bytes):
            plaintext_bytes = plaintext
        else:
            plaintext_bytes = plaintext.encode('utf-8')

        padded = pad(plaintext_bytes)

        blocks = []
        block_size = 16
        
        for i in range(0, len(padded), block_size):
            blocks.append(padded[i:i + block_size])

        ciphertext = bytearray()

        for block in blocks:
            encrypted_block = self.encrypt_block(block)
            ciphertext.extend(encrypted_block)

        return base64_encode(ciphertext)

    def decrypt(self, ciphertext):
        ciphertext_bytes = base64_decode(ciphertext)

        blocks = []
        block_size = 16
        
        for i in range(0, len(ciphertext_bytes), block_size):
            blocks.append(ciphertext_bytes[i:i + block_size])

        plaintext = bytearray()

        for block in blocks:
            decrypted_block = self.decrypt_block(block)
            plaintext.extend(decrypted_block)
        
        plaintext = unpad(plaintext).decode('utf-8')
        return plaintext
