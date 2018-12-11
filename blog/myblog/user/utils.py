from hashlib import sha256
import random, string
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from . import models
from django.core.cache import cache

# 加密
def hash_256(pwd):
    h = sha256()
    # 此处必须声明encode
    h.update(pwd.encode(encoding='utf-8'))
    h = h.hexdigest()
    return h


# 验证码
def getRandomChar(count=4):
    # 生成随机字符串
    # string 模块包含各种字符串，以下为小写字母加数字
    ran = string.ascii_lowercase + string.digits
    char = ''
    for i in range(count):
        char += random.choice(ran)
    return char


# 返回一个随机的 RGB 颜色
def getRandomColor():
    return (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))


def create_code():
    # 创建图片，模式，大小，背景色
    img = Image.new('RGB', (120, 30), (255, 255, 255))
    # 创建画布
    draw = ImageDraw.Draw(img)
    # 设置字体
    font = ImageFont.truetype('Lobster-Regular.ttf', 25)
    code = getRandomChar()
    # 将生成的字符画在画布上
    for t in range(4):
        draw.text((30 * t + 5, 0), code[t], getRandomColor(), font)
    # 生成干扰点
    for _ in range(random.randint(0, 50)):
    # 位置，颜色
        draw.point((random.randint(0, 120),
                random.randint(0, 30)), fill=getRandomColor())
    # 使用模糊滤镜使图片模糊
    # img = img.filter(ImageFilter.BLUR)
    # 保存
    # img.save(''.join(code)+'.jpg','jpeg')
    return img, code


#缓存主页
def cache_allarticle(ischange=False):
    articles = cache.get('allarticles')
    print('从缓存中查找主页数据')
    if articles is None or ischange:
        print('缓存中没有数据，查找数据库')
        articles = models.Article.objects.all().order_by('-publishtime')
        cache.set('allarticles', articles)
        print('从数据库中查到数据，并保存到缓存中')
    return articles

#缓存个人文章
def cache_article(request,ischange=False):
    articles = cache.get('article_list')
    print('从缓存中查找个人文章数据')
    if articles is None or ischange:
        print('缓存中没有数据，查找数据库')
        user = request.session['loginuser']
        articles = models.Article.objects.filter(auth=user).order_by('-publishtime')
        cache.set('article_list', articles)
        print('从数据库中查到数据，并保存到缓存中')

    return articles