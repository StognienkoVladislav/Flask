
from flask import request
from models.item import ItemModel
from flask_restful import Resource
from schemas.item import ItemSchema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, fresh_jwt_required

ITEM_DELETED = "Item deleted."
ITEM_NOT_FOUND = "Item not found."
ERROR_INSERTING = "An error occurred while inserting the item."
NAME_ALREADY_EXISTS = "An item with name '{}' already exists."

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):

    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):  # /item/chair
        if ItemModel.find_by_name(name):
            return (
                {"message": NAME_ALREADY_EXISTS.format(name)},
                400,
            )

        item_json = request.get_json()  # price, store_id
        item_json["name"] = name

        item = item_schema.load(item_json)

        try:
            item.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return item_schema.dump(item), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": ITEM_DELETED}, 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    def put(cls, name: str):
        item_json = request.get_json()
        item = ItemModel.find_by_name(name)

        if item:
            item.price = item_json["price"]
        else:
            item_json["name"] = name
            item = item_schema.load(item_json)

        item.save_to_db()

        return item_schema.dump(item), 200


class ItemList(Resource):

    @classmethod
    def get(cls):
        return {"items": item_list_schema.dump(ItemModel.find_all())}, 200
