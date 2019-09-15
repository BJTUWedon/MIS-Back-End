# encoding: utf-8
from __future__ import division
from Project.models import *
from django.http import JsonResponse,HttpResponse
import hashlib
import os
import base64
import datetime
import json
from collections import Iterable
from django.utils import timezone
import subprocess
import time
import pexpect
from django.core.files.storage import FileSystemStorage
from wand.image import Image
from wand.color import Color
from PyPDF2 import PdfFileReader, PdfFileWriter
import math
import glob
import io
# Create your views here.

globalUserId = 0
def convert_video(video_input, video_output):
    # cmds = ['ffmpeg', '-i', video_input, video_output]
    # subprocess.Popen(cmds)


    cmd = 'ffmpeg -i'+' '+video_input+' '+video_output
    thread = pexpect.spawn(cmd)
    print ("started %s" % cmd)
    cpl = thread.compile_pattern_list([
        pexpect.EOF,
        "frame= *\d+",
        '(.+)'
    ])
    while True:
        i = thread.expect_list(cpl, timeout=None)
        if i == 0:  # EOF
            print
            "the sub process exited"
            break
        elif i == 1:
            frame_number = thread.match.group(0)
            print(frame_number)
            thread.close
        elif i == 2:
            # unknown_line = thread.match.group(0)
            # print unknown_line
            pass

def login(request):
    if request.method =="POST":
        try:
            username = json.loads(request.body)['username']
            password = json.loads(request.body)['password']
            if username:  # 确保用户名和密码都不为空

                username = username.strip()
                # 用户名字符合法性验证
                # 密码长度验证
                # 更多的其它验证.....
                try:
                    user = User.objects.get(username=username)
                    id = user.id

                    if user.password == hash_code(password):
                        message = "登陆成功！"
                        success = True
                        Userinfo = User.objects.get(id=id)
                        expires = Userinfo.authTime/1440
                        if expires == 0:
                            return JsonResponse({"success":False,"data":"You don`t have permission"}, safe=False)
                        token = hashlib.sha1(os.urandom(24)).hexdigest()
                        print(token)
                        Token.objects.create(username_id=id,Token=token,createDate=timezone.now(),expires=expires)
                        global globalUserId
                        globalUserId = id
                        Data = {"isManager": user.isManager, "token": token,"expires":expires}
                        # response = HttpResponse('ok')
                        # response.set_cookie(response,'ok','ok')
                        # print(token)
                        # return HttpResponse(json.dumps({"msg": "ok!"}))
                    else:
                        success = False
                        Data = "Wrong Password！"
                        return JsonResponse({"success": success, "data": Data})
                except Exception as e:
                    success = False
                    # Data = str(e)
                    # token = '1'
                    Data = "Username is wrong!"
                    return JsonResponse({"success": success, "data": Data})
                # except:
                #     success = False
                #     Data = "用户名不存在！"
        except Exception as e:
            success = False
            Data = str(e)
            token = '2'
            return JsonResponse({"success": success, "data": Data})
        resp = JsonResponse({"success":success,"data":Data}, safe=False)
        resp.set_cookie('token', token, expires=expires*60*60*24)
        resp.set_cookie('isManager', user.isManager, expires=expires*60*60*24)
        if user.isManager == False and user.authTime != 999999:
            User.objects.filter(id=id).update(authTime=0)
        return resp


def register(request):
    if request.method == "POST":
        Data = []
        try:
            username = json.loads(request.body)['username']
            password = json.loads(request.body)['password']
            email = json.loads(request.body)['email']
            same_name_user = User.objects.filter(username=username)
            if same_name_user:  # 用户名唯一
                Data = '用户已经存在，请重新选择用户名！'
                success = False
                return JsonResponse({"success": success, "data": Data})
                return JsonResponse({"success": success, "data": Data})
            User.objects.create(username=username, password=hash_code(password), email=email, createDate=datetime.datetime.now())
            message = "注册成功"
            success = True
            return JsonResponse({"success": success, "data": Data})
        except Exception as e:
            success = False
            Data = str(e)
        return JsonResponse({"success": success, "data": Data})

def hash_code(s):  # 加点盐
    h = hashlib.sha256()
    salt = 'mysite'
    c = salt+s
    h.update(c.encode())  # update方法只接收bytes类型
    return h.hexdigest()

def searchuser(request):
    if request.method == "GET":
        username = request.GET.get('username')
        users = User.objects.filter(username__icontains=username)
        jsonArry = []
        if users: #如果存在
            try:
                for user in users:
                    name = user.username
                    authtime = user.authtime
                    jsonObj = {"username":name,"authtime":authtime}
                    jsonArry.append(jsonObj)
            except:
                jsonArry.append({"username":name,"authtime":authtime})
        return JsonResponse(jsonArry, safe=False) #返回list的json

