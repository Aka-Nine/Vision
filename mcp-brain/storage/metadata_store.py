import json
import os


class MetadataStore:
    def __init__(self, db_path="market_data.json"):
        self.db_path = db_path
        self.schema_version = "1.0"
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump({
                    "schema_version": self.schema_version,
                    "trends": [],
                    "design_references": [],
                    "ui_patterns": [],
                    "demand_scores": [],
                    "design_briefs": []
                }, f)

    def _read_db(self):
        with open(self.db_path, "r") as f:
            data = json.load(f)
            # Schema migration logic could be added here
            if data.get("schema_version") != self.schema_version:
                data["schema_version"] = self.schema_version
            return data

    def _write_db(self, data):
        data["schema_version"] = self.schema_version
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=4)

    def save_trend(self, trend):
        data = self._read_db()
        data["trends"].append(trend)
        self._write_db(data)

    def save_design_reference(self, reference):
        data = self._read_db()
        data["design_references"].append(reference)
        self._write_db(data)

    def save_ui_pattern(self, pattern):
        data = self._read_db()
        data["ui_patterns"].append(pattern)
        self._write_db(data)

    def save_demand_score(self, score):
        data = self._read_db()
        data["demand_scores"].append(score)
        self._write_db(data)

    def save_design_brief(self, brief):
        data = self._read_db()
        data["design_briefs"].append(brief)
        self._write_db(data)

    def get_trends(self):
        data = self._read_db()
        return data.get("trends", [])

    def get_design_briefs(self):
        data = self._read_db()
        return data.get("design_briefs", [])

metadata_store = MetadataStore()
