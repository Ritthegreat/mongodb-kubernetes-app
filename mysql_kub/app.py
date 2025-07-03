from flask import Flask, request, render_template_string
import mysql.connector
import os

app = Flask(__name__)

# HTML template for the form
form_html = """
<!doctype html>
<title>Submit Data</title>
<h2>Enter your details</h2>
<form method=post>
  Name: <input type=text name=name required><br>
  Email: <input type=email name=email required><br>
  <input type=submit value=Submit>
</form>
{% if message %}
  <p>{{ message }}</p>
{% endif %}
"""

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'mysql123'),
        database=os.environ.get('MYSQL_DATABASE', 'yourdbname')
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255))"
            )
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (%s, %s)", (name, email)
            )
            conn.commit()
            message = 'Data submitted successfully!'
        except Exception as e:
            message = f'Error: {e}'
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    return render_template_string(form_html, message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 