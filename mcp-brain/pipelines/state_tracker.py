import json
import os
import time

class PipelineStateTracker:
    def __init__(self, db_path="pipeline_states.json"):
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump({}, f)

    def _read_db(self):
        with open(self.db_path, "r") as f:
            return json.load(f)

    def _write_db(self, data):
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=4)

    def create_pipeline(self, pipeline_id: str):
        data = self._read_db()
        data[pipeline_id] = {
            "pipeline_id": pipeline_id,
            "current_stage": "started",
            "completed_stages": [],
            "status": "running",
            "start_time": time.time(),
            "end_time": None,
            "errors": []
        }
        self._write_db(data)

    def update_stage(self, pipeline_id: str, current_stage: str, completed_stage: str = None):
        data = self._read_db()
        if pipeline_id in data:
            data[pipeline_id]["current_stage"] = current_stage
            if completed_stage and completed_stage not in data[pipeline_id]["completed_stages"]:
                data[pipeline_id]["completed_stages"].append(completed_stage)
            self._write_db(data)

    def complete_pipeline(self, pipeline_id: str):
        data = self._read_db()
        if pipeline_id in data:
            data[pipeline_id]["status"] = "completed"
            data[pipeline_id]["end_time"] = time.time()
            self._write_db(data)

    def fail_pipeline(self, pipeline_id: str, error: str):
        data = self._read_db()
        if pipeline_id in data:
            data[pipeline_id]["status"] = "failed"
            data[pipeline_id]["errors"].append(error)
            data[pipeline_id]["end_time"] = time.time()
            self._write_db(data)
            
    def get_pipeline(self, pipeline_id: str) -> dict:
        return self._read_db().get(pipeline_id)

state_tracker = PipelineStateTracker()
