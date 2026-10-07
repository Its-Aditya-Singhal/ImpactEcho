"""
ImpactEcho Custom INR Blockchain
A blockchain built specifically for Indian Rupee donations
"""

import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import secrets

class Transaction:
    """Represents a donation transaction"""
    
    def __init__(self, sender: str, recipient: str, amount: float, cause_id: int, cause_name: str):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.cause_id = cause_id
        self.cause_name = cause_name
        self.timestamp = datetime.now().isoformat()
        self.transaction_id = self._generate_transaction_id()
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        data = f"{self.sender}{self.recipient}{self.amount}{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary"""
        return {
            'transaction_id': self.transaction_id,
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'cause_id': self.cause_id,
            'cause_name': self.cause_name,
            'timestamp': self.timestamp
        }
    
    def __repr__(self):
        return f"Transaction({self.sender[:10]}... → {self.recipient[:10]}... : ₹{self.amount})"


class Block:
    """Represents a block in the blockchain"""
    
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str, difficulty: int = 2):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = datetime.now().isoformat()
        self.nonce = 0
        self.difficulty = difficulty
        self.hash = self._mine_block()
    
    def _calculate_hash(self) -> str:
        """Calculate block hash"""
        block_data = {
            'index': self.index,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def _mine_block(self) -> str:
        """Mine block with proof of work"""
        target = '0' * self.difficulty
        
        while True:
            hash_value = self._calculate_hash()
            if hash_value[:self.difficulty] == target:
                print(f"✅ Block #{self.index} mined! Hash: {hash_value[:16]}... (nonce: {self.nonce})")
                return hash_value
            self.nonce += 1
            
            # Limit mining time for demo
            if self.nonce > 100000:
                self.difficulty = max(1, self.difficulty - 1)
                self.nonce = 0
    
    def to_dict(self) -> dict:
        """Convert block to dictionary"""
        return {
            'index': self.index,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'hash': self.hash,
            'difficulty': self.difficulty
        }
    
    def __repr__(self):
        return f"Block #{self.index} [{len(self.transactions)} txs] - {self.hash[:16]}..."


class INRBlockchain:
    """ImpactEcho INR Blockchain"""
    
    def __init__(self, blockchain_file: str = "inr_blockchain.json"):
        self.blockchain_file = blockchain_file
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.mining_reward = 10  # ₹10 reward for mining (optional)
        self.difficulty = 2
        self.block_size = 5  # Max transactions per block
        
        # Initialize blockchain
        self._load_or_create_blockchain()
    
    def _load_or_create_blockchain(self):
        """Load existing blockchain or create genesis block"""
        try:
            with open(self.blockchain_file, 'r') as f:
                data = json.load(f)
                self._deserialize_blockchain(data)
            print(f"📚 Loaded blockchain: {len(self.chain)} blocks")
        except (FileNotFoundError, json.JSONDecodeError):
            print("🆕 Creating new INR blockchain...")
            self._create_genesis_block()
            self._save_blockchain()
    
    def _create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_transaction = Transaction(
            sender="SYSTEM",
            recipient="ImpactEcho",
            amount=0,
            cause_id=0,
            cause_name="Genesis Block"
        )
        genesis_block = Block(0, [genesis_transaction], "0" * 64, difficulty=1)
        self.chain.append(genesis_block)
        print(f"✅ Genesis block created: {genesis_block.hash}")
    
    def _deserialize_blockchain(self, data: dict):
        """Load blockchain from saved data"""
        for block_data in data['chain']:
            transactions = []
            for tx_data in block_data['transactions']:
                tx = Transaction(
                    sender=tx_data['sender'],
                    recipient=tx_data['recipient'],
                    amount=tx_data['amount'],
                    cause_id=tx_data['cause_id'],
                    cause_name=tx_data['cause_name']
                )
                tx.timestamp = tx_data['timestamp']
                tx.transaction_id = tx_data['transaction_id']
                transactions.append(tx)
            
            block = Block.__new__(Block)
            block.index = block_data['index']
            block.transactions = transactions
            block.previous_hash = block_data['previous_hash']
            block.timestamp = block_data['timestamp']
            block.nonce = block_data['nonce']
            block.difficulty = block_data.get('difficulty', 2)
            block.hash = block_data['hash']
            
            self.chain.append(block)
    
    def _save_blockchain(self):
        """Save blockchain to file"""
        data = {
            'chain': [block.to_dict() for block in self.chain],
            'last_updated': datetime.now().isoformat()
        }
        with open(self.blockchain_file, 'w') as f:
            json.dump(data, f, indent=4)
    
    def add_transaction(self, sender: str, recipient: str, amount: float, cause_id: int, cause_name: str) -> Transaction:
        """Add a new transaction to pending transactions"""
        transaction = Transaction(sender, recipient, amount, cause_id, cause_name)
        self.pending_transactions.append(transaction)
        
        print(f"💳 Transaction added: {transaction}")
        
        # Auto-mine if block is full
        if len(self.pending_transactions) >= self.block_size:
            self.mine_pending_transactions()
        
        return transaction
    
    def mine_pending_transactions(self, miner_address: str = "ImpactEcho") -> Optional[Block]:
        """Mine pending transactions into a new block"""
        if not self.pending_transactions:
            return None
        
        print(f"⛏️  Mining new block with {len(self.pending_transactions)} transactions...")
        
        # Create new block
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions[:self.block_size],
            previous_hash=self.get_latest_block().hash,
            difficulty=self.difficulty
        )
        
        # Add to chain
        self.chain.append(new_block)
        
        # Remove mined transactions
        self.pending_transactions = self.pending_transactions[self.block_size:]
        
        # Save blockchain
        self._save_blockchain()
        
        print(f"✅ Block mined and added to chain!")
        return new_block
    
    def get_latest_block(self) -> Block:
        """Get the latest block in the chain"""
        return self.chain[-1]
    
    def get_balance(self, address: str) -> float:
        """Get balance for an address"""
        balance = 0
        
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.recipient == address:
                    balance += transaction.amount
                if transaction.sender == address:
                    balance -= transaction.amount
        
        return balance
    
    def get_transaction_history(self, address: str) -> List[dict]:
        """Get transaction history for an address"""
        history = []
        
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == address or transaction.recipient == address:
                    tx_data = transaction.to_dict()
                    tx_data['block_number'] = block.index
                    tx_data['block_hash'] = block.hash
                    tx_data['type'] = 'sent' if transaction.sender == address else 'received'
                    history.append(tx_data)
        
        return history
    
    def verify_transaction(self, transaction_id: str) -> Optional[dict]:
        """Verify a transaction exists in the blockchain"""
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.transaction_id == transaction_id:
                    return {
                        'verified': True,
                        'transaction': transaction.to_dict(),
                        'block_number': block.index,
                        'block_hash': block.hash,
                        'timestamp': transaction.timestamp,
                        'confirmations': len(self.chain) - block.index
                    }
        
        return None
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if hash is correct
            if current_block.hash != current_block._calculate_hash():
                print(f"❌ Block #{i} hash is invalid!")
                return False
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                print(f"❌ Block #{i} previous hash doesn't match!")
                return False
        
        return True
    
    def get_blockchain_stats(self) -> dict:
        """Get blockchain statistics"""
        total_transactions = sum(len(block.transactions) for block in self.chain)
        total_volume = 0
        
        for block in self.chain[1:]:  # Skip genesis
            for tx in block.transactions:
                if tx.sender != "SYSTEM":
                    total_volume += tx.amount
        
        return {
            'total_blocks': len(self.chain),
            'total_transactions': total_transactions,
            'total_volume': total_volume,
            'pending_transactions': len(self.pending_transactions),
            'latest_block_hash': self.get_latest_block().hash,
            'is_valid': self.is_chain_valid(),
            'difficulty': self.difficulty
        }
    
    def get_block(self, block_index: int) -> Optional[dict]:
        """Get a specific block by index"""
        if 0 <= block_index < len(self.chain):
            return self.chain[block_index].to_dict()
        return None
    
    def search_blocks(self, search_term: str) -> List[dict]:
        """Search blocks by various criteria"""
        results = []
        
        for block in self.chain:
            # Search in transactions
            for tx in block.transactions:
                if (search_term.lower() in tx.sender.lower() or
                    search_term.lower() in tx.recipient.lower() or
                    search_term.lower() in tx.cause_name.lower() or
                    search_term in tx.transaction_id):
                    results.append({
                        'block': block.to_dict(),
                        'matched_transaction': tx.to_dict()
                    })
        
        return results


# Initialize global blockchain
inr_blockchain = INRBlockchain()

# Auto-mine any pending transactions on startup
if inr_blockchain.pending_transactions:
    inr_blockchain.mine_pending_transactions()

