"""
ByteDocs Flask - Template Loader
Load and render HTML templates
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


class TemplateLoader:
    """Simple template loader with caching"""

    def __init__(self):
        self.cache: Dict[str, str] = {}
        self.template_dir = Path(__file__).parent / "templates"

    def load(self, template_name: str) -> str:
        """Load template file with caching"""
        if template_name in self.cache:
            return self.cache[template_name]

        template_path = self.template_dir / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")

        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.cache[template_name] = content
        return content

    def render(self, template: str, data: Dict[str, Any]) -> str:
        """Simple template rendering - replace placeholders"""
        rendered = template

        # Replace __PLACEHOLDER__ style placeholders
        for key, value in data.items():
            placeholder = f"__BYTEDOCS_{key.upper()}__"
            rendered = rendered.replace(placeholder, str(value) if value is not None else "")

        return rendered

    def clear_cache(self):
        """Clear template cache"""
        self.cache.clear()


# Global template loader instance
_loader = TemplateLoader()


def load_template(template_name: str) -> str:
    """Load template file"""
    return _loader.load(template_name)


def render_template(template: str, data: Dict[str, Any]) -> str:
    """Render template with data"""
    return _loader.render(template, data)


def clear_template_cache():
    """Clear template cache"""
    _loader.clear_cache()
