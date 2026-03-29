import os
import shutil
import time
import json
import logging

class DatasetLifecycleManager:
    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = storage_dir
        self.images_dir = os.path.join(storage_dir, "design_images")
        self.archive_dir = os.path.join(storage_dir, "archive")
        self.compressed_dir = os.path.join(storage_dir, "compressed")
        
        for d in [self.images_dir, self.archive_dir, self.compressed_dir]:
            os.makedirs(d, exist_ok=True)

    def enforce_retention_policy(self, max_days: int = 30, max_images: int = 100):
        logging.info("Running Dataset Lifecycle Manager...")
        self._archive_old_images(max_days)
        self._limit_stored_images(max_images)

    def _archive_old_images(self, max_days: int):
        now = time.time()
        for root, _, files in os.walk(self.images_dir):
            for file in files:
                if file.endswith('.png') or file.endswith('.jpg'):
                    file_path = os.path.join(root, file)
                    creation_time = os.path.getmtime(file_path)
                    days_old = (now - creation_time) / (24 * 3600)
                    if days_old > max_days:
                        shutil.move(file_path, os.path.join(self.archive_dir, file))
                        logging.info(f"Archived old image: {file}")

    def _limit_stored_images(self, max_images: int):
        images = []
        for root, _, files in os.walk(self.images_dir):
            for file in files:
                if file.endswith('.png') or file.endswith('.jpg'):
                    filepath = os.path.join(root, file)
                    images.append((filepath, os.path.getmtime(filepath)))
        
        # Sort by oldest first
        images.sort(key=lambda x: x[1])
        
        if len(images) > max_images:
            excess = len(images) - max_images
            for i in range(excess):
                file_to_archive = images[i][0]
                filename = os.path.basename(file_to_archive)
                shutil.move(file_to_archive, os.path.join(self.archive_dir, filename))
                logging.info(f"Archived image due to max limit: {filename}")

dataset_manager = DatasetLifecycleManager()
