import time

# --- Protection brute force ---

FAILED_ATTEMPTS = {}  # {username: {"count": int, "last_fail": timestamp}}
MAX_ATTEMPTS = 3
LOCK_TIME = 60  # 60 secondes


def is_locked(username: str) -> bool:
    """Retourne True si le compte est temporairement bloqué."""
    info = FAILED_ATTEMPTS.get(username)
    if not info:
        return False

    if info["count"] >= MAX_ATTEMPTS:
        elapsed = time.time() - info["last_fail"]
        if elapsed < LOCK_TIME:
            return True
        else:
            # Le lock est expiré, on réinitialise
            FAILED_ATTEMPTS.pop(username, None)
            return False

    return False


def record_failed_attempt(username: str):
    """Enregistre une tentative échouée pour ce username."""
    info = FAILED_ATTEMPTS.get(username, {"count": 0, "last_fail": 0})
    info["count"] += 1
    info["last_fail"] = time.time()
    FAILED_ATTEMPTS[username] = info


# --- Gestion des utilisateurs (exemple simple CSV / BDD) ---
# Adapte ces fonctions à ton implémentation existante
from data_manager import verify_credentials, create_user, get_role  # par ex. [file:119]


def login_user(username: str, password: str):
    """
    Tente de connecter l'utilisateur.
    Retourne (success: bool, role: str | None, message: str).
    """
    username = username.strip()
    if not username or not password:
        return False, None, "Nom d'utilisateur et mot de passe obligatoires."

    # Ici tu appelles ta logique réelle de vérification (BDD / CSV)
    if verify_credentials(username, password):
        # Succès -> on reset le compteur
        FAILED_ATTEMPTS.pop(username, None)
        role = get_role(username) or "client"
        return True, role, "Connexion réussie."
    else:
        # Mauvais mot de passe
        record_failed_attempt(username)
        info = FAILED_ATTEMPTS.get(username, {"count": 0, "last_fail": 0})
        if info["count"] >= MAX_ATTEMPTS:
            return False, None, "Compte bloqué pendant 1 minute après plusieurs échecs."
        remaining = max(0, MAX_ATTEMPTS - info["count"])
        return False, None, f"Identifiants incorrects. Tentatives restantes : {remaining}."


def register_user(username: str, password: str, role: str = "client", email: str = ""):
    """
    Crée un utilisateur.
    Retourne (success: bool, message: str).
    """
    username = username.strip()
    email = email.strip()

    if not username or not password:
        return False, "Nom d'utilisateur et mot de passe obligatoires."

    # utilise ta logique réelle pour créer l'utilisateur
    ok, msg = create_user(username, password, role, email)
    return ok, msg
