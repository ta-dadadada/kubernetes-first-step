from typing import List
from starlette.responses import JSONResponse
from fastapi import FastAPI, Query
from pydantic import BaseModel, Schema
app = FastAPI()


class Item(BaseModel):
    id: int
    name: str = Schema(..., description='item name')
    price: int = Schema(..., description='item price')


class Shop(BaseModel):
    id: int
    name: str = Schema(..., description='shop name')


class ShopWithItems(Shop):
    items: List[Item] = Schema([], description='sale items in the shop')


class ItemWithDealingShop(Item):
    shops: List[Shop] = Schema([], description='shops dealing with the item')


@app.get('/')
async def root():
    return {"message": "Hello World"}


@app.get('/item/{item_id}', response_model=Item, tags=['item'])
async def get_item_by_id(*, item_id: int):
    """商品をIDでとる"""
    item = Item(id=item_id, name='ME', price=200)
    return item


@app.get('/shop/{shop_id}', tags=['shop'])
async def get_shop_by_id(*, shop_id: int,
                         with_item: bool = Query(False, description = 'if true, return sale items in the shop.')):
    shop_dic = {
        'id': shop_id,
        'name': '711'
    }
    if with_item:
        shop_dic['items'] = [
            Item(id=1, name='ME', price=200),
            Item(id=2, name='WJ', price=240),
        ]
        shop = ShopWithItems.parse_obj(shop_dic)
    else:
        shop = Shop.parse_obj(shop_dic)
    return shop


async def get_item_with_dealing_shop(*, item_id: int):
    shops = [
        Shop(id=1, name='711'),
        Shop(id=2, name='matsukiyo'),
    ]
    item = ItemWithDealingShop(id=item_id, name='ME', price=200, shops=shops)
    return item


@app.get('/health')
async def health_check():
    return JSONResponse({'message': 'I\'m fine.'}, status_code=200)
