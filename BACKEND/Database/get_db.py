from BACKEND.Database.database import session_local

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        print("DB Connection before")
        db.close()
        print("DB Connection before")