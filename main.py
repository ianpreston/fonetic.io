#!/usr/bin/python
from flask import Flask, render_template, request, g
from flask.ext.sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/query.db'
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


if __name__ == '__main__':
    app.run(debug=True)