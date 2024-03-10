from flask import Flask, render_template, request, jsonify, Response
import psycopg2
import psycopg2.extras
import json
import requests

app = Flask(__name__, static_url_path='/static', static_folder='static')


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
    
    conn.set_client_encoding('UTF8')
    
    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    
    column_names = [desc[0] for desc in cur.description]
    tasks_list = [dict(zip(column_names, task)) for task in tasks]
    
    cur.close()
    conn.close()
    
    return json.dumps(tasks_list, ensure_ascii=False, default=str)


def fetch_tasks_as_json(conn_params, task_id=None):
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    conn.set_client_encoding('UTF8')
    
    if task_id:
        cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        tasks = cur.fetchone()
        if tasks is None:
            cur.close()
            conn.close()
            return None
        tasks = [tasks]  # Оборачиваем результат в список для унификации
    else:
        cur.execute("SELECT * FROM tasks")
        tasks = cur.fetchall()
    
    column_names = [desc[0] for desc in cur.description]
    tasks_list = [dict(zip(column_names, task)) for task in tasks]
    
    cur.close()
    conn.close()
    
    return json.dumps(tasks_list, ensure_ascii=False, default=str)


#########################################################
@app.route('/tasks', methods=['GET'])
def get_tasks():
    task_id = request.args.get('id')  # Получаем ID задачи из параметров запроса
    try:
        tasks_json = fetch_tasks_as_json(conn_params, task_id)
        if tasks_json:
            return Response(tasks_json, content_type='application/json; charset=utf-8')
        else:
            return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500