import hashlib

class DeduplicationEngine:
    def __init__(self):
        self.seen_hashes = set()

    def generate_hash(self, item: dict) -> str:
        # Create a stable string representation
        try:
            items_tuple = tuple(sorted(str(v) for k, v in item.items() if k not in ['timestamp']))
        except Exception:
            items_tuple = str(item)
            
        return hashlib.md5(str(items_tuple).encode('utf-8')).hexdigest()

    def is_duplicate(self, item: dict) -> bool:
        item_hash = self.generate_hash(item)
        if item_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(item_hash)
        return False
        
    def reset(self):
        self.seen_hashes.clear()

deduplication_engine = DeduplicationEngine()
