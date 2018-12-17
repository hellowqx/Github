from . import views
from django.conf.urls import url


app_name='user'
urlpatterns=[

    url(r'^changeinfo/$',views.changeinfo,name='changeinfo'),
    url(r'^changeavatar/$',views.changeavatar,name='changeavatar'),
    url(r'^changepwd/$',views.changepwd,name='changepwd'),
    url(r'^login/$',views.login,name='login'),
    url(r'^register/$',views.register,name='register'),



    url(r'^article_add/$',views.article_add,name='article_add'),
    url(r'^article_update/(?P<a_id>\d+)/$',views.article_update,name='article_update'),
    url(r'^article_del/(?P<a_id>\d+)/$',views.article_del,name='article_del'),
    url(r'^article_list/$',views.article_list,name='article_list'),
    #别人所有文章
    url(r'^article_other/(?P<u_id>\d+)/$',views.article_other,name='article_other'),
    url(r'^article_show/(?P<a_id>\d+)/$',views.article_show,name='article_show'),

    url(r'^get_code/$',views.get_code,name='get_code'),
    url(r'^checkname/$',views.checkname,name='checkname'),
    url(r'^checkemail/$',views.checkemail,name='checkemail'),
    #邮箱
    url(r"^reg_email/$", views.reg_email, name="reg_email"),
    url(r"^active/(?P<token>.*)/$", views.active, name="active"),
    url(r'^logout/$',views.logout,name='logout'),
    url(r'^showinfo/$',views.showinfo,name='showinfo'),
    url(r'^showlist/$',views.showlist,name='showlist'),
    url(r'^index/$',views.index,name='index'),
    url(r'^test/$',views.test,name='test'),
    url(r'^$', views.index, name='index'),
]