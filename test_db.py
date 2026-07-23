from sqlalchemy import text
from backend.database import engine


def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            print("Result:", result.scalar())
    except Exception as e:
        print("❌ Database connection failed!")
        print(e)


if __name__ == "__main__":
    test_connection()