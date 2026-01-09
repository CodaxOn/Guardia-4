# api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime

import database  # ton module existant pour la BDD

SECRET_KEY = "change-me-super-secret"  # à mettre en variable d'environnement en vrai

app = Flask(__name__)
CORS(app)


# ===================== JWT ======================

def create_token(username, role):
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def require_auth(f):
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token manquant"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except Exception:
            return jsonify({"error": "Token invalide ou expiré"}), 401
        request.user = payload  # username + role
        return f(*args, **kwargs)

    return wrapper


# ===================== HELPERS BDD ======================

def get_user_role(username: str) -> str:
    """
    Récupère le rôle de l'utilisateur depuis la BDD.
    À adapter selon ta table users.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT role FROM users WHERE username = %s", (username,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return row["role"]
    return "client"


def get_products_paginated(page: int, per_page: int):
    """
    Renvoie (liste_produits, total).
    Chaque produit est un dict JSON‑serializable.
    """
    offset = (page - 1) * per_page
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS c FROM products")
    total = cursor.fetchone()["c"]
    cursor.execute(
        "SELECT id, name, price, stock FROM products ORDER BY id LIMIT %s OFFSET %s",
        (per_page, offset),
    )
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return items, total


def get_product_by_id(product_id: int):
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name, price, stock FROM products WHERE id = %s", (product_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def create_product_from_api(data: dict):
    name = (data.get("name") or "").strip()
    price = data.get("price")
    stock = data.get("stock", 0)

    if not name or price is None:
        return False, "Champs name et price obligatoires."

    try:
        price = float(price)
        stock = int(stock)
    except ValueError:
        return False, "price doit être un nombre, stock un entier."

    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
        (name, price, stock),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    product = get_product_by_id(new_id)
    return True, product


def update_product_from_api(product_id: int, data: dict):
    product = get_product_by_id(product_id)
    if not product:
        return False, "Produit introuvable."

    name = (data.get("name") or product["name"]).strip()
    price = data.get("price", product["price"])
    stock = data.get("stock", product["stock"])

    try:
        price = float(price)
        stock = int(stock)
    except ValueError:
        return False, "price doit être un nombre, stock un entier."

    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET name = %s, price = %s, stock = %s WHERE id = %s",
        (name, price, stock, product_id),
    )
    conn.commit()
    cursor.close()
    conn.close()

    updated = get_product_by_id(product_id)
    return True, updated


def delete_product(product_id: int):
    product = get_product_by_id(product_id)
    if not product:
        return False, "Produit introuvable."

    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return True, "Produit supprimé."


# ===================== ENDPOINTS AUTH ======================

@app.post("/api/auth/login")
def api_login():
    """
    POST /api/auth/login
    body JSON : { "username": "...", "password": "..." }
    """
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    ok, mail = database.login_user(username, password)
    if not ok:
        return jsonify({"error": "Identifiants invalides"}), 401

    role = get_user_role(username)
    token = create_token(username, role)
    return jsonify({"token": token, "role": role})


# ===================== ENDPOINTS PRODUITS ======================

@app.get("/api/products")
def list_products():
    """
    GET /api/products?page=1&per_page=20
    Liste paginée des produits.
    """
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except ValueError:
        return jsonify({"error": "Paramètres page/per_page invalides"}), 400

    items, total = get_products_paginated(page, per_page)
    return jsonify({"items": items, "total": total, "page": page, "per_page": per_page})


@app.get("/api/products/<int:product_id>")
def get_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({"error": "Produit introuvable"}), 404
    return jsonify(product)


@app.post("/api/products")
@require_auth
def create_product():
    """
    Création de produit (admin seulement).
    """
    if request.user.get("role") != "admin":
        return jsonify({"error": "Admin requis"}), 403

    data = request.get_json() or {}
    ok, result = create_product_from_api(data)
    if not ok:
        return jsonify({"error": result}), 400
    return jsonify(result), 201


@app.put("/api/products/<int:product_id>")
@require_auth
def update_product(product_id):
    if request.user.get("role") != "admin":
        return jsonify({"error": "Admin requis"}), 403

    data = request.get_json() or {}
    ok, result = update_product_from_api(product_id, data)
    if not ok:
        return jsonify({"error": result}), 400
    return jsonify(result)


@app.delete("/api/products/<int:product_id>")
@require_auth
def delete_product_endpoint(product_id):
    if request.user.get("role") != "admin":
        return jsonify({"error": "Admin requis"}), 403

    ok, msg = delete_product(product_id)
    if not ok:
        return jsonify({"error": msg}), 400
    return jsonify({"message": msg})


# ===================== MAIN ======================

if __name__ == "__main__":
    app.run(debug=True)
