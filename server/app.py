import os
import click

from website.app import create_app

from config import username, password, database_name

os.environ.setdefault('AUTHLIB_INSECURE_TRANSPORT', '1')  # use http

app = create_app({
    'SECRET_KEY': 'secret',
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': True,
    # 'SQLALCHEMY_ECHO': True,
    'SQLALCHEMY_DATABASE_URI': f'mysql+pymysql://{username}:{password}@{database_name}',
})

# python -m flask initdb
@app.cli.command("initdb")
def initdb():
    from website.models import db
    db.create_all()
    click.echo("Create all tables.")


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)
