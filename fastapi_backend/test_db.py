from sqlalchemy import text

from database.database import engine


try:

    with engine.connect() as connection:

        connection.execute(
            text("SELECT 1")
        )

    print("MySQL connection successful.")

except Exception as error:

    print("MySQL connection failed.")
    print(error)