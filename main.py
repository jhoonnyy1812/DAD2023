import boto3
import psycopg2
from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

# AWS RDS configuration
RDS_HOST = os.getenv("RDS_HOST")
RDS_DB_NAME = os.getenv("RDS_DB_NAME")
RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

LAMBDA_URL = os.getenv("LAMBDA_URL")


# Connect to RDS PostgreSQL
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname=RDS_DB_NAME,
            user=RDS_USER,
            password=RDS_PASSWORD,
            host=RDS_HOST,
            port="5432",
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def s3():
    return boto3.client(
        service_name="s3",
        region_name="us-east-2",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


@app.route("/get_document", methods=["GET"])
def download_image():
    try:
        document = request.args.get("document")
        s3().download_file(
            "mybycketdad", "{0}.jpeg".format(document), "./downloaded_image.jpeg"
        )
        return jsonify("Arquivo baixado.")
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/end_user", methods=["POST"])
def end_user():
    try:
        document = request.args.get("document")
        lambda_response = requests.get(LAMBDA_URL + "?document={0}".format(document))
        if lambda_response.status_code == 200:
            conn = connect_to_db()
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM users WHERE document = %s", (document,))
                    conn.commit()
                    cursor.close()
                    conn.close()
            return jsonify("Usuário finalizado.")
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/create_user", methods=["POST"])
def create_user():
    try:
        content = request.get_json()
        name = content.get("name")
        document = content.get("document")
        print(content)
        s3().upload_file(
            "{0}.jpeg".format(document), "mybycketdad", "{0}.jpeg".format(document)
        )
        conn = connect_to_db()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (name, document) VALUES (%s, %s)",
                    (name, document),
                )
                conn.commit()
                cursor.close()
                conn.close()
            return jsonify("Usuário criado.")
    except Exception as e:
        return jsonify({"error": str(e)})


# API endpoint to retrieve user data
@app.route("/users", methods=["GET"])
def get_users():
    try:
        conn = connect_to_db()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                users = cursor.fetchall()
                cursor.close()
                conn.close()
                return jsonify(users)
        else:
            return jsonify({"error": "Database connection error"})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run("0.0.0.0")
