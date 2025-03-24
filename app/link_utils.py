import random
import string
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Link


def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def create_unique_short_code(db: Session, length=6):
    while True:
        short_code = generate_short_code(length)
        existing = db.query(Link).filter(Link.short_code == short_code).first()
        if not existing:
            return short_code

def is_expired(link: Link) -> bool:
    if link.expires_at and link.expires_at < datetime.utcnow():
        return True
    return False

def update_link_usage(db: Session, link: Link):
    link.clicks += 1
    link.last_used_at = datetime.utcnow()
    db.commit()