def change_info(request):
    if request.method == "GET":
        username = request.GET.get('username')
        password = request.GET.get('password')
        new_password = request.GET.get('New_password')
        message = "所有字段都必须填写！"
        if username and password:  # 确保用户名和密码都不为空
            username = username.strip()
            # 用户名字符合法性验证
            # 密码长度验证
            # 更多的其它验证.....
            try:
                user = User.objects.get(username=username)
                if user.password == hash_code(password):
                    User.objects.filter(username=username).update(password=hash_code(new_password))
                    message = "修改成功"
                    status = 1
                    return JsonResponse({"status": status})  # 成功修改
                else:
                    status = -1
                    message = "密码不正确！"
            except:
                status = 0
                message = "用户名不存在！"
                return JsonResponse({"status": status})
            return JsonResponse({"status": status})

def deluser(request):
    if request.method == "GET":
        username = request.GET.get('username')
        # try:
        File_User.objects.filter(username_id=username).delete()
        User.objects.filter(username=username).delete()
        status = 1
        # except:
        status = 0
        return JsonResponse({"status": status})


# def addkey(request):
#     if request.method == "GET":
#         key = request.GET.get('key')
#         authlevel = request.GET.get('authlevel')
#         authtime = request.GET.get('authtime')
#         files = request.GET.get('file') #每个文件访问时间，是一个二重Json文件，有fileaddress,time
#         new_key = Auth.objects.create()
#         new_key.key = key
#         new_key.authlevel = authlevel
#         new_key.authtime = authtime
#         new_file_user = File_User.objects.create()
#         for file in files:
#             new_file_user.key_id = key
#             new_file_user.filename_id = file.filename
#             new_file_user.time = file.time
#         new_key.save()
#         new_file_user.save()
#         return JsonResponse({"status":1})

# def delectkey(request): #访问到时间了就删除
#     if request.method == "GET":
#         key = request.GET.get('key')
#         File_User.objects.filter(key = key).delete()
#         Auth.objects.filter(key=key).delete()
#         return JsonResponse({"status": 1})
def buildauth(request):#创建访问权限
    if request.method == "GET":
        # try:
            username = request.GET.get('username')
            filename = request.GET.get('filename')
            time = request.GET.get('time')
            File_User.objects.create(username_id=username, filename_id=filename, time=time)
            status = 1
        # except:
        #     status = 0
            return JsonResponse({"status": status})

def delauth(request):#删除访问权限
    if request.method == "GET":
        username = request.GET.get('username')
        filename = request.GET.get('filename')
        File_User.objects.filter(username_id=username, filename_id=filename).delete()
        return JsonResponse({"status": 1})

def changeauth(request):#修改访问权限
    if request.method == "GET":
        username = request.GET.get('username')
        filename = request.GET.get('filename')
        time = request.GET.get('time')
        File_User.objects.filter(username_id=username, filename_id=filename).update(time=time)
        return JsonResponse({"status": 1})

def changeauthtime_user(request): #修改该用户访问权限
    if request.method == "GET":
        username = request.GET.get('username')
        authtime = request.GET.get('authtime')
        User.objects.filter(username=username).update(authtime=authtime)
        return JsonResponse({"status": 1})

def clearauth_user(request): #清空该用户权限
    if request.method == "GET":
        username = request.GET.get('username')
        try:
            authtime = 0
            File_User.objects.filter(username_id=username).delete()
            User.objects.filter(username=username).update(authtime=authtime)
            status = 1
        except:
            status = 0
    return JsonResponse({"status": status})

def searchauth_user(request): #查找该用户权限
    if request.method == "GET":
        username = request.GET.get('username')
        Auth_obj = File_User.objects.filter(username_id=username)
        AuthArray = []
        try:
            for auth in Auth_obj:
                filename = auth.filename_id
                time = auth.time
                authArray = {"filename":filename,"time": time}
                AuthArray.append(authArray)
            Result = {"username": username, "auth": AuthArray}
        except:
            Result = {"username": username, "auth": [{"filename":filename,"time": time}]}
        return JsonResponse(Result,safe=False)

def clearauth_file(request): #清空该文档权限
    if request.method == "GET":
        filename = request.GET.get('filename')
        try:
            File_User.objects.filter(filename_id=filename).delete()
            status = 1
        except:
            status = 0
    return JsonResponse({"status": status})

