from django.shortcuts import *
from django.http import *
from gestor.models import *
from django.template import *
from django.urls import *
import json
import urllib
from SistemaEncuesta import *
# Create your views here.

#Aqui se realiza el login
def login(request):
    if request.method == 'POST' :
        try:
            usuario = Usuario.objects.get(correo=request.POST.get('email', ''), contrasenia=request.POST.get('password',''))
            return redirect('/gestor/administracion/' + str(usuario.id) + '/')
        except:
            return redirect('/gestor/')
    else:
        contexto = {}
        return render(request, 'Login.html', contexto)

def administracion(request, id_usuario):
    if request.method == 'POST' :
        obtener_usuario = Usuario.objects.get(id=id_usuario)
        obtener_enc = Encuesta.objects.filter(usuario=obtener_usuario)
        opcion = request.POST.get('eliminar','')
        if opcion == 'Eliminar Seleccionados' :    
            for el1 in obtener_enc:
                eliminar = request.POST.get('chech_enc' + str(el1.id), '')
                if eliminar != '' :
                    enc_eliminada = Encuesta.objects.get(id=int(eliminar))
                    enc_eliminada.delete()  
            return redirect('/gestor/administracion/' + str(id_usuario))
        for enc in obtener_enc:
            opcion2 = request.POST.get('opcion' + str(enc.id))
            if opcion2 == 'Editar' :
                return redirect('/gestor/editar/' + str(enc.id))
            elif opcion2 == 'Ver' :
                return redirect('/gestor/ver/' + str(enc.id))
    else:
        contexto = {}
        obtener_usuario = Usuario.objects.get(id=id_usuario)
        contexto['usuario'] = obtener_usuario
        obtener_enc = Encuesta.objects.filter(usuario=obtener_usuario)
        contexto['encuesta'] = obtener_enc
        return render(request, 'Administrador.html', contexto)

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

########RESPONDER ENCUESTA########################
def responder_encuesta(request, id_encuesta):
    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req =  urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())

        if result['success'] :
            ip_usuario = obtenerIp(request)
            
            pasar = True
            resp = EncuestaRespuesta.objects.filter(ip=ip_usuario)
            for elemento in resp :
                if elemento.ip == ip_usuario:
                    pasar = False
                    break

            if pasar == False :
                return redirect('/gestor/error/')
            else:
                #puedes continuar
                enc = Encuesta.objects.get(id=id_encuesta)
                visitas = enc.visitas
                visitas = visitas + 1
                enc.visitas = visitas
                enc.save()
                enc_resp = EncuestaRespuesta(encuesta=enc, ip=ip_usuario)
                enc_resp.save()
                id_enc = enc_resp.id
                preguntas = Pregunta.objects.filter(encuesta=enc)
                
                try:
                    for el1 in preguntas:
                        opcion_elegida = request.POST.get('Radio' + str(el1.id), '')
                        if opcion_elegida != '':
                            get_encuesta_respuesta = EncuestaRespuesta.objects.get(id=id_enc)
                            respuesta = Respuesta.objects.get(id=int(opcion_elegida))
                            eleccion = RespuestaElegida(respuesta_encuesta=get_encuesta_respuesta, pregunta=el1, respuesta=respuesta)
                            eleccion.save()
                    return redirect('/gestor/gracias/' + str(id_encuesta))  
                except:
                    return render(request, 'ResponderEncuesta.html', contexto)
        else:
            return redirect('/gestor/responder/' + str(id_encuesta) + '/')
    else:
        contexto = {}
        encuesta = Encuesta.objects.get(id=id_encuesta)
        contexto["encuesta"]=encuesta
        preguntas = Pregunta.objects.filter(encuesta=encuesta)
        
        list_preguntas=[]
        list_resp=[]

        for el in preguntas:
            list_preguntas.append(el)
            respuestas = Respuesta.objects.filter(pregunta=el).order_by('id')
            for el2 in respuestas:
                list_resp.append(el2)

        contexto["pregunta"]=list_preguntas
        contexto["respuesta"]=list_resp
        return render(request, 'ResponderEncuesta.html', contexto)

