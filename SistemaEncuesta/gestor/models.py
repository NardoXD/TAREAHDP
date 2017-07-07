from django.db import models
from django.utils import timezone
from django import forms
# Create your models here.
class Usuario(models.Model):
	correo = models.CharField(max_length=255)
	contrasenia = models.CharField(max_length=100)

class Encuesta(models.Model):
	usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
	titulo_encuesta = models.CharField(max_length=255,)
	descripcion = models.CharField(max_length=255)
	fecha_creacion = models.DateField(auto_now_add=timezone.now().date)
	visitas = models.IntegerField(default=0)

	def __str__(self):
		return self.titulo_encuesta

class Pregunta(models.Model):
	contenido = models.CharField(max_length=255)
	encuesta = models.ForeignKey(Encuesta, null=False, on_delete=models.CASCADE)

	def __str__(self):
		return self.contenido

class Respuesta(models.Model):
	contenido = models.CharField(max_length=255)
	pregunta = models.ForeignKey(Pregunta, null=False, on_delete=models.CASCADE)

	def __str__(self):
		return self.contenido

class EncuestaRespuesta(models.Model):
	encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
	ip = models.CharField(max_length=50)

class RespuestaElegida(models.Model):
	respuesta_encuesta = models.ForeignKey(EncuestaRespuesta, on_delete=models.CASCADE)
	pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
	respuesta = models.ForeignKey(Respuesta, on_delete=models.CASCADE)