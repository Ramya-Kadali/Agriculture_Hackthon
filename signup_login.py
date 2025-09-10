from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import Config
import MySQLdb.cursors  # Import DictCursor

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)
CORS(app)

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"message": "Missing fields"}), 400

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                       (name, email, password))
        mysql.connection.commit()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"message": "User already exists"}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()

    if user:
        return jsonify({
            "message": "Login successful",
            "user": {
                "name": user['name'],
                "email": user['email']
            }
        }), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@app.route('/api/profile', methods=['POST'])
def save_profile():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    location = data.get('location')
    farmSize = data.get('farmSize')
    crops = data.get('crops')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM profiles WHERE email=%s", (email,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE profiles SET name=%s, location=%s, farm_size=%s, crops=%s WHERE email=%s
        """, (name, location, farmSize, crops, email))
    else:
        cursor.execute("""
            INSERT INTO profiles (email, name, location, farm_size, crops)
            VALUES (%s, %s, %s, %s, %s)
        """, (email, name, location, farmSize, crops))

    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Profile saved successfully."}), 200

# Tasks CRUD
@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO tasks (farm_id, name, description, date, recurrence)
        VALUES (%s, %s, %s, %s, %s)
    """, (data['farmId'], data['name'], data['description'], data['date'], data['recurrence']))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Task added"}), 201

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    cursor.close()
    columns = ['id','farmId','name','description','date','recurrence']
    records = [dict(zip(columns, row)) for row in rows]
    return jsonify(records)



# Expenses CRUD
@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.json
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO expenses (farm_id, description, category, date)
        VALUES (%s, %s, %s, %s)
    """, (data['farmId'], data['description'], data['category'], data['date']))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Expense added"}), 201

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    cursor.close()
    columns = ['id','farmId','description','category','date']
    records = [dict(zip(columns, row)) for row in rows]
    return jsonify(records)

@app.route('/api/profile', methods=['GET'])
def get_profile():
    email = request.args.get('email')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT name, location, farm_size, crops FROM profiles WHERE email=%s", (email,))
    row = cursor.fetchone()
    cursor.close()

    if row:
        profile = {
            "name": row['name'],
            "location": row['location'],
            "farmSize": row['farm_size'],
            "crops": row['crops']
        }
        return jsonify({"profile": profile}), 200

    return jsonify({"message": "Profile not found"}), 404


@app.route('/api/inventory', methods=['POST'])
def add_inventory():
    data = request.json
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO inventory (farm_id, item_name, quantity, units, threshold, purchase_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (data['farmId'], data['itemName'], data['quantity'], data['units'], data['threshold'], data['purchaseDate']))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Inventory added"}), 201

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()
    cursor.close()
    columns = ['id','farmId','itemName','quantity','units','threshold','purchaseDate']
    records = [dict(zip(columns, row)) for row in rows]
    return jsonify(records)

@app.route('/api/inventory/<int:id>', methods=['PUT'])
def update_inventory(id):
    data = request.json
    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE inventory SET item_name=%s, quantity=%s, units=%s, threshold=%s, purchase_date=%s
        WHERE id=%s
    """, (data['itemName'], data['quantity'], data['units'], data['threshold'], data['purchaseDate'], id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Inventory updated"})

@app.route('/api/inventory/<int:id>', methods=['DELETE'])
def delete_inventory(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM inventory WHERE id=%s", (id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Inventory deleted"})


if __name__ == '__main__':
    app.run(debug=True)
