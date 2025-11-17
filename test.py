import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase

load_dotenv()

# Test OpenAI connection
print(ChatOpenAI(model="gpt-4o-mini", temperature=0.2).invoke("Say hi in 5 words.").content)

# Load database credentials from environment variables
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

if not all([db_user, db_password, db_host, db_name]):
    raise ValueError("Missing required environment variables. Please set DB_USER, DB_PASSWORD, DB_HOST, and DB_NAME in .env file")

db = SQLDatabase.from_uri(
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",
    sample_rows_in_table_info=3
)

print(db.table_info[:500])