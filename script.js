const BASE_URL = "http://127.0.0.1:5000";
let currentUser = null;
let taskChart = null;
let expenseChart = null;


// -------------------- AUTH & INITIALIZATION --------------------
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    if (sessionStorage.getItem('isLoggedIn') !== 'true') {
        window.location.href = 'sign.html';
        return;
    }
    currentUser = JSON.parse(sessionStorage.getItem('currentUser'));

    // Display user info and setup logout
    document.getElementById('user-display').textContent = `Welcome, ${currentUser.name}`;
    document.getElementById('logout-btn').addEventListener('click', () => {
        sessionStorage.clear();
        window.location.href = 'sign.html';
    });

    // Pre-fill farm ID fields (and make them read-only)
    document.getElementById("task-farm-id").value = currentUser.farm_id;
    document.getElementById("inv-farm-id").value = currentUser.farm_id;
    document.getElementById("exp-farm-id").value = currentUser.farm_id;

    // Attach event listeners for report generation
    document.querySelector('li[onclick*="reports-section"]').addEventListener('click', loadReports);
});


// -------------------- Section Switching --------------------
function showSection(id) {
    document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

// -------------------- TASKS (FIXED) --------------------
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
        method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(data)
    });
    alert("Task Added!");
    e.target.reset();
    loadTasks();
});

async function loadTasks() {
    const farm_id = document.getElementById("task-farm-id").value;
    if (!farm_id) return alert("Farm ID not found.");

    const res = await fetch(`${BASE_URL}/api/tasks/${farm_id}`);
    const tasks = await res.json();
    const tbody = document.querySelector("#task-list tbody");
    tbody.innerHTML = "";
    tasks.forEach(task => {
        tbody.innerHTML += `<tr>
            <td>${task.id}</td><td>${task.name}</td><td>${task.description}</td>
            <td>${task.date}</td><td>${task.recurrence}</td><td>${task.status}</td>
        </tr>`;
    });
}
document.getElementById("load-tasks").addEventListener("click", loadTasks);

// -------------------- INVENTORY (FIXED) --------------------
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
        method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(data)
    });
    alert("Inventory Added!");
    e.target.reset();
    loadInventory();
});

async function loadInventory() {
    const farm_id = document.getElementById("inv-farm-id").value;
    if (!farm_id) return alert("Farm ID not found.");

    const res = await fetch(`${BASE_URL}/api/inventory/${farm_id}`);
    const items = await res.json();
    const tbody = document.querySelector("#inventory-list tbody");
    tbody.innerHTML = "";
    items.forEach(item => {
        tbody.innerHTML += `<tr>
            <td>${item.id}</td><td>${item.item_name}</td>
            <td>${item.quantity} ${item.unit}</td><td>${item.status}</td>
        </tr>`;
    });
}
document.getElementById("load-inventory").addEventListener("click", loadInventory);

// -------------------- EXPENSES (FIXED) --------------------
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
        method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(data)
    });
    alert("Expense Added!");
    e.target.reset();
    loadExpenses();
});

async function loadExpenses() {
    const farm_id = document.getElementById("exp-farm-id").value;
    if (!farm_id) return alert("Farm ID not found.");

    const res = await fetch(`${BASE_URL}/api/expenses/${farm_id}`);
    const expenses = await res.json();
    const tbody = document.querySelector("#expense-list tbody");
    tbody.innerHTML = "";
    expenses.forEach(exp => {
        tbody.innerHTML += `<tr>
            <td>${exp.id}</td><td>${exp.description}</td><td>${exp.amount}</td>
            <td>${exp.category}</td><td>${exp.date}</td>
        </tr>`;
    });
}
document.getElementById("load-expenses").addEventListener("click", loadExpenses);

// -------------------- REPORTS (REFACTORED) --------------------
async function loadReports() {
    if (!currentUser || !currentUser.farm_id) return;
    const farm_id = currentUser.farm_id;

    // --- Task Report ---
    const taskRes = await fetch(`${BASE_URL}/api/reports/tasks/${farm_id}`);
    const taskReportData = await taskRes.json();
    const statusCount = {};
    taskReportData.forEach(item => { statusCount[item.status] = item.count; });
    
    if (taskChart) taskChart.destroy();
    taskChart = new Chart(document.getElementById('task-chart').getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(statusCount),
            datasets: [{ data: Object.values(statusCount), backgroundColor: ['#27ae60', '#c0392b', '#f39c12', '#3498db'] }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // --- Expense Report ---
    const expRes = await fetch(`${BASE_URL}/api/reports/expenses/${farm_id}`);
    const expReportData = await expRes.json();
    const categorySum = {};
    expReportData.forEach(item => { categorySum[item.category] = item.total; });

    if (expenseChart) expenseChart.destroy();
    expenseChart = new Chart(document.getElementById('expense-chart').getContext('2d'), {
        type: 'bar',
        data: {
            labels: Object.keys(categorySum),
            datasets: [{ label: 'Expenses', data: Object.values(categorySum), backgroundColor: '#2980b9' }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });
}