import aiomysql
from error_handler import MyAppError

import os
import json
from decimal import Decimal
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

ItemsTable = os.environ["MARIADB_ITEMS_TABLE"]
UsersInProcessTable = os.environ["MARIADB_USERSINPROCESS_TABLE"]


async def get_items_table():
    try:
        async with aiomysql.connect(
            host=os.environ["MARIADB_HOST"],       
            port=int(os.environ["MARIADB_PORT"]),
            user=os.environ["MARIADB_USER"],
            password=os.environ["MARIADB_PASSWORD"],
            db=os.environ["MARIADB_DATABASE"]
        ) as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = f"""
                    SELECT 
                        i.ItemCode,
                        i.Name,
                        i.Unit,
                        i.Stock,
                        i.SellingPrice,
                        c.Name AS Category,
                        i.CategoryID
                    FROM {os.environ["MARIADB_ITEMS_TABLE"]} i
                    LEFT JOIN {os.environ["MARIADB_CATEGORIES_TABLE"]} c ON i.CategoryID = c.CategoryID;
                    """
                await cursor.execute(query)
                rows = await cursor.fetchall()
        processed_rows = []
        for row in rows:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
            processed_rows.append(row)
        processed_rows = json.dumps(processed_rows, indent = 2)
        return processed_rows
    except Exception as e:
        raise MyAppError("GetItemsTableError", e)


async def get_user_in_process_data(UserID):
    try:
        async with aiomysql.connect(
            host=os.environ["MARIADB_HOST"],       
            port=int(os.environ["MARIADB_PORT"]),
            user=os.environ["MARIADB_USER"],
            password=os.environ["MARIADB_PASSWORD"],
            db=os.environ["MARIADB_DATABASE"]
        ) as conn:
            async with conn.cursor() as cursor:
                query = f"SELECT Data FROM {UsersInProcessTable} WHERE UserID = %s"
                await cursor.execute(query, (UserID,))
                rows = await cursor.fetchall()
        rows = [row[0] for row in rows]
        return rows, len(rows)
    except Exception as e:
        raise MyAppError("FetchUsersInProcessTableError", e)
    
async def delete_user_in_process(UserID):
    try:
        async with aiomysql.connect(
            host=os.environ["MARIADB_HOST"],
            port=int(os.environ["MARIADB_PORT"]),
            user=os.environ["MARIADB_USER"],
            password=os.environ["MARIADB_PASSWORD"],
            db=os.environ["MARIADB_DATABASE"],
            autocommit=True  # optional, but convenient for deletes
        ) as conn:
            async with conn.cursor() as cursor:
                query = f"DELETE FROM {UsersInProcessTable} WHERE UserID = %s"
                await cursor.execute(query, (UserID,))
    except Exception as e:
        raise MyAppError("DeleteUsersInProcessTableError", e)
  
  
def GenerateTimeStamps(count):
    TimeStamps = [datetime.now(timezone.utc) for _ in range(count)]
    return TimeStamps
async def update_user_in_process_data(UserID, contents, conversation_count):
    try:
        contents = contents[conversation_count:]
        TimeStamps = GenerateTimeStamps(len(contents))
        records = [(UserID, TimeStamps[i], content) for i, content in enumerate(contents)]
        
        async with aiomysql.connect(
            host=os.environ["MARIADB_HOST"],       
            port=int(os.environ["MARIADB_PORT"]),
            user=os.environ["MARIADB_USER"],
            password=os.environ["MARIADB_PASSWORD"],
            db=os.environ["MARIADB_DATABASE"]
        ) as conn:
            async with conn.cursor() as cursor:
                query = f"""
                INSERT INTO {UsersInProcessTable} (UserId, TimeStamp, Data)
                VALUES (%s, %s, %s)
                """
                await cursor.executemany(query, records)
                await conn.commit()
        print(f"{UserID}: Updated UsersInProcess table successfully")   
    except Exception as e:
        raise MyAppError("UpdateUsersInProcessTableError", e)
        
        
   
  

   
   
    
