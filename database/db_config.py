import streamlit as st
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Read database credentials from Streamlit Secrets
db = st.secrets["database"]

DB_USER = db["user"]
DB_PASSWORD = quote_plus(db["password"])
DB_HOST = db["host"]
DB_PORT = db["port"]
DB_NAME = db["database"]

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
