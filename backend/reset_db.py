from app import create_app
from models import db

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating fresh tables...")
    db.create_all()
    print("Database has been reset. All random data is gone.")
