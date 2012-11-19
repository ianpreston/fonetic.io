#!/usr/bin/python
from flask import Flask, render_template, redirect, request, url_for, session, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form, TextField, IntegerField, PasswordField, FileField, FormField, FieldList, Required, HiddenInput
import functools
import sys
import datetime
import os.path
import random

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, name, description):
        self.name = name
        self.description = description

class Clip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term', backref=db.backref('clips', lazy='dynamic'))

    def __init__(self, url, term):
        self.url = url
        self.term = term


class TermForm(Form):
    name = TextField('Name', validators=[Required()])
    description = TextField('Description')
    create_clip_with_file = FileField('Add a new clip')

class LoginForm(Form):
    username = TextField('Username')
    password = PasswordField('Password')


def save_termform_clip(form):
    '''
    Helper function that takes a TermForm with create_clip_with_file uploaded by the user, saves the file
    to disk, and returns the URL to that file (which should be used as the URL for a new Clip).
    '''
    destination_fname = (''.join([random.choice('abcdefghijklmnopqrstuvwzyz') for x in range(0, 16)])) + \
                        (os.path.splitext(form.create_clip_with_file.data.filename)[1])
    destination_path = os.path.join(sys.path[0], 'static', 'clips', destination_fname)
    destination_url  = url_for('static', filename=os.path.join('clips', destination_fname))
    form.create_clip_with_file.data.save(destination_path)
    return destination_url


@app.before_request
def before_request():
    g.username = session.get('username', None)

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if g.username == None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/terms/search')
def terms_search():
    query = request.args.get('q', '')

    if len(query) < 3: return ''

    terms = Term.query.filter(Term.name.like(r'%{0}%'.format(query)))
    return render_template('terms/search.html', terms=terms)

@app.route('/terms/<int:id>')
def terms_view(id):
    term = Term.query.get(id)
    return render_template('terms/view.html', term=term)


@app.route('/admin/')
@login_required
def admin_index():
    terms = Term.query.all()
    return render_template('admin/index.html', terms=terms)

@app.route('/admin/terms/create', methods=['GET', 'POST'])
@login_required
def admin_terms_create():
    form = TermForm()

    if form.validate_on_submit():
        new_term = Term(form.name.data, form.description.data)

        if form.create_clip_with_file.data.filename != '':
            destination_url = save_termform_clip(form)

            new_clip = Clip(destination_url, new_term)
            db.session.add(new_clip)

        db.session.add(new_term)
        db.session.commit()
        
        return redirect(url_for('admin_index'))

    return render_template('admin/terms/create.html', form=form)

@app.route('/admin/terms/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_terms_edit(id):
    term = Term.query.get(id)
    form = TermForm(obj=term)

    if form.validate_on_submit():
        form.populate_obj(term)

        if form.create_clip_with_file.data.filename != '':
            destination_url = save_termform_clip(form)

            new_clip = Clip(destination_url, term)
            db.session.add(new_clip)

        db.session.commit()
        

    return render_template('admin/terms/edit.html', form=form, term=term)

@app.route('/admin/terms/delete/<int:id>', methods=['POST'])
@login_required
def admin_terms_delete(id):
    term = Term.query.get(id)
    db.session.delete(term)
    db.session.commit()
    return 'success'


@app.route('/admin/clips/delete/<int:id>', methods=['POST'])
@login_required
def admin_clips_delete(id):
    clip = Clip.query.get(id)
    db.session.delete(clip)
    db.session.commit()
    return 'success'


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if (form.username.data, form.password.data) in app.config['ADMIN_USERS']:
            session['username'] = form.username.data
            return redirect(url_for('admin_index'))

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session['username'] = None
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)