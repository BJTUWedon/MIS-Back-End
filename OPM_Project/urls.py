"""OPM_Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https:docs.djangoproject.comen1.11topicshttpurls
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from Project.views import *

urlpatterns = [
    url(r'^admin$', admin.site.urls),
    url(r'^login$', login),
    url(r'^register$', register),
    url(r'^searchuser$', searchuser),
    url(r'^deluser$', deluser),
    url(r'^buildauth$', buildauth),
    url(r'^changeinfo$', change_info),
    url(r'^delauth$', delauth),
    url(r'^changeauth$', changeauth),
    url(r'^changeauthtime$', changeauthtime_user),
    url(r'^clearauth$', clearauth_user),
    url(r'^searchauth_user$',searchauth_user),
    url(r'^clearauth_file$', clearauth_file),
    url(r'^searchauth_file$', searchauth_file),
    url(r'^addfile$', addfile),
    url(r'^delfile$', delectfile),
    url(r'^searchfile$', searchfile),
    url(r'^grouplogin$', grouplogin),
    url(r'^buildgroup$', buildgroup),
    url(r'^getUserList$', getUserList),
    url(r'^getFileList$', getFileList),
    url(r'^postFile$', postFile),
    url(r'^uploadFile$',uploadFile),
    url(r'^postUser$', postUser),
    url(r'^getUser$', getUser),
    url(r'^getFile$', getFile),
    url(r'^deleteUser$', deleteUser),
    url(r'^deleteFile', deleteFile),
    url(r'^logOut', logout),
    url(r'^postFileList',postFileList),
    url(r'^deleteFolder',deleteFolder),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
