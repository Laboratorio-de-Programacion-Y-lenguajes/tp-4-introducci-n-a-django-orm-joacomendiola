from __future__ import annotations

from django.db import models
from django.utils import timezone


class Autor(models.Model):
    """
    Representa a un autor/a.
    Requerido: nombre, email único, biografía opcional.
    """
    nombre = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    biografia = models.TextField(blank=True)

  # definimos __str__ para que sea legible en el admin y en el shell
    def __str__(self) -> str:
        return self.nombre
    

class Categoria(models.Model):
    """
    Categoría temática de libros.
    Ejemplos: 'fantasía', 'ciencia ficción', 'historia'.
    """

    nombre = models.CharField(max_length=120, unique=True)

    def __str__(self) -> str:
        return self.nombre


class Libro(models.Model):
    """
    Libro del catálogo de la biblioteca.
    Tiene relación N:1 con Autor y N:M con Categoria.
    """
    titulo = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True)
    fecha_publicacion = models.DateField()
    cantidad_total = models.PositiveIntegerField()
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT)
    categorias = models.ManyToManyField(Categoria)

    # Preguntas guía:
    # ¿Qué pasa si eliminás un autor que tiene libros? (PROTECT vs CASCADE)
    #Respuesta: Quiero evitar eliminar un autor si tiene libros asociados, para no perder esa información. Por eso usamos PROTECT en lugar de CASCADE.

    # ¿Por qué isbn debe ser único?
    #Respuesta: El ISBN es un identificador único para cada libro, por lo que no puede haber dos libros con el mismo ISBN en el catálogo. Esto nos permite identificar de manera precisa cada libro y evitar confusiones.

    def prestamos_activos(self) -> int:
        """
        Retorna la cantidad de préstamos activos (fecha_devolucion IS NULL).
        Un préstamo es "activo" cuando no se ha registrado devolución.
        Es decir, cuando fecha_devolucion es NULL.
        """
        return self.prestamo_set.filter(fecha_devolucion__isnull=True).count()

    def disponibles(self) -> int:
        """
        Retorna cuántas copias están disponibles:
        cantidad_total - prestamos_activos()
        Nunca retorna un numero negativo.
        """
        return max(self.cantidad_total - self.prestamos_activos(), 0) 
        

    def tiene_disponibles(self) -> bool:
        """Retorna True si hay al menos una copia disponible.
        La función debe retornar un booleano, no un número."""
        
        return self.disponibles() > 0


class Prestamo(models.Model):
    """
    Registro de un préstamo de libro a un usuario.
    Si fecha_devolucion es NULL → el préstamo está activo.
    """
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    nombre_prestatario = models.CharField(max_length=120)
    fecha_prestamo = models.DateField(default=timezone.now)
    fecha_devolucion = models.DateField(null=True, blank=True)

    # Preguntas guía:
    # ¿Por qué usamos CASCADE aquí y PROTECT en Libro→Autor?
    #Respuesta: En el caso de Prestamo→Libro, queremos que si se elimina un libro, también se eliminen todos los préstamos asociados a ese libro, ya que esos préstamos no tendrían sentido sin el libro. Por eso usamos CASCADE. En cambio, en Libro→Autor, queremos proteger la integridad de los datos y evitar eliminar un autor si tiene libros asociados, por eso usamos PROTECT.
    # ¿Qué valor por defecto tendría sentido para fecha_prestamo?
    #Respuesta: Un valor por defecto razonable para fecha_prestamo sería la fecha actual, ya que generalmente se registra el préstamo en el momento en que se realiza. Por eso podríamos usar default=timezone.now para que se asigne automáticamente la fecha actual al crear un nuevo préstamo. Sin embargo, también podríamos dejarlo sin default para que el test lo defina explícitamente, dependiendo de cómo queramos manejar los casos de prueba y la flexibilidad que necesitemos en la creación de préstamos.
    