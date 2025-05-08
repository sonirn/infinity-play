# mining_simulation.py
import time
import matplotlib.pyplot as plt
from blockchain_core import Blockchain, Block

def run_simulation(difficulty=3, duration=60):
    """Run blockchain mining simulation with performance tracking"""
    blockchain = Blockchain()
    blockchain.difficulty = difficulty
    
    start_time = time.time()
    iterations = 0
    best_hash = ''
    hash_rates = []
    timestamps = []
    
    try:
        while time.time() - start_time < duration:
            # Create test transaction
            blockchain.add_transaction("Test", "Address", 1)
            
            # Mine block and track performance
            block, mining_time = blockchain.mine_pending_transactions("miner_address")
            iterations += 1
            
            # Calculate metrics
            if block:
                current_hash = block.hash
                if current_hash > best_hash:
                    best_hash = current_hash
                
                hash_rate = 1 / mining_time if mining_time > 0 else 0
                hash_rates.append(hash_rate)
                timestamps.append(time.time() - start_time)
                
    except KeyboardInterrupt:
        pass
    
    # Calculate final statistics
    total_time = time.time() - start_time
    avg_hash_rate = sum(hash_rates)/len(hash_rates) if hash_rates else 0
    
    return {
        'difficulty': difficulty,
        'duration': total_time,
        'iterations': iterations,
        'best_hash': best_hash,
        'avg_hash_rate': avg_hash_rate,
        'hash_rates': hash_rates,
        'timestamps': timestamps
    }

def plot_results(results):
    """Visualize simulation results with detailed metrics"""
    plt.figure(figsize=(12, 6))
    
    # Hash Rate Timeline
    plt.subplot(1, 2, 1)
    plt.plot(results['timestamps'], results['hash_rates'], 'b-')
    plt.title('Hash Rate Over Time')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Hashes per Second')
    plt.grid(True)
    
    # Difficulty Summary
    plt.subplot(1, 2, 2)
    plt.bar([str(results['difficulty'])], [results['avg_hash_rate']], color='g')
    plt.title('Average Performance by Difficulty')
    plt.xlabel('Difficulty Level')
    plt.ylabel('Average Hash Rate (H/s)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
