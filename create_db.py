from user.models import *
from accesstoken.models import *
from snippet.models import *
from story.models import *
from chainstories import db
db.create_all()
