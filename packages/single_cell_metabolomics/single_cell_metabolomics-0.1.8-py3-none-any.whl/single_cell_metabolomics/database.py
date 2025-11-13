import psycopg
from psycopg.sql import SQL, Identifier
from .config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

class DatabaseController:
    def __init__(self, table_name='analysis_results'):
        self.conn = self.connect_db()
        self.table_name = table_name

    def connect_db(self):
        conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn

    def create_data(self, dataset_id, pipeline_stage, result_type, result_data):
        try:
            with self.conn.cursor() as cursor:
                insert_sql = SQL('''
                    INSERT INTO {} ("dataset_id", "pipeline_stage", "result_type", "result_data")
                    VALUES (%s, %s, %s, %s)
                ''').format(Identifier(self.table_name))
                cursor.execute(insert_sql, (dataset_id, pipeline_stage, result_type, result_data))
                self.conn.commit()
        except Exception as e:
            print(f"Error inserting data: {e}")
    
    def read_data(self, dataset_id, pipeline_stage, result_type):
        try:
            with self.conn.cursor() as cursor:
                select_sql = SQL('''
                    SELECT "result_data" FROM {}
                    WHERE "dataset_id" = %s AND "pipeline_stage" = %s AND "result_type" = %s
                ''').format(Identifier(self.table_name))
                cursor.execute(select_sql, (dataset_id, pipeline_stage, result_type))
                result = cursor.fetchall()
                return result if result else None
        except Exception as e:
            print(f"Error reading data: {e}")
            return None
    
    def update_data(self, dataset_id, pipeline_stage, result_type, new_result_data):
        try:
            with self.conn.cursor() as cursor:
                update_sql = SQL('''
                    UPDATE {}
                    SET "result_data" = %s, "updated_at" = NOW()
                    WHERE "dataset_id" = %s AND "pipeline_stage" = %s AND "result_type" = %s
                ''').format(Identifier(self.table_name))
                cursor.execute(update_sql, (new_result_data, dataset_id, pipeline_stage, result_type))
                self.conn.commit()
        except Exception as e:
            print(f"Error updating data: {e}")

    def delete_data(self, dataset_id, pipeline_stage, result_type):
        try:
            with self.conn.cursor() as cursor:
                delete_sql = SQL('''
                    DELETE FROM {}
                    WHERE "dataset_id" = %s AND "pipeline_stage" = %s AND "result_type" = %s
                ''').format(Identifier(self.table_name))
                cursor.execute(delete_sql, (dataset_id, pipeline_stage, result_type))
                self.conn.commit()
        except Exception as e:
            print(f"Error deleting data: {e}")

    def close_connection(self):
        if self.conn:
            self.conn.close()