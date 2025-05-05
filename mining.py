import hashlib
import time
import json
from multiprocessing import Pool, cpu_count
import numpy as np

class EnhancedMiner:
    def __init__(self, difficulty=4, max_iterations=10000000):
        self.difficulty = difficulty
        self.max_iterations = max_iterations
        self.target = '0' * difficulty
        
    def process_data_chunk(self, params):
        """Process a chunk of nonce values to find a valid hash"""
        start_nonce, block_data = params
        
        # Number of iterations in this chunk
        chunk_size = 100000
        end_nonce = start_nonce + chunk_size
        
        for nonce in range(start_nonce, end_nonce):
            if nonce >= self.max_iterations:
                return None, nonce
                
            # Add nonce to data
            block_data["nonce"] = nonce
            
            # Convert to string and calculate hash
            data_string = json.dumps(block_data, sort_keys=True)
            hash_result = hashlib.sha256(data_string.encode()).hexdigest()
            
            # Check if hash meets target
            if hash_result.startswith(self.target):
                return hash_result, nonce
                
        # No solution found in this chunk
        return None, end_nonce
        
    def start_mining(self, block_data):
        """Start the mining process with enhanced efficiency"""
        print(f"Starting optimized mining process...")
        print(f"Difficulty level: {self.difficulty}")
        
        start_time = time.time()
        nonce = 0
        result = None
        
        # Use multiple CPU cores for processing with optimized workload distribution
        num_cores = max(1, cpu_count() - 1)  # Leave one core free
        print(f"Utilizing {num_cores} processing cores")
        
        # Use numpy for more efficient data handling
        with Pool(processes=num_cores) as pool:
            while nonce < self.max_iterations and result is None:
                # Create tasks with different starting points for each core
                # Use prime number offsets to reduce collision probability
                tasks = [(nonce + i * 100003, block_data.copy()) for i in range(num_cores)]
                
                # Process chunks in parallel with improved work distribution
                results = pool.map(self.process_data_chunk, tasks)
                
                # Check if any chunk found a solution
                for hash_result, end_nonce in results:
                    if hash_result is not None:
                        result = (hash_result, end_nonce)
                        break
                    nonce = max(nonce, end_nonce)
                
                # Show progress with more informative metrics
                if result is None and nonce % 500000 == 0:
                    elapsed = time.time() - start_time
                    hashes_per_second = nonce / elapsed if elapsed > 0 else 0
                    print(f"Processing... {nonce:,} iterations completed ({hashes_per_second:.2f} H/s)")
        
        # Show results with comprehensive statistics
        if result:
            hash_result, nonce = result
            mining_time = time.time() - start_time
            hashes_per_second = nonce / mining_time if mining_time > 0 else 0
            
            print(f"\nMining complete after {nonce:,} iterations ({mining_time:.2f} seconds)")
            print(f"Result hash: {hash_result}")
            print(f"Final nonce: {nonce}")
            print(f"Mining speed: {hashes_per_second:,.2f} hashes/second")
            
            # Calculate estimated energy usage (educational purposes)
            estimated_watts = num_cores * 75  # Rough estimate: 75W per CPU core
            kwh_used = (estimated_watts * mining_time) / (1000 * 3600)
            print(f"Estimated energy used: {kwh_used:.6f} kWh")
            
            return hash_result, nonce
        else:
            print("\nMaximum iterations reached without finding a valid hash.")
            return None, nonce
