from flask import render_template, redirect, url_for, current_app, g
from flask_login import current_user, login_required
from .forms import InputGoodInfo
from . import goods
from .. import photos, db
from ..models import Goods
import os


@goods.route('/home', methods=['GET'])
def home():
    return render_template('goods/home.html')

@goods.route('/<id>')
def show(id):
    good = Goods.query.filter_by(id=id).first()
    photo_name = good.photo_path.rsplit('/',-1)[-1]
    good.photo_url = photos.url(photo_name)
    return render_template('goods/show_one_good.html', good=good)

@goods.route('/upgrade/id')
def upgrade():
    return render_template()

photos_count = 0
@goods.route('/add-new-good', methods=['GET','POST'])
@login_required
def add_new_good():
    form = InputGoodInfo()
    if form.validate_on_submit():
        app = current_app._get_current_object()
        photo_name = photos.save(form.photo.data)
        photo_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'],photo_name)
        good = Goods(name=form.name.data,
                     price=form.price.data,
                     amount=form.amount.data,
                     text=form.text.data,
                     photo_path=photo_path)
        db.session.add(good)
        db.session.commit()
        return redirect(url_for('goods.show', id=good.id))
        # print(Goods.query.filter_by(name=form.name.data).first())
    else:
        photo_url = None
    return  render_template('goods/add_new_good.html', form=form, file_url=photo_url)

@goods.route('/delete-goods', methods=['GET','POST'])
def delet_new_good():
    return
