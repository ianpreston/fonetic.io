#!/usr/bin/python
from flask import Flask, render_template, redirect, request, url_for, session, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form, TextField, PasswordField, FileField, FormField, FieldList, Required
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


class ClipForm(Form):
    clip_file = FileField('Clip')

    def __init__(self, *args, **kwargs):
       kwargs['csrf_enabled'] = False
       super(ClipForm, self).__init__(*args, **kwargs)

class TermForm(Form):
    name = TextField('Name', validators=[Required()])
    description = TextField('Description')
    clips = FieldList(FormField(ClipForm))

class LoginForm(Form):
    username = TextField('Username')
    password = PasswordField('Password')


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

    if len(form.clips) == 0:
        form.clips.append_entry(ClipForm())

    if form.validate_on_submit():
        new_term = Term(form.name.data, form.description.data)

        for clip_form in form.clips:
            if clip_form.clip_file.data.filename == '':
                continue

            destination_fname = (''.join([random.choice('abcdefghijklmnopqrstuvwzyz') for x in range(0, 16)])) + \
                                (os.path.splitext(clip_form.clip_file.data.filename)[1])
            destination_path = os.path.join(sys.path[0], 'static', 'clips', destination_fname)
            destination_url  = url_for('static', filename=os.path.join('clips', destination_fname))
            clip_form.clip_file.data.save(destination_path)

            new_clip = Clip(destination_url, new_term)
            db.session.add(new_clip)

        db.session.add(new_term)
        db.session.commit()
        
        return redirect(url_for('admin_index'))

    return render_template('admin/terms/create.html', form=form)

@app.route('/admin/terms/delete/<int:id>')
@login_required
def admin_terms_delete(id):
    ##TODO some kind of confirmation. don't modify data on a GET request.
    term = Term.query.get(id)
    db.session.delete(term)
    db.session.commit()
    return redirect(url_for('admin_index'))


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