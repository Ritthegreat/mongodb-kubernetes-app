import os
from flask import Flask, request, render_template_string, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

app = Flask(__name__)

# HTML template with Customer Management operations
customer_html = """
<!doctype html>
<html>
<head>
    <title>Customer Management</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input, select { width: 100%; padding: 8px; box-sizing: border-box; }
        button { padding: 10px 15px; background-color: #4CAF50; color: white; border: none; cursor: pointer; margin-right: 10px; }
        .btn-danger { background-color: #f44336; }
        .btn-warning { background-color: #ff9800; }
        .result { margin-top: 20px; padding: 10px; background-color: #f5f5f5; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .customer-actions { display: flex; }
        .customer-actions form { margin-right: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Customer Management</h1>
        
        <h2>{{ form_title }}</h2>
        <form method="post" action="{{ form_action }}">
            {% if customer_id %}
            <input type="hidden" name="customer_id" value="{{ customer_id }}">
            {% endif %}
            
            <div class="form-group">
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" value="{{ customer.name if customer else '' }}" required>
            </div>
            
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" value="{{ customer.email if customer else '' }}" required>
            </div>
            
            <div class="form-group">
                <label for="phone">Phone Number:</label>
                <input type="tel" id="phone" name="phone" value="{{ customer.phone if customer else '' }}" required>
            </div>
            
            <div class="form-group">
                <label for="age">Age:</label>
                <input type="number" id="age" name="age" min="1" max="120" value="{{ customer.age if customer else '' }}" required>
            </div>
            
            <div class="form-group">
                <button type="submit">{{ submit_button }}</button>
                {% if customer_id %}
                <a href="/" style="text-decoration: none;"><button type="button">Cancel</button></a>
                {% endif %}
            </div>
        </form>
        
        {% if message %}
        <div class="result" {% if error %}style="background-color: #ffdddd;"{% endif %}>
            <h3>{{ message_title }}:</h3>
            <p>{{ message }}</p>
        </div>
        {% endif %}
        
        {% if customers %}
        <h2>Customer List</h2>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Age</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for customer in customers %}
                <tr>
                    <td>{{ customer.name }}</td>
                    <td>{{ customer.email }}</td>
                    <td>{{ customer.phone }}</td>
                    <td>{{ customer.age }}</td>
                    <td class="customer-actions">
                        <form method="get" action="/edit">
                            <input type="hidden" name="id" value="{{ customer._id }}">
                            <button type="submit" class="btn-warning">Edit</button>
                        </form>
                        <form method="post" action="/delete" onsubmit="return confirm('Are you sure you want to delete this customer?');">
                            <input type="hidden" name="id" value="{{ customer._id }}">
                            <button type="submit" class="btn-danger">Delete</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
    </div>
</body>
</html>
"""

def get_mongo_connection():
    # Get MongoDB connection details from environment variables or use defaults
    mongo_host = os.environ.get('MONGO_HOST', 'mongodb-service')
    mongo_port = int(os.environ.get('MONGO_PORT', '27017'))
    mongo_user = os.environ.get('MONGO_USER', '')
    mongo_password = os.environ.get('MONGO_PASSWORD', '')
    mongo_db = os.environ.get('MONGO_DB', 'test')
    
    # Build connection string
    if mongo_user and mongo_password:
        connection_string = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}"
    else:
        connection_string = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db}"
    
    # Connect to MongoDB
    client = MongoClient(connection_string)
    return client, mongo_db

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    message_title = None
    error = False
    
    # Connect to MongoDB
    client, db_name = get_mongo_connection()
    db = client[db_name]
    collection = db['customers']
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            age = int(request.form['age'])
            
            # Create customer document
            customer_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'age': age
            }
            
            # Insert the customer
            result = collection.insert_one(customer_data)
            message = f"Customer added successfully with ID: {result.inserted_id}"
            message_title = "Success"
            
        except Exception as e:
            message = str(e)
            message_title = "Error"
            error = True
    
    # Get all customers
    customers = list(collection.find())
    
    # Convert ObjectId to string for template rendering
    for customer in customers:
        customer['_id'] = str(customer['_id'])
    
    client.close()
    
    return render_template_string(
        customer_html,
        form_title="Add New Customer",
        form_action="/",
        submit_button="Add Customer",
        message=message,
        message_title=message_title,
        error=error,
        customers=customers,
        customer=None,
        customer_id=None
    )

@app.route('/edit', methods=['GET'])
def edit():
    customer_id = request.args.get('id')
    
    # Connect to MongoDB
    client, db_name = get_mongo_connection()
    db = client[db_name]
    collection = db['customers']
    
    # Find the customer
    customer = collection.find_one({'_id': ObjectId(customer_id)})
    
    client.close()
    
    # Get all customers for the list
    client, db_name = get_mongo_connection()
    db = client[db_name]
    collection = db['customers']
    customers = list(collection.find())
    
    # Convert ObjectId to string for template rendering
    for c in customers:
        c['_id'] = str(c['_id'])
    
    client.close()
    
    return render_template_string(
        customer_html,
        form_title="Edit Customer",
        form_action="/update",
        submit_button="Update Customer",
        message=None,
        message_title=None,
        error=False,
        customers=customers,
        customer=customer,
        customer_id=str(customer['_id'])
    )

@app.route('/update', methods=['POST'])
def update():
    customer_id = request.form['customer_id']
    
    try:
        # Get form data
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        age = int(request.form['age'])
        
        # Create customer document
        customer_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'age': age
        }
        
        # Connect to MongoDB
        client, db_name = get_mongo_connection()
        db = client[db_name]
        collection = db['customers']
        
        # Update the customer
        collection.update_one(
            {'_id': ObjectId(customer_id)},
            {'$set': customer_data}
        )
        
        client.close()
        
        # Redirect to home page
        return redirect('/')
        
    except Exception as e:
        # Connect to MongoDB
        client, db_name = get_mongo_connection()
        db = client[db_name]
        collection = db['customers']
        
        # Get all customers for the list
        customers = list(collection.find())
        
        # Convert ObjectId to string for template rendering
        for c in customers:
            c['_id'] = str(c['_id'])
        
        client.close()
        
        return render_template_string(
            customer_html,
            form_title="Edit Customer",
            form_action="/update",
            submit_button="Update Customer",
            message=str(e),
            message_title="Error",
            error=True,
            customers=customers,
            customer=request.form,
            customer_id=customer_id
        )

@app.route('/delete', methods=['POST'])
def delete():
    customer_id = request.form['id']
    
    # Connect to MongoDB
    client, db_name = get_mongo_connection()
    db = client[db_name]
    collection = db['customers']
    
    # Delete the customer
    collection.delete_one({'_id': ObjectId(customer_id)})
    
    client.close()
    
    # Redirect to home page
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 