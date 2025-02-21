from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error
from flask import Blueprint, request, session, url_for
from flask import render_template, redirect, jsonify
from werkzeug.security import gen_salt

from models import db, User, OAuth2Client, OAuth2Token, AllowedUsers
from oauth2 import authorization, require_oauth

from urllib.parse import urlparse, parse_qs



bp = Blueprint('home', __name__)


def current_user():
    print("session", session)
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None

def split_by_crlf(s):
    return [v for v in s.splitlines() if v]

@bp.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user:
            if user.check_password(password):
                print("User in session and good password")        
                session['id'] = user.id
                # if user is not just to log in, but need to head back to the auth page, then go for it
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('/')
            else:
                return {"message": "Incorrect password"}
            
        else: # not user:
            print("User not registered (not in user table)")

            print("buscar en la taula allowed")
            query = AllowedUsers.query.filter_by(user_id=username).all() # select from where

            if len(query) == 0: # si és 0 no està allowed
                return {"message": "User not allowed"}
          
            elif user.username == "usuari0": # exemple, per tenir un permès
                userAllowed = AllowedUsers(user_id=user.id)
                db.session.add(userAllowed)
                db.session.commit()

                print("Registrant usuari")
                user = User(username=username, password=password)
                db.session.add(user)
                db.session.commit()

            else: # usuari dins de la llista de permesos
                print("Registrant usuari")
                user = User(username=username, password=password)
                db.session.add(user)
                db.session.commit()

        
    user = current_user()
    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()
        # tokens = OAuth2Token.query.filter_by(user_id=user.id).all()
        # print("tokens del user", user.id)
        # print([t.access_token for t in tokens])

        
    else:
        clients = []
    return render_template('home.html', user=user, clients=clients)


@bp.route('/logout')
def logout():
    session.clear()
    if 'returnTo' in request.args:
        return redirect(request.args['returnTo'])
    else:
        return redirect('/')


@bp.route('/create_client', methods=('GET', 'POST'))
def create_client():
    import time
    import json
    
    user = current_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        return render_template('create_client.html')
    
    # """
    client_id = gen_salt(24)
    client_id_issued_at = int(time.time())
    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_id=user.id,
    )

    form = request.form
    client_metadata = {
        "client_name": form["client_name"],
        "client_uri": "http://127.0.0.1:5000", # form["client_uri"] = "http://127.0.0.1:3000"
        "grant_types": split_by_crlf(form["grant_type"]),
        "redirect_uris": ["http://127.0.0.1:5000/callback"],  # split_by_crlf(form["redirect_uri"])
        "response_types": ["code"], # split_by_crlf(form["response_type"])
        "scope": "profile", # form["scope"]
        "token_endpoint_auth_method": form["token_endpoint_auth_method"]
    }
    client.set_client_metadata(client_metadata)
    
    if form['token_endpoint_auth_method'] == 'none': 
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)
    
    client_return = {"client_id": client_id,
                     "client_secret": client.client_secret}

    db.session.add(client)
    db.session.commit()
    # """
    
    # res = requests.post('http://localhost:3000/prova', json= {"client_secret": "client.client_secret"})
    # print ('response from server:',res.text)
    
    return json.dumps(client_return) 
    # return redirect('/')


@bp.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    user = current_user()
    if not user:
        return redirect(url_for('home.home', next=request.url))
    if request.method == 'GET':
        try:
            grant = authorization.get_consent_grant(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template('authorize.html', user=user, grant=grant)
    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
    # if request.form['confirm']:
    #     grant_user = user
    #     print("grant_user", grant_user)
    # else:
    #     grant_user = None
    grant_user = user
    response = authorization.create_authorization_response(grant_user=grant_user)
    redirect_url = response.location
    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    # print("code: ", query_params["code"][0])
    return {"code": query_params["code"][0]} # response


@bp.route('/oauth/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()


@bp.route('/oauth/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')


@bp.route('/api/me')
@require_oauth('profile')
def api_me():
    # current token instance of the OAuth Token model
    user = current_token.user
    return jsonify(id=user.id, username=user.username)






# poligons ------------------------------------------
from components import database

@bp.route('/get_polygons') # , methods=['POST']
@require_oauth('profile')
def getPolygons():
    # data = request.get_json()
    # date = data.get('date', '')
    date = "2024-12-27"
    polygons_list = database.returnPolygons(date)

    return jsonify({'polygons': polygons_list})

