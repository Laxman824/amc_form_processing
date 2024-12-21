
# app/utils/storage.py
import json
from pathlib import Path
from typing import Dict, Optional
from ..models.template import Template
import shutil

class TemplateStorage:
    def __init__(self, template_dir: Path = Path("templates")):
        self.template_dir = template_dir
        self.template_dir.mkdir(exist_ok=True)

    def save_template(self, template: Template) -> bool:
        """Save template to file"""
        try:
            template_path = self.template_dir / f"{template.name.lower().replace(' ', '_')}.json"
            with open(template_path, "w") as f:
                json.dump(template.to_dict(), f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving template: {str(e)}")
            return False

    def load_template(self, name: str) -> Optional[Template]:
        """Load specific template"""
        template_path = self.template_dir / f"{name.lower().replace(' ', '_')}.json"
        if template_path.exists():
            with open(template_path, "r") as f:
                data = json.load(f)
                return Template.from_dict(data)
        return None

    def list_templates(self) -> Dict[str, Template]:
        """List all available templates"""
        templates = {}
        for file in self.template_dir.glob("*.json"):
            templates[file.stem] = self.load_template(file.stem)
        return templates

    def delete_template(self, name: str) -> bool:
        """Delete template"""
        template_path = self.template_dir / f"{name.lower().replace(' ', '_')}.json"
        try:
            template_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting template: {str(e)}")
            return False

    def backup_templates(self, backup_dir: Path) -> bool:
        """Backup all templates"""
        try:
            backup_dir.mkdir(exist_ok=True)
            for file in self.template_dir.glob("*.json"):
                shutil.copy2(file, backup_dir / file.name)
            return True
        except Exception as e:
            print(f"Error backing up templates: {str(e)}")
            return False