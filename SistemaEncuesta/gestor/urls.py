from django.conf.urls import url
from . import views
from django.contrib.auth.views import login
app_name = 'gestor'
urlpatterns = [
    url(r'^inicio/$', views.index, name='inicio'),
    url(r'^responder/(?P<id_encuesta>[0-9]+)/$', views.responder_encuesta, name='responder_encuesta'),
    url(r'^editar/(?P<id_encuesta>[0-9]+)/$',views.editar_encuesta, name='editar_encuesta'),
    url(r'^agregar/pregunta/(?P<id_encuesta>[0-9]+)/$', views.agregar_pregunta, name='agregar_pregunta'),
    url(r'^agregar/respuesta/(?P<id_encuesta>[0-9]+)/(?P<id_pregunta>[0-9]+)/$', views.agregar_respuesta, name='agregar_respuesta'),
    url(r'^$', views.login, name='login'),
    url(r'^administracion/(?P<id_usuario>[0-9]+)/$', views.administracion, name='administrar'),
    url(r'^agregar/encuesta/(?P<id_usuario>[0-9]+)/$', views.agregar_encuesta, name='agregar_encuesta'),
    url(r'^ver/(?P<id_encuesta>[0-9]+)/$', views.ver_encuesta, name='ver'),
    url(r'^gracias/(?P<id_encuesta>[0-9]+)/$', views.gracias, name='gracias'),
    url(r'^error/$', views.error, name='error'),
	]

