from flask import Flask, render_template, request, jsonify
import requests, logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


@app.route('/')
def accueil():
    return render_template('accueil.j2')

@app.route('/affichage')
def affichage():
    return render_template('affichage.j2')

@app.route('/edition')
def edition():
    return render_template('edition.j2')

@app.route('/livres')
def livres():
    response = requests.get('http://localhost:5000/livres')
    livres = response.json()
    #return jsonify(livres)
    return render_template('liste_livres.j2', livres=livres)

@app.route('/auteurs')
def auteurs():
    response = requests.get('http://localhost:5000/auteurs')
    auteurs = response.json()
    return render_template('liste_auteurs.j2', auteurs=auteurs)

@app.route('/utilisateurs')
def utilisateurs():
    response = requests.get('http://localhost:5000/utilisateurs')
    utilisateurs = response.json()
    return render_template('liste_utilisateurs.j2', utilisateurs=utilisateurs)

@app.route('/resultat', methods=['POST'])
def resultat():
    user = request.form.get("user")
    response = requests.get(f'http://localhost:5000/utilisateur/{user}')
    if response.content:
        try:
            return render_template('utilisateur.j2', user=response.json())
            #return jsonify(response.json())
        except ValueError as e:
            app.logger.error(f"JSON decode error: {e}")
            return jsonify({"error": "Invalid JSON response"}), 500
    else:
        return jsonify({"error": "No content in response"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)