def searchauth_file(request): #查找该文件权限
    if request.method == "GET":
        filename = request.GET.get('filename')
        Auth_obj = File_User.objects.filter(filename_id=filename)
        AuthArray = []
        try:
            for auth in Auth_obj:
                username = auth.username_id
                time = auth.time
                authArray = {"username":username,"time": time}
                AuthArray.append(authArray)
            Result = {"filename":filename, "auth": AuthArray}
        except:
            Result = {"filename":filename, "auth": [{"username":username,"time": time}]}
        return JsonResponse(Result,safe=False)

# def searchauth(request): #查找权限
#     if request.method == "GET":
#         keyname = request.GET.get('keyname')
#         keys = Auth.objects.filter(key__icontains=keyname)
#         jsonArry= []
#         for key in keys:
#             authlevel = key.authlevel
#             authtime = key.authtime
#             files = File_User.objects.filter(key = key) #Json形式
#             filejson = []
#             for file in files:
#                 name = file.filename
#                 time = file.time
#                 filejson = {"filename": name, "time": time}
#                 filejson.append(filejson)
#             objArry = {"key":key, "authlevel":authlevel, "authtime":authtime, "file": filejson}
#             jsonArry.append(objArry)
#         return JsonResponse(jsonArry)  # 返回list的json

def addfile(request):
    if request.method == "GET":
        type = request.GET.get('type')
        file_obj = request.FILES.get('file')
        same_name = File.objects.filter(filename=file_obj.name)
        address = '/file/'
        if same_name:  # 用户名唯一
            return JsonResponse({"message":"文件名重复"})
        FileDB = File.objects.create()
        FileDB.filename = file_obj.name
        FileDB.type = type
        FileDB.save()
        fileaddress = address+file_obj.name
        with open(fileaddress,'wb')as f:
            for ffile in file_obj.chunks():
                f.write(ffile)
        return JsonResponse({"status": 1})

def delectfile(request):
    if request.method == "GET":
        filename = request.GET.get('filename')
        file = File.objects.filter(filename=filename)
        if file:
            print(file['src'])
            os.remove(file.src)
            File.objects.filter(filename=filename).delete()
            return JsonResponse({"status": 1})

def searchfile(request):
    if request.method == "GET":
        filename = request.GET.get('filename')
        files = File.objects.get(filename__icontains=filename)
        jsonArry = []
        try:
            for file in files:
                name = file.filename
                type = file.type
        except:
            name = files.filename
            type = files.type
        jsonObj = {"filename":name,"type":type}
        jsonArry.append(jsonObj)
        return JsonResponse(jsonArry,safe=False) #返回list的json

def grouplogin(request):
    if request.method == "GET":
        key = request.GET.get('key')
        try:
            code = base64.b32decode(key)
            username = code.split(':')[0]
            password = code.split(':')[1]
            if username and password:  # 确保用户名和密码都不为空

                username = username.strip()
                # 用户名字符合法性验证
                # 密码长度验证
                # 更多的其它验证.....
                try:
                    user = User.objects.get(username=username)
                    if user.password == hash_code(password):
                        message = "登陆成功！"
                        return JsonResponse({"status": 1}) #成功登陆
                        # return HttpResponse(json.dumps({"msg": "ok!"}))
                    else:
                        message = "密码不正确！"
                except:
                    message = "用户名不存在！"
                    return JsonResponse({"status": 0})
            return JsonResponse({"status": 0})
        except:
            return JsonResponse({"status": 0})

def buildgroup(request):
    if request.method == "GET":
        username = request.GET.get('username')
        password = request.GET.get('password')
        same_name_user = User.objects.filter(username=username)
        key = ""
        if same_name_user:  # 用户名唯一
            message = '用户已经存在，请重新选择用户名！'
            return JsonResponse({"status": 0, "key":key})
        new_user = User.objects.create()
        new_user.username = username
        new_user.password = hash_code(password)
        new_user.authtime = 0  # 注册新用户 默认无权限
        new_user.save()
        message = "注册成功"
        code = username+':'+password
        key = base64.b32encode(code)
        return JsonResponse({"status": 1, "key":key})  # 自动跳转到登录页面,返回可访问时间、访问等级

def getUserList(request):
    if request.method == "GET":
        Users = User.objects.all()
        Data = []
        try:
            success = True
            if Users:  # 数据库有数据
                if isinstance(Users, Iterable) == True:
                    for user in Users:
                        id = user.id
                        username = user.username
                        createDate = user.createDate
                        authTime = user.authTime #API新增
                        userinfo = {"id":str(id), "username":username, "createDate":createDate, "limit":authTime}#API新增
                        Data.append(userinfo)
                else:
                    id = Users.id
                    username = Users.username
                    createDate = Users.createDate
                    authTime = Users.authTime  # API新增
                    Data = {"id": str(id), "username": username, "createDate": createDate, "authTime": authTime}  # API新增
            else:
                pass
        except Exception as e:
            success = False
            Data = str(e)
        # response = HttpResponse("{'success': success, 'data': Data}",content_type="application/json")
        return JsonResponse({"success": success, "data": Data})
        # response = HttpResponse()
        # response['Age']=120
        # del response['Age']
        # response = HttpResponse(({"success": success, "data": Data}), content_type="application/json")
        # return response

