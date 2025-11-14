import db_ops
import config
import time
from error_handler import MyAppError

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()
        
        
async def search_stock(search_items):
    t1 = time.time()
    items_json = await db_ops.get_items_table()
    try:
        contents = [types.Content(role = "user", parts = [types.Part.from_text(text = f"stock.json:\n\n{items_json}\n\n\nsearch_stock: {search_items}")])]
        response = await client.aio.models.generate_content(
            model = config.ttt.model,
            contents = contents,
            config = config.ttt.config_2
        )
        response = response.text
        t2 = time.time()
        print(f"SearchStock: {t2-t1}")
        return response
    except Exception as e:
        raise MyAppError("SearchStockError", e)

