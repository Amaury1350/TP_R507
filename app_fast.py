import sqlite3
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/utilisateurs")
async def get_utilisateurs():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM utilisateurs")
        return cur.fetchall()

@app.get("/livres")
async def get_livres():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM livres")
        return cur.fetchall()

@app.get("/auteurs")
async def get_auteurs():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM auteurs")
        return cur.fetchall()

@app.get("/utilisateur/{utilisateur}")
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

@app.get("/livres/siecle/{siecle}")
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

@app.post("/livres/ajouter")
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

@app.post("/utilisateur/ajouter")
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