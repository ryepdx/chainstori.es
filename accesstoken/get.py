from flask.ext.login import current_user

def machine(request):
    if current_user.is_authenticated():
        return { "data": { "token": current_user.get_auth_token() } }
    return { "error": "Current user is not authenticated." }
