import os
import json
import uuid
from typing import List, Optional, Dict, Any
from app.models.project import Project
from app.models.brand import BrandProfile

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
BRANDS_FILE = os.path.join(DATA_DIR, "brands.json")

class StorageService:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(PROJECTS_FILE):
            with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
        if not os.path.exists(BRANDS_FILE):
            with open(BRANDS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _read_json(self, path: str) -> List[Dict]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_json(self, path: str, data: List[Dict]):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ---------------- Projects ----------------
    def list_projects(self) -> List[Dict[str, Any]]:
        return self._read_json(PROJECTS_FILE)

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        projects = self._read_json(PROJECTS_FILE)
        for p in projects:
            if p.get("id") == project_id:
                return p
        return None

    def save_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        projects = self._read_json(PROJECTS_FILE)
        p_id = project_data.get("id") or str(uuid.uuid4())[:8]
        project_data["id"] = p_id

        existing_index = next((i for i, p in enumerate(projects) if p.get("id") == p_id), -1)
        if existing_index >= 0:
            projects[existing_index] = project_data
        else:
            projects.insert(0, project_data)

        self._write_json(PROJECTS_FILE, projects)
        return project_data

    def duplicate_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        orig = self.get_project(project_id)
        if not orig:
            return None
        dup = json.loads(json.dumps(orig))
        dup["id"] = f"{project_id}_copy_{str(uuid.uuid4())[:4]}"
        dup["name"] = f"{orig.get('name', 'Project')} (Copy)"
        return self.save_project(dup)

    def delete_project(self, project_id: str) -> bool:
        projects = self._read_json(PROJECTS_FILE)
        filtered = [p for p in projects if p.get("id") != project_id]
        if len(filtered) < len(projects):
            self._write_json(PROJECTS_FILE, filtered)
            return True
        return False

    # ---------------- Brands ----------------
    def list_brands(self) -> List[Dict[str, Any]]:
        return self._read_json(BRANDS_FILE)

    def save_brand(self, brand_data: Dict[str, Any]) -> Dict[str, Any]:
        brands = self._read_json(BRANDS_FILE)
        b_id = brand_data.get("id") or str(uuid.uuid4())[:8]
        brand_data["id"] = b_id

        existing_index = next((i for i, b in enumerate(brands) if b.get("id") == b_id), -1)
        if existing_index >= 0:
            brands[existing_index] = brand_data
        else:
            brands.insert(0, brand_data)

        self._write_json(BRANDS_FILE, brands)
        return brand_data

    def delete_brand(self, brand_id: str) -> bool:
        brands = self._read_json(BRANDS_FILE)
        filtered = [b for b in brands if b.get("id") != brand_id]
        if len(filtered) < len(brands):
            self._write_json(BRANDS_FILE, filtered)
            return True
        return False
