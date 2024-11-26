import sqlite3

# Effacer le fichier de base de données s'il existe déjà
import os
if os.path.exists("database.db"):
    os.remove("database.db")

# Création / ouverture d'une base de données SQLite3
with sqlite3.connect('database.db') as conn:

    # écriture dans la base de données
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS utilisateurs (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, email TEXT)")

    # ajouter des données dans la base de données
    cur.execute("INSERT INTO utilisateurs (nom, email) VALUES (?, ?)", ("Alice", "alice@ex.com"))

    # Insertion de données dans la table 'utilisateurs'
    nouvel_utilisateur = ("John Doe", "john.doe@example.com")
    cur.execute("INSERT INTO utilisateurs (nom, email) VALUES (?, ?)", nouvel_utilisateur)

    # Pour insérer plusieurs lignes en une seule requête, utilisez executemany
    nouveaux_utilisateurs = [("Jane Smith", "jane.smith@example.com"), ("Bob Johnson", "bob.johnson@example.com")]
    cur.executemany("INSERT INTO utilisateurs (nom, email) VALUES (?, ?)", nouveaux_utilisateurs)

    # Validez la transaction et enregistrez les modifications
    conn.commit()

    # Lire les données de la base de données
    cur.execute("SELECT * FROM utilisateurs")
    resultat = cur.fetchall()

    # Afficher les données
    print(" Après l'insertion des données : ".center(80, "-"))
    for ligne in resultat:
        print(ligne)

    # Mise à jour du champ 'email' pour un utilisateur spécifique
    utilisateur_id = 1
    nouvel_email = "nouveau.email.alice@example.com"
    cur.execute("UPDATE utilisateurs SET email = ? WHERE id = ?", (nouvel_email, utilisateur_id))

    # stopper la transaction et enregistrer les modifications dans la base de données
    conn.commit()

    # Suppression d'un utilisateur spécifique en fonction de son ID
    utilisateur_id = 4
    cur.execute("DELETE FROM utilisateurs WHERE id = ?", (utilisateur_id,))

    # stopper la transaction et enregistrer les modifications dans la base de données
    conn.commit()

    # Lire les données de la base de données
    cur.execute("SELECT * FROM utilisateurs")
    resultat = cur.fetchall()

    # Afficher les données
    print(" Après la mise à jour et la suppression des données : ".center(80, "-"))
    for ligne in resultat:
        print(ligne)

# fermer la connexion
# conn.close() non nécessaire car le 'with' s'en charge

import json

# Lecture du fichier JSON
with open('data_books.json', 'r') as file:
    data = json.load(file)

# Création / ouverture d'une base de données SQLite3
with sqlite3.connect('database.db') as conn:

    # écriture dans la base de données
    cur = conn.cursor()
    
    # Création des tables 'auteurs' et 'livres'
    cur.execute("""
        CREATE TABLE IF NOT EXISTS auteurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_auteur TEXT UNIQUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS livres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT UNIQUE,
            pitch TEXT,
            auteur_id INTEGER,
            date_public DATE,
            FOREIGN KEY (auteur_id) REFERENCES auteurs (id)
        )
    """)

    # Insertion des données dans les tables
    for item in data:
        # Insertion de l'auteur
        cur.execute("INSERT OR IGNORE INTO auteurs (nom_auteur) VALUES (?)", (item['author'],))
        cur.execute("SELECT id FROM auteurs WHERE nom_auteur = ?", (item['author'],))
        auteur_id = cur.fetchone()[0]

        # Insertion du livre
        cur.execute("""
            INSERT OR IGNORE INTO livres (titre, pitch, auteur_id, date_public) 
            VALUES (?, ?, ?, ?)
        """, (item['title'], item['content'], auteur_id, item['date']))

    # Valider les transactions
    conn.commit()

    # Afficher les données insérées
    print(" Auteurs : ".center(80, "-"))
    cur.execute("SELECT * FROM auteurs")
    for ligne in cur.fetchall():
        print(ligne)

    print(" Livres : ".center(80, "-"))
    cur.execute("SELECT * FROM livres")
    for ligne in cur.fetchall():
        print(ligne)


import random

with sqlite3.connect('database.db') as conn:
    # écriture dans la base de données
    cur = conn.cursor()
    cur.execute("""
        ALTER TABLE livres ADD COLUMN emprunteur_id INTEGER DEFAULT 0 REFERENCES utilisateurs(id) 
    """)
    conn.commit()
    
print(" Livres : ".center(80, "-"))
cur.execute("SELECT * FROM livres")
for ligne in cur.fetchall():
    print(ligne)
    
utilisateurs = cur.execute("SELECT * FROM utilisateurs").fetchall()
livres = cur.execute("SELECT titre FROM livres").fetchall()
# Dictionnaire pour stocker les emprunts
emprunts = {}

for utilisateur in utilisateurs:
    livres_empruntes = random.sample(livres, random.randint(1, 4))
    
    emprunts[utilisateur[1]] = livres_empruntes
    for livre in livres_empruntes:
        cur.execute("UPDATE livres SET emprunteur_id = ? WHERE titre = ?", (utilisateur[0], livre[0]))

conn.commit()





cur.execute("""
    SELECT utilisateurs.nom, livres.titre 
    FROM livres 
    JOIN utilisateurs ON livres.emprunteur_id = utilisateurs.id
""")
emprunts = cur.fetchall()

for emprunt in emprunts:
    message = f"{emprunt[0]} a emprunté le livre {emprunt[1]}"
    print(message)
