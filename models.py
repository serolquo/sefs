import base64
import hashlib
from hmac import HMAC
from datetime import datetime, timedelta

from flask import g

from utils import RandomString
#from sefs import db, flask_bcrypt

class UserFile:
 
    def __init__(self, s3_object=None):
        #if object!=none, then grab object from sql database
        if s3_object is not None:
            result = g.db.execute('select * from entries where s3_object = ?',(s3_object,))
            row = result.fetchone()
            if row is not None:
                self.s3_object = s3_object
            else:
                self.s3_object = None

        else:
            self.s3_object = str(RandomString(6))
            enc_key = RandomString(32)
            self.enc_key = enc_key.base64()
            self.enc_key_md5 = enc_key.base64_md5()
            self.policy_string = self.policy()
            utc_date = datetime.utcnow().isoformat('T')+'Z'
            salt = str(RandomString(16))
            g.db.execute(
"insert into entries (hashed_key,salt,s3_object,date_uploaded,uploaded) "
"VALUES (?,?,?,?,?)", (
                    enc_key.sha256(''),
                    salt,
                    self.s3_object,
                    utc_date,
                    0
                    )
)
            g.db.commit()                 
 
    def __repr__(self):
        return '<s3obj:%s>' % self.s3_object
    
    def url(self):
        return 'http://localhost:5000/uploaded/%s' % self.s3_object
       
    def policy(self):
        current_date = datetime.utcnow()
        extra_time = timedelta(hours=+1)
        expiration_time = (current_date + extra_time).isoformat('T')

        url = self.url()
        policy_string = ( 
'{'
    '"expiration": "%sZ",'
    '"conditions": ['
        '{"bucket": "sefss"},'
        '{"key": "%s"},'
        '{"success_action_redirect": "%s"}'
    ']'
'}' % (expiration_time, self.s3_object, url)
)
        
        return policy_string

    def base64_policy(self):
        return base64.b64encode(self.policy_string)
    
    def sign_policy(self,key):
        hmac = HMAC(key,self.base64_policy(),hashlib.sha1)
        return base64.b64encode(hmac.digest())
    
