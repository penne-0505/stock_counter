import os
import requests

import firebase_admin
from firebase_admin import credentials, firestore

import utils
from utils import Stock


class DBManager(metaclass=utils.Singleton):
    def __init__(self):
        url = os.getenv('DS_BOT_STOCK_CONTROL_DB_CRED')
        self.cred = credentials.Certificate(requests.get(url).json())
        firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()
    
    def set(self, collection: str, document: str | None, data: dict) -> None:
        self.db.collection(collection).document(document).set(data)
    
    def get(self, collection: str, document: str | None) -> dict:
        if document:
            return self.db.collection(collection).document(document).get().to_dict()
        return {doc.id: doc.to_dict() for doc in self.db.collection(collection).stream()}
    
    def delete(self, collection: str, document: str | None) -> None:
        self.db.collection(collection).document(document).delete()
    
    async def increment_stock(self, stock: Stock) -> Stock:
        stock_data = self.get(collection='stocks', document=stock.stock_id)

        if stock_data['count'] + stock.count > 9000000000000000:
            raise ValueError('The stock count is too high.')
        else:
            stock_data['count'] += stock.count
        
        self.set(collection='stocks', document=stock.stock_id, data=stock_data)
        return Stock(
            detail=stock_data['detail'],
            stock_id=stock.stock_id,
            count=stock_data['count'],
            price=stock_data['price'],
            group=stock_data['group']
        )

    async def decrease_stock(self, stock: Stock) -> Stock:
        stock_data = self.get(collection='stocks', document=stock.stock_id)
        
        if stock_data['count'] - stock.count < 0:
            stock_data['count'] = 0
        else:
            stock_data['count'] -= stock.count
        
        self.set(collection='stocks', document=stock.stock_id, data=stock_data)
        return Stock(
            detail=stock_data['detail'],
            stock_id=stock.stock_id,
            count=stock_data['count'],
            price=stock_data['price'],
            group=stock_data['group']
        )

    async def add_stock(self, stock: Stock) -> Stock:
        stock_id = utils.generate_id(stock.group + stock.detail)
        self.set(
            collection='stocks',
            document=stock_id,
            data={
                'group': stock.group,
                'detail': stock.detail,
                'count': 0,
                'price': stock.price,
            }
        )
        return Stock(
            detail=stock.detail,
            stock_id=stock_id,
            count=0,
            price=stock.price,
            group=stock.group
        )

    async def remove_stock(self, stock_id: str) -> None:
        self.delete(collection='stocks', document=stock_id)

    async def get_stock(self, stock_id: str) -> Stock:
        stock_data = self.get(collection='stocks', document=stock_id)
        return Stock(
            detail=stock_data['detail'],
            stock_id=stock_id,
            count=stock_data['count'],
            price=stock_data['price'],
            group=stock_data['group']
        )

    async def get_all_stock(self) -> list[Stock]:
        data = self.get(collection='stocks', document=None)
        result = []
        for stock_id, stock_data in data.items():
            result.append(
                Stock(
                    detail=stock_data['detail'],
                    stock_id=stock_id,
                    count=stock_data['count'],
                    price=stock_data['price'],
                    group=stock_data['group']
                )
            )
        
        return result
