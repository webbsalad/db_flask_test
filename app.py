from flask import Flask, render_template, request, jsonify, Response
import psycopg2
import psycopg2.extras
from psycopg2 import Error
import json

app = Flask(__name__, static_url_path='/static', static_folder='static')

conn_params = {
    'dbname' : "igyewlez",
    'user': "igyewlez",
    'password': "TFg3xtI25QbqQUOERaKvd-yJwn3GXq47",
    'host': "ziggy.db.elephantsql.com",
    'port': "5432",
}

def connect_to_db():
    try:
        connection = psycopg2.connect(**conn_params)
        return connection
    except Error as e:
        print(f"Error while connecting to PostgreSQL: {e}")
        return None

def add_item(new_item_json):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()

            # Пример SQL запроса для вставки нового элемента
            sql_query = """INSERT INTO items (id, title, description, deadline, priority, status, assignees) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s);"""
            cursor.execute(sql_query, (new_item_json['id'], new_item_json['title'], new_item_json['description'], 
                                       new_item_json['deadline'], new_item_json['priority'], new_item_json['status'], 
                                       new_item_json['assignees']))

            connection.commit()
            print("Item added successfully")
        except Error as e:
            print(f"Error while adding item to PostgreSQL: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()

def delete_item_by_id(item_id):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()

            # Пример SQL запроса для удаления элемента по id
            sql_query = "DELETE FROM items WHERE id = %s;"
            cursor.execute(sql_query, (item_id,))

            connection.commit()
            print("Item deleted successfully")
        except Error as e:
            print(f"Error while deleting item from PostgreSQL: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()

def fetch_items_as_json(conn_params, item_id=None):
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    conn.set_client_encoding('UTF8')
    
    if item_id:
        cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        item = cur.fetchone()
        if item is None:
            cur.close()
            conn.close()
            return None
        column_names = [desc[0] for desc in cur.description]
        item_dict = dict(zip(column_names, item))
        items_list = [item_dict]  
    else:
        cur.execute("SELECT * FROM items")
        items = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        items_list = [dict(zip(column_names, item)) for item in items]
    
    cur.close()
    conn.close()
    
    return json.dumps(items_list, ensure_ascii=False, default=str)

#########################################################
@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        item_id = request.args.get('id')
        try:
            items_json = fetch_items_as_json(conn_params, item_id)
            if items_json:
                return Response(items_json, content_type='application/json; charset=utf-8')
            else:
                return jsonify({"error": "Item not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == 'POST':
        try:
            new_item_json = request.get_json()
            add_item(new_item_json)
            return "Item added successfully", 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        # Обработка удаления элемента по его id
        delete_item_by_id(item_id)
        return "Item deleted successfully", 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