def getFileList(request):
    if request.method == "GET":
        try:
            success = True
            token = request.COOKIES["token"]
            tokenInfo = Token.objects.get(Token=token)
            userid = tokenInfo.username_id
            Userinfo = User.objects.get(id=userid)
            creator = Userinfo.username
            isManager = Userinfo.isManager
            Data = []
            if(isManager==False):
                Fileinfo = File_User.objects.filter(username_id=userid).order_by('-filename_id')
                if Fileinfo:
                    for a in Fileinfo:
                        id = a.filename_id
                        file = File.objects.get(id=id)
                        id = file.id
                        filename = file.filename
                        content = file.content
                        type = file.type
                        createDate = file.createDate
                        if (filename[0:6] == "_fake_"):
                            info = {"id": filename, "title": filename, "content": content, "type": type,
                                    "createDate": createDate, "group": charIntoarray(file.group),"creator":creator}
                        else:
                            info = {"id": str(id), "title": filename, "content": content, "type": type,
                                    "createDate": createDate, "group": charIntoarray(file.group),"creator":creator}
                        # info = {"id":id, "title":filename, "content":content,"type":type,"createDate":createDate,"group":[]}
                        Data.append(info)
            else:
                Files = File.objects.all().order_by('-id')
                try:
                    if Files:  # 数据po库有数据
                        if isinstance(Files, Iterable) == True:
                            for file in Files:
                                id = file.id
                                filename = file.filename
                                content = file.content
                                type = file.type
                                createDate = file.createDate
                                if (filename[0:6]=="_fake_"):
                                    info = {"id": filename, "title": filename, "content": content, "type": type,"createDate": createDate,"group":charIntoarray(file.group),"creator":"wedon"}
                                else:
                                    info = {"id": str(id), "title": filename, "content": content, "type": type, "createDate": createDate,"group":charIntoarray(file.group),"creator":"wedon"}
                                # info = {"id":id, "title":filename, "content":content,"type":type,"createDate":createDate,"group":[]}
                                Data.append(info)
                        else:
                            id = Files.id
                            filename = Files.filename
                            content = Files.content
                            type = Files.type
                            createDate = Files.createDate
                            Data = {"id": str(id), "title": filename, "content": content, "type": type, "createDate": createDate,"group":charIntoarray(Files.group),"creator":"wedon"}
                            # Data = {"id": "_fake_asdsa", "title": filename, "content": content, "type": type,"createDate":createDate,"group":[111]}
                    else:
                        pass
                except Exception as e:
                    success = False
                    Data = str(e)
        except Exception as e:
            success = False
            Data = str(e)
        # response_data = {}
        # response_data['success'] = success
        # response_data['data'] = Data
        # response_data['userid'] = globalUserId
        # return HttpResponse(json.dumps(response_data), content_type="application/json")
        # Data = {"id": "_fake_", "title": "", "content": "", "type": "", "createDate": "",
        #         "group": ["111"]}
        return JsonResponse({"success": success, "data": Data,"userid":globalUserId},safe=False)
def postFile(request):
    if request.method =="POST":
        Data = []
        try:
            success = True
            id = json.loads(request.body)['id']
            # id = request.POST.get('id')
            try:
                type = json.loads(request.body)['file']
            except:
                type = json.loads(request.body)['type']
            title = json.loads(request.body)['title']
            content = json.loads(request.body)['content']
            authUserList = json.loads(request.body)['authUserList']#API需要新增time
            print(authUserList)
            if id == "-1":
                File.objects.create(type=type,filename=title, content=content,createDate=datetime.datetime.now())
                lastFile = File.objects.order_by('createDate')[0:1].get()
                filename_id = lastFile.id#如果重复上传 会出BUG
                print(filename_id)
                if isinstance(authUserList,Iterable)==True:
                    for authlist in authUserList:
                        File_User.objects.create(filename_id=filename_id,username_id=authlist['id'], time=authlist['limit'])
                    Data = {"title": title, "id": str(filename_id)}
                else:
                    File_User.objects.create(filename_id=filename_id, username_id=authUserList['id'],time=authUserList['limit'])
                    Data = {"title": title, "id": str(filename_id)}
            else:
                if type:
                    File.objects.filter(id=id).update(type=type, filename=title, content=content,createDate=datetime.datetime.now())
                else:
                    File.objects.filter(id=id).update(filename=title, content=content,createDate=datetime.datetime.now())
                File_User.objects.filter(filename_id=id).delete()
                if isinstance(authUserList, Iterable) == True:
                    for authlist in authUserList:
                        File_User.objects.create(filename_id=id, username_id=authlist['id'], time=authlist['limit'])
                        print(1)
                    Data = {"title": title, "id":str(id)}
                else:
                    File_User.objects.create(filename_id=id, username_id=authUserList['id'], time=authUserList['limit'])
                    Data = {"title": title, "id": str(id)}
        except Exception as e:
            success = False
            Data = str(e)
        return JsonResponse({"success": success, "data": Data})

