from django.db import models
from tinymce.models import HTMLField

# Create your models here.


class User(models.Model):
    id=models.AutoField(primary_key='True',verbose_name='标识')
    name=models.CharField(max_length=50,unique=True,null=False)
    age=models.IntegerField(null=False,default=18)
    pwd=models.CharField(max_length=100,null=False)
    nickname=models.CharField(max_length=100,null=False,default='匿名用户')
    email=models.CharField(max_length=100,null=False,default='110@qq.com')
    sex=models.CharField(max_length=100,default='男')
    phone=models.CharField(max_length=100,default='110')
    status=models.IntegerField(default=1,verbose_name='用户状态')
    #设置头像存放在根静态文件夹下 ，默认头像放在子模块static 下
    avatar=models.ImageField(upload_to='static/user/avatar',default='static/user/avatar/default.jpg')


    def __str__(self):
        return self.name


class Article(models.Model):
    id=models.AutoField(primary_key=True,verbose_name='标识')
    title=models.CharField(max_length=255,verbose_name='标题')
    content=HTMLField(verbose_name='内容')
    # content=models.TextField(verbose_name='内容')
    count=models.IntegerField(default=0,verbose_name='点击量')
    # 文章发表时间
    publishtime = models.DateTimeField(auto_now_add=True, verbose_name='发表时间')
    modifytime = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    auth=models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='作者外键')


    def __str__(self):
        return self.title