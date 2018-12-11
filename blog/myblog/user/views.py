from django.shortcuts import render, redirect, reverse
from django.db import models
from django.http import HttpResponse
from . import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from .utils import hash_256, create_code
from io import BytesIO
from django.core.cache import cache
from . import utils
from django.contrib.auth.decorators import login_required
from django.conf import settings
#检查用户
# from django.contrib.auth import authenticate,login,logout
# 分页插件在 core 包中
from django.core.paginator import Paginator
# 导入 setting 配置文件
from django.conf import settings


# 主页
def index(request):
    #当前页
    pageNow=int(request.GET.get('pageNow',1))
    # 展示所有文章
    articles = utils.cache_allarticle()
    pagesize=settings.PAGESIZE
    # 文章按点击量排序 排名前100
    paginator=Paginator(articles,pagesize)
    page=paginator.page(pageNow)
    hotpeoples = models.Article.objects.filter().order_by('-count')[:100]
    sethot = set()
    # 讲文章的作者添加到set
    for i in hotpeoples:
        sethot.add(i.auth)
    return render(request, 'user/index.html', {'page': page, 'sethot': sethot})


# 注册函数
def register(request):
    if request.method == 'GET':
        return render(request, 'user/register.html', {'msg': '请输入信息'})

    else:
        name = request.POST['name'].strip()
        password = request.POST['pwd'].strip()
        confirm = request.POST['confirm'].strip()
        code = request.POST['code'].strip()
        if name == '':
            return render(request, 'user/register.html', {'msg': '用户名不能为空！'})
        if len(password) < 4:
            return render(request, 'user/register.html', {'msg': '密码小于四位'})
        if password != confirm:
            return render(request, 'user/register.html', {'msg': '两次密码不一致！'})

        if request.session['code'].upper() != code.upper():
            return render(request, 'user/register.html', {'msg': '验证码错误'})
        try:
            # 判断用户名是否已注册 get 查找到0或多条都会报错
            models.User.objects.get(name=name)
            return render(request, 'user/register.html', {'msg': '用户名已存在'})
        except:
            pwd = hash_256(password)
            # 这种方式每次加密结果不同
            # pwd=make_password(password,None,'pbkdf2_sha256')
            users = models.User(name=name, pwd=pwd)

            users.save()
            # 跳转到登录页面

            # return redirect(reverse('user:login',kwargs={'msg':'注册成功，请登录！！'}))
            return redirect(reverse('user:login'))


# 登录
def login(request):
    if request.method == 'GET':
        request.session['num'] = 0
        try:
            next_url = request.GET['next']
        except:
            next_url = '/'

        return render(request, 'user/login.html', {'msg': '请填写登录信息！', 'next_url': next_url})
    elif request.method == 'POST':
        request.session['num'] += 1
        name = request.POST['name'].strip()
        pwd = request.POST['pwd'].strip()
        next_url = request.POST.get('next', '/')
        # 判断验证码
        if request.session['num'] > 2:
            print(request.session['num'], '登录错误次数')
            try:
                code = request.POST['code'].strip()
                if request.session['code'].upper() != code.upper():
                    return render(request, 'user/login.html', {'msg': '验证码错误'})
                else:
                    request.session['num'] = 0
            except:
                return render(request, 'user/login.html', {'msg': '验证码不能为空'})

        # 判断用户
        #这种方式检测密码 跟 自己写的加密方式不同 不能判断用户
        # user1 = authenticate(name=name, pwd=pwd)
        user = models.User.objects.filter(name=name)
        if len(user) == 0:
            return render(request, 'user/login.html', {'msg': '用户名不存在'})
        # 判断密码
        # if user[0].pwd == hash_256(pwd):
        if user[0].pwd == hash_256(pwd):
            # 跳转到首页
            request.session['loginuser'] = user[0]
            return redirect(next_url)

            # 向url传参数
            # return redirect(reverse('user:index',kwargs={'u_id':user[0].id}))
            # return redirect(reverse('user:index'))
            # return render(request, 'user/index.html', {'user': user[0]})
        else:
            return render(request, 'user/login.html', {'msg': '用户名或密码错误'})




# 展示个人信息

def showinfo(request):
    user = request.session['loginuser']
    return render(request, 'user/showinfo.html', {'user': user})


# 展示所有人信息

def showlist(request):
    userlist = models.User.objects.all()
    return render(request, 'user/showlist.html', {'userlist': userlist})


# 修改资料

def changeinfo(request):
    user = request.session['loginuser']
    if request.method == 'GET':
        return render(request, 'user/changeinfo.html', {'user': user})

    else:
        nickname = request.POST['nickname'].strip()
        age = request.POST['age'].strip()
        email = request.POST['email'].strip()
        phone = request.POST['phone'].strip()
        sex = request.POST['sex'].strip()

        if nickname == '':
            return render(request, 'user/changeinfo.html', {'msg': '昵称不能为空'})
        # 年龄要判断
        if age == '' or int(age) < 0 or int(age) > 120:
            return render(request, 'user/changeinfo.html', {'msg': '年龄输入有误'})
        if email == '':
            return render(request, 'user/changeinfo.html', {'msg': '邮箱不能为空'})
        if phone == '':
            return render(request, 'user/changeinfo.html', {'msg': '手机号不能为空'})

        try:
            user.nickname = nickname
            user.age = age
            user.email = email
            user.phone = phone
            user.sex = sex
            user.save()
            request.session['loginuser'] = user
            # 重定向到个人信息页面
            return redirect('/showinfo/')
        except Exception as e:
            print(e)
            return render(request, 'user/changeinfo.html', {'msg': '信息修改失败！！！'})


