from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from psycopg2 import Error
import json
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

conn_params = {
    'dbname': "postgres",
    'user': "postgres.ppoohvwxcftgaqioemzy",
    'password': "ufnvauifaj1_",
    'host': "aws-0-eu-central-1.pooler.supabase.com",
    'port': "5432",
}

# Секретный ключ для подписи токенов
SECRET_KEY = 'jnfvjasdnvnsadvklnkflbnkfabfa'

def connect_to_db():
    try:
        connection = psycopg2.connect(**conn_params)
        return connection
    except Error as e:
        print(f"Error while connecting to PostgreSQL: {e}")
        return None

def generate_token(user_id):
    payload = {'user_id': user_id}
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def get_max_id(table_name):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(f"SELECT MAX(id) FROM {table_name};")
            max_id = cursor.fetchone()[0]
            return max_id if max_id else 0
        except Error as e:
            print(f"Error while getting max ID from PostgreSQL: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()

def add_item(table_name, new_item_json):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()

            max_id = get_max_id(table_name)
            new_item_json['id'] = max_id + 1

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

def fetch_data_as_json(table_name, filters=None, sort_by=None):
    connection = connect_to_db()
    cursor = connection.cursor()

    connection.set_client_encoding('UTF8')

    where_clause = ''
    params = []
    if filters:
        conditions = []
        for key, value in filters.items():
            if '*' in value:
                if value.startswith('*'):
                    value = value.replace('*', '%') + '%'
                    conditions.append(f'"{key}" ILIKE %s') 
                else:
                    value = '%' + value.replace('*', '%')
                    conditions.append(f'"{key}" ILIKE %s') 
                params.append(value)
            else:
                conditions.append(f'"{key}" = %s') 
                params.append(value)
        where_clause = ' AND '.join(conditions)

    order_clause = ''
    if sort_by:
        if sort_by == '-':
            sort_by = 'id'  
        order_clause = f"ORDER BY {sort_by}"

    sql_query = f'SELECT * FROM "{table_name}"' 
    if where_clause:
        sql_query += f" WHERE {where_clause}"
    sql_query += f" {order_clause};"

    cursor.execute(sql_query, tuple(params))
    items = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    items_list = [dict(zip(column_names, item)) for item in items]

    cursor.close()
    connection.close()

    for item in items_list:
        if 'timingslist' in item:
            item['timingsList'] = item.pop('timingslist')

    return json.dumps(items_list, ensure_ascii=False, default=str)


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

def update_item_status(table_name, item_id, status):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()

            sql_query = f"UPDATE {table_name} SET status = %s WHERE id = %s;"
            cursor.execute(sql_query, (status, item_id))

            connection.commit()
            print(f"Item status updated successfully in {table_name}")
        except Error as e:
            print(f"Error while updating item status in PostgreSQL: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()

################################################################################################

@app.route('/auth_me', methods=['GET', 'POST'])
def zero():
    return jsonify('заглушка'), 500


@app.route('/<string:table_name>', methods=['GET', 'POST'])
def handle_items(table_name):
    if request.method == 'GET':
        filters = {}
        sort_by = request.args.get('sortBy')
        for key, value in request.args.items():
            if key != 'sortBy':
                filters[str(key)] = value 
        try:
            items_json = fetch_data_as_json(table_name, filters, sort_by)
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


@app.route('/<string:table_name>/<int:item_id>', methods=['GET', 'DELETE'])
def get_item(table_name, item_id):
    if request.method == 'GET':
        try:
            filters = {'id': str(item_id)}
            items_json = fetch_data_as_json(table_name, filters)
            if items_json:
                return Response(items_json[1:-1], content_type='application/json; charset=utf-8')
            else:
                return jsonify({"error": f"Item with id {item_id} not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == 'DELETE':
        try:
            delete_item_by_id(table_name, item_id)
            return "Item deleted successfully", 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/<string:table_name>/<int:item_id>', methods=['DELETE'])
def delete_item(table_name, item_id):
    try:
        delete_item_by_id(table_name, item_id)
        return "Item deleted successfully", 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/<string:table_name>/<int:item_id>', methods=['PATCH'])
def update_item(table_name, item_id):
    if request.method == 'PATCH':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Empty request body"}), 400

            # Extract all fields from the JSON request and update them in the database
            update_fields = ", ".join([f"{key} = %s" for key in data.keys()])
            update_values = tuple(data.values())
            update_values += (item_id,)

            connection = connect_to_db()
            if connection:
                try:
                    cursor = connection.cursor()

                    sql_query = f"UPDATE {table_name} SET {update_fields} WHERE id = %s;"
                    cursor.execute(sql_query, update_values)

                    connection.commit()
                    print(f"Item updated successfully in table {table_name}")
                    return "Item updated successfully", 200
                except Error as e:
                    print(f"Error while updating item in PostgreSQL: {e}")
                    return jsonify({"error": str(e)}), 500
                finally:
                    if connection:
                        cursor.close()
                        connection.close()
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Маршрут для регистрации нового пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    fullName = data.get('fullName')
    email = data.get('email')
    age = data.get('age')
    gender = data.get('gender')
    password = data.get('password')

    # Проверка наличия всех необходимых полей
    if not (fullName and email and age and gender and password):
        return jsonify({'error': 'Missing fields'}), 400

    # Проверка, не существует ли уже пользователь с таким email-адресом
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT id FROM users WHERE email = %s
            """, (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                return jsonify({'error': 'User with this email already exists'}), 400

            # Хеширование пароля перед сохранением в базу данных
            hashed_password = generate_password_hash(password)

            # Определение следующего доступного id
            next_id = get_max_id("users") + 1

            # Добавление пользователя в базу данных
            cursor.execute("""
                INSERT INTO users (id, fullName, email, age, gender, password)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (next_id, fullName, email, age, gender, hashed_password))
            user_id = cursor.fetchone()[0]

            # Создание токена
            token = generate_token(user_id)

            # Сохранение токена в таблице register
            cursor.execute("""
                INSERT INTO register (user_id, token)
                VALUES (%s, %s)
            """, (user_id, token))

            connection.commit()

            return jsonify({
                'token': token,
                'data': {
                    'fullName': fullName,
                    'email': email,
                    'age': age,
                    'gender': gender,
                    'id': user_id
                }
            }), 200
        except Error as e:
            print(f"Error while registering user: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if connection:
                cursor.close()
                connection.close()
    else:
        return jsonify({'error': 'Unable to connect to the database'}), 500


# Маршрут для аутентификации пользователя
@app.route('/auth', methods=['POST'])
def auth():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Проверка наличия всех необходимых полей
    if not (email and password):
        return jsonify({'error': 'Missing fields'}), 400

    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()

            # Поиск пользователя в базе данных
            cursor.execute("""
                SELECT id, fullName, email, age, gender, password
                FROM users
                WHERE email = %s
            """, (email,))
            user = cursor.fetchone()

            if not user:
                return jsonify({'error': 'User is not found'}), 404
            if not check_password_hash(user[5], password):
                return jsonify({'error': 'wrong password'}), 401

            user_id, fullName, email, age, gender, _ = user

            # Создание токена
            token = generate_token(user_id)

            return jsonify({
                'token': token,
                'data': {
                    'id': user_id,
                    'fullName': fullName,
                    'email': email,
                    'age': age,
                    'gender': gender
                }
            }), 200
        except Error as e:
            print(f"Error while authenticating user: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if connection:
                cursor.close()
                connection.close()
    else:
        return jsonify({'error': 'Unable to connect to the database'}), 500
