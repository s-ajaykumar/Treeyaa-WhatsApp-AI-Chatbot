import prompt 

import os
from google import genai
from sarvamai import SarvamAI
from dotenv import load_dotenv
from google.genai import types

load_dotenv()


# AI
# Clients
sarvam = SarvamAI(api_subscription_key = os.environ['SARVAM_API_KEY'])  
gemini = genai.Client(api_key = os.environ.get("GOOGLE_API_KEY"),)
 
## Model Configurations  
model = "gemini-2.5-flash"  

main_prompt =  prompt.main_instruction
catalogue_prompt = prompt.catalogue_instruction
search_stock_prompt = prompt.search_stock

main_config = types.GenerateContentConfig(
    temperature = 0,
    thinking_config = types.ThinkingConfig(thinking_budget = 0),
    response_mime_type = "application/json",
    system_instruction = [types.Part.from_text(text = main_prompt)]
)

catalogue_config = types.GenerateContentConfig(
    temperature = 0,
    thinking_config = types.ThinkingConfig(thinking_budget = 0),
    response_mime_type = "application/json",
    system_instruction = [types.Part.from_text(text = catalogue_prompt)]
)

search_stock_config = types.GenerateContentConfig(
    temperature = 0,
    thinking_config = types.ThinkingConfig(thinking_budget = 0),
    response_mime_type = "application/json",
    system_instruction = [types.Part.from_text(text = search_stock_prompt)]
)

# MariaDB 
MARIADB_CONFIG = {
    "host": os.environ["MARIADB_HOST"],
    "port": int(os.environ["MARIADB_PORT"]),
    "user": os.environ["MARIADB_USER"],
    "password": os.environ["MARIADB_PASSWORD"],
    "db": os.environ["MARIADB_DATABASE"],
}
TABLES = {
    "items": os.environ["MARIADB_ITEMS_TABLE"],
    "users_in_process": os.environ["MARIADB_USERSINPROCESS_TABLE"],
    "catalogue_users_in_process" : os.environ["MARIADB_CATALOGUE_USERSINPROCESS_TABLE"],
    "categories": os.environ["MARIADB_CATEGORIES_TABLE"],
}

# Authentication
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
