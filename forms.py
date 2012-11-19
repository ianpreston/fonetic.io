from flask.ext.wtf import Form, TextField, IntegerField, PasswordField, FileField, FormField, FieldList, Required, HiddenInput

class TermForm(Form):
    name = TextField('Name', validators=[Required()])
    description = TextField('Description')
    create_clip_with_file = FileField('Add a new clip')

class LoginForm(Form):
    username = TextField('Username')
    password = PasswordField('Password')