from flask import Flask, request, render_template, send_file
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# Sample customer data
customers = {
    1: {"Name": "John Doe", "Email": "john@example.com", "Phone": "1234567890",
        "Task": "Install Software", "User": "Admin", "Status": "Pending", "Date": "2024-12-01"},
    2: {"Name": "Jane Smith", "Email": "jane@example.com", "Phone": "0987654321",
        "Task": "Update Database", "User": "User1", "Status": "Completed", "Date": "2024-11-30"},
    3: {"Name": "Alice Brown", "Email": "alice@example.com", "Phone": "1122334455",
        "Task": "Configure Network", "User": "User2", "Status": "In Progress", "Date": "2024-12-02"}
}

@app.route("/", methods=["GET"])
def index():
    # Get status filter from query parameters, default to "Pending"
    status_filter = request.args.get("status", "Pending")
    
    # Filter customers based on status
    if status_filter == "All":
        filtered_customers = customers
    else:
        filtered_customers = {k: v for k, v in customers.items() if v["Status"] == status_filter}

    return render_template("index.html", status_filter=status_filter, customers=filtered_customers)

@app.route("/add", methods=["POST"])
def add_customer():
    global customers
    new_id = max(customers.keys()) + 1 if customers else 1
    customers[new_id] = {
        "Name": request.form["name"],
        "Email": request.form["email"],
        "Phone": request.form["phone"],
        "Task": request.form["task"],
        "User": request.form["user"],  # Add the user field here
        "Status": request.form["status"],
        "Date": "2024-12-02"  # Example: Automatically adding today's date
    }
    return index()

@app.route("/edit/<int:customer_id>", methods=["GET", "POST"])
def edit_customer(customer_id):
    if request.method == "POST":
        customers[customer_id] = {
            "Name": request.form["name"],
            "Email": request.form["email"],
            "Phone": request.form["phone"],
            "Task": request.form["task"],
            "User": request.form["user"],  # Add the user field here
            "Status": request.form["status"],
            "Date": customers[customer_id]["Date"]  # Keep original date
        }
        return index()
    return render_template("edit.html", customer_id=customer_id, customer=customers[customer_id])

@app.route("/delete/<int:customer_id>", methods=["POST"])
def delete_customer(customer_id):
    customers.pop(customer_id, None)
    return index()

# New route to export data to Excel
@app.route("/export", methods=["GET"])
def export_to_excel():
    # Prepare the data for export (excluding the 'Actions' column)
    data = [
        {
            "Name": customer["Name"],
            "Email": customer["Email"],
            "Phone": customer["Phone"],
            "Task": customer["Task"],
            "User": customer["User"],
            "Status": customer["Status"],
            "Date": customer["Date"]
        }
        for customer in customers.values()
    ]
    
    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    
    # Convert the DataFrame to Excel in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Customers")
    output.seek(0)  # Rewind the file pointer
    
    # Send the Excel file as an attachment
    return send_file(output, as_attachment=True, download_name="customers.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    app.run(debug=True)
