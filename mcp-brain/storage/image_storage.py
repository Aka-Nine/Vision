import os
import uuid
import json

class ImageStorage:
    def __init__(self, storage_dir: str = "storage/design_images"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.metadata_index = os.path.join(self.storage_dir, "index.json")
        if not os.path.exists(self.metadata_index):
            with open(self.metadata_index, "w") as f:
                json.dump([], f)

    def store_image_metadata(self, image_url: str, source: str, file_path_override: str = None) -> dict:
        image_id = f"design_{uuid.uuid4().hex[:8]}"
        file_path = file_path_override or os.path.join(self.storage_dir, f"{image_id}.png")
        
        metadata = {
            "image_id": image_id,
            "source": source,
            "file_path": file_path,
            "original_url": image_url
        }

        with open(self.metadata_index, "r") as f:
            index = json.load(f)
            
        index.append(metadata)
        
        with open(self.metadata_index, "w") as f:
            json.dump(index, f, indent=4)
            
        return metadata

    def get_all_images(self) -> list:
        if os.path.exists(self.metadata_index):
            with open(self.metadata_index, "r") as f:
                return json.load(f)
        return []

image_storage = ImageStorage()
