from db.core import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

def get_all_secrets():
    session: Session = next(get_db())
    result = session.execute(text("select * from vault.decrypted_secrets"))
    return {row.name: row.decrypted_secret for row in result}
