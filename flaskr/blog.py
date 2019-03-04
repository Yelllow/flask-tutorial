from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    cur = get_db()
    cur.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN blog_user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    )
    posts = cur.fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            cur = get_db()
            cur.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (%s,%s,%s)',
                (title, body, g.user['id'])
            )
            g.db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    cur = get_db()
    cur.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN blog_user u ON p.author_id = u.id'
        ' WHERE p.id = %s',
        (id,)
    )
    post = cur.fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            cur = get_db()
            cur.execute(
                'UPDATE post SET title = %s, body = %s'
                ' WHERE id = %s',
                (title, body, id)
            )
            g.db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    cur = get_db()
    cur.execute('DELETE FROM post WHERE id = %s', (id,))
    g.db.commit()
    return redirect(url_for('blog.index'))
