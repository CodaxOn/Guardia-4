import mysql.connector
import hashlib, os, requests, csv, datetime, random
from data_manager import DataManager

# --- INITIALISATION ---
dm = DataManager()

# VARIABLES REQUISES PAR MAIN.PY
FILE_PRODS = 'produit.csv'
FILE_LOGS = 'logs.csv'
FILE_USERS = 'users.csv'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '', 
    'database': 'projet4'
}

# Chemin absolu vers le fichier users géré par DataManager
FILE_USERS_PATH = os.path.join(dm.path, dm.files['users'][0])

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    """Initialise la base MySQL et force la création des CSV via DataManager"""
    dm.__init__() 
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], 
            user=DB_CONFIG['user'], 
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user VARCHAR(50),
                action TEXT
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur MySQL: {e}")

# --- SÉCURITÉ ---

def hash_password(password, salt):
    """Hachage SHA-256 avec grain de sel"""
    return hashlib.sha256((password + salt).encode()).hexdigest()

def check_pwned_password(password):
    """Vérifie si le mot de passe est compromis via API"""
    try:
        sha1_pwd = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        res = requests.get(f"https://api.pwnedpasswords.com/range/{sha1_pwd[:5]}", timeout=5)
        return any(line.split(':')[0] == sha1_pwd[5:] for line in res.text.splitlines())
    except: return False

# --- GESTION DES UTILISATEURS ---

def register_user(u, m, p):
    """Inscription avec stockage SHA-256 dans le CSV géré par DataManager"""
    # 1. Nettoyage strict
    u_new = u.strip().lower()
    m_new = m.strip().lower()
    p_clean = p.strip()
    
    users = dm.get_data('users')
    
    # 2. Vérification d'existence
    if any(user.get('username') == u_new for user in users):
        return False, "Pseudo déjà utilisé."

    # 3. Préparation des données de sécurité
    salt = os.urandom(16).hex()
    pwd_hash = hash_password(p_clean, salt)

    try:
        # 4. Écriture sécurisée
        # newline='' est CRUCIAL pour éviter que les lignes se collent ou sautent une ligne
        with open(FILE_USERS_PATH, 'a', newline='', encoding='utf-8') as f:
            # On récupère les colonnes définies dans DataManager
            fieldnames = dm.files['users'][1]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Si le fichier est vide, on écrit l'en-tête (sécurité supplémentaire)
            if os.path.getsize(FILE_USERS_PATH) == 0:
                writer.writeheader()

            writer.writerow({
                'id': len(users) + 1,
                'username': u_new,
                'mail': m_new,
                'salt': salt,
                'password_hash': pwd_hash,
                'role': 'client'
            })
        return True, "Inscription réussie !"
    except Exception as e:
        return False, f"Erreur d'écriture : {e}"

def login_user(u, p):
    """Vérifie les identifiants et retourne le mail"""
    u_target = u.strip().lower()
    p_target = p.strip()
    users = dm.get_data('users')
    
    for row in users:
        # Comparaison insensible à la casse et nettoyage des espaces
        if str(row.get('username', '')).strip().lower() == u_target:
            salt = row.get('salt')
            stored_hash = row.get('password_hash')
            
            if salt and stored_hash:
                if hash_password(p_target, salt) == stored_hash:
                    return True, row.get('mail')
    return False, None

# --- COMPATIBILITÉ MAINWINDOW ---

def add_log(user, action):
    """Ajoute un log dans le CSV local et dans MySQL"""
    dm.log(user, action) 
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (user, action) VALUES (%s, %s)", (user, action))
        conn.commit()
        cursor.close()
        conn.close()
    except: pass

def safe_read(key):
    """Récupère les données demandées par MainWindow"""
    try:
        # 1. Logs : Priorité MySQL
        if 'logs' in key:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT timestamp, user, action FROM logs ORDER BY timestamp DESC")
                data = cursor.fetchall()
                for d in data: d['timestamp'] = str(d['timestamp'])
                cursor.close()
                conn.close()
                return data
            except:
                return dm.get_data('logs')
        
        # 2. Produits
        if 'produit' in key:
            return dm.get_data('products')
            
        # 3. Utilisateurs
        if 'users' in key:
            return dm.get_data('users')

        # 4. Commandes ou autres fichiers
        path = os.path.join(dm.path, key)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return list(csv.DictReader(f))
    except Exception as e:
        print(f"Erreur safe_read ({key}): {e}")
        
    return []