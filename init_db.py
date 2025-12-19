from app import create_app, db  # ✅ db is in app (this matches your working command)

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ DB tables created")
