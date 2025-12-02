from models.exceptions import MyAppError
from config import TABLES, MARIADB_CONFIG   

import json
import time
import aiomysql
from decimal import Decimal
from datetime import datetime, timezone



async def get_items_table():
    try:
        t1 = time.time()
        async with aiomysql.connect(
            host = MARIADB_CONFIG['host'],       
            port = MARIADB_CONFIG['port'],
            user = MARIADB_CONFIG['user'],
            password = MARIADB_CONFIG['password'],
            db = MARIADB_CONFIG['db']
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
                    FROM {TABLES['items']} i
                    LEFT JOIN {TABLES['categories']} c ON i.CategoryID = c.CategoryID;
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
        t2 = time.time()
        time_taken = (t2-t1)*1000
        return processed_rows, time_taken
    
    except Exception as e:
        raise MyAppError("GetItemsTableError", e)

async def get_prev_conv(UserID, is_catalogue_mode):
    try:
        async with aiomysql.connect(
            host = MARIADB_CONFIG['host'],       
            port = MARIADB_CONFIG['port'],
            user = MARIADB_CONFIG['user'],
            password = MARIADB_CONFIG['password'],
            db = MARIADB_CONFIG['db']
        ) as conn:
            async with conn.cursor() as cursor:
                table = TABLES['catalogue_users_in_process'] if is_catalogue_mode else TABLES['users_in_process']
                query = f"SELECT Data FROM {table} WHERE UserID = %s"
                await cursor.execute(query, (UserID,))
                rows = await cursor.fetchall()
        rows = [row[0] for row in rows]
        return rows, len(rows)
    
    except Exception as e:
        raise MyAppError("FetchUsersInProcessTableError", e)
    
async def delete_prev_conv(UserID):
    try:
        async with aiomysql.connect(
            host = MARIADB_CONFIG['host'],       
            port = MARIADB_CONFIG['port'],
            user = MARIADB_CONFIG['user'],
            password = MARIADB_CONFIG['password'],
            db = MARIADB_CONFIG['db'],
            autocommit = True  # optional, but convenient for deletes
        ) as conn:
            async with conn.cursor() as cursor:
                query = f"DELETE FROM {TABLES['users_in_process']} WHERE UserID = %s"
                await cursor.execute(query, (UserID,))
        return {"type" : "success", "data" : f"✅ Deleted UsersInProcess data"}
        
    except Exception as e:
        raise MyAppError("DeleteUsersInProcessTableError", e)
  
def generate_time_stamps(count):
    TimeStamps = [datetime.now(timezone.utc) for _ in range(count)]
    return TimeStamps

async def update_prev_conv(UserID, contents, conversation_count, is_catalogue_mode):
    try:
        contents = contents[conversation_count:]
        TimeStamps = generate_time_stamps(len(contents))
        records = [(UserID, TimeStamps[i], content) for i, content in enumerate(contents)]
        table = TABLES['catalogue_users_in_process'] if is_catalogue_mode else TABLES['users_in_process']
        
        async with aiomysql.connect(
            host = MARIADB_CONFIG['host'],       
            port = MARIADB_CONFIG['port'],
            user = MARIADB_CONFIG['user'],
            password = MARIADB_CONFIG['password'],
            db = MARIADB_CONFIG['db']
        ) as conn:
            async with conn.cursor() as cursor:
                query = f"""
                INSERT INTO {table} (UserId, TimeStamp, Data)
                VALUES (%s, %s, %s)
                """
                await cursor.executemany(query, records)
                await conn.commit()
        print(f"{UserID}: ✅ Update UsersInProcess table")   
        
    except Exception as e:
        raise MyAppError("UpdateUsersInProcessTableError", e)
        
        
   
  

   
   
    
