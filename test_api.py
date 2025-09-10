import requests

BASE_URL = "http://127.0.0.1:5000"

# 1️⃣ Create a Task
def test_create_task():
    url = f"{BASE_URL}/api/tasks"
    data = {
        "farm_id": 1,
        "name": "Water Tomatoes",
        "description": "Morning watering",
        "date": "2025-09-12",
        "recurrence": "daily"
    }
    res = requests.post(url, json=data)
    print("Create Task:", res.json())

# 2️⃣ Get Tasks by Date
def test_get_tasks():
    url = f"{BASE_URL}/api/tasks?date=2025-09-12"
    res = requests.get(url)
    print("Tasks on 2025-09-12:", res.json())

# 3️⃣ Update Task
def test_update_task(task_id):
    url = f"{BASE_URL}/api/tasks/{task_id}"
    data = {
        "name": "Water Tomatoes",
        "description": "Evening watering",
        "date": "2025-09-13",
        "recurrence": "daily"
    }
    res = requests.put(url, json=data)
    print("Update Task:", res.json())

# 4️⃣ Mark Task as Completed
def test_mark_completed(task_id):
    url = f"{BASE_URL}/api/tasks/{task_id}/status"
    data = {"status": "Completed"}
    res = requests.patch(url, json=data)
    print("Mark Completed:", res.json())

# 5️⃣ Delete Task
def test_delete_task(task_id):
    url = f"{BASE_URL}/api/tasks/{task_id}"
    res = requests.delete(url)
    print("Delete Task:", res.json())

# Run tests in sequence
if __name__ == "__main__":
    test_create_task()
    test_get_tasks()
    test_update_task(1)      
    test_mark_completed(1)   
    test_delete_task(1)      