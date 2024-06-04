import pandas as pd
from sqlalchemy import create_engine
import logging
import config

logging.basicConfig(level=logging.INFO)

def store_data_to_db(df, table_name):
    try:
        engine = create_engine(f'postgresql://{config.DB_CONFIG["user"]}:{config.DB_CONFIG["password"]}@{config.DB_CONFIG["host"]}:{config.DB_CONFIG["port"]}/{config.DB_CONFIG["database"]}')
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info(f"Data stored in {table_name} successfully")
    except Exception as e:
        logging.error(f"Error storing data in {table_name}: {e}")

def fetch_data_from_db(table_name):
    try:
        engine = create_engine(f'postgresql://{config.DB_CONFIG["user"]}:{config.DB_CONFIG["password"]}@{config.DB_CONFIG["host"]}:{config.DB_CONFIG["port"]}/{config.DB_CONFIG["database"]}')
        df = pd.read_sql_table(table_name, engine)
        logging.info(f"Fetched data from {table_name} successfully")
        return df
    except Exception as e:
        logging.error(f"Error fetching data from {table_name}: {e}")
        return pd.DataFrame()