# 修改头像

def changeavatar(request):
    user = request.session['loginuser']
    if request.method == 'GET':
        return render(request, 'user/changeinfo.html', {'user': user})

    else:
        avatar = request.FILES['avatar']
        try:
            user.avatar = avatar
            user.save()
            # 更新 session 数据
            request.session['loginuser'] = user
            return redirect('/showinfo/')
        except:
            return render(request, 'user/changeinfo.html', {"msg": '头像修改失败！！'})


# 修改密码

def changepwd(request):
    user = request.session['loginuser']
    if request.method == 'GET':
        return render(request, 'user/changeinfo.html', {'user': user})

    else:
        oldpwd = request.POST['oldpwd']
        newpwd = request.POST['newpwd']
        confirm = request.POST['confirm']

        if newpwd != confirm:
            return render(request, '/user/changeinfo.html', {'msg': '输入的密码不一致'})
        if hash_256(oldpwd) != user.pwd:
            return render(request, '/user/changeinfo.html', {'msg': '旧密码错误'})
        try:
            user.pwd = hash_256(newpwd)
            user.save()
            request.session['loginuser'] = user
            # 重定向到登录页面
            return redirect('/logout/')
        except:
            return render(request, 'user/changeinfo.html', {"msg": '密码修改失败！！'})


# 用户退出

def logout(request):
    del request.session['loginuser']
    return redirect('/login/')


# 添加文章

def article_add(request):
    auth = request.session['loginuser']
    if request.method == 'GET':
        return render(request, 'user/article_add.html')
    else:
        title = request.POST['title'].strip()
        content = request.POST['content'].strip()

        if title == '':
            return render(request, 'user/article_add.html', {'msg': '标题不能为空'})
        if content == '':
            return render(request, 'user/article_add.html', {'msg': '内容不能为空'})
        try:
            article = models.Article(title=title, content=content, auth=auth)
            article.save()
            # 更新文章缓存
            utils.cache_allarticle(ischange=True)
            utils.cache_article(request, ischange=True)

            # 重定向到文章详情页面
            return redirect(reverse('user:article_show', kwargs={'a_id': article.id}))
        except Exception as e:
            print(e, '发表文章报错------------')
            return render(request, 'user/article_add.html', {'msg': '文章保存失败'})


# 文章修改

def article_update(request, a_id):
    article = models.Article.objects.get(pk=a_id)
    if request.method == 'GET':
        return render(request, 'user/article_update.html', {'article': article})
    else:
        title = request.POST['title'].strip()
        content = request.POST['content'].strip()

        if title == '':
            return render(request, 'user/article_add.html', {'msg': '标题不能为空'})
        if content == '':
            return render(request, 'user/article_add.html', {'msg': '内容不能为空'})
        try:
            article.content = content
            article.title = title
            article.save()
            # 更新文章缓存
            utils.cache_allarticle(ischange=True)
            utils.cache_article(request, ischange=True)
            # 重定向到文章详情页面
            return redirect(reverse('user:article_show', kwargs={'a_id': article.id}))
        except Exception as e:
            print(e, '文章修改失败')
            return render(request, 'user/article_update.html', {'msg': '文章修改失败'})


# 删除文章

def article_del(request, a_id):
    article = models.Article.objects.get(pk=a_id)
    article.delete()
    # 重定向到文章详情页面
    # 更新文章缓存
    utils.cache_allarticle(ischange=True)
    utils.cache_article(request, ischange=True)
    return redirect('user:article_list')
    # return render(request,'user/article_list.html',{'msg':'文章删除成功'})



# 展示别人所有文章
def article_other(request, u_id):
    user = models.User.objects.get(pk=u_id)
    articles = models.Article.objects.filter(auth=user).order_by('-count')
    # articles = models.Article.objects.getlist(auth_id=u_id)
    return render(request, 'user/article_other.html', {'articles': articles})


# 展示个人所有文章

def article_list(request):
    articles = utils.cache_article(request)

    return render(request, 'user/article_list.html', {'articles': articles})


# 展示文章详情
def article_show(request, a_id):
    at = models.Article.objects.get(pk=a_id)
    # 文章点击量
    at.count += 1
    at.save()

    utils.cache_article(request, ischange=True)

    return render(request, 'user/article_show.html', {'at': at})


# 获取验证码
def get_code(request):
    img, code = create_code()
    f = BytesIO()
    request.session['code'] = code
    img.save(f, 'PNG')
    return HttpResponse(f.getvalue())




