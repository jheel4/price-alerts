import requests
from bs4 import BeautifulSoup
import re
from src.common.database import Database
import uuid
from src.models.stores.store import Store

class Item(object):
    def __init__(self,name,url, _id=None):
        self.name = name
        self.url = url
        store = Store.find_by_url(url)
        self.tag_name = store.tag_name
        self.query = store.query
        self.price = None
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<Item {} with URL {}>".format(self.name,self.url)

    def load_price(self):
        request = requests.get(self.url)
        content = request.content
        soup = BeautifulSoup(content,"html.parser")
        element = soup.find(self.tag_name, self.query)
        string_price = element.text.strip()
        pattern = re.compile("(\d+.\d+)")
        match = pattern.search(string_price)
        self.price = float(match.group())
        return self.price

    def save_to_mongo(self):
        Database.insert('items',self.json())

    def json(self):
        return {
            '_id': self._id,
            'name': self.name,
            'url': self.url,
        }

    @classmethod
    def from_mongo(cls,_id):
        return cls(**Database.find_one('items',{'_id':_id}))

