"""
INR Blockchain Wallet System
Manages user wallets for the custom INR blockchain
"""

import json
import os
import secrets
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
from datetime import datetime

class INRWallet:
    """Wallet for INR Blockchain"""
    
    def __init__(self, wallets_file: str = "inr_wallets.json", encryption_key_file: str = "inr_master_key.key"):
        self.wallets_file = wallets_file
        self.encryption_key_file = encryption_key_file
        self._init_encryption()
        self._init_wallets_file()
    
    def _init_encryption(self):
        """Initialize encryption for storing wallet seeds"""
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
    
    def _generate_wallet_address(self, email: str) -> str:
        """Generate unique wallet address for user"""
        # Create deterministic but unique address
        timestamp = str(datetime.now().timestamp())
        data = f"{email}{timestamp}{secrets.token_hex(16)}"
        hash_object = hashlib.sha256(data.encode())
        address = "INR" + hash_object.hexdigest()[:37]  # INR prefix + 37 chars = 40 char address
        return address
    
    def create_wallet(self, user_email: str, password: str, user_name: str) -> dict:
        """Create a new INR blockchain wallet for user"""
        try:
            # Generate wallet address
            address = self._generate_wallet_address(user_email)
            
            # Generate wallet seed (for future use)
            wallet_seed = secrets.token_hex(32)
            
            # Generate salt for this user
            salt = secrets.token_bytes(16)
            
            # Derive encryption key from user password
            user_key = self._derive_key_from_password(password, salt)
            user_cipher = Fernet(user_key)
            
            # Encrypt wallet seed with user's password
            encrypted_seed = user_cipher.encrypt(wallet_seed.encode()).decode()
            
            # Load existing wallets
            with open(self.wallets_file, 'r') as f:
                wallets = json.load(f)
            
            # Check if user already exists
            if user_email in wallets:
                return {
                    "success": False,
                    "error": "User already exists"
                }
            
            # Store wallet info
            wallets[user_email] = {
                "address": address,
                "name": user_name,
                "email": user_email,
                "encrypted_seed": encrypted_seed,
                "salt": base64.b64encode(salt).decode(),
                "created_at": datetime.now().isoformat(),
                "balance": 10000  # Initial balance of ₹10,000 for demo
            }
            
            # Save to file
            with open(self.wallets_file, 'w') as f:
                json.dump(wallets, f, indent=4)
            
            print(f"✅ INR Wallet created for {user_email}: {address}")
            
            return {
                "success": True,
                "address": address,
                "name": user_name,
                "balance": 10000,
                "message": "INR Wallet created successfully!"
            }
            
        except Exception as e:
            print(f"❌ Error creating wallet: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_wallet(self, user_email: str) -> dict:
        """Get wallet information for user"""
        try:
            with open(self.wallets_file, 'r') as f:
                wallets = json.load(f)
            
            if user_email in wallets:
                return wallets[user_email]
            return None
        except:
            return None
    
    def get_wallet_by_address(self, address: str) -> dict:
        """Get wallet by address"""
        try:
            with open(self.wallets_file, 'r') as f:
                wallets = json.load(f)
            
            for email, wallet in wallets.items():
                if wallet["address"] == address:
                    return wallet
            return None
        except:
            return None
    
    def verify_password(self, user_email: str, password: str) -> bool:
        """Verify user's password"""
        try:
            wallet = self.get_wallet(user_email)
            if not wallet:
                return False
            
            salt = base64.b64decode(wallet["salt"])
            encrypted_seed = wallet["encrypted_seed"]
            
            # Derive key from password
            user_key = self._derive_key_from_password(password, salt)
            user_cipher = Fernet(user_key)
            
            # Try to decrypt - if successful, password is correct
            user_cipher.decrypt(encrypted_seed.encode())
            return True
            
        except:
            return False
    
    def update_balance(self, address: str, amount: float, operation: str = "add"):
        """Update wallet balance"""
        try:
            with open(self.wallets_file, 'r') as f:
                wallets = json.load(f)
            
            for email, wallet in wallets.items():
                if wallet["address"] == address:
                    if operation == "add":
                        wallet["balance"] += amount
                    elif operation == "subtract":
                        if wallet["balance"] >= amount:
                            wallet["balance"] -= amount
                        else:
                            return {"success": False, "error": "Insufficient balance"}
                    
                    wallet["last_updated"] = datetime.now().isoformat()
                    break
            
            with open(self.wallets_file, 'w') as f:
                json.dump(wallets, f, indent=4)
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_balance(self, address: str) -> dict:
        """Get balance for an address"""
        wallet = self.get_wallet_by_address(address)
        if wallet:
            return {
                "success": True,
                "balance": wallet.get("balance", 0),
                "address": address
            }
        return {
            "success": False,
            "error": "Wallet not found"
        }
    
    def list_all_wallets(self) -> list:
        """List all wallets (for admin)"""
        try:
            with open(self.wallets_file, 'r') as f:
                wallets = json.load(f)
            
            wallet_list = []
            for email, wallet in wallets.items():
                wallet_list.append({
                    "email": email,
                    "address": wallet["address"],
                    "name": wallet.get("name", "Unknown"),
                    "balance": wallet.get("balance", 0),
                    "created_at": wallet.get("created_at", "")
                })
            
            return wallet_list
        except:
            return []


# Initialize global wallet manager
inr_wallet_manager = INRWallet()

