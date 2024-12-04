from django.contrib.auth.models import User
from .models import *

def users_and_projects(request):
    if request.user.is_authenticated:
        access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    else:
        access=''
    return {'access': access}