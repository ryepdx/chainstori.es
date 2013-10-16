import string, random
from accesstoken.models import AccessToken
from chainstories import db, login_manager

LOGGED_OUT = "You are now logged out."
LOGGED_IN = "You are now logged in."
TOKEN_SIZE = 20
TOKEN_CHARS = string.ascii_uppercase + string.ascii_lowercase + string.digits

def generate_token(size = TOKEN_SIZE, chars = TOKEN_CHARS):
    ''' Generates a random token of <size> characters, using the characterset
    defined by the "chars" array.

    Example:
    >>> generate_token(size = 1, chars = ['a'])
    'a'
    >>> generate_token(size = 10, chars = ['a'])
    'aaaaaaaaaa'
    '''
    return ''.join(random.choice(chars) for x in range(size))

def create_for(user_obj):
    access_token = AccessToken(user_obj, generate_token())
    db.session.add(access_token)
    db.session.commit()
    return access_token

@login_manager.token_loader
def token_loader(token):
    token_obj = AccessToken.query.filter_by(token = token).first()

    if token_obj:
        return token_obj.user
    
    return None

if __name__ == '__main__':
    import doctest
    doctest.testmod()
