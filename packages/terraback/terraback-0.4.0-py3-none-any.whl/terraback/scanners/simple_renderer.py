"""Simple template renderer for Terraform files."""
from pathlib import Path
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from terraback.utils.logging import get_logger

logger = get_logger(__name__)


class SimpleRenderer:
    """Simple template renderer without complexity."""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render_resources(self, resources: List[Dict[str, Any]], resource_type: str, output_dir: Path) -> Path:
        """Render resources to a Terraform file."""
        if not resources:
            return None
        
        # Get template
        template_name = f"{resource_type}.tf.j2"
        try:
            template = self.env.get_template(f"aws/{template_name}")
        except TemplateNotFound as e:
            logger.warning(f"No template found for {resource_type}, using generic: {e}")
            template = self.env.get_template("aws/generic_resource.tf.j2")
        
        # Deduplicate names
        self._deduplicate_names(resources)
        
        # Render
        output = template.render(resources=resources)
        
        # Write file
        output_file = output_dir / f"{resource_type}.tf"
        output_file.write_text(output)
        logger.info(f"Wrote {len(resources)} {resource_type} resources to {output_file}")
        
        return output_file
    
    def _deduplicate_names(self, resources: List[Dict[str, Any]]):
        """Ensure unique resource names."""
        seen = {}
        
        for resource in resources:
            name = resource.get('name_sanitized', 'unnamed')
            
            if name in seen:
                seen[name] += 1
                resource['name_sanitized'] = f"{name}_{seen[name]}"
            else:
                seen[name] = 1


def render_all(results: Dict[str, List[Dict]], template_dir: Path, output_dir: Path):
    """Render all scan results to Terraform files."""
    renderer = SimpleRenderer(template_dir)
    
    for resource_type, resources in results.items():
        if resources:
            # Extract terraform type from first resource
            tf_type = resources[0].get('terraform_type', resource_type)
            renderer.render_resources(resources, tf_type, output_dir)