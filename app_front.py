from flask import Flask, render_template, request, jsonify
import requests, logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests, logging, jwt, datetime
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mon_secret'
logging.basicConfig(level=logging.DEBUG)

SECRET_KEY = "your_secret_key"  # Assurez-vous que cette clé est la même que celle utilisée pour signer le token

def get_username_from_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/')
def accueil():
    token = request.cookies.get('token')
    username = get_username_from_token(token) if token else None
    return render_template('accueil.j2', username=username)

@app.route('/affichage')
def affichage():
    token = request.cookies.get('token')
    username = get_username_from_token(token) if token else None
    return render_template('affichage.j2', username=username)

@app.route('/edition')
def edition():
    token = request.cookies.get('token')
    username = get_username_from_token(token) if token else None
    return render_template('edition.j2', username=username)



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

@app.route('/ajout', methods=['POST'])
def ajout():
    token = request.cookies.get('token')
    if token is None or get_username_from_token(token) is None:
        return render_template('login.j2', error="Permission non accordée")
    url = "http://localhost:5000/livres/ajouter"
    titre = request.form.get('titre')
    pitch = request.form.get('pitch')
    auteur = request.form.get('auteur')
    date_public = request.form.get('date_public')
    data = {
        'titre': titre, 
        'pitch': pitch, 
        'auteur': auteur, 
        'date_public': date_public
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {request.cookies.get('token')}"
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status() 
        return redirect(url_for('livres'))
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request failed: {e}")
        return render_template('login.j2', error=0)


@app.route('/ajout_utilisateur', methods=['POST'])
def ajout_utilisateur():
    token = request.cookies.get('token')
    if token is None or get_username_from_token(token) is None:
        return render_template('login.j2', error="Permission non accordée")
    url = "http://localhost:5000/utilisateur/ajouter"
    nom = request.form.get('nom')
    email = request.form.get('email')
    data = {
        'nom': nom, 
        'email': email
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {request.cookies.get('token')}"
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status() 
        return redirect(url_for('utilisateurs'))
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request failed: {e}")
        return render_template('edition.j2', error=1)

@app.route('/delete_user', methods=['POST'])
def delete_user():
    token = request.cookies.get('token')
    if token is None or get_username_from_token(token) is None:
        return render_template('login.j2', error="Permission non accordée")
    url = "http://localhost:5000/utilisateur/"
    user = request.form.get('user')
    data = {
        'user': user
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {request.cookies.get('token')}"
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status() 
        return redirect(url_for('utilisateurs'))
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request failed: {e}")
        return render_template('edition.j2', error=1)

@app.route('/logout')
def logout():
    resp = redirect(url_for('accueil'))
    resp.delete_cookie('token')
    return resp

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)