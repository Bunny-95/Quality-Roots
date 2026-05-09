"""
Organic Roots Blockchain Implementation
Simulated blockchain using SHA-256 with proof-of-work
"""
import hashlib
import json
import time
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
from blockchain.models import BlockchainBlock
from config import BLOCKCHAIN_DIFFICULTY

class Block:
    """Represents a single block in the blockchain"""
    
    def __init__(self, index: int, data: Dict[str, Any], previous_hash: str, timestamp: Optional[datetime] = None):
        self.index = index
        self.timestamp = timestamp or datetime.utcnow()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
        """Mine the block using proof-of-work"""
        target = "0" * difficulty
        print(f"[MINING] Mining block {self.index}...")
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        print(f"[OK] Block {self.index} mined: {self.hash}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary"""
        return {
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce
        }

class Blockchain:
    """Represents the entire blockchain"""
    
    def __init__(self, difficulty: int = BLOCKCHAIN_DIFFICULTY):
        self.difficulty = difficulty
        self.chain: List[Block] = []
        self.pending_data: List[Dict[str, Any]] = []
    
    def create_genesis_block(self) -> Block:
        """Create the first block in the chain"""
        genesis_data = {
            "event_type": "GENESIS",
            "message": "Organic Roots Blockchain Genesis Block",
            "created_by": "Organic Roots System",
            "description": "Initial block to start the Organic Roots supply chain"
        }
        
        return Block(0, genesis_data, "0")
    
    def get_latest_block(self) -> Optional[Block]:
        """Get the most recent block in the chain"""
        if not self.chain:
            return None
        return self.chain[-1]
    
    def add_block(self, data: Dict[str, Any]) -> Block:
        """Add a new block to the chain"""
        if not self.chain:
            # Create genesis block if chain is empty
            genesis_block = self.create_genesis_block()
            genesis_block.mine_block(self.difficulty)
            self.chain.append(genesis_block)
            return genesis_block
        
        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            data=data,
            previous_hash=latest_block.hash
        )
        
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        return new_block
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block's hash is correct
            if current_block.hash != current_block.calculate_hash():
                print(f"[ERROR] Block {current_block.index} has invalid hash")
                return False
            
            # Check if current block points to previous block
            if current_block.previous_hash != previous_block.hash:
                print(f"[ERROR] Block {current_block.index} has invalid previous hash")
                return False
            
            # Check if block was properly mined
            target = "0" * self.difficulty
            if current_block.hash[:self.difficulty] != target:
                print(f"[ERROR] Block {current_block.index} was not properly mined")
                return False
        
        return True
    
    def get_chain_length(self) -> int:
        """Get the length of the blockchain"""
        return len(self.chain)
    
    def get_block_by_index(self, index: int) -> Optional[Block]:
        """Get a specific block by its index"""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert entire chain to list of dictionaries"""
        return [block.to_dict() for block in self.chain]

class BlockchainManager:
    """Manages blockchain persistence and operations"""
    
    def __init__(self):
        self.blockchain = Blockchain()
        self._db_ready = False
        self._load_chain_from_db()
    
    def init(self) -> None:
        """Initialize blockchain after database tables are created"""
        if self._db_ready:
            return
        
        db = SessionLocal()
        try:
            # Check if we need to create genesis block
            existing_blocks = db.query(BlockchainBlock).count()
            if existing_blocks == 0 and len(self.blockchain.chain) == 0:
                print("[INIT] Creating genesis block...")
                genesis_block = self.blockchain.create_genesis_block()
                genesis_block.mine_block(self.blockchain.difficulty)
                self._save_block_to_db(genesis_block, db)
                self.blockchain.chain.append(genesis_block)
                print(f"[OK] Genesis block created: {genesis_block.hash}")
            self._db_ready = True
        finally:
            db.close()
    
    def _load_chain_from_db(self) -> None:
        """Load blockchain from database"""
        db = SessionLocal()
        try:
            blocks = db.query(BlockchainBlock).order_by(BlockchainBlock.index).all()
            
            if not blocks:
                # No blocks in database, will create genesis block later in init()
                print("[INIT] No blocks found in database, will create genesis block after tables ready...")
                self.blockchain.chain = []
            else:
                # Load existing blocks
                self.blockchain.chain = []
                for db_block in blocks:
                    block = Block(
                        index=db_block.index,
                        data=json.loads(db_block.data_json),
                        previous_hash=db_block.previous_hash,
                        timestamp=db_block.timestamp
                    )
                    block.nonce = db_block.nonce
                    block.hash = db_block.hash
                    self.blockchain.chain.append(block)
                
                print(f"[INIT] Loaded {len(blocks)} blocks from database")
                self._db_ready = True
                
                # Validate loaded chain
                if not self.blockchain.is_chain_valid():
                    print("[WARN] Loaded chain is invalid! This should not happen.")
        except Exception as e:
            # Table doesn't exist yet, initialize empty chain
            print(f"[WARN] Database tables not ready yet (will initialize later): {type(e).__name__}")
            self.blockchain.chain = []
        finally:
            db.close()
    
    def _save_block_to_db(self, block: Block, db: Session) -> None:
        """Save a block to the database"""
        db_block = BlockchainBlock(
            index=block.index,
            timestamp=block.timestamp,
            data_json=json.dumps(block.data),
            previous_hash=block.previous_hash,
            hash=block.hash,
            nonce=block.nonce
        )
        db.add(db_block)
        db.commit()
    
    def add_supply_chain_event(self, event_data: Dict[str, Any]) -> Block:
        """Add a supply chain event to the blockchain"""
        db = SessionLocal()
        try:
            # Add block to blockchain
            block = self.blockchain.add_block(event_data)
            
            # Save to database
            self._save_block_to_db(block, db)
            
            print(f"[CHAIN] Added supply chain event to blockchain: Block {block.index}")
            return block
        
        finally:
            db.close()
    
    def get_chain(self) -> List[Dict[str, Any]]:
        """Get the entire blockchain"""
        return self.blockchain.to_dict_list()
    
    def get_block(self, index: int) -> Optional[Dict[str, Any]]:
        """Get a specific block by index"""
        block = self.blockchain.get_block_by_index(index)
        return block.to_dict() if block else None
    
    def verify_chain(self) -> Dict[str, Any]:
        """Verify the integrity of the blockchain"""
        is_valid = self.blockchain.is_chain_valid()
        chain_length = self.blockchain.get_chain_length()
        
        return {
            "is_valid": is_valid,
            "chain_length": chain_length,
            "verified_at": datetime.utcnow().isoformat(),
            "message": "Blockchain is valid" if is_valid else "Blockchain is invalid!"
        }
    
    def get_chain_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics"""
        chain_length = self.blockchain.get_chain_length()
        latest_block = self.blockchain.get_latest_block()
        
        return {
            "chain_length": chain_length,
            "latest_block_index": latest_block.index if latest_block else None,
            "latest_block_hash": latest_block.hash if latest_block else None,
            "latest_block_timestamp": latest_block.timestamp.isoformat() if latest_block else None,
            "difficulty": self.blockchain.difficulty,
            "total_blocks_mined": chain_length
        }

# Global blockchain manager instance
blockchain_manager = BlockchainManager()

# Test function
def test_blockchain():
    """Test blockchain functionality"""
    print("[TEST] Testing blockchain functionality...")
    
    # Test adding supply chain events
    test_events = [
        {
            "event_type": "BATCH_CREATED",
            "batch_code": "TEST001",
            "farmer_id": 1,
            "product_id": 1,
            "quantity_kg": 100.0,
            "grade": "A"
        },
        {
            "event_type": "QUALITY_CHECKED",
            "batch_code": "TEST001",
            "quality_score": 92.5,
            "inspector": "AI Quality Grader"
        }
    ]
    
    for event in test_events:
        blockchain_manager.add_supply_chain_event(event)
    
    # Test chain verification
    verification = blockchain_manager.verify_chain()
    print(f"Chain verification: {verification}")
    
    # Test chain stats
    stats = blockchain_manager.get_chain_stats()
    print(f"Chain stats: {stats}")
    
    # Test getting chain
    chain = blockchain_manager.get_chain()
    print(f"Chain length: {len(chain)}")
    
    print("[TEST] Blockchain tests completed!")

if __name__ == "__main__":
    test_blockchain()
