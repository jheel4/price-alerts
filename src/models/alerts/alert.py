import uuid
import requests
import src.models.alerts.constants as AlertConstants
import datetime
from src.common.database import Database
from src.models.items.item import Item

class Alert(object):
    def __init__(self,user_email,price_limit,item_id, last_checked=None,_id=None):
        self.user_email = user_email
        self.price_limit = price_limit
        self.item = Item.from_mongo(item_id)
        self.last_checked = datetime.datetime.utcnow() if last_checked is None else last_checked
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<Alert for {} on item {} with price {}>".format(self.user_email, self.item.name, self.price_limit)

    def send(self):
        return requests.post(
            AlertConstants.URL,
            auth=('api', AlertConstants.API_KEY),
            data={
                'from': AlertConstants.FROM,
                'to': self.user_email,
                'subject': 'Price limit reached for {}'.format(self.item.name),
                'text': 'We found a deal! (link here).'
            }
        )

    @classmethod
    def find_needing_update(cls, minutes_since_update=AlertConstants.ALERT_TIMEOUT):
        last_updated_limit = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes_since_update)
        return [cls(**elem) for elem in Database.find('alerts',{'last_checked':{'$lte':last_updated_limit}})]

    def save_to_mongo(self):
        Database.update("alerts",{"_id":self._id},self.json())

    def json(self):
        return {
            "_id": self._id,
            "price_limit": self.price_limit,
            "last_checked": self.last_checked,
            "user_email": self.user_email,
            "item_name": self.item._id
        }


    def load_item_price(self):
        self.item.load_price()
        self.last_checked = datetime.datetime.utcnow()
        self.save_to_mongo()
        return self.item.price

    def send_email_if_price_reached(self):
        if self.item.price < self.price_limit:
            self.send()