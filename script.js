const BASE_URL = "http://127.0.0.1:5000";

// -------------------- Section Switching --------------------
function showSection(id) {
    document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

// -------------------- TASKS --------------------
document.getElementById("task-form").addEventListener("submit", async e => {
    e.preventDefault();
    const data = {
        farm_id: parseInt(document.getElementById("task-farm-id").value),
        name: document.getElementById("task-name").value,
        description: document.getElementById("task-desc").value,
        date: document.getElementById("task-date").value,
        recurrence: document.getElementById("task-recurrence").value
    };
    await fetch(`${BASE_URL}/api/tasks`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });
    alert("Task Added!");
    loadTasks(); // auto-refresh table
});

async function loadTasks() {
    const res = await fetch(`${BASE_URL}/api/tasks`);
    const tasks = await res.json();
    const tbody = document.querySelector("#task-list tbody");
    tbody.innerHTML = "";
    tasks.forEach(task => {
        tbody.innerHTML += `<tr>
            <td>${task.id}</td>
            <td>${task.name}</td>
            <td>${task.description}</td>
            <td>${task.date}</td>
            <td>${task.recurrence}</td>
            <td>${task.status}</td>
        </tr>`;
    });

    // Render Task Status Chart
    const statusCount = {};
    tasks.forEach(t => { statusCount[t.status] = (statusCount[t.status] || 0) + 1; });
    const ctx = document.getElementById('task-chart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(statusCount),
            datasets: [{ 
                data: Object.values(statusCount),
                backgroundColor: ['#27ae60', '#c0392b', '#f39c12'] 
            }]
        }
    });
}

document.getElementById("load-tasks").addEventListener("click", loadTasks);

// -------------------- INVENTORY --------------------
document.getElementById("inventory-form").addEventListener("submit", async e => {
    e.preventDefault();
    const data = {
        farm_id: parseInt(document.getElementById("inv-farm-id").value),
        item_name: document.getElementById("inv-item-name").value,
        quantity: parseFloat(document.getElementById("inv-quantity").value),
        unit: document.getElementById("inv-unit").value,
        threshold: parseFloat(document.getElementById("inv-threshold").value),
        purchase_date: document.getElementById("inv-purchase-date").value
    };
    await fetch(`${BASE_URL}/api/inventory`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });
    alert("Inventory Added!");
    loadInventory();
});

async function loadInventory() {
    const farm_id = document.getElementById("inv-farm-id").value;
    if (!farm_id) return alert("Enter Farm ID to load inventory.");
    const res = await fetch(`${BASE_URL}/api/inventory/${farm_id}`);
    const items = await res.json();
    const tbody = document.querySelector("#inventory-list tbody");
    tbody.innerHTML = "";
    items.forEach(item => {
        tbody.innerHTML += `<tr>
            <td>${item.id}</td>
            <td>${item.item_name}</td>
            <td>${item.quantity}</td>
            <td>${item.status}</td>
        </tr>`;
    });
}

document.getElementById("load-inventory").addEventListener("click", loadInventory);

// -------------------- EXPENSES --------------------
document.getElementById("expense-form").addEventListener("submit", async e => {
    e.preventDefault();
    const data = {
        farm_id: parseInt(document.getElementById("exp-farm-id").value),
        description: document.getElementById("exp-desc").value,
        amount: parseFloat(document.getElementById("exp-amount").value),
        category: document.getElementById("exp-category").value,
        date: document.getElementById("exp-date").value
    };
    await fetch(`${BASE_URL}/api/expenses`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });
    alert("Expense Added!");
    loadExpenses();
});

async function loadExpenses() {
    const farm_id = document.getElementById("exp-farm-id").value;
    if (!farm_id) return alert("Enter Farm ID to load expenses.");
    const res = await fetch(`${BASE_URL}/api/expenses/${farm_id}`);
    const expenses = await res.json();
    const tbody = document.querySelector("#expense-list tbody");
    tbody.innerHTML = "";
    expenses.forEach(exp => {
        tbody.innerHTML += `<tr>
            <td>${exp[0]}</td>
            <td>${exp[2]}</td>
            <td>${exp[3]}</td>
            <td>${exp[4]}</td>
            <td>${exp[5]}</td>
        </tr>`;
    });

    // Render Expense Chart
    const categorySum = {};
    expenses.forEach(e => { categorySum[e[4]] = (categorySum[e[4]] || 0) + e[3]; });
    const ctx = document.getElementById('expense-chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(categorySum),
            datasets: [{ label: 'Expenses', data: Object.values(categorySum), backgroundColor: '#2980b9' }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
}

document.getElementById("load-expenses").addEventListener("click", loadExpenses);
