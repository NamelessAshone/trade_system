from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, BooleanField, SelectMultipleField, \
    SubmitField, IntegerField, FloatField, FileField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, NumberRange
from wtforms import ValidationError
from .. import photos


class InputGoodInfo(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 64)])
    text = StringField('Description', validators=[DataRequired(), Length(1, 200)])
    price = FloatField('Price', validators=[
        DataRequired(), NumberRange(1, 100000, 'The price must be between 1 and 10000')])
    amount = IntegerField('Amount', validators=[
        DataRequired(), NumberRange(1, 100000, 'The amount must be between 1 and 10000')])
    photo = FileField('Photo', validators=[
        FileAllowed(photos, 'Only can update photos'), FileRequired("Must chose a photo")])
    _class = StringField('Class', validators=[])
    submit = SubmitField('Commit')


class UpdateGoodInfo(InputGoodInfo):
    submit = SubmitField('Update')
