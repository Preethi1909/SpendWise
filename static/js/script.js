
const addBtn = document.getElementById("addBtn");

let editingId = null;

let categoryChart = null;
let monthlyChart = null;


// =====================================
// ADD / UPDATE EXPENSE
// =====================================

addBtn.addEventListener("click", function() {

    const amount = document.getElementById("amount").value;
    const category = document.getElementById("category").value;
    const date = document.getElementById("date").value;
    const description = document.getElementById("description").value;


    // Validation

    if (!amount || !category || !date) {
        alert("Please fill Amount, Category and Date.");
        return;
    }


    // =================================
    // UPDATE
    // =================================

    if (editingId !== null) {

        fetch(`/expenses/update/${editingId}`, {

            method: "PUT",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                amount: Number(amount),
                category: category,
                date: date,
                description: description
            })
        })

        .then(response => response.json())

        .then(data => {

            console.log(data);

            editingId = null;

            location.reload();
        });

        return;
    }


    // =================================
    // ADD
    // =================================

    fetch("/expenses/add", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            amount: Number(amount),
            category: category,
            date: date,
            description: description
        })
    })

    .then(response => response.json())

    .then(data => {

        console.log(data);

        location.reload();
    });

});


// =====================================
// LOAD EXPENSES
// =====================================

function loadExpenses() {

    fetch("/expenses")

        .then(response => response.json())

        .then(data => {

            const expenses =
                document.getElementById("expenses");

            expenses.innerHTML = "";


            if (data.length === 0) {

                expenses.innerHTML =
                    "<p>No expenses recorded yet.</p>";

                return;
            }


            data.forEach(expense => {

                expenses.innerHTML += `

                    <div class="expense-card">

                        <p>
                            <strong>ID:</strong>
                            ${expense.id}
                        </p>

                        <p>
                            <strong>Amount:</strong>
                            ₹${expense.amount}
                        </p>

                        <p>
                            <strong>Category:</strong>
                            ${expense.category}
                        </p>

                        <p>
                            <strong>Date:</strong>
                            ${expense.date}
                        </p>

                        <p>
                            <strong>Description:</strong>
                            ${expense.description}
                        </p>


                        <button
                            class="edit-btn"
                            onclick="editExpense(${expense.id})">

                            Edit

                        </button>


                        <button
                            class="delete-btn"
                            onclick="deleteExpense(${expense.id})">

                            Delete

                        </button>

                    </div>
                `;
            });

        });
}


// =====================================
// DELETE
// =====================================

function deleteExpense(id) {

    const confirmDelete =
        confirm("Are you sure you want to delete this expense?");


    if (!confirmDelete) {
        return;
    }


    fetch(`/expenses/delete/${id}`, {

        method: "DELETE"

    })

    .then(response => response.json())

    .then(data => {

        console.log(data);

        loadExpenses();

        loadSummary();

    });
}


// =====================================
// EDIT
// =====================================

function editExpense(id) {

    fetch("/expenses")

        .then(response => response.json())

        .then(data => {

            const expense =
                data.find(item => item.id === id);


            if (!expense) {
                return;
            }


            editingId = id;


            document.getElementById("amount").value =
                expense.amount;

            document.getElementById("category").value =
                expense.category;

            document.getElementById("date").value =
                expense.date;

            document.getElementById("description").value =
                expense.description;


            addBtn.textContent =
                "Update Expense";


            document.getElementById("formTitle").textContent =
                "Update Expense";


            document.querySelector(".form-section")
                .scrollIntoView({
                    behavior: "smooth"
                });

        });
}


// =====================================
// SUMMARY + CHARTS
// =====================================

function loadSummary() {

    fetch("/expenses/summary")

        .then(response => response.json())

        .then(data => {


            // Total expenses

            document.getElementById("totalExpenses")
                .textContent = data.total_expenses;


            // Total amount

            document.getElementById("totalAmount")
                .textContent =
                "₹" + data.total_amount.toFixed(2);


            // =================================
            // CATEGORY CHART
            // =================================

            const categoryLabels =
                Object.keys(data.by_category);

            const categoryValues =
                Object.values(data.by_category);


            const categoryCanvas =
                document.getElementById("categoryChart");


            if (categoryChart) {
                categoryChart.destroy();
            }


            categoryChart = new Chart(
                categoryCanvas,
                {
                    type: "doughnut",

                    data: {

                        labels: categoryLabels,

                        datasets: [{
                            data: categoryValues
                        }]
                    },

                    options: {

                        responsive: true,

                        plugins: {

                            legend: {
                                position: "bottom"
                            }

                        }
                    }
                }
            );


            // =================================
            // MONTHLY CHART
            // =================================

            const monthlyLabels =
                Object.keys(data.by_month);

            const monthlyValues =
                Object.values(data.by_month);


            const monthlyCanvas =
                document.getElementById("monthlyChart");


            if (monthlyChart) {
                monthlyChart.destroy();
            }


            monthlyChart = new Chart(
                monthlyCanvas,
                {
                    type: "bar",

                    data: {

                        labels: monthlyLabels,

                        datasets: [{

                            label: "Spending (₹)",

                            data: monthlyValues

                        }]
                    },

                    options: {

                        responsive: true,

                        scales: {

                            y: {
                                beginAtZero: true
                            }

                        },

                        plugins: {

                            legend: {
                                display: false
                            }

                        }
                    }
                }
            );

        });
}




loadExpenses();

loadSummary();
