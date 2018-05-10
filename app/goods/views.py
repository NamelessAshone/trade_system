from flask import render_template, redirect, url_for, current_app, flash, request
from flask_paginate import Pagination#, get_page_parameter
from flask_login import current_user, login_required
from sqlalchemy import or_, and_
from .forms import InputGoodInfo, UpdateGoodInfo, SearchItems
from . import goods
from .. import photos, db
from ..models import Good, User
from collections import OrderedDict
import flask_whooshalchemyplus
import os


@goods.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # first = Good.query.order_by(Good.id).first()
    # print(first)
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    per_page = 2
    form = SearchItems()
    offset = (page - 1) * per_page

    if form.validate_on_submit():
        flask_whooshalchemyplus.index_all(current_app)

        key = form.search.data
        show_goods = Good.query.whoosh_search(key, or_=True)\
            .limit(per_page).offset(offset)
        total = Good.query.whoosh_search(key, or_=True).count()
        pagination = Pagination(page=page,
                                total=total,
                                per_page=per_page,
                                search=True,
                                found=total,
                                record_name='goods',
                                css_framework='bootstrap3')

    else:
        total = len(Good.query.all())
        show_goods = Good.query.limit(per_page).offset(offset)
        pagination = Pagination(page=page,
                                total=total,
                                per_page=per_page,
                                search=False,
                                record_name='goods',
                                css_framework='bootstrap3')
    # page = request.args.get(get_page_parameter(), type=int, default=1)
    # print(total)

    # print(pagination.links)
    return render_template('goods/home.html',
                           form=form,
                           page=page,
                           per_page=per_page,
                           show_goods=show_goods,
                           pagination=pagination)


@goods.route('/<id>')
@login_required
def show(id):
    good = Good.query.filter_by(id=id).first()
    photo_name = good.photo_path.rsplit('/', -1)[-1]
    good.photo_url = photos.url(photo_name)
    current_url = request.url.split('/', -1)[-2:]
    is_owner = False
    if current_user.id == good.owner.id:
        is_owner = True
    return render_template('goods/show_one_good.html',
                           good=good,
                           current_url=current_url,
                           is_owner=is_owner)


@goods.route('/show-my-goods')
@login_required
def show_my_goods():
    user = User.query.filter_by(id=current_user.id).first()
    my_goods = user.my_goods
    return render_template('goods/show_my_goods.html', my_goods=my_goods)


@goods.route('/add-new-good', methods=['GET', 'POST'])
@login_required
def add_new_good():
    form = InputGoodInfo()
    if form.validate_on_submit():
        app = current_app._get_current_object()
        photo_name = photos.save(form.photo.data)
        photo_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], photo_name)
        photo_url = photos.url(photo_name)

        good = Good(name=form.name.data,
                    price=form.price.data,
                    amount=form.amount.data,
                    text=form.text.data,
                    photo_path=photo_path,
                    photo_url=photo_url,
                    owner_id=current_user.id)

        db.session.add(good)
        db.session.commit()
        flash('Success to add a item')
        return redirect(url_for('goods.show', id=good.id))
    return render_template('goods/add_new_good.html', form=form)


@goods.route('/update-good/<id>', methods=['GET', 'POST'])
@login_required
def update_one_good(id):
    form = UpdateGoodInfo()
    good = Good.query.filter_by(id=id).first()
    # Debug: print('S1 ok')
    if form.validate_on_submit():
        app = current_app._get_current_object()
        if form.photo.data:
            pos_postfix_begin = request.files['photo'].filename.rfind('.')
            photo_postfix = request.files['photo'].filename[pos_postfix_begin:]
            # Debug: print(photo_postfix)
            # Debug: print('S2 ok')
            good.del_photo()
            photo_name = photos.save(form.photo.data, name=good.id_str + photo_postfix)
            # Debug: print('S3 ok')
            good.photo_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], photo_name)
            good.photo_url = photos.url(photo_name)

        if form.name.data:
            good.name = form.name.data
        if form.price.data:
            good.price = form.price.data
        if form.amount.data:
            good.amount = form.amount.data
        if form.text.data:
            good.text = form.text.data

        db.session.add(good)
        db.session.commit()
        flash('Success to update information of this item')
        return redirect(url_for('goods.show', id=good.id))
    return render_template('goods/update_good_info.html', form=form, good=good)


@goods.route('/delete-good/<id>', methods=['GET'])
@login_required
def delete_one_good(id):
    good = Good.query.filter_by(id=id).first()

    # whether here can use del_obj.id, del_obj.name = good.id, good.name
    delete_id = good.id
    delete_name = good.name
    user = User.query.filter_by(id=current_user.id).first()
    user.my_goods.remove(good)

    good.del_photo()
    db.session.delete(good)
    db.session.commit()
    flash('Success to delete item '
          'with the id "{}" and the name "{}".'.format(delete_id, delete_name))
    return redirect(url_for('goods.show_my_goods'))


# TODO : add statistics
@goods.route('/statistics')
@login_required
# @admin_required
def show_statistics():
    #do satistics on prices of goods
    MAX_PRICE = current_app.config['GOOD_MAX_PRICE']
    delta = 1000

    class Result():
        price = OrderedDict()
        price_total = 0

    result = Result()
    result.price_total = Good.query.count()
    for upper in range(delta, MAX_PRICE, delta):
        lower = upper - delta
        goods = Good.query.filter(and_(Good.price >= lower, Good.price <= upper)).all()
        interval = str(lower) + ' < price < '+ str(upper)
        result.price[interval] = len(goods)
    data = {'Chrome': 52.9, 'Opera': 1.6, 'Firefox': 27.7}
    print(result.price, '\n', result.price_total)
    return render_template('goods/statistics.html', result=result)
