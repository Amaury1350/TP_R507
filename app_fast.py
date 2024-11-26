import sqlite3
import pathlib
from fastapi import FastAPI, Body, HTTPException
from typing import Union
import uvicorn

app = FastAPI()

def get_db_cursor():
    path_to_db = pathlib.Path(__file__).parent.absolute() / "data" / "database.db"
    conn = sqlite3.connect(path_to_db)
    conn.row_factory = sqlite3.Row
    return conn.cursor(), conn

@app.get("/utilisateurs")
def get_utilisateurs():
    cur, conn = get_db_cursor()
    cur.execute("SELECT * FROM utilisateurs")
    rows = cur.fetchall()
    return [dict(row) for row in rows]

@app.get("/livres")
def get_livres():
    cur, conn = get_db_cursor()
    cur.execute("SELECT * FROM livres")
    rows = cur.fetchall()
    return [dict(row) for row in rows]

@app.get("/auteurs")
def get_auteurs():
    cur, conn = get_db_cursor()
    cur.execute("SELECT * FROM auteurs")
    rows = cur.fetchall()
    return [dict(row) for row in rows]

@app.get("/utilisateur/{utilisateur}")
def get_utilisateur(utilisateur: Union[int, str]):
    cur, conn = get_db_cursor()
    if isinstance(utilisateur, int):
        cur.execute("SELECT * FROM utilisateurs WHERE id = ?", (utilisateur,))
    else:
        cur.execute("SELECT * FROM utilisateurs WHERE nom = ?", (utilisateur,))
    result = cur.fetchall()
    if len(result) == 1:
        return dict(result[0])
    elif len(result) > 1:
        raise HTTPException(status_code=400, detail="Multiple users found with the same name")
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/utilisateur/emprunts/{utilisateur}")
def get_emprunts(utilisateur: Union[int, str]):
    cur, conn = get_db_cursor()
    try:
        if isinstance(utilisateur, int):
            cur.execute("SELECT * FROM utilisateurs WHERE id = ?", (utilisateur,))
        else:
            cur.execute("SELECT * FROM utilisateurs WHERE nom = ?", (utilisateur,))
        result = cur.fetchall()
        if len(result) == 1:
            utilisateur_id = result[0]['id']
            cur.execute("""
                SELECT livres.titre 
                FROM livres 
                WHERE emprunteur_id = ?
            """, (utilisateur_id,))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        elif len(result) > 1:
            raise HTTPException(status_code=400, detail="Multiple users found with the same name")
        else:
            raise HTTPException(status_code=404, detail="User not found")
    finally:
        conn.close()

@app.get("/livres/siecle/{numero}")
def get_livres_siecle(numero: int):
    cur, conn = get_db_cursor()
    start_date = f"{(numero-1)*100 + 1}-01-01"
    end_date = f"{numero*100}-12-31"
    cur.execute("SELECT * FROM livres WHERE date_public BETWEEN ? AND ?", (start_date, end_date))
    rows = cur.fetchall()
    return [dict(row) for row in rows]

@app.post("/livres/ajouter")
def ajouter_livre(livre: dict = Body(...)):
    cur, conn = get_db_cursor()
    cur.execute("INSERT OR IGNORE INTO auteurs (nom_auteur) VALUES (?)", (livre['author'],))
    cur.execute("SELECT id FROM auteurs WHERE nom_auteur = ?", (livre['author'],))
    auteur_id = cur.fetchone()['id']
    cur.execute("""
        INSERT OR IGNORE INTO livres (titre, pitch, auteur_id, date_public) 
        VALUES (?, ?, ?, ?)
    """, (livre['title'], livre['content'], auteur_id, livre['date']))
    conn.commit()
    return {"message": "Livre ajouté avec succès"}

@app.post("/utilisateur/ajouter")
def ajouter_utilisateur(utilisateur: dict = Body(...)):
    cur, conn = get_db_cursor()
    cur.execute("INSERT INTO utilisateurs (nom, email) VALUES (?, ?)", (utilisateur['nom'], utilisateur['email']))
    conn.commit()
    return {"message": "Utilisateur ajouté avec succès"}

@app.delete("/utilisateur/{utilisateur}")
def supprimer_utilisateur(utilisateur: Union[int, str]):
    cur, conn = get_db_cursor()
    if isinstance(utilisateur, int):
        cur.execute("DELETE FROM utilisateurs WHERE id = ?", (utilisateur,))
    else:
        cur.execute("DELETE FROM utilisateurs WHERE nom = ?", (utilisateur,))
    conn.commit()
    return {"message": "Utilisateur supprimé avec succès"}

@app.put("/utilisateur/{utilisateur_id}/emprunter/{livre_id}")
def emprunter_livre(utilisateur_id: int, livre_id: int):
    cur, conn = get_db_cursor()
    cur.execute("UPDATE livres SET emprunteur_id = ? WHERE id = ?", (utilisateur_id, livre_id))
    conn.commit()
    return {"message": "Livre emprunté avec succès"}

@app.put("/utilisateur/{utilisateur_id}/rendre/{livre_id}")
def rendre_livre(utilisateur_id: int, livre_id: int):
    cur, conn = get_db_cursor()
    cur.execute("UPDATE livres SET emprunteur_id = 0 WHERE id = ? AND emprunteur_id = ?", (livre_id, utilisateur_id))
    conn.commit()
    return {"message": "Livre rendu avec succès"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
