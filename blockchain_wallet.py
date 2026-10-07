"""
ImpactEcho Custom Blockchain Wallet System
Handles wallet creation, transaction signing, and blockchain interactions
"""

from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
import json
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import secrets

class BlockchainWallet:
    def __init__(self, rpc_url="http://127.0.0.1:8545"):
        """Initialize blockchain connection"""
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.wallets_file = "user_wallets.json"
        self.encryption_key_file = "master_key.key"
        self._init_encryption()
        self._init_wallets_file()
        
    def _init_encryption(self):
        """Initialize encryption for storing private keys"""
        if not os.path.exists(self.encryption_key_file):
            key = Fernet.generate_key()
            with open(self.encryption_key_file, 'wb') as f:
                f.write(key)
        
        with open(self.encryption_key_file, 'rb') as f:
            self.master_key = f.read()
        
        self.cipher = Fernet(self.master_key)
    
    def _init_wallets_file(self):
        """Initialize wallets storage file"""
        if not os.path.exists(self.wallets_file):
            with open(self.wallets_file, 'w') as f:
                json.dump({}, f, indent=4)
    
    def _derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from user password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def create_wallet(self, user_email: str, password: str) -> dict:
        """Create a new blockchain wallet for user"""
        try:
            # Generate new Ethereum account
            account = Account.create()
            address = account.address
            private_key = account.key.hex()
            
            # Generate salt for this user
            salt = secrets.token_bytes(16)
            
            # Derive encryption key from user password
            user_key = self._derive_key_from_password(password, salt)
            user_cipher = Fernet(user_key)
            
            # Encrypt private key with user's password
            encrypted_private_key = user_cipher.encrypt(private_key.encode()).decode()
            
            # Load existing wallets
            with open(self.wallets_file, 'r') as f:
                wallets = json.load(f)
            
            # Store wallet info
            wallets[user_email] = {
                "address": address,
                "encrypted_private_key": encrypted_private_key,
                "salt": base64.b64encode(salt).decode(),
                "created_at": str(self.w3.eth.get_block('latest')['timestamp'])
            }
            
            # Save to file
            with open(self.wallets_file, 'w') as f:
                json.dump(wallets, f, indent=4)
            
            print(f"✅ Wallet created for {user_email}: {address}")
            
            return {
                "success": True,
                "address": address,
                "message": "Wallet created successfully!"
            }
            
        except Exception as e:
            print(f"❌ Error creating wallet: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_wallet_address(self, user_email: str) -> str:
        """Get wallet address for user"""
        try:
            with open(self.wallets_file, 'r') as f:
                wallets = json.load(f)
            
            if user_email in wallets:
                return wallets[user_email]["address"]
            return None
        except:
            return None
    
    def _decrypt_private_key(self, user_email: str, password: str) -> str:
        """Decrypt user's private key"""
        try:
            with open(self.wallets_file, 'r') as f:
                wallets = json.load(f)
            
            if user_email not in wallets:
                raise Exception("Wallet not found")
            
            wallet_data = wallets[user_email]
            salt = base64.b64decode(wallet_data["salt"])
            encrypted_key = wallet_data["encrypted_private_key"]
            
            # Derive key from password
            user_key = self._derive_key_from_password(password, salt)
            user_cipher = Fernet(user_key)
            
            # Decrypt private key
            private_key = user_cipher.decrypt(encrypted_key.encode()).decode()
            
            return private_key
            
        except Exception as e:
            print(f"❌ Error decrypting private key: {e}")
            raise Exception("Invalid password or wallet not found")
    
    def get_balance(self, address: str) -> dict:
        """Get ETH balance for address"""
        try:
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            
            return {
                "success": True,
                "balance_wei": balance_wei,
                "balance_eth": float(balance_eth),
                "address": address
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_transaction(self, user_email: str, password: str, to_address: str, amount_eth: float) -> dict:
        """Send ETH transaction"""
        try:
            # Get private key
            private_key = self._decrypt_private_key(user_email, password)
            account = Account.from_key(private_key)
            from_address = account.address
            
            # Check balance
            balance = self.get_balance(from_address)
            if not balance["success"] or balance["balance_eth"] < amount_eth:
                return {
                    "success": False,
                    "error": "Insufficient balance"
                }
            
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(from_address)
            
            # Build transaction
            tx = {
                'nonce': nonce,
                'to': to_address,
                'value': self.w3.to_wei(amount_eth, 'ether'),
                'gas': 21000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.w3.eth.chain_id
            }
            
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "block_number": tx_receipt['blockNumber'],
                "gas_used": tx_receipt['gasUsed'],
                "status": "success" if tx_receipt['status'] == 1 else "failed"
            }
            
        except Exception as e:
            print(f"❌ Transaction error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def donate_to_cause(self, user_email: str, password: str, cause_id: int, amount_eth: float, contract_address: str, contract_abi: list) -> dict:
        """Donate to a cause via smart contract"""
        try:
            # Get private key
            private_key = self._decrypt_private_key(user_email, password)
            account = Account.from_key(private_key)
            from_address = account.address
            
            # Load contract
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)
            
            # Check balance
            balance = self.get_balance(from_address)
            if not balance["success"] or balance["balance_eth"] < amount_eth:
                return {
                    "success": False,
                    "error": "Insufficient balance"
                }
            
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(from_address)
            
            # Build transaction
            tx = contract.functions.fund(cause_id).build_transaction({
                'from': from_address,
                'value': self.w3.to_wei(amount_eth, 'ether'),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
                'chainId': self.w3.eth.chain_id
            })
            
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "block_number": tx_receipt['blockNumber'],
                "gas_used": tx_receipt['gasUsed'],
                "status": "success" if tx_receipt['status'] == 1 else "failed",
                "from": from_address,
                "cause_id": cause_id,
                "amount_eth": amount_eth
            }
            
        except Exception as e:
            print(f"❌ Donation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_transaction_history(self, address: str, start_block: int = 0) -> list:
        """Get transaction history for an address"""
        try:
            current_block = self.w3.eth.block_number
            transactions = []
            
            # This is a simplified version - in production, use etherscan API
            for block_num in range(max(start_block, current_block - 1000), current_block + 1):
                try:
                    block = self.w3.eth.get_block(block_num, full_transactions=True)
                    for tx in block['transactions']:
                        if tx['from'] == address or tx['to'] == address:
                            transactions.append({
                                'hash': tx['hash'].hex(),
                                'from': tx['from'],
                                'to': tx['to'],
                                'value': self.w3.from_wei(tx['value'], 'ether'),
                                'block': block_num,
                                'timestamp': block['timestamp']
                            })
                except:
                    continue
            
            return transactions
            
        except Exception as e:
            print(f"❌ Error fetching history: {e}")
            return []
    
    def verify_transaction(self, tx_hash: str) -> dict:
        """Verify a transaction on blockchain"""
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            block = self.w3.eth.get_block(receipt['blockNumber'])
            
            return {
                "success": True,
                "verified": True,
                "from": tx['from'],
                "to": tx['to'],
                "value": float(self.w3.from_wei(tx['value'], 'ether')),
                "block_number": receipt['blockNumber'],
                "timestamp": block['timestamp'],
                "confirmations": self.w3.eth.block_number - receipt['blockNumber'],
                "status": "success" if receipt['status'] == 1 else "failed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "verified": False,
                "error": str(e)
            }

# Initialize global wallet manager
wallet_manager = BlockchainWallet()

