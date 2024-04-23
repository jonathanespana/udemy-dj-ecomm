import hashlib
import json
import re
import requests
from django.conf import settings

mailchimp_api_key = settings.MAILCHIMP_API_KEY
mailchimp_data_center = settings.MAILCHIMP_DATA_CENTER
mailchimp_audience_list_id = settings.MAILCHIMP_AUDIENCE_LIST_ID


def check_email(email):
    if not re.match(r".+@.+\..+", email):
        raise ValueError('String passed is not a valid email address')
    return email

def get_subscriber_hash(member_email):
    check_email(member_email)
    member_email = member_email.lower().encode()
    m = hashlib.md5(member_email)
    return m.hexdigest()

class Mailchimp(object):
    def __init__(self):
        super(Mailchimp, self).__init__
        self.key = mailchimp_api_key
        self.api_url = f"https://{mailchimp_data_center}.api.mailchimp.com/3.0"
        self.list_id = mailchimp_audience_list_id
        self.list_endpoint = f'{self.api_url}/lists/{self.list_id}'

    def get_members_endpoint(self):
        return self.list_endpoint + '/members'

    def change_subscription_status(self, email, status='unsubscribed'):
        hashed_email = get_subscriber_hash(email)
        endpoint = self.get_members_endpoint() + '/' + hashed_email
        data = {
            'email_address': email,
            'status': self.check_valid_status(status),
            'merge_fields': {},
        }
        r = requests.put(endpoint, auth=("", self.key), data=json.dumps(data))
        return r.status_code, r.json()
    
    def check_subscription_status(self, email):
        hashed_email = get_subscriber_hash(email)
        endpoint = self.get_members_endpoint() + '/' + hashed_email
        r = requests.get(endpoint, auth=("", self.key))
        return r.status_code, r.json()
    
    def check_valid_status(self, status):
        choices = ['subscribed', 'unsubscribed', 'cleaned', 'pending']
        if status not in choices:
            raise ValueError("Not a valid a email status")
        return status
    

    def add_email(self, email):
        return self.change_subscription_status(email, status='subscribed')
        # status ='subscribed'
        # self.check_valid_status(status)
        # data = {
        #     "email": email,
        #     "status": status,
        # }
        # endpoint = self.get_members_endpoint()
        # r = requests.post(endpoint, auth=("", self.key), data=json.dumps(data))
        # return r.json()
    
    def unsubscribe(self, email):
        return self.change_subscription_status(email, status='unsubscribed')
    
    def subscribe(self, email):
        return self.change_subscription_status(email, status='subscribed')
    
    def pending(self, email):
        return self.change_subscription_status(email, status='pending')