def uploadFile(request):
    if request.method =="POST":
        Data = []
        try:
            success = True
            id = request.POST.get('id')
            print(id)
            title = request.POST.get('title','')
            content = request.POST.get('content','')
            type = request.POST.get('type','')
            file_obj = request.FILES['file']
            group = request.POST.get('group')
            name = os.path.splitext(file_obj.name)[0]
            address = os.path.splitext(file_obj.name)[-1]
            src = hash_code(name)+address #到时候修改成服务器的地址
            print("FIletype:"+address)
            print(src)
            if id == "-1":
                if address == '.pdf' or address == '.PDF': #切片操作
                    with open(src, 'wb')as f:
                        for ffile in file_obj.chunks():
                            f.write(ffile)
                    inputpdf = PdfFileReader(open(src, "rb"))
                    output = PdfFileWriter()
                    print("1")
                    # for i in range(inputpdf.numPages):
                    #     output.addPage(inputpdf.getPage(i))
                    # pdf_bytes = io.BytesIO()
                    # output.write(pdf_bytes)
                    # pdf_bytes.seek(0)
                    # img = Image(file=pdf_bytes, resolution=300)
                    # img.format = 'JPEG'
                    # img.compression_quality = 92
                    # img.background_color = Color("white")
                    # img.save(filename=src + "-page.jpeg")
                    # # img.save(filename=src + "-page%s.jpeg" % (i + 1))
                    # img.destroy()
                    for i in range(inputpdf.numPages):
                        output.addPage(inputpdf.getPage(i))
                        # output.encrypt(user_pwd="wyd",owner_pwd="None",use_128bit=True,allow_printing=False, allow_commenting=False,overwrite_permission=False)
                        pagesrc = src+"-page%s.pdf" % (i+1)
                        print(pagesrc)
                        with open(pagesrc, "wb") as outputStream: #页码
                            output.write(outputStream)
                    File.objects.create(filename=title, type=type, content=content, createDate=datetime.datetime.now(),src=r"http://lvmaozi.info:9999/" + src,group=group)

                    # for img in sorted(glob.glob(src+'*'))
                    #     imgdoc = fitz.open(img)
                    #     pdfbytes = imgdoc.convertToPDF()
                    #     imgpdf = fitz.open("pdf", pdfbytes)
                    #     doc.insertPDF(imgpdf)
                    # doc.save(".pdf")
                    # doc.close()
                else:
                    print('no video')
                    with open(src, 'wb')as f:
                        for ffile in file_obj.chunks():
                            f.write(ffile)
                    if address == '.avi' or address =='.AVI'or address =='.asf'or address =='.ASF' or address =='.wav'or address =='.WAV' or address =='.flv'or address =='.FLV' or address =='.siff'or address =='.SIFF':
                        print("filetype: video")
                        convert_video(src,hash_code(name)+'.mp4')
                        # time.sleep(5)
                        os.remove(src)
                        newsrc = hash_code(name)+'.mp4'
                        File.objects.create(filename=title, type=type, content=content,createDate=datetime.datetime.now(), src=r"http://lvmaozi.info:9999/"+newsrc,group=group)#我认为下面还要返回id
                    else:#不准确
                        print("filetype:img")
                        File.objects.create(filename=title, type=type, content=content, createDate=datetime.datetime.now(),src=r"http://lvmaozi.info:9999/" + src,group=group)

                lastFile = File.objects.order_by("-createDate")[0:1].get()
                id = lastFile.id
                print(id)
                Data = {"title": title, "id": str(id), "type":type}
            else:
                if address == '.pdf': #切片操作
                    inputpdf = PdfFileReader(open(src, "wb"))
                    for i in range(inputpdf.numPages):
                        output = PdfFileWriter()
                        output.addPage(inputpdf.getPage(i))
                        with open(src+"-page%s.pdf" % i, "wb") as outputStream: #页码
                            output.write(outputStream)
                    File.objects.filter(id=id).update(filename=title, type=type, content=content,createDate=datetime.datetime.now(),src=r"http://lvmaozi.info:9999/"+src,group=group)
                else:
                    with open(src, 'wb')as f:
                        for ffile in file_obj.chunks():
                            f.write(ffile)
                    if address == '.avi' or address =='.AVI'or address =='.asf'or address =='.ASF' or address =='.wav'or address =='.WAV' or address =='.flv'or address =='.FLV' or address =='.siff'or address =='.SIFF':
                        convert_video(src,hash_code(name)+'.mp4')
                        # time.sleep(5)
                        os.remove(src)
                        newsrc = hash_code(name)+'.mp4'
                        File.objects.create(filename=title, type=type, content=content,createDate=datetime.datetime.now(), src=r"http://lvmaozi.info:9999/"+newsrc,group=group)#我认为下面还要返回id
                    if address == '.jpg' or address == '.JPG' or address == '.png' or address == '.PNG' or address == '.gif' or address == '.GIF':#不准确
                        print("filetype:img")
                        File.objects.create(filename=title, type=type, content=content, createDate=datetime.datetime.now(),src=r"http://lvmaozi.info:9999/" + src,group=group)
                    else:
                        print("error")
                        success = False
                Data = {"title": title, "id": str(id), "type": type}
        except Exception as e:
            success = False
            Data = str(e)
        return JsonResponse({"success": success, "data": Data})

