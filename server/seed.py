from app import create_app
from models import db, User, Transaction

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()

    print("Creating all tables...")
    db.create_all()

    print("Seeding users...")
    user1 = User(username="st")
    user1.password_hash = "123"

    user2 = User(username="mike")
    user2.password_hash = "password"

    db.session.add_all([user1, user2])
    db.session.commit()

    print("Seeding transactions...")
    t1 = Transaction(
        user_id=user1.id,
        amount=50,
        category="Food",
        description="Groceries"
    )

    t2 = Transaction(
        user_id=user1.id,
        amount=20,
        category="Transport",
        description="Bus pass"
    )

    t3 = Transaction(
        user_id=user2.id,
        amount=100,
        category="Shopping",
        description="Clothes"
    )

    db.session.add_all([t1, t2, t3])
    db.session.commit()

    print("Seeding complete!")
