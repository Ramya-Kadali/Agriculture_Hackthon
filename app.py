from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import Config
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable Cross-Origin Resource Sharing
mysql = MySQL(app)

# -------------------- AUTHENTICATION --------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data['name']
    email = data['email']
    password = data['password']  # In production, this should be hashed
    farm_id = 1  # Assign all new users to the default farm for simplicity

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({"message": "User with this email already exists"}), 409

    cursor.execute("INSERT INTO users (name, email, password, farm_id) VALUES (%s, %s, %s, %s)",
                   (name, email, password, farm_id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "User registered successfully!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, email, farm_id FROM users WHERE email = %s AND password = %s", (email, password))
    user_row = cursor.fetchone()

    if user_row:
        columns = [col[0] for col in cursor.description]
        user_data = dict(zip(columns, user_row))
        cursor.close()
        return jsonify(user_data)
    else:
        cursor.close()
        return jsonify({"message": "Invalid email or password"}), 401

# -------------------- TASKS --------------------
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    cursor = mysql.connection.cursor()
    
    cursor.execute("""
        INSERT INTO tasks (farm_id, name, description, date, recurrence)
        VALUES (%s, %s, %s, %s, %s)
    """, (data['farm_id'], data['name'], data.get('description',''),
          data['date'], data.get('recurrence')))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message":"Task created!"})

@app.route('/api/tasks/<int:farm_id>', methods=['GET'])
def get_tasks(farm_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tasks WHERE farm_id = %s", (farm_id,))
    columns = [col[0] for col in cursor.description]
    tasks = [dict(zip(columns, row)) for row in cursor.fetchall()]
    for task in tasks:
        task['date'] = str(task['date'])
    cursor.close()
    return jsonify(tasks)

# -------------------- INVENTORY (IMPROVED) --------------------
@app.route('/api/inventory', methods=['POST'])
def add_inventory():
    data = request.json
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO inventory (farm_id, item_name, quantity, unit, threshold, purchase_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (data['farm_id'], data['item_name'], data['quantity'],
          data['unit'], data['threshold'], data['purchase_date']))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message":"Item added!"})

@app.route('/api/inventory/<int:farm_id>', methods=['GET'])
def get_inventory(farm_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, item_name, quantity, unit, threshold FROM inventory WHERE farm_id=%s", (farm_id,))
    columns = [col[0] for col in cursor.description]
    result = []
    for row in cursor.fetchall():
        item = dict(zip(columns, row))
        item['status'] = "Low Stock" if item['quantity'] < item['threshold'] else "OK"
        result.append(item)
    cursor.close()
    return jsonify(result)

# -------------------- EXPENSES --------------------
@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.json
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO expenses (farm_id, description, amount, category, date)
        VALUES (%s, %s, %s, %s, %s)
    """, (data['farm_id'], data['description'], data['amount'],
          data['category'], data['date']))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message":"Expense added!"})

@app.route('/api/expenses/<int:farm_id>', methods=['GET'])
def get_expenses(farm_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, description, amount, category, date FROM expenses WHERE farm_id=%s", (farm_id,))
    columns = [col[0] for col in cursor.description]
    expenses = [dict(zip(columns, row)) for row in cursor.fetchall()]
    for exp in expenses:
        exp['date'] = str(exp['date'])
    cursor.close()
    return jsonify(expenses)

# -------------------- REPORTS --------------------
@app.route('/api/reports/tasks/<int:farm_id>', methods=['GET'])
def task_report(farm_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT status, COUNT(*) as count FROM tasks WHERE farm_id=%s GROUP BY status", (farm_id,))
    columns = [col[0] for col in cursor.description]
    report = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    return jsonify(report)

@app.route('/api/reports/expenses/<int:farm_id>', methods=['GET'])
def expense_report(farm_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT category, SUM(amount) as total FROM expenses WHERE farm_id=%s GROUP BY category", (farm_id,))
    columns = [col[0] for col in cursor.description]
    report = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    return jsonify(report)

# -------------------- DATA SYNC --------------------
@app.route('/api/sync', methods=['POST'])
def sync_data():
    data = request.json
    cursor = mysql.connection.cursor()

    # Sync tasks from calendar app
    for task in data.get("tasks", []):
        cursor.execute("""
            INSERT INTO tasks (farm_id, name, description, date, recurrence, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name=VALUES(name), description=VALUES(description), date=VALUES(date), status=VALUES(status)
        """, (task['farm_id'], task.get('name'), task.get('description', ''),
              task.get('date'), task.get('recurrence'), task.get('status','Pending')))

    mysql.connection.commit()
    cursor.close()
    return jsonify({"message":"Data synced successfully!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)