def postUser(request):
    if request.method =="POST":
        Data = []
        try:
            success = True
            id = json.loads(request.body)['id']
            username = json.loads(request.body)['username']
            email = json.loads(request.body)['email']
            try:
                password = json.loads(request.body)['password']
            except:
                pass
            limit = json.loads(request.body)['limit']#API请求参数新增 authtime
            if limit is None:
                limit = 999999
            print(limit)
            authFileList = json.loads(request.body)['authFileList']#API请求参数新增 time
            print(authFileList)
            if id == -1:
                User.objects.create(username=username, email=email, password=hash_code(password),createDate=datetime.datetime.now(),authTime=limit)
                username_id = User.objects.all()[0].id
                if isinstance(authFileList, Iterable) == True:
                    for authlist in authFileList:
                        if authlist['id'][0:6]=="_fake_":
                            fakeid = File.objects.get(filename=authlist['id']).id
                            File_User.objects.create(username_id=username_id, filename_id=fakeid,time=authlist['limit'])
                        else:
                            File_User.objects.create(username_id=username_id,filename_id=authlist['id'], time=authlist['limit'])
                else:
                    File_User.objects.create(username_id=username_id, filename_id=authFileList['id'],time=authFileList['limit'])
                # fakeFileInfo = FIle.objects.filter(filename__contains='fake')
                # for fakeinfo in fakeFileInfo:
                #     File_User.objects.create(username_id=username_id,filename_id=fakeinfo[id]) #创建文件夹权限表
            else:
                if password:
                    User.objects.filter(id=id).update(username=username, email=email, password=hash_code(password),createDate=datetime.datetime.now(),authTime=limit)
                else:
                    User.objects.filter(id=id).update(username=username, email=email,createDate=datetime.datetime.now(),authTime=limit)
                    # ,authtime=authtime

                for authFile in authFileList:
                    if authFile['id'][0:6] == "_fake_":
                        filename_id = File.objects.get(filename=authFile['id']).id
                        File_User.objects.filter(username_id=id, filename_id=filename_id).delete()
                        # fakeid = File.objects.get(filename=authlist['id']).id
                        # File_User.objects.create(username_id=username_id, filename_id=fakeid, time=authlist['limit'])
                fakefileinfo = File.objects.filter(filename__contains='fake')
                fakeinfolist=[]
                for fakefile in fakefileinfo:
                    fakefileid=fakefile.id
                    fakeinfolist.append(fakefileid)
                File_User.objects.filter(username_id=id).exclude(filename_id__in=fakeinfolist).delete()
                if isinstance(authFileList, Iterable) == True:
                    for authlist in authFileList:
                        if (authlist['id'][0:6]=="_fake_"):
                            filename_id = File.objects.get(filename=authlist['id']).id
                            print(filename_id)
                            File_User.objects.create(username_id=id, filename_id=filename_id, time=authlist['limit'])
                        else:
                            File_User.objects.create(username_id=id, filename_id=authlist['id'], time=authlist['limit'])
                else:
                    File_User.objects.create(username_id=id, filename_id=authFileList['id'], time=authFileList['limit'])
        except Exception as e:
            success = False
            Data = str(e)
        return JsonResponse({"success": success, "data": Data})

