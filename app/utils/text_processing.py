import re
from typing import List
from fastapi import HTTPException, status

def clean_and_validate_skills(skills: List[str]) -> List[str]:
    """Clean and validate skills list"""
    cleaned = []
    for skill in skills:
        if skill and skill.strip():
            clean_skill = re.sub(r'[^a-zA-Z0-9\s\+\#\.\-]', '', skill.strip())
            if len(clean_skill) >= 2:
                cleaned.append(clean_skill)
    
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one valid skill is required"
        )
    
    if len(cleaned) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 20 skills allowed"
        )
    
    return list(set(cleaned))  # Remove duplicates

def clean_and_validate_tags(tags: List[str]) -> List[str]:
    """Clean and validate tags list"""
    cleaned = []
    for tag in tags:
        if tag and tag.strip():
            clean_tag = re.sub(r'[^a-zA-Z0-9\s\-]', '', tag.strip().lower())
            if len(clean_tag) >= 2:
                cleaned.append(clean_tag)
    
    if len(cleaned) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 tags allowed"
        )
    
    return list(set(cleaned)) 