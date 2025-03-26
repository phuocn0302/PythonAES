from .aes import AES
from .aes_utils import *
import time

def benchmark_operations(variable, functions_and_args):
    start_time = time.perf_counter()
    
    for func, args in functions_and_args:
        if not isinstance(args, tuple):
            args = (args,)
        variable = func(*args)
    
    exec_time = time.perf_counter() - start_time
    
    return variable, exec_time


class BenchmarkedAES(AES):
    def __init__(self, key):
        super().__init__(key)

        total_operations = self.rounds + 1

        self.round_timings = [0] * total_operations
        self.block_count = 0

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

        block_timings = []

        initial_round_operations = [
            (add_round_key, (state, 0, self.round_keys))
        ]

        def round_operations(round_idx):
            return [
                (sub_bytes, (state,)),
                (shift_rows, (state,)),
                (mix_columns, (state,)),
                (add_round_key, (state, round_idx, self.round_keys))
            ]

        final_round_operation = [
            (sub_bytes, state),
            (shift_rows, state),
            (add_round_key, (state, self.rounds, self.round_keys))
        ]

        state, exec_time = benchmark_operations(state, initial_round_operations)
        block_timings.append(exec_time)

        for round_idx in range(1, self.rounds):
            state, exec_time = benchmark_operations(state, round_operations(round_idx))
            block_timings.append(exec_time)

        state, exec_time = benchmark_operations(state, final_round_operation)
        block_timings.append(exec_time)

        for i in range(len(block_timings)):
            if i < len(self.round_timings):
                self.round_timings[i] += block_timings[i]

        result = bytearray(16)

        for col in range(4):
            for row in range(4):
                result[col * 4 + row] = state[row][col]

        self.block_count += 1
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

        block_timings = []

        initial_round_operations = [
            (add_round_key, (state, self.rounds, self.round_keys))
        ]

        def round_operations(round_idx):
            return [
                (inv_shift_rows, state),
                (inv_sub_bytes, state),
                (add_round_key, (state, round_idx, self.round_keys)),
                (inv_mix_columns, state)
            ]

        final_round_operation = [
            (inv_shift_rows, state),
            (inv_sub_bytes, state),
            (add_round_key, (state, 0, self.round_keys))
        ]

        state, exec_time = benchmark_operations(state, initial_round_operations)
        block_timings.append(exec_time)

        for round_idx in range(self.rounds -1 , 0, -1):
            state, exec_time = benchmark_operations(state, round_operations(round_idx))
            block_timings.append(exec_time)

        state, exec_time = benchmark_operations(state, final_round_operation)
        block_timings.append(exec_time)

        for i in range(len(block_timings)):
            if i < len(self.round_timings):
                self.round_timings[i] += block_timings[i]

        result = bytearray(16)

        for col in range(4):
            for row in range(4):
                result[col + row * 4] = state[col][row]
        
        self.block_count += 1
        return result
    
    def get_round_timings(self):
        if self.block_count > 0:
            return [timing / self.block_count for timing in self.round_timings]
        return self.round_timings
    
    def get_block_count(self):
        return self.block_count
