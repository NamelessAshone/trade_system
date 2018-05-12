from flask import render_template, redirect, url_for, current_app, flash, request, abort
from flask_paginate import Pagination#, get_page_parameter
from flask_login import current_user, login_required
from sqlalchemy import or_, and_
from .forms import InputGoodInfo, UpdateGoodInfo, SearchItems, PurchaseItems
from . import goods
from .. import photos, db
from ..models import Good, User, Purchase_log
from collections import OrderedDict
import flask_whooshalchemyplus
import os


@goods.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # Debug: first = Good.query.order_by(Good.id).first()
    # Debug: print(first)
    '''
    The view function to show home page.
    :return: a html page of home in which page show the items in database.
    '''
    # 得到分页参数
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    # 设置每页显示的物品数量
    per_page = 6
    # 实例化搜索表单
    form = SearchItems()
    # 计算页偏移
    offset = (page - 1) * per_page
    # 处理提交后的表单
    if form.validate_on_submit():
        # 建立goods表的索引
        flask_whooshalchemyplus.index_all(current_app)
        # 获取搜索关键字,并使用关键字查询商品
        key = form.search.data
        show_goods = Good.query.whoosh_search(key, or_=True)\
            .limit(per_page).offset(offset)
        # 计算查询得到的表项的总数
        total = Good.query.whoosh_search(key, or_=True).count()
        # 得到分页对象
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
    # Debug: page = request.args.get(get_page_parameter(), type=int, default=1)
    #        print(total)
    #        print(pagination.links)

    # 返回渲染后的html
    return render_template('goods/home.html',
                           form=form,
                           page=page,
                           per_page=per_page,
                           show_goods=show_goods,
                           pagination=pagination)


def purchase_good(good_id, form):
    buyer_id = current_user.id
    current_good = Good.query.filter_by(id=good_id).first()
    owner_id = current_good.id
    if form.amount.data > current_good.amount:
        class Value():
            amout = 0
            address = ''

        last_value = Value()
        last_value.amount = form.amount.data
        last_value.address = form.address.data
        flash("You buy too much. Max amount of this item is '{}'.".format(current_good.amount))
        return last_value

    purchase_log = Purchase_log(owner_id=owner_id,
                                buyer_id=buyer_id,
                                good_id=current_good.id,
                                amount=form.amount.data,
                                total_price=form.amount.data*current_good.price,
                                address=form.address.data)

    current_good.amount = current_good.amount - purchase_log.amount
    db.session.add(purchase_log)
    db.session.add(current_good)
    db.session.commit()
    flash('Successfully added a order.')
    return None


@goods.route('/<id>', methods=['GET', 'POST'])
@login_required
def show(id):
    '''
    The view funtion show the detail of one item by doing query with 'id'.
    :param id: the shown item's id
    :return: the html page of one item
    '''
    good = Good.query.filter_by(id=id).first()
    # 从图片的路径中得到图片文件的名字
    photo_name = good.photo_path.rsplit('/', -1)[-1]
    # 保存图片文件的url, 方便渲染html时使用
    good.photo_url = photos.url(photo_name)
    # 得到当前的url路径
    current_url = request.url.split('/', -1)[-2:]
    # 判断是否为物品的所有者:
    #   若是. 则渲染update和detele按钮（所有者）
    #   若不是, 则渲染purchase按钮（购买者）
    is_owner = False
    last_value = None
    form = None
    if current_user.id == good.owner.id:
        is_owner = True
    if is_owner == True:
        last_value = None
        form = None
    else:
        form = PurchaseItems()
        if form.validate_on_submit():
            last_value = purchase_good(id, form)
    return render_template('goods/show_one_good.html',
                            good=good,
                            current_url=current_url,
                            is_owner=is_owner,
                            last_value=last_value,
                            form=form)


@goods.route('/show-my-goods')
@login_required
def show_my_goods():
    # 通过model中建立的relationship找到当前user上传的items
    user = User.query.filter_by(id=current_user.id).first()
    my_goods = user.my_goods
    return render_template('goods/show_my_goods.html', my_goods=my_goods)


@goods.route('/add-new-good', methods=['GET', 'POST'])
@login_required
def add_new_good():
    form = InputGoodInfo()
    # 通过提交的表单, 在数据库的goods表中添加一条记录
    if form.validate_on_submit():
        app = current_app._get_current_object()
        photo_name = photos.save(form.photo.data)
        photo_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], photo_name)
        photo_url = photos.url(photo_name)
        # 初始化一个表项对象
        good = Good(name=form.name.data,
                    price=form.price.data,
                    amount=form.amount.data,
                    text=form.text.data,
                    photo_path=photo_path,
                    photo_url=photo_url,
                    owner_id=current_user.id)
        # 添加并提交修改
        db.session.add(good)
        db.session.commit()
        # 成功添加记录后, 返回item的详细信息页面
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
    flash('Successfully deleted item '
          'with the id "{}" and the name "{}".'.format(delete_id, delete_name))
    return redirect(url_for('goods.show_my_goods'))


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
    # data = {'Chrome': 52.9, 'Opera': 1.6, 'Firefox': 27.7}
    # Debug: print(result.price, '\n', result.price_total)
    return render_template('goods/statistics.html', result=result)


@goods.route('/show-my-received-orders')
@login_required
def show_my_received_orders():
    purchase_logs = Purchase_log.query.filter_by(owner_id=current_user.id).all()
    return render_template('goods/show_my_received_orders.html', logs=purchase_logs, str=str)


@goods.route('/show-my-requested-orders')
@login_required
def show_my_requested_orders():
    purchase_logs = Purchase_log.query.filter_by(buyer_id=current_user.id).all()
    return render_template('goods/show_my_requested_orders.html', logs=purchase_logs)


@goods.route('/confirm-order/<id>')
@login_required
def confirm_order(id):
    order_id = id
    order = Purchase_log.query.filter_by(id=order_id).first()
    if order.owner_id != current_user.id:
        return render_template('404.html')
    order.confirmed = True
    flash('Successfully confirmed the order with id "{}".'.format(order.id))
    return redirect(url_for('goods.show_my_received_orders'))


@goods.route('/reject-order/<id>')
@login_required
def reject_order(id):
    order_id = id
    order = Purchase_log.query.filter_by(id=order_id).first()
    if order.owner_id != current_user.id:
        return render_template('404.html')
    if order.confirmed == True:
        flash("The confirmed order with id '{}' can't be rejected and deleted.".format(order_id))
        return redirect(url_for('goods.show_my_received_orders'))
    good = Good.query.filter_by(good_id=order.good_id).first()
    good.amount = good.amount + order.amount
    db.session.add(good)
    db.session.delete(order)
    db.session.commit()
    flash('Successfully deleted the order with id "{}".'.format(order.id))
    return redirect(url_for('goods.show_my_received_orders'))


@goods.route('/cancel-order/<id>')
@login_required
def cancel_order(id):
    order_id = id
    order = Purchase_log.query.filter_by(id=order_id).first()
    if order.buyer_id != current_user.id:
        return render_template('404.html')
    if order.confirmed == True:
        flash("The confirmed order with id '{}' can't be canceled and deleted.".format(order_id))
        return redirect(url_for('goods.show_my_requested_orders'))
    good = Good.query.filter_by(good_id=order.good_id).first()
    good.amount = good.amount + order.amount
    db.session.add(good)
    db.session.delete(order)
    db.session.commit()
    flash('Successfully deleted the order with id "{}".'.format(order.id))
    return redirect(url_for('goods.show_my_requested_orders'))
