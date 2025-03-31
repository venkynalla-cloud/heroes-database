import os
import pymysql
from flask import Flask, jsonify
from flask_cors import CORS
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

app = Flask(__name__)
CORS(app)

# Get database credentials from Azure Key Vault
key_vault_uri = os.getenv("AZURE_KEY_VAULT_URI")
credential = ManagedIdentityCredential()
secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

server = secret_client.get_secret("MYSQL-DB-SERVER").value
database = secret_client.get_secret("MYSQL-DB-NAME").value
username = secret_client.get_secret("MYSQL-DB-USER").value
password = secret_client.get_secret("MYSQL-DB-PASSWORD").value

# Function to create a database connection
def get_db_connection():
    return pymysql.connect(
        host=server,
        user=username,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/api/employees", methods=["GET"])
def fetch_data():
    """Fetches employee data."""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, first_name, last_name, email FROM heroes LIMIT 10")
            data = cursor.fetchall()
        connection.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
