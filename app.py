from flask import Flask, render_template, request, jsonify
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')


def get_db_connection():
    dbname = os.environ.get('DBNAME')
    user = os.environ.get('USER')
    password = os.environ.get('PASSWORD')
    host = os.environ.get('HOST')
    port = os.environ.get('PORT')

    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    return conn

# Create the 'item' table
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item (
            id SERIAL PRIMARY KEY,
            name VARCHAR(25) NOT NULL,
            mail VARCHAR(50) NOT NULL,
            rating FLOAT DEFAULT 0
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

#############################################################################

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM item ORDER BY id")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", data=items)

@app.route('/update', methods=['POST'])
def update():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    for row in data:
        cursor.execute("SELECT * FROM item WHERE id = %s", (row['id'],))
        item = cursor.fetchone()
        if item:
            cursor.execute("""
                UPDATE item SET name = %s, mail = %s, rating = %s WHERE id = %s
            """, (row['name'], row['mail'], row['rating'], row['id']))
        else:
            cursor.execute("""
                INSERT INTO item (id, name, mail, rating) VALUES (%s, %s, %s, %s)
            """, (row['id'], row['name'], row['mail'], row['rating']))
    conn.commit()
    cursor.close()
    conn.close()
    return 'Success'

@app.route('/delete/<int:item_id>', methods=['DELETE'])
def delete(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM item WHERE id = %s", (item_id,))
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    if deleted:
        return 'Success', 200
    else:
        return 'Not Found', 404

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
