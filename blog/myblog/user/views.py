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
from django.http import JsonResponse



# 检查用户
# from django.contrib.auth import authenticate,login,logout
# 分页插件在 core 包中
from django.core.paginator import Paginator
# 导入 setting 配置文件
from django.conf import settings
from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


# 主页
def index(request):
    # 当前页
    pageNow = int(request.GET.get('pageNow', 1))
    # 展示所有文章
    articles = utils.cache_allarticle()
    pagesize = settings.PAGESIZE
    # 文章按点击量排序 排名前100
    paginator = Paginator(articles, pagesize)
    page = paginator.page(pageNow)
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
        # 这种方式检测密码 跟 自己写的加密方式不同 不能判断用户
        # user1 = authenticate(name=name, pwd=pwd)
        user = models.User.objects.get(name=name)
        if user is None :
            return render(request, 'user/login.html', {'msg': '用户名不存在'})
        # 判断密码
        # if user[0].pwd == hash_256(pwd):
        if user.pwd == hash_256(pwd):
            # 跳转到首页
            print(next_url)
            # login(request,user)
            request.session['loginuser'] = user
            return redirect(next_url)

            # 向url传参数
            # return redirect(reverse('user:index',kwargs={'u_id':user[0].id}))
            # return redirect(reverse('user:index'))
            # return render(request, 'user/index.html', {'user': user[0]})
        else:
            return render(request, 'user/login.html', {'msg': '用户名或密码错误'})


# 展示个人信息
@login_required
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
    print(a_id,111111111)
    user = request.session['loginuser']
    pl = models.Judge.objects.filter(article_id=a_id)
    print(pl,222222222222222222222)
    #文章评论
    if request.method == 'GET':
        return render(request, 'user/article_show.html', {'pinglun': pl,'at':at})
    elif request.method == 'POST':
        ps = request.POST['pinglun'].strip()
        if ps == '':
            return render(request,'user/article.html',{'msg1':'评论为空--'})
        pinglun = models.Judge(content=ps, article=at, user=user)
        pinglun.save()
    utils.cache_article(request, ischange=True)
    pls = models.Judge.objects.filter(article_id=a_id)
    return render(request, 'user/article_show.html', {'at': at,'pinglun':pls})


# 获取验证码
def get_code(request):
    img, code = create_code()
    f = BytesIO()
    request.session['code'] = code
    img.save(f, 'PNG')
    return HttpResponse(f.getvalue())


# 邮箱注册
def reg_email(request):
    if request.method == "GET":
        return render(request, "user/register.html", {})
    else:
        email = request.POST["email"].strip()
        password = request.POST.get("pwd").strip()
        confirmpwd = request.POST.get("confirm").strip()
    # 数据校验
    if len(email) < 1:
        return render(request, "user/register.html", {"msg": "用户邮箱为空！！"})
    if len(password) < 4:
        return render(request, "user/register.html", {"msg": "长度小于 4 位！！"})
    if password != confirmpwd:
        return render(request, "user/register.html", {"msg": "两次密码不一致！！"})
    try:
        user = models.User.objects.get(name=email)
        return render(request, "user/register.html", {"msg": "名称已经存在"})
    except:
        password = utils.hash_256(password)
        user = models.User(name=email, pwd=password, nickname=email, email=email)
    try:
        user.save()
        try:
            # 保存成功，发送邮件
            m_title = "wqx测试电商账号激活邮件"
            m_msg = "点击激活您的账号"
            # 调用 JWT 来加密和解密需要的数据
            serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
            code = serializer.dumps({"confirm": user.id}).decode("utf-8")
            href = "http://ww.ljh.com/blog/active/" + code + "/"
            m_html = '<a href="' + href + '" target="_blank">马上点击激活，一个小时内有效</a>'
            send_mail(m_title, m_msg, settings.EMAIL_FROM, [email], html_message=m_html)
            return render(request, "user/login.html", {"msg": "恭喜您，注册成功，请登录邮箱激活账号！！"})
        except Exception as e:
            print(e,111111111111111)
            return render(request, "user/login.html", {"msg": "恭喜您，注册成功，邮箱发送失败，请点击重新发送"})
    except Exception as e:
        return render(request, "user/register.html", {"msg": "注册失败，请重新注册，或者联系管理员"})


def active(request, token):
    serializer = Serializer(settings.SECRET_KEY, 3600)
    try:
        info = serializer.loads(token)
        active_id = info["confirm"]
        user = models.User.objects.get(pk=active_id)
        user.is_active = True
        user.save()
        return render(request, "user/login.html", {"msg": "恭喜您，激活账号成功，请登录！！"})
    except Exception as e:
        return HttpResponse("激活失败")
#
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
@csrf_exempt
def test1(request):
    if request.method=='GET':
        return render(request,'user/testajax.html',)
    if request.method=='POST':
        data=dict()
        data['msg']={'name':'wqx','age':18}
        return JsonResponse(data)


from django.core.serializers import serialize,deserialize
@csrf_exempt
def test(request):
    if request.method=='GET':

        return render(request,'user/testajax.html',)
    if request.method=='POST':
        id = request.POST['id']
        print(id,3333333333333333333333)
        users=models.Article.objects.all()
        users=serialize('json',users,fields=('title','content'))
        return HttpResponse(users)
        # return JsonResponse(users,safe=False)

        # serialize('json',users,fields=('name','nickname'))




#ajax 检查名字
def checkname(request):
    name=request.GET['name'].strip()
    try:
        user=models.User.objects.get(name=name)
        print(user,000000000000000)
        return JsonResponse({'msg':'该账号已存在,请更换 ','success':False})
    except:
        return JsonResponse( {'msg': '该账号可用','success':True})


#ajax 检查名字
def checkemail(request):
    email=request.GET['email'].strip()
    try:
        user=models.User.objects.get(name=email)
        return JsonResponse({'msg':'该账号已存在,请更换 ','success':False})
    except:
        return JsonResponse( {'msg': '该账号可用','success':True})


