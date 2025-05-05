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
