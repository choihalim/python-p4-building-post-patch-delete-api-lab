#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():

    bakeries = Bakery.query.all()
    bakeries_serialized = [bakery.to_dict() for bakery in bakeries]

    response = make_response(
        bakeries_serialized,
        200
    )
    return response

@app.route('/baked_goods', methods=['GET','POST'])
def baked_goods():
    if request.method == 'GET':
        goods = BakedGood.query.all()
        serialized_goods = [good.to_dict() for good in goods]
        response = make_response(jsonify(serialized_goods), 200)
        return response
    
    elif request.method == 'POST':
        new_good = BakedGood(
            name=request.get_json()['name'],
            price=request.get_json()['price'],
            bakery_id=request.get_json()['bakery_id']
        )
        if new_good:
            db.session.add(new_good)
            db.session.commit()

            good_dict = new_good.to_dict()
            response = make_response(jsonify(good_dict), 201)
            return response
    return make_response('Validation Error', 422)

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()
    if bakery:
        if request.method == 'GET':
            bakery_serialized = bakery.to_dict()

            response = make_response(
                bakery_serialized,
                200
            )
            return response
        
        elif request.method == 'PATCH':
            for attr in request.get_json():
                setattr(bakery, attr, request.get_json()[attr])
            db.session.add(bakery)
            db.session.commit()

            bakery_dict = bakery.to_dict()
            response = make_response(jsonify(bakery_dict), 200)
            return response
    return make_response('Bakery not found', 404)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    
    response = make_response(
        baked_goods_by_price_serialized,
        200
    )
    return response

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()

    response = make_response(
        most_expensive_serialized,
        200
    )
    return response

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_good(id):
    good = BakedGood.query.filter(BakedGood.id == id).first()

    if good:
        if request.method == 'DELETE':
            db.session.delete(good)
            db.session.commit()
            response = make_response('', 204)
            return response
        
if __name__ == '__main__':
    app.run(port=5555, debug=True)
