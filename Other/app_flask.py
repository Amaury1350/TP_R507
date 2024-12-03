import sqlite3
from flask import Flask, request, jsonify, abort


app = Flask(__name__)


@app.route("/utilisateurs", methods=["GET"])
def get_utilisateurs():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM utilisateurs")
        return jsonify(cur.fetchall())

@app.route("/livres", methods=["GET"])
def get_livres():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM livres")
        return jsonify(cur.fetchall())

@app.route("/auteurs", methods=["GET"])
def get_auteurs():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM auteurs")
        return jsonify(cur.fetchall())

@app.route("/utilisateur/<utilisateur>", methods=["GET"])
def get_utilisateur(utilisateur):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if utilisateur.isdigit():
            cur.execute("SELECT * FROM utilisateurs WHERE id = ?", (int(utilisateur),))
        else:
            cur.execute("SELECT * FROM utilisateurs WHERE nom = ?", (utilisateur,))
        result = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        if len(result) == 1:
            return jsonify(result[0])
        elif len(result) > 1:
            abort(400, description="Multiple users found with the same name")
        else:
            abort(404, description="User not found")

@app.route("/utilisateur/emprunts/<utilisateur>", methods=["GET"])
def get_emprunts(utilisateur):
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
            return jsonify(cur.fetchall())
        elif len(result) > 1:
            abort(400, description="Multiple users found with the same name")
        else:
            abort(404, description="User not found")

@app.route("/livres/siecle/<int:siecle>", methods=["GET"])
def get_livres_par_siecle(siecle):
    debut_annee = (siecle - 1) * 100 + 1
    fin_annee = siecle * 100
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM livres 
            WHERE date_public BETWEEN ? AND ?
        """, (f"01-01-{debut_annee}", f"31-12-{fin_annee}"))
        return jsonify(cur.fetchall())

@app.route("/livres/ajouter", methods=["POST"])
def ajouter_livre():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        livre = request.json
        cur.execute("INSERT OR IGNORE INTO auteurs (nom_auteur) VALUES (?)", (livre['author'],))
        cur.execute("SELECT id FROM auteurs WHERE nom_auteur = ?", (livre['author'],))
        auteur_id = cur.fetchone()[0]
        cur.execute("""
            INSERT OR IGNORE INTO livres (titre, pitch, auteur_id, date_public) 
            VALUES (?, ?, ?, ?)
        """, (livre['title'], livre['content'], auteur_id, livre['date']))
        conn.commit()
        return jsonify({"message": "Livre ajouté avec succès"})

@app.route("/utilisateur/ajouter", methods=["POST"])
def ajouter_utilisateur():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        utilisateur = request.json
        cur.execute("INSERT INTO utilisateurs (nom, email) VALUES (?, ?)", (utilisateur['nom'], utilisateur['email']))
        conn.commit()
        return jsonify({"message": "Utilisateur ajouté avec succès"})

@app.route("/utilisateur/<utilisateur>", methods=["DELETE"])
def supprimer_utilisateur(utilisateur):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if utilisateur.isdigit():
            cur.execute("DELETE FROM utilisateurs WHERE id = ?", (int(utilisateur),))
        else:
            cur.execute("DELETE FROM utilisateurs WHERE nom = ?", (utilisateur,))
        conn.commit()
        return jsonify({"message": "Utilisateur supprimé avec succès"})

@app.route("/utilisateur/<int:utilisateur_id>/emprunter/<int:livre_id>", methods=["PUT"])
def emprunter_livre(utilisateur_id, livre_id):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("UPDATE livres SET emprunteur_id = ? WHERE id = ?", (utilisateur_id, livre_id))
        conn.commit()
        return jsonify({"message": "Livre emprunté avec succès"})

@app.route("/utilisateur/<int:utilisateur_id>/rendre/<int:livre_id>", methods=["PUT"])
def rendre_livre(utilisateur_id, livre_id):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("UPDATE livres SET emprunteur_id = 0 WHERE id = ? AND emprunteur_id = ?", (livre_id, utilisateur_id))
        conn.commit()
        return jsonify({"message": "Livre rendu avec succès"})

if __name__ == "__main__":
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    app.run(host="0.0.0.0", port=5000, debug=True)
    