def getUser(request):
    if request.method =="POST":
        try:
            success = True
            id = json.loads(request.body)['userId']
            userInfo = User.objects.get(id=id)
            username = userInfo.username
            email = userInfo.email
            createDate = userInfo.createDate
            authFileList = []
            FileList = File_User.objects.filter(username_id=id)

            print(1)
            if isinstance(FileList, Iterable) == True:
                for authlist in FileList:
                    filename_id = authlist.filename_id
                    time = authlist.time
                    fakename = File.objects.get(id=filename_id).filename
                    if fakename[0:6]=="_fake_":
                        if time is not None:
                            jsonArray = {"id": fakename, "limit": float(time)}
                        else:
                            jsonArray = {"id": fakename, "limit": time}
                    else:
                        jsonArray = {"id": str(filename_id), "limit": float(time)}
                    authFileList.append(jsonArray)
                    print(3)
                Data = {"username": username, "email": email, "createDate": createDate,
                                "limit": userInfo.authTime, "authFileList": authFileList}
            else:
                filename_id = FileList.filename_id
                time = FileList.time
                fakename = File.objects.get(id=filename_id).filename
                if fakename[0:6] == "_fake_":
                    jsonArray = {"id": fakename, "limit": float(time)}
                else:
                    jsonArray = {"id": str(filename_id), "limit": float(time)}
                authFileList.append(jsonArray)
                Data = {"username":username,"email":email,"createDate":createDate,"limit":userInfo.authTime,"authFileList":authFileList}
                print(4)
            print(5)
            return JsonResponse({"success": success, "data": Data})
            # except:
            #     Data = {"username": username, "email": email, "createDate": createDate, "limit": userInfo.authTime,"authFileList": authFileList}
            #     print(2)
            #     return JsonResponse({"success": success, "data": Data})
        except Exception as e:
            success = False
            Data = str(e)
            return JsonResponse({"success": success, "data": Data})

def getFile(request):
    if request.method =="POST":
        try:
            success = True
            id = int(json.loads(request.body)['fileId'])
            fileInfo = File.objects.get(id=id)
            title = fileInfo.filename
            content = fileInfo.content
            createDate = fileInfo.createDate
            type = fileInfo.type
            src = fileInfo.src
            print(type)
            authUserList = []
            token = request.COOKIES["token"]
            # print(token)
            tokenInfo = Token.objects.get(Token=token)
            userid = tokenInfo.username_id

            if (User.objects.get(id=userid).isManager == False):
                #判断有无权限
                try:
                    FileList = File_User.objects.get(username_id=userid, filename_id=id)
                except:
                    return JsonResponse({"success": False, "data": "You can`t open this file"})
                #判断父文件夹有无全新啊
                thisUserFile = File.objects.get(id=id) #取出文件
                thisGroup = thisUserFile.group
                try:
                    thisFakeFile = File.objects.get(filename__contains='fake', group=thisGroup)
                    fakeid = thisFakeFile.id
                    limit = File_User.objects.get(filename_id=fakeid, username_id=userid).time
                except:
                    limit = File_User.objects.get(filename_id=id,username_id=userid).time
                if limit is None:
                    limit = File_User.objects.get(filename_id=id, username_id=userid).time
                if type == "pdf":
                    list = src.split("/")
                    totalPage = PdfFileReader(open(list[3], "rb")).numPages
                    timepage = int(math.ceil(float(limit)*totalPage))
                    page = '-page' + str(timepage) + '.pdf'
                    src = src + page
                try:
                    # if type=="pdf":
                    #     Fileinfo = File_User.objects.filter(filename_id=id)
                    #     if isinstance(Fileinfo, Iterable) == True:
                    #         for authlist in Fileinfo:
                    #             username_id = authlist.username_id
                    #             time = authlist.time
                    #             timepage = math.ceil(time)  # 向上取证
                    #             page = '-page' + str(int(timepage))+'.pdf'
                    #             jsonArray = {"id": str(username_id), "limit": float(time)}
                    #             authUserList.append(jsonArray)
                    #             src = src + page
                    #             print(src)
                    #     else:
                    #         print(2)
                    #         username_id = Fileinfo.username_id
                    #         time = Fileinfo.time
                    #         authUserList = [{"id": str(username_id), "limit": float(time)}]

                    Fileinfo = File_User.objects.filter(filename_id=id)
                    if isinstance(Fileinfo, Iterable) == True:
                        for authlist in Fileinfo:
                            username_id = authlist.username_id
                            time = authlist.time
                            jsonArray = {"id":str(username_id), "limit":float(time)}
                            authUserList.append(jsonArray)
                            print(1)
                    else:
                        print(2)
                        username_id = Fileinfo.username_id
                        time = Fileinfo.time
                        authUserList = [{"id": str(username_id), "limit":float(time)}]
                    Data = {"id":str(id),"title":title,"content":content,"src":src,"createDate":createDate,"type":type,"authUserList":authUserList,"limit":math.ceil(float(limit))}
                    print("普通账户")
                    print(limit)
                except Exception as e:
                    # print(3)
                    # success = False
                    # Data = str(e)
                    print("error")
                    time = FileList.time
                    Data = {"id": str(id), "title": title, "content": content, "src": src, "createDate": createDate,"type":type,
                            "authUserList": authUserList,"limit":math.ceil(float(limit))}
            if (User.objects.get(id=userid).isManager == True):
                    try:
                        thisUserFile = File_User.objects.get(filename_id=id, username_id=userid)
                        limit = thisUserFile.time
                        print('try1')
                    except:
                        limit = 1
                        print(limit)
                    Fileinfo = File_User.objects.filter(filename_id=id)
                    if isinstance(Fileinfo, Iterable) == True:
                        for authlist in Fileinfo:
                            username_id = authlist.username_id
                            time = authlist.time
                            jsonArray = {"id":str(username_id), "limit":float(time)}
                            authUserList.append(jsonArray)
                            print(1)
                    else:
                        print(2)
                        username_id = Fileinfo.username_id
                        time = Fileinfo.time
                        authUserList = [{"id": str(username_id), "limit": float(time)}]
                    Data = {"id": str(id), "title": title, "content": content, "src": src, "createDate": createDate,
                                "type": type, "authUserList": authUserList, "limit": math.ceil(float(limit))}
                    print("管理员账户")
                    print(limit)
        except Exception as e:
            success = False
            Data = str(e)
        return JsonResponse({"success": success, "data": Data})

