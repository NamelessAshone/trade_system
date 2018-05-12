from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, BooleanField, SelectMultipleField, \
    SubmitField, IntegerField, FloatField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, NumberRange
from wtforms import ValidationError
from .. import photos


class InputGoodInfo(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 64)])
    text = TextAreaField('Description')
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


class SearchItems(FlaskForm):
    search = StringField(description="Search items", validators=[
        DataRequired(), Length(min=1, max=50)])
    submit = SubmitField('Search')


class PurchaseItems(FlaskForm):
    amount = IntegerField('Amount', validators=[
        DataRequired(), NumberRange(1, 100000, 'The price must be between 1 and 10000')])
    address = TextAreaField('Your address')
    submit = SubmitField('Commit')
