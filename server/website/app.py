import os
import click
from flask import Flask

from models import db
from oauth2 import config_oauth
from routes import bp


def create_app(config=None):
    print("creating app")
    app = Flask(__name__)

    # load default configuration
    app.config.from_object('settings')

    # load environment configuration
    if 'WEBSITE_CONF' in os.environ:
        app.config.from_envvar('WEBSITE_CONF')

    # load app sepcified configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)

    setup_app(app)
    return app


def setup_app(app):
    print("setup app")
    db.init_app(app)
    config_oauth(app)
    app.register_blueprint(bp, url_prefix='')
    

# --------------------------- app server ----------------------------------------------

from config import username, password, database_name

os.environ.setdefault('AUTHLIB_INSECURE_TRANSPORT', '1')  # use http

app = create_app({
    'SECRET_KEY': 'secret',
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    # 'SQLALCHEMY_ECHO': True,
    'SQLALCHEMY_DATABASE_URI': f'mysql+pymysql://{username}:{password}@{database_name}',
})

# Client ---------------------------------------------
from authlib.integrations.flask_client import OAuth
app.secret_key = 'secret'
oauth = OAuth(app)
# Client ---------------------------------------------



# python -m flask initdb
@app.cli.command("initdb")
def initdb():
    from website.models import db
    db.create_all()
    click.echo("Create all tables.")


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)