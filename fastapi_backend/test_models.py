from database.database import SessionLocal
from database.models import Card


db = SessionLocal()

try:

    cards = db.query(Card).all()

    print("Total cards:", len(cards))

    for card in cards:

        print(
            "Card ID:",
            card.id
        )

        print(
            "User ID:",
            card.user_id
        )

        print(
            "Masked Card:",
            card.masked_card_number
        )

        print(
            "Last Four:",
            card.last_four_digits
        )

finally:

    db.close()