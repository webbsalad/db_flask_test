from flask import Flask, render_template, request, jsonify, Response
import psycopg2
import psycopg2.extras
import json
import requests

app = Flask(__name__, static_url_path='/static', static_folder='static')


# Database connection parameters
conn_params = {
    'dbname' : "igyewlez",
    'user': "igyewlez",
    'password': "TFg3xtI25QbqQUOERaKvd-yJwn3GXq47",
    'host': "ziggy.db.elephantsql.com",
    'port': "5432",

}

def fetch_tasks_as_json(conn_params):
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    # Установка кодировки UTF-8 при чтении данных из базы данных
    conn.set_client_encoding('UTF8')
    
    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    
    column_names = [desc[0] for desc in cur.description]
    tasks_list = [dict(zip(column_names, task)) for task in tasks]
    
    cur.close()
    conn.close()
    
    # Преобразование данных в строку JSON с кодировкой UTF-8
    return json.dumps(tasks_list, ensure_ascii=False, default=str)

# # Establish a connection to the database
# def get_db_connection():
#     conn = psycopg2.connect(
#         dbname=dbname,
#         user=user,
#         password=password,
#         host=host,
#         port=port
#     )
#     return conn

# # Create the 'item' table
# def create_tables():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS item (
#             id SERIAL PRIMARY KEY,
#             name VARCHAR(25) NOT NULL,
#             mail VARCHAR(50) NOT NULL,
#             rating FLOAT DEFAULT 0
#         )
#     """)
#     conn.commit()
#     cursor.close()
#     conn.close()

#############################################################################
@app.route('/tasks', methods=['GET', 'POST'])
def get_tasks():
    if request.method == 'GET':
        try:
            tasks = fetch_tasks_as_json(conn_params)
            return Response(tasks, content_type='application/json; charset=utf-8')
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
# @app.route('/')
# def index():
#     conn = get_db_connection()
#     cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#     cursor.execute("SELECT * FROM item ORDER BY id")
#     items = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template("index.html", data=items)

# @app.route('/update', methods=['POST'])
# def update():
#     data = request.json
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     for row in data:
#         cursor.execute("SELECT * FROM item WHERE id = %s", (row['id'],))
#         item = cursor.fetchone()
#         if item:
#             cursor.execute("""
#                 UPDATE item SET name = %s, mail = %s, rating = %s WHERE id = %s
#             """, (row['name'], row['mail'], row['rating'], row['id']))
#         else:
#             cursor.execute("""
#                 INSERT INTO item (id, name, mail, rating) VALUES (%s, %s, %s, %s)
#             """, (row['id'], row['name'], row['mail'], row['rating']))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return 'Success'

# @app.route('/delete/<int:item_id>', methods=['DELETE'])
# def delete(item_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM item WHERE id = %s", (item_id,))
#     deleted = cursor.rowcount
#     conn.commit()
#     cursor.close()
#     conn.close()
#     if deleted:
#         return 'Success', 200
#     else:
#         return 'Not Found', 404

if __name__ == '__main__':
    app.run(debug=True)
