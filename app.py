from flask import Flask, render_template, request, jsonify, Response
import psycopg2
import psycopg2.extras
from psycopg2 import Error
import json

app = Flask(__name__, static_url_path='/static', static_folder='static')

conn_params = {
    'dbname' : "postgres",
    'user': "postgres.ppoohvwxcftgaqioemzy",
    'password': "ufnvauifaj1_",
    'host': "aws-0-eu-central-1.pooler.supabase.com",
    'port': "5432",
}

def connect_to_db():
    try:
        connection = psycopg2.connect(**conn_params)
        return connection
    except Error as e:
        print(f"Error while connecting to PostgreSQL: {e}")
        return None

def fetch_data_as_json(table_name, item_id=None, sort_by=None):
    connection = connect_to_db()
    cursor = connection.cursor()
    
    connection.set_client_encoding('UTF8')
    
    if item_id:
        cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        if item is None:
            cursor.close()
            connection.close()
            return None
        column_names = [desc[0] for desc in cursor.description]
        item_dict = dict(zip(column_names, item))
        items_list = [item_dict]  
    else:
        if sort_by:
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY {sort_by}")
        else:
            cursor.execute(f"SELECT * FROM {table_name}")
        items = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        items_list = [dict(zip(column_names, item)) for item in items]
    
    cursor.close()
    connection.close()
    
    return json.dumps(items_list, ensure_ascii=False, default=str)

def add_item(table_name, new_item_json):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()

            columns = ', '.join(new_item_json.keys())
            placeholders = ', '.join(['%s'] * len(new_item_json))
            sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"

            cursor.execute(sql_query, list(new_item_json.values()))

            connection.commit()
            print(f"Item added successfully to {table_name}")
            return jsonify({"message": f"Item added successfully to {table_name}"})
        except Error as e:
            print(f"Error while adding item to PostgreSQL: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            if connection:
                cursor.close()
                connection.close()

def delete_item_by_id(table_name, item_id):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()

            sql_query = f"DELETE FROM {table_name} WHERE id = %s;"
            cursor.execute(sql_query, (item_id,))

            connection.commit()
            print(f"Item deleted successfully from {table_name}")
        except Error as e:
            print(f"Error while deleting item from PostgreSQL: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()

@app.route('/<string:table_name>', methods=['GET', 'POST'])
def handle_items(table_name):
    if request.method == 'GET':
        item_id = request.args.get('id')
        sort_by = request.args.get('sortBy')
        try:
            items_json = fetch_data_as_json(table_name, item_id, sort_by)
            if items_json:
                return Response(items_json, content_type='application/json; charset=utf-8')
            else:
                return jsonify({"error": "Item not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == 'POST':
        try:
            new_item_json = request.get_json()
            add_item(table_name, new_item_json)
            return f"{new_item_json}", 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/<string:table_name>/<int:item_id>', methods=['DELETE'])
def delete_item(table_name, item_id):
    try:
        delete_item_by_id(table_name, item_id)
        return "Item deleted successfully", 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)