from flask import Flask, render_template, request, jsonify
import requests, logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests, logging, jwt, datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mon_secret'
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



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            response = requests.post('http://localhost:5002/token', data={'username': username, 'password': password})
            response.raise_for_status()  # Raise an exception for HTTP errors
            token = response.json().get('access_token')
            if token:
                resp = redirect(url_for('accueil'))
                resp.set_cookie('token', token)
                return resp
            else:
                return jsonify({"error": "Token not found in response"}), 500
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Request failed: {e}")
            return render_template('login.j2', error="Authentication failed")
            #return jsonify({"error": "Authentication failed"}), 401
    
    return render_template('login.j2')

@app.route('/livres')
def livres():
    response = requests.get('http://localhost:5000/livres')
    livres = response.json()
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
        except ValueError as e:
            app.logger.error(f"JSON decode error: {e}")
            return jsonify({"error": "Invalid JSON response"}), 500
    else:
        return jsonify({"error": "No content in response"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)