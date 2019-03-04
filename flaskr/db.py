import psycopg2
import psycopg2.extras

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            database=current_app.config['DATABASE'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PSWD'],
            host=current_app.config['DB_HOST'],
            port=current_app.config['DB_PORT']
        )
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    return cur


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.cursor().execute(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
