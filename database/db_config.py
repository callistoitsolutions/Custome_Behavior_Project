from sqlalchemy import create_engine
from urllib.parse import quote_plus

DB_USER = "root"
DB_PASSWORD = quote_plus("palash@123")  # IMPORTANT
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "Customer_Behavior_Analytics"

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
