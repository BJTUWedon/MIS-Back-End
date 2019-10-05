from django.db import models

# Create your models here.
# class Auth(models.Model):
#     """Auth Table"""
#     key = models.CharField(primary_key=True, max_length=100, default="")
#     authlevel = models.IntegerField()
#     authtime = models.IntegerField()
#     def __unicode__(self):
#         return self.key


class User(models.Model):
    """User Table"""
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=250)
    authTime = models.IntegerField(default=0)
    createDate = models.DateTimeField(default="")
    email = models.EmailField(default="")
    isManager = models.BooleanField(default=False)
    group = models.CharField(max_length=250, default="")
    def __unicode__(self):
        return self.username

class File(models.Model):
    """File Table"""
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=128, default="")
    content = models.CharField(max_length=250, default="")
    type = models.CharField(max_length=128)
    createDate = models.DateTimeField(default="")
    src = models.URLField(default="")
    group = models.CharField(max_length=250, default="")
    def __unicode__(self):
        return self.filename

class File_User(models.Model):
    id = models.AutoField(primary_key=True)
    filename = models.ForeignKey(File)
    username = models.ForeignKey(User)
    time = models.DecimalField(max_digits=10,decimal_places=2,null=True)
    timeLimit = models.IntegerField(default=0,null=True)
    auth = models.IntegerField(default=0)

class Token(models.Model):
    Token = models.CharField(max_length=250)
    username = models.ForeignKey(User)
    createDate = models.DateTimeField()
    expires = models.DecimalField(max_digits=20,decimal_places=9)