#########EDITAR ENCUESTA################
def editar_encuesta(request, id_encuesta):
    if request.method == 'POST':
#########Aqui se agregan y eliminan las respuestas########################################################
        obtener_enc = Encuesta.objects.get(id=id_encuesta)
        obtener_preg = Pregunta.objects.filter(encuesta=obtener_enc)
        for el1 in obtener_preg :
            accion2 = request.POST.get('btn_res' + str(el1.id), '')
            if accion2 == 'Agregar respuesta':
                return redirect('/gestor/agregar/respuesta/' + id_encuesta + '/' + str(el1.id) + '/')
            elif accion2 == 'Eliminar respuestas' :
                obtener_resp = Respuesta.objects.filter(pregunta=el1)
                for el2 in obtener_resp :
                    eliminar = request.POST.get('check_res' + str(el2.id),'')
                    if eliminar != '' :
                        resp_eliminada = Respuesta.objects.get(id=el2.id)
                        resp_eliminada.delete()
                return redirect('/gestor/editar/' + id_encuesta + '/')
#########Aqui se agregan preguntas, se guarda la edicion de le encuesta, se elimina y cancela edicion##############
        accion = request.POST.get("btn", '')
#########Guardar edicion de la encuesta################################################################
        if accion == 'Guardar':
            obtener_encuesta = Encuesta.objects.get(id=id_encuesta)
            enc = request.POST.get('id_enc' + str(obtener_encuesta.id))
            obtener_encuesta.titulo_encuesta = enc
            obtener_encuesta.save()
            obtener_preguntas = Pregunta.objects.filter(encuesta=obtener_encuesta)

            for elemento_pregunta in obtener_preguntas:
                pregunta_modificada = request.POST.get('id_pr' + str(elemento_pregunta.id), '')
                if pregunta_modificada != '' :
                    elemento_pregunta.contenido = pregunta_modificada
                    elemento_pregunta.save()

                    obtener_respuestas = Respuesta.objects.filter(pregunta=elemento_pregunta)
                    
                    for elemento_respuesta in obtener_respuestas:
                        respuesta_modificada = request.POST.get('id_res' + str(elemento_respuesta.id), '')
                        if respuesta_modificada != '' :
                            elemento_respuesta.contenido = respuesta_modificada
                            elemento_respuesta.save()
            return redirect('/gestor/administracion/'+ str(obtener_encuesta.usuario.id) + '/')
#########Agregar pregunta################################################################################
        elif accion == 'Agregar nueva pregunta': 
            return redirect('/gestor/agregar/pregunta/' + id_encuesta + '/')
#########Eliminar preguntas################################################################################
        elif accion == 'Eliminar preguntas':
            obtener_encuesta = Encuesta.objects.get(id=id_encuesta)
            obtener_preguntas = Pregunta.objects.filter(encuesta=obtener_encuesta)
            for elemento_pregunta in obtener_preguntas:
                eliminar = request.POST.get('check_pr' + str(elemento_pregunta.id), '')
                if eliminar != '':
                    preg_eliminada = Pregunta.objects.get(id=int(eliminar))
                    preg_eliminada.delete()
            return redirect('/gestor/editar/' + id_encuesta + '/')
        elif accion == 'Cancelar':
            obtener_enc = Encuesta.objects.get(id=id_encuesta)
            return redirect('/gestor/administracion/'+ str(obtener_enc.usuario.id) + '/')
            
    contexto = {}
    lista_respuesta = []
    get_encuesta = Encuesta.objects.get(id=id_encuesta)
    contexto['encuesta'] = get_encuesta
    get_pregunta = Pregunta.objects.filter(encuesta=get_encuesta)
    contexto['pregunta'] = get_pregunta
    for el in get_pregunta:
        get_respuesta = Respuesta.objects.filter(pregunta=el).order_by('id')
        lista_respuesta.append(get_respuesta)

    contexto['respuesta'] = lista_respuesta
    contexto['id_encuesta'] = id_encuesta
    return render(request, 'EditarEncuesta.html', contexto)

