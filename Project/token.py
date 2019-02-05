from Project.models import *
from django.http import JsonResponse,HttpResponse
import hashlib
import os
import base64
import datetime
import json
from collections import Iterable

def task():
   # tokenInfo = Token.objects.all()
   # if tokenInfo:
   #     for token in tokenInfo:
   #         if token.createDate>=-datetime.datetime.now()-datetime.timedelta(days=1): #一天失效
   #              Token.objects.filter(Token=token.Token).delete()
   #         else:
   #             pass
   print(12313)
