from flask import render_template
from . import goods


@goods.route('/home', methods=['GET'])
def home():
    return render_template('goods/home.html')

@goods.route('/goods/grounding')
def grounding():
    return render_template()

@goods.route('/goods/<id>')
def show(id):
    return render_template()

@goods.route('/goods/upgrade/id')
def upgrade():
    return render_template()