########AGREGAR PREGUNTA########################
def agregar_pregunta(request,id_encuesta):
    contexto = {}
    obtener_encuesta = Encuesta.objects.get(id=id_encuesta)
    contexto['encuesta'] = obtener_encuesta

    if request.method == 'POST':
        texto_pregunta = request.POST.get('texto_pregunta', '')
        if texto_pregunta != '':
            nueva_pregunta = Pregunta(contenido=texto_pregunta, encuesta=obtener_encuesta)
            nueva_pregunta.save()
            return redirect('/gestor/editar/' + id_encuesta + '/')
        else:
            return redirect('/gestor/editar/' + id_encuesta + '/')
    return render(request, 'IngresarPregunta.html', contexto)

########AGREGAR RESPUESTA########################
def agregar_respuesta(request, id_encuesta, id_pregunta):
    contexto = {}
    obtener_encuesta = Encuesta.objects.get(id=id_encuesta)
    contexto['encuesta'] = obtener_encuesta
    obtener_pregunta = Pregunta.objects.get(id=id_pregunta)
    contexto['pregunta'] = obtener_pregunta

    if (request.method == 'POST'):
        texto_respuesta = request.POST.get('texto_respuesta', '')
        if texto_respuesta != '' :
            nueva_respuesta = Respuesta(contenido=texto_respuesta, pregunta=obtener_pregunta)
            nueva_respuesta.save()
            return redirect('/gestor/editar/' + id_encuesta + '/')
        else:
            return redirect('/gestor/editar/' + id_encuesta + '/')

    return render(request, 'IngresarRespuesta.html', contexto)

def agregar_encuesta(request, id_usuario):
    if request.method == 'POST' :
        obtener_usuario = Usuario.objects.get(id=id_usuario)
        texto_encuesta = request.POST.get('encuesta', '')
        texto_descripcion = request.POST.get('descripcion', '')
        try:
            if texto_encuesta != '' and texto_descripcion != '' :
                nueva_encuesta = Encuesta(usuario=obtener_usuario, titulo_encuesta=texto_encuesta, \
                    descripcion=texto_descripcion, visitas=0)
                nueva_encuesta.save()
                return redirect('/gestor/administracion/' + str(id_usuario))
        except:
            return redirect('/gestor/administracion/' + str(id_usuario))
    else:
        contexto = {}
        obtener_usuario = Usuario.objects.get(id=id_usuario)
        contexto['usuario'] = obtener_usuario
        return render(request, 'IngresarEncuesta.html', contexto)

def ver_encuesta(request, id_encuesta):
    if request.method == 'POST' :
        obtener_encuesta = Encuesta.objects.get(id=id_encuesta)
        volver = request.POST.get('volver','')
        if volver == 'Volver' :
            return redirect('/gestor/administracion/' + str(obtener_encuesta.usuario.id))
    else:
        contexto = {}
        encuesta = Encuesta.objects.get(id=id_encuesta)
        contexto["encuesta"]=encuesta
        preguntas = Pregunta.objects.filter(encuesta=encuesta)
        get_ip = obtenerIp(request)
        contexto["ip"] = get_ip

        list_preguntas=[]
        list_resp=[]

        for el in preguntas:
            list_preguntas.append(el)
            respuestas = Respuesta.objects.filter(pregunta=el).order_by('id')
            for el2 in respuestas:
                list_resp.append(el2)

        contexto["pregunta"]=list_preguntas
        contexto["respuesta"]=list_resp
        return render(request, 'VerEncuesta.html', contexto)

def gracias(request, id_encuesta):
    contexto = {}
    obtener_encuesta = Encuesta.objects.get(id=id_encuesta)
    contexto['encuesta'] = obtener_encuesta
    return render(request, 'EncuestaContestada.html', contexto)
####Agregar error######
def error(request):
    contexto = {}
    return render(request, 'EncuestaError.html', contexto)

def obtenerIp(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = None

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip