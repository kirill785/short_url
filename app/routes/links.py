from typing import Optional, List
from datetime import datetime
import re
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import Link, User
from app.schemas import LinkCreate, LinkResponse, LinkUpdate, LinkStats
from app.auth_utils import get_current_active_user, get_optional_user
from app.link_utils import create_unique_short_code, is_expired, update_link_usage
from app.config import settings

router = APIRouter(tags=["links"])

@router.post("/links/shorten", response_model=LinkResponse)
def create_short_link(
        link_data: LinkCreate, 
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_optional_user)):
    if link_data.custom_alias:
        if not re.match(r'^[a-zA-Z0-9_-]+$', link_data.custom_alias):
            raise HTTPException(
                status_code=400,
                detail="Custom alias contains invalid characters"
            )
        
        existing_link = db.query(Link).filter(Link.short_code == link_data.custom_alias).first()
        if existing_link:
            raise HTTPException(
                status_code=400,
                detail="Custom alias already in use"
            )
        short_code = link_data.custom_alias
        is_custom = True
    else:
        short_code = create_unique_short_code(db)
        is_custom = False
    
    new_link = Link(
        original_url=str(link_data.original_url),
        short_code=short_code,
        user_id=current_user.id if current_user else None,
        expires_at=link_data.expires_at,
        is_custom=is_custom
    )
    
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    
    return LinkResponse(
        original_url=new_link.original_url,
        short_code=new_link.short_code,
        short_url=f"{settings.BASE_URL}/{new_link.short_code}"
    )

@router.get("/links/search", response_model=List[LinkResponse])
def search_links(original_url: str, db: Session = Depends(get_db)):
    search_term = f"%{original_url.rstrip('/')}%"
    links = db.query(Link).filter(
        Link.original_url.ilike(search_term),
        or_(Link.expires_at.is_(None), Link.expires_at > datetime.utcnow())
    ).all()
    
    return [
        LinkResponse(
            original_url=link.original_url, 
            short_code=link.short_code,
            short_url=f"{settings.BASE_URL}/{link.short_code}"
        ) 
        for link in links
    ]

@router.get("/links/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    if is_expired(link):
        db.delete(link)
        db.commit()
        raise HTTPException(status_code=410, detail="Link has expired")
    
    update_link_usage(db, link)
    
    return RedirectResponse(url=link.original_url)

@router.get("/links/{short_code}/stats", response_model=LinkStats)
def get_link_stats(short_code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    if is_expired(link):
        db.delete(link)
        db.commit()
        raise HTTPException(status_code=410, detail="Link has expired")
    
    return link

@router.put("/links/{short_code}", response_model=LinkResponse)
def update_link(
    short_code: str, 
    link_data: LinkUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    if link.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this link")
    
    if is_expired(link):
        db.delete(link)
        db.commit()
        raise HTTPException(status_code=410, detail="Link has expired")
    
    if link_data.original_url:
        link.original_url = str(link_data.original_url)
    
    if link_data.short_code:
        if not re.match(r'^[a-zA-Z0-9_-]+$', link_data.short_code):
            raise HTTPException(
                status_code=400,
                detail="Short code contains invalid characters"
            )
        
        existing_link = db.query(Link).filter(
            Link.short_code == link_data.short_code,
            Link.id != link.id
        ).first()
        
        if existing_link:
            raise HTTPException(
                status_code=400,
                detail="Short code already in use"
            )
        
        link.short_code = link_data.short_code
        link.is_custom = True
    
    db.commit()
    db.refresh(link)
    
    return LinkResponse(
        original_url=link.original_url,
        short_code=link.short_code,
        short_url=f"{settings.BASE_URL}/{link.short_code}"
    )

@router.delete("/links/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(
    short_code: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    if link.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this link")
    
    db.delete(link)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

