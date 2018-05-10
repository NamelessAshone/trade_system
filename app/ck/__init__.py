from flask import Blueprint
import chartkick

ck = Blueprint('ck', __name__, static_folder=chartkick.js(), static_url_path='/static')
