import sqlite3
from fastapi import FastAPI, HTTPException, status, Request, Response
# from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
# from passlib.context import CryptContext
# from fastapi.encoders import jsonable_encoder
from starlette.middleware.sessions import SessionMiddleware
import jwt
from typing import Optional


SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except :
        raise credentials_exception
    return token_data

class Livre(BaseModel):
    title: str
    pitch: str
    author_id: int  
    date_public: str
    emprunteur_id: int

class Utilisateur(BaseModel):
    id: int
    nom: str
    email: str
    
class Auteur(BaseModel):
    id: int
    nom_auteur: str
    
class LivreAjout(BaseModel):
    title: str
    content: str
    author: str
    date: str

class UtilisateurAjout(BaseModel):
    nom: str
    email: str

class Emprunt(BaseModel):
    utilisateur_id: int
    livre_id: int
    
class TokenData(BaseModel):
    username: Optional[str] = None
    


app = FastAPI()

app.add_middleware(SessionMiddleware)


@app.middleware("http")
async def verify_token_middleware(request: Request, call_next):
    protected_routes = [
        "/utilisateur/emprunts/",
        "/livres/siecle/",
        "/livres/ajouter",
        "/utilisateur/ajouter"
    ]
    for route in protected_routes:
        if request.url.path.startswith(route):
            token = request.headers.get('Authorization')
            if token is None or not token.startswith("Bearer "):
                return Response(content="Invalid token", status_code=400)
            token = token[len("Bearer "):]
            try:
                verify_token(token)
            except HTTPException:
                return Response(content="Invalid token", status_code=400)
            break
    response = await call_next(request)
    return response

@app.get("/utilisateurs", response_model=Utilisateur)
async def get_utilisateurs():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM utilisateurs")
        return cur.fetchall()

@app.get("/livres", response_model=Livre)
async def get_livres():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM livres")
        return cur.fetchall()

@app.get("/auteurs", response_model=Auteur)
async def get_auteurs():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM auteurs")
        return cur.fetchall()

@app.get("/utilisateur/{utilisateur}", response_model=Utilisateur)
async def get_utilisateur(utilisateur: str):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if utilisateur.isdigit():
            cur.execute("SELECT * FROM utilisateurs WHERE id = ?", (int(utilisateur),))
        else:
            cur.execute("SELECT * FROM utilisateurs WHERE nom = ?", (utilisateur,))
        result = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        if len(result) == 1:
            return result[0]
        elif len(result) > 1:
            raise HTTPException(status_code=400, detail="Multiple users found with the same name")
        else:
            raise HTTPException(status_code=404, detail="User not found")

@app.get("/utilisateur/emprunts/{utilisateur}")
async def get_emprunts(utilisateur: str):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if utilisateur.isdigit():
            cur.execute("SELECT * FROM utilisateurs WHERE id = ?", (int(utilisateur),))
        else:
            cur.execute("SELECT * FROM utilisateurs WHERE nom = ?", (utilisateur,))
        result = cur.fetchall()
        if len(result) == 1:
            utilisateur_id = result[0][0]
            cur.execute("""
                SELECT livres.titre 
                FROM livres 
                WHERE livres.emprunteur_id = ?
            """, (utilisateur_id,))
            return cur.fetchall()
        elif len(result) > 1:
            raise HTTPException(status_code=400, detail="Multiple users found with the same name")
        else:
            raise HTTPException(status_code=404, detail="User not found")

@app.get("/livres/siecle/{siecle}", response_model=Livre)
async def get_livres_par_siecle(siecle: int):
    debut_annee = (siecle - 1) * 100 + 1
    fin_annee = siecle * 100
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM livres 
            WHERE date_public BETWEEN ? AND ?
        """, (f"01-01-{debut_annee}", f"31-12-{fin_annee}"))
        return cur.fetchall()

@app.post("/livres/ajouter", response_model=LivreAjout)
async def ajouter_livre(request: Request):
    livre = await request.json()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO auteurs (nom_auteur) VALUES (?)", (livre['author'],))
        cur.execute("SELECT id FROM auteurs WHERE nom_auteur = ?", (livre['author'],))
        auteur_id = cur.fetchone()[0]
        cur.execute("""
            INSERT OR IGNORE INTO livres (titre, pitch, auteur_id, date_public) 
            VALUES (?, ?, ?, ?)
        """, (livre['title'], livre['content'], auteur_id, livre['date']))
        conn.commit()
        return {"message": "Livre ajouté avec succès"}

@app.post("/utilisateur/ajouter", response_model=UtilisateurAjout)
async def ajouter_utilisateur(request: Request):
    utilisateur = await request.json()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO utilisateurs (nom, email) VALUES (?, ?)", (utilisateur['nom'], utilisateur['email']))
        conn.commit()
        return {"message": "Utilisateur ajouté avec succès"}

@app.delete("/utilisateur/{utilisateur}")
async def supprimer_utilisateur(utilisateur: str):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if utilisateur.isdigit():
            cur.execute("DELETE FROM utilisateurs WHERE id = ?", (int(utilisateur),))
        else:
            cur.execute("DELETE FROM utilisateurs WHERE nom = ?", (utilisateur,))
        conn.commit()
        return {"message": "Utilisateur supprimé avec succès"}

@app.put("/utilisateur/{utilisateur_id}/emprunter/{livre_id}")
async def emprunter_livre(utilisateur_id: int, livre_id: int):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("UPDATE livres SET emprunteur_id = ? WHERE id = ?", (utilisateur_id, livre_id))
        conn.commit()
        return {"message": "Livre emprunté avec succès"}

@app.put("/utilisateur/{utilisateur_id}/rendre/{livre_id}")
async def rendre_livre(utilisateur_id: int, livre_id: int):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("UPDATE livres SET emprunteur_id = 0 WHERE id = ? AND emprunteur_id = ?", (livre_id, utilisateur_id))
        conn.commit()
        return {"message": "Livre rendu avec succès"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)