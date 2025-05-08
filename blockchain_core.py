import hashlib
import json
import time
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key, Encoding, PublicFormat

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.signature = None
        
    def calculate_hash(self):
        """Calculate hash of transaction data for signing"""
        tx_string = json.dumps({
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp
        }, sort_keys=True).encode()
        
        return hashlib.sha256(tx_string).hexdigest()
    
    def sign_transaction(self, private_key):
        """Sign transaction with sender's private key"""
        if self.sender == "System":  # Mining rewards don't need signatures
            return
            
        tx_hash = self.calculate_hash()
        self.signature = private_key.sign(
            tx_hash.encode(),
            ec.ECDSA(hashes.SHA256())
        )
    
    def verify_signature(self, public_key):
        """Verify transaction signature with sender's public key"""
        if self.sender == "System":  # Mining rewards don't need verification
            return True
            
        if not self.signature:
            return False
            
        try:
            tx_hash = self.calculate_hash()
            public_key.verify(
                self.signature,
                tx_hash.encode(),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception:
            return False
class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.calculate_hash()
    
    def calculate_merkle_root(self):
        """Calculate Merkle root of transactions for efficient verification"""
        if not self.transactions:
            return hashlib.sha256("empty".encode()).hexdigest()
            
        tx_hashes = [tx.calculate_hash() for tx in self.transactions]
        
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])
                
            temp_hashes = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i+1]
                temp_hashes.append(hashlib.sha256(combined.encode()).hexdigest())
            tx_hashes = temp_hashes
            
        return tx_hashes[0]
    
    def calculate_hash(self):
        """Calculate SHA-256 hash of the block using Merkle root for efficiency"""
        block_string = json.dumps({
            "index": self.index,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()
        
    def mine_block(self, difficulty, max_nonce=10000000):
        """Mine block with adaptive difficulty"""
        target = '0' * difficulty
        start_time = time.time()
        
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
            
            if self.nonce > max_nonce:
                return False
                
        mining_time = time.time() - start_time
        return mining_time

# Properly dedented Blockchain class
class Blockchain:
    def __init__(self):
        self.chain = []
        self.difficulty = 4
        self.pending_transactions = []
        self.mining_reward = 10
        self.target_block_time = 60
        self.difficulty_adjustment_interval = 10
        self.create_genesis_block()

    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(0, [], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0")
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)

    # ... rest of Blockchain methods ...

    # Rest of the Blockchain methods follow with proper indentation...
    
    def adjust_difficulty(self):
        """Dynamically adjust mining difficulty to maintain target block time"""
        if len(self.chain) % self.difficulty_adjustment_interval != 0:
            return
            
        # Calculate average block time for the last interval
        if len(self.chain) <= self.difficulty_adjustment_interval:
            return
            
        start_block = self.chain[-self.difficulty_adjustment_interval]
        end_block = self.chain[-1]
        
        start_time = datetime.strptime(start_block.timestamp, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end_block.timestamp, "%Y-%m-%d %H:%M:%S")
        
        time_diff = (end_time - start_time).total_seconds()
        avg_block_time = time_diff / self.difficulty_adjustment_interval
        
        # Adjust difficulty based on average block time
        if avg_block_time < self.target_block_time * 0.5:
            self.difficulty += 1
        elif avg_block_time > self.target_block_time * 1.5:
            self.difficulty = max(1, self.difficulty - 1)
            
        print(f"Difficulty adjusted to {self.difficulty} (avg block time: {avg_block_time:.2f}s)")
    
    def add_transaction(self, transaction):
        """Add a verified transaction to pending transactions"""
        # In a real implementation, verify transaction (balance, signature, etc.)
        if transaction.sender != "System":  # Mining rewards don't need verification
            # 1. Verify signature
            if not transaction.verify_signature(self.get_public_key(transaction.sender)):
                return False
                
            # 2. Verify sender has sufficient balance
            sender_balance = self.get_balance(transaction.sender)
            if sender_balance < transaction.amount:
                return False
        
        self.pending_transactions.append(transaction)
        return True
    
    def get_public_key(self, address):
        """Get public key for an address (simplified)"""
        # In a real implementation, this would retrieve the public key from a registry
        # or derive it from the address
        pass
    
    def get_balance(self, address):
        """Calculate balance for an address"""
        balance = 0
        
        # Check all transactions in all blocks
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount
        
        # Check pending transactions
        for tx in self.pending_transactions:
            if tx.recipient == address:
                balance += tx.amount
            if tx.sender == address:
                balance -= tx.amount
                
        return balance
    
    def mine_pending_transactions(self, miner_address):
        """Mine pending transactions into a new block"""
        # Create mining reward transaction
        reward_tx = Transaction("System", miner_address, self.mining_reward)
        
        # Create new block with pending transactions plus reward
        transactions = self.pending_transactions + [reward_tx]
        block = Block(
            len(self.chain),
            transactions,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            self.get_latest_block().hash
        )
        
        # Mine the block
        mining_time = block.mine_block(self.difficulty)
        if mining_time:
            # Add block to chain
            self.chain.append(block)
            
            # Reset pending transactions
            self.pending_transactions = []
            
            # Adjust difficulty if needed
            self.adjust_difficulty()
            
            return block, mining_time
        
        return None, 0
