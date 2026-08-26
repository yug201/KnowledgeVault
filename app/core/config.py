import os
from dotenv import load_dotenv
load_dotenv() # it will load .env
DATABASE_URL = os.getenv("DATABASE_URL") #readd .env 
# if not DATABASE_URL:
#     raise RuntimeError(
#         "DATABASE_URL is not configured"
#     )
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
# We provide default values ("HS256" and "30") just in case they are missing in .env
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")  
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

IMAGEKIT_PRIVATE_KEY = os.getenv("IMAGEKIT_PRIVATE_KEY")
IMAGEKIT_URL_ENDPOINT = os.getenv("IMAGEKIT_URL_ENDPOINT")

# if not JWT_SECRET_KEY:
#     raise RuntimeError(
#         "JWT_SECRET_KEY is not configured"
#     )