def deleteUser(request):
    if request.method =="POST":
        Data = []
        try:
            success = True
            id = json.loads(request.body)['id']
            User.objects.filter(id = id).delete()
        except Exception as e:
            success = False
            Data = str(e)
        return JsonResponse({"success": success, "data": Data})

def deleteFile(request):
    if request.method =="POST":
        Data=[]
        try:
            success = True
            id = json.loads(request.body)['id']
            file = File.objects.get(id=id)
            list = file.src.split("/")
            File.objects.filter(id=id).delete()
            if file.type == "pdf":
                filenames = glob.glob(list[3]+'*')
                for filename in filenames: os.remove(filename)
            else:
                os.remove(list[3])
        except Exception as e:
            success = False
            Data = str(e)
        return JsonResponse({"success": success, "data": Data})


def logout(request):
    if request.method =="GET":
        Data=[]
        try:
            success = True

            resp = JsonResponse({"success": success, "data": Data}, safe=False)
            resp.delete_cookie('token')
            resp.delete_cookie('isManager')
            return resp
        except Exception as e:
            success = False
            Data = str(e)
            return JsonResponse({"success": success, "data": Data})


def arrayIntochar(array):
    # char = array.join("|")
    char = ','.join(array)
    return char

def charIntoarray(char):
    if char == "":
        return []
    array = char.split(",")
    return array
def postFileList(request):
    if request.method =="POST":
        Data=[]
        try:
            success = True
            arrays = json.loads(request.body)
            # for array in arrays:
            #     id = array['id']
            #     if (id[0:6]=="_fake_"):
            #         File.objects.filter(filename__contains="_fake_").delete() #一检测到就删除然后跳出循环
            #         continue
            for array in arrays:
                id = array['id']
                group = array['group']
                if (id[0:6]=="_fake_"):
                    fakeinfo = File.objects.filter(filename__contains="_fake_")
                    result = 0
                    for fake in fakeinfo: #防止重复
                        oldgroup = fake.group
                        if (oldgroup==arrayIntochar(group)):
                            result = 1
                            continue
                    if (result ==1):
                        continue
                    filename = "_fake_"+hash_code(str(datetime.datetime.now()))
                    File.objects.create(filename=filename,group=arrayIntochar(group),createDate=datetime.datetime.now(),type="folder")
                    #更新权限表的问题
                    filename_id = File.objects.all().order_by('-id')[0].id
                    print(filename_id)
                    Userinfo = User.objects.all()
                    for authlist in Userinfo:
                        File_User.objects.create(filename_id=filename_id,username_id=authlist.id) #创建文件夹权限表

                else:
                    File.objects.filter(id=id).update(group=arrayIntochar(group)) #group全量更新
        except Exception as e:
            success = False
            Data = str(e)
        return JsonResponse({"success": success, "Data":Data})

def deleteFolder(request):
    if request.method =="POST":
        Data=[]
        try:
            success = True
            infos = json.loads(request.body)
            for info in infos:
                id = info['id']
                print(id)
                file = File.objects.get(filename=id)
                File_User.objects.filter(filename_id=file.id).delete()
                File.objects.filter(filename=id).delete()
        except Exception as e:
            success = False
            Data = str(e)
        return JsonResponse({"success": success, "data": Data})
