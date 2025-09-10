from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from config import Config
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)

# 1️⃣ Create Task
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

# 2️⃣ Read Tasks (by date or farm)
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    farm_id = request.args.get('farm_id')
    date = request.args.get('date')
    cursor = mysql.connection.cursor()
    
    if date:
        cursor.execute("SELECT * FROM tasks WHERE date=%s", (date,))
    elif farm_id:
        cursor.execute("SELECT * FROM tasks WHERE farm_id=%s", (farm_id,))
    else:
        cursor.execute("SELECT * FROM tasks")
    
    tasks = cursor.fetchall()
    cursor.close()
    return jsonify(tasks)

# 3️⃣ Update Task
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE tasks SET name=%s, description=%s, date=%s, recurrence=%s
        WHERE id=%s
    """, (data['name'], data['description'], data['date'], data['recurrence'], task_id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message":"Task updated!"})

# 4️⃣ Delete Task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message":"Task deleted!"})

# 5️⃣ Mark as Completed / Pending
@app.route('/api/tasks/<int:task_id>/status', methods=['PATCH'])
def update_task_status(task_id):
    data = request.json
    status = data.get("status","Pending")
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE tasks SET status=%s WHERE id=%s", (status, task_id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message":"Status updated!"})


# Add Inventory
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

# Get Inventory List with Low Stock Check
@app.route('/api/inventory/<int:farm_id>', methods=['GET'])
def get_inventory(farm_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM inventory WHERE farm_id=%s", (farm_id,))
    rows = cursor.fetchall()
    result = []
    for row in rows:
        status = "Low Stock" if row[3] < row[5] else "OK"
        result.append({
            "id": row[0],
            "item_name": row[2],
            "quantity": str(row[3]) + " " + row[4],
            "status": status
        })
    cursor.close()
    return jsonify(result)


# Add Expense
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

# Retrieve Expense History
@app.route('/api/expenses/<int:farm_id>', methods=['GET'])
def get_expenses(farm_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM expenses WHERE farm_id=%s", (farm_id,))
    rows = cursor.fetchall()
    cursor.close()
    return jsonify(rows)


# Completed Tasks Summary
@app.route('/api/reports/tasks/<int:farm_id>', methods=['GET'])
def task_report(farm_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM tasks WHERE farm_id=%s GROUP BY status", (farm_id,))
    rows = cursor.fetchall()
    cursor.close()
    return jsonify(rows)

# Expense Summary
@app.route('/api/reports/expenses/<int:farm_id>', methods=['GET'])
def expense_report(farm_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE farm_id=%s GROUP BY category", (farm_id,))
    rows = cursor.fetchall()
    cursor.close()
    return jsonify(rows)


@app.route('/api/sync', methods=['POST'])
def sync_data():
    data = request.json
    cursor = mysql.connection.cursor()

    # Sync tasks
    for task in data.get("tasks", []):
        cursor.execute("""
            INSERT INTO tasks (farm_id, name, description, date, recurrence, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (task['farm_id'], task['name'], task['description'],
              task['date'], task.get('recurrence'), task.get('status','Pending')))

    # Sync inventory
    for item in data.get("inventory", []):
        cursor.execute("""
            INSERT INTO inventory (farm_id, item_name, quantity, unit, threshold, purchase_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (item['farm_id'], item['item_name'], item['quantity'],
              item['unit'], item['threshold'], item['purchase_date']))

    # Sync expenses
    for exp in data.get("expenses", []):
        cursor.execute("""
            INSERT INTO expenses (farm_id, description, amount, category, date)
            VALUES (%s, %s, %s, %s, %s)
        """, (exp['farm_id'], exp['description'], exp['amount'],
              exp['category'], exp['date']))

    mysql.connection.commit()
    cursor.close()
    return jsonify({"message":"Data synced successfully!"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
