# all the imports
import os
import hashlib
import base64
from random import SystemRandom 

#probably need to refactor this name
class RandomString:
    charsets = 'abcdefghijklmnpqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ0123456789'
        
    def __init__(self, length=16):
        rand = SystemRandom()
        rand_chars = rand.sample(RandomString.charsets,length)
        self.generated_string = "".join(rand_chars)
        
        m = hashlib.md5()
        m.update(self.generated_string)
        self.md5 = m.digest()
 
    def __repr__(self):
        return self.generated_string
        
    def sha256(self,salt=''):
        return hashlib.sha256(self.generated_string+salt).hexdigest()
        
    def base64(self):
        return base64.b64encode(self.generated_string)
    
    def base64_md5(self):
        return base64.b64encode(self.md5)
        
