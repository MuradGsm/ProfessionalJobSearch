import re
from unidecode import unidecode


def generate_unique_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    # Convert to ASCII
    slug = unidecode(title.lower())
    
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Limit length
    return slug[:50]