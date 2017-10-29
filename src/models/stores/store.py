import uuid
from src.common.database import Database
import src.models.stores.errors as StoreErrors


class Store(object):
    def __init__(self,name,url_prefix,tag_name,query,_id=None):
        self.name = name
        self.url_prefix = url_prefix
        self.tag_name = tag_name
        self.query = query
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<Store {}>".format(self.name)

    def json(self):
        return {
            'name': self.name,
            'url_prefix': self.url_prefix,
            'tag_name': self.tag_name,
            'query': self.query,
            '_id':self._id
        }

    @classmethod
    def get_by_id(cls,id):
        store_data = Database.find_one('stores', {'_id':id})
        return cls(**store_data)

    def save_to_mongo(self):
        Database.insert('stores',self.json())

    @classmethod
    def get_by_name(cls,name):
        store_data = Database.find_one('stores', {'name':name})
        return cls(**store_data)

    @classmethod
    def get_by_url_prefix(cls,url_prefix):
        store_data = Database.find_one('stores', {'url_prefix':{"$regex": '^{}'.format(url_prefix)}})
        return cls(**store_data)

    @classmethod
    def find_by_url(cls,url):
        """
        return a store from a url like "http://www.johnlewis.com/item/123434dsfwe3"
        :param url: the item's url
        :return: a store, or raises a StoreNotFoundException
        """
        for i in range(0,len(url)+1):
            try:
                store = cls.get_by_url_prefix(url[:i])
                return store
            except:
                raise StoreErrors.StoreNotFoundException("The URL prefix used to find the store didn't give us any results")





