from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import os
import uuid

app = FastAPI(title="InvestBuddy API")

# CORS - autorise le frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# Configuration base de données
# ===========================
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "investbuddy"),
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# ===========================
# Schémas Pydantic
# ===========================
class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    nom: str
    prenom: str
    email: str
    password: str


# ===========================
# Endpoint : GET /
# ===========================
@app.get("/")
def root():
    return {"message": "InvestBuddy API is running"}


# ===========================
# Endpoint : POST /login
# ===========================
@app.post("/login")
def login(data: LoginRequest):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT nom, prenom, email, mot_de_passe FROM User WHERE email = %s",
            (data.email,),
        )
        user = cursor.fetchone()
        cursor.close()
        db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {str(e)}")

    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    # Vérification du mot de passe (stocké en clair pour la démo)
    if user["mot_de_passe"] != data.password:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token = str(uuid.uuid4())

    return {
        "email": user["email"],
        "nom": user["nom"],
        "prenom": user["prenom"],
        "token": token,
    }


# ===========================
# Endpoint : POST /register
# ===========================
@app.post("/register", status_code=201)
def register(data: RegisterRequest):
    # Validation basique
    if not data.nom.strip():
        raise HTTPException(status_code=422, detail="Le nom est requis.")
    if not data.prenom.strip():
        raise HTTPException(status_code=422, detail="Le prénom est requis.")
    if not data.email.strip():
        raise HTTPException(status_code=422, detail="L'email est requis.")
    if len(data.password) < 6:
        raise HTTPException(status_code=422, detail="Le mot de passe doit contenir au moins 6 caractères.")

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Vérifier si l'email est déjà utilisé
        cursor.execute("SELECT email FROM User WHERE email = %s", (data.email,))
        existing = cursor.fetchone()

        if existing:
            cursor.close()
            db.close()
            raise HTTPException(status_code=409, detail="Cet email est déjà utilisé.")

        # Insérer le nouvel utilisateur
        cursor.execute(
            "INSERT INTO User (nom, prenom, email, mot_de_passe) VALUES (%s, %s, %s, %s)",
            (data.nom.strip(), data.prenom.strip(), data.email.strip(), data.password),
        )
        db.commit()
        cursor.close()
        db.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {str(e)}")

    return {
        "message": "Compte créé avec succès.",
        "email": data.email.strip(),
        "nom": data.nom.strip(),
        "prenom": data.prenom.strip(),
    }


# ===========================
# Lancement du serveur
# ===========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8080, reload=True)
