#!/usr/bin/env python3
# Genera diccionario.txt (formato: "palabra frecuencia") a partir de lemas en español.
# Las palabras se guardan en minúsculas y SIN tildes ni ñ (ASCII), igual que normaliza el programa en C++.
import zlib

FUNCIONALES = """de la que el en y a los se del las un por con no una su para es al lo como mas o pero sus le ya este si
porque esta entre cuando muy sin sobre tambien me hasta hay donde quien desde todo nos durante todos uno les ni contra
otros ese eso ante ellos esto mi antes algunos unos yo otro otras otra tanto esa estos mucho quienes nada muchos cual poco
ella estas algunas algo nosotros tu usted ellas aqui alli ahora siempre nunca bien mal asi donde cada mismo misma
""".split()

NOMBRES_TECH = """algoritmo arbol arreglo archivo atributo binario bit byte boton bucle cadena cifrado clase clave codigo
cola compilador complejidad computadora conjunto constante cursor dato diccionario disco diseno dominio elemento entero
error estructura funcion grafo hash indice instruccion interfaz iteracion lenguaje lista llave matriz memoria metodo
modulo nodo objeto operacion ordenamiento pantalla parametro pila programa programacion puntero raiz recursion red
registro rendimiento secuencia servidor sistema software hardware tabla teclado tiempo usuario valor variable vector
version ventana pagina internet ingenieria informatica prefijo sufijo palabra letra texto corrector sugerencia
distancia busqueda ordenador pseudocodigo prueba resultado solucion problema espacio memoria dimension altura nivel
hijo padre hoja camino fila columna celda tamano limite promedio caso rama pivote mezcla particion subproblema""".split()

NOMBRES = """casa perro gato libro mesa silla ciudad pueblo pais mundo tierra agua fuego aire sol luna estrella cielo mar
rio lago montana bosque campo calle plaza parque jardin flor planta fruta manzana naranja platano uva pera limon papa
tomate cebolla arroz pan queso leche carne pollo pescado huevo sopa comida cena almuerzo desayuno cafe vino cerveza jugo
azucar sal escuela colegio universidad profesor maestro alumno estudiante curso clase examen nota tarea trabajo oficina
empresa negocio tienda mercado banco dinero precio costo pago cuenta factura producto cliente vendedor comprador
familia padre madre hijo hija hermano hermana abuelo abuela tio tia primo prima amigo amiga vecino persona gente
hombre mujer nino nina joven senor senora doctor enfermera medico hospital salud cuerpo cabeza cara ojo nariz boca oreja
mano brazo pierna pie dedo corazon espalda cabello pelo diente lengua voz idea pensamiento sueno recuerdo historia
cuento novela poema cancion musica pelicula teatro juego deporte futbol equipo partido gol pelota carrera premio
viaje vuelo avion tren autobus carro auto bicicleta moto barco puerto aeropuerto estacion hotel habitacion cama bano cocina
sala puerta ventana pared techo piso escalera llave reloj telefono celular camara foto imagen video radio television
pantalla mensaje correo carta sobre papel lapiz pluma cuaderno mochila bolsa caja botella vaso plato cuchara tenedor
cuchillo mesa ropa camisa pantalon zapato sombrero vestido abrigo guante calcetin color rojo verde azul numero cifra
semana dia mes hora minuto segundo noche manana tarde ayer hoy invierno verano otono primavera lluvia nieve viento
tormenta trueno nube animal pajaro pez caballo vaca oveja cerdo conejo raton leon tigre oso lobo zorro mono elefante
serpiente insecto mosca abeja mariposa arana ley norma regla derecho justicia gobierno estado nacion pueblo ciudadano
alcalde presidente ministro congreso ejercito policia guerra paz libertad igualdad respeto amor amistad alegria tristeza
miedo ira sorpresa duda esperanza fuerza energia luz sombra ruido silencio sonido olor sabor tacto vista oido gusto
ciencia fisica quimica biologia matematica geometria algebra calculo estadistica probabilidad teoria practica
experimento laboratorio investigacion proyecto informe reporte resumen tema titulo capitulo pagina parrafo frase oracion
significado definicion ejemplo ejercicio respuesta pregunta duda razon motivo causa efecto cambio mejora avance
meta objetivo logro plan etapa fase paso proceso metodo tecnica herramienta maquina motor fabrica industria""".split()

ADJETIVOS = """grande pequeno bueno malo nuevo viejo joven alto bajo largo corto ancho angosto rapido lento facil dificil
simple complejo eficiente ordenado correcto incorrecto dinamico estatico recursivo iterativo voraz logico matematico
algoritmico exacto aproximado optimo minimo maximo limitado infinito vacio lleno completo parcial total unico multiple
actual anterior siguiente primero ultimo segundo tercero cuarto quinto rojo azul verde amarillo negro blanco hermoso
bonito feo feliz triste alegre contento enojado cansado fuerte debil duro blando suave caliente frio tibio dulce amargo
salado rico pobre caro barato limpio sucio claro oscuro profundo superficial ligero pesado seguro peligroso util inutil
importante necesario posible imposible comun raro extrano normal especial general particular publico privado local
nacional internacional social cultural natural artificial digital virtual real falso verdadero libre ocupado abierto
cerrado listo preparado dispuesto cercano lejano antiguo moderno futuro pasado presente diario semanal mensual anual
personal basico avanzado intermedio principal secundario inicial final central lateral superior inferior interno
externo propio ajeno cierto distinto diferente igual parecido similar tipico estable inestable valido invalido""".split()

# Verbos regulares (sin cambios de raíz), para que las formas generadas sean correctas
VERBOS_AR = """hablar cantar bailar caminar estudiar trabajar comprar buscar mirar escuchar llamar esperar ayudar usar utilizar
necesitar ganar pasar llevar tomar dejar entregar practicar preparar programar compilar ejecutar implementar analizar
calcular comparar ordenar clasificar organizar almacenar guardar cargar procesar generar crear mejorar optimizar
evaluar validar verificar marcar activar desactivar actualizar eliminar borrar copiar cambiar intercambiar explicar
presentar completar terminar iniciar finalizar sumar restar multiplicar cocinar lavar limpiar pintar dibujar nadar
viajar visitar saludar celebrar amar olvidar preguntar contestar apagar cuidar cortar tocar cenar desayunar mandar
enviar conectar desconectar instalar descargar navegar grabar editar publicar comentar opinar votar lanzar
levantar saltar tirar mostrar_ imaginar inventar probar_ resolver_ clasificar indicar insertar buscar
reservar reducir_ aumentar disminuir_ ampliar ajustar adaptar aplicar asignar centrar codificar decodificar
demostrar_ detectar determinar dominar encaminar enfocar enlazar enumerar escalar estimar examinar explorar
extraer_ formar fundar identificar ignorar iterar jerarquizar medir_ modificar nombrar notar observar ocupar
operar organizar orientar participar pensar_ planificar plantear preparar privar procurar proponer_ proteger_
reciclar recorrer_ reflexionar reparar representar reunir_ revisar señalar_ simular sintetizar sostener_ tardar
transformar trasladar tratar usar valorar variar vigilar visualizar""".split()

VERBOS_ER = """comer beber vender aprender comprender correr responder deber meter prometer temer romper esconder ofender
depender sorprender ceder exceder proceder suceder tejer barrer""".split()

VERBOS_IR = """vivir escribir abrir subir partir decidir recibir permitir compartir existir describir definir unir cumplir
repartir discutir sufrir admitir omitir imprimir dividir insistir resistir persistir aplaudir convivir sobrevivir
transmitir emitir incluir_ distribuir_ prohibir asistir interrumpir suprimir percibir""".split()


def limpio(lista):
    """Quita las entradas marcadas con '_' (verbos irregulares descartados) y las que no sean ASCII."""
    return [p for p in lista if not p.endswith("_") and p.isascii() and p.isalpha()]


def plural(p):
    if p.endswith("z"):
        return p[:-1] + "ces"
    if p.endswith(("a", "e", "i", "o", "u")):
        return p + "s"
    if p.endswith("s"):
        return p
    return p + "es"


def formas_adjetivo(a):
    if a.endswith("o"):
        r = a[:-1]
        return [a, r + "a", r + "os", r + "as"]
    return [a, plural(a)]


def formas_verbo(v):
    r, fin = v[:-2], v[-2:]
    inf = v
    if fin == "ar":
        f = ["o", "as", "a", "amos", "an", "aba", "abas", "abamos", "aban", "ando", "ado", "ada", "ados", "adas"]
    else:
        v1 = "e" if fin == "er" else "i"
        f = ["o", "es", "e", v1 + "mos", "en", "ia", "ias", "iamos", "ian", "iendo", "ido", "ida", "idos", "idas"]
    out = [inf] + [r + x for x in f]
    # futuro y condicional (sin tilde)
    out += [inf + x for x in ["e", "as", "a", "emos", "an", "ia", "ias", "iamos", "ian"]]
    return out


def frecuencia(p, base=0):
    return base + 1 + zlib.crc32(p.encode()) % 400


def main():
    d = {}

    def add(p, f):
        if p.isascii() and p.isalpha() and p.islower():
            d[p] = max(d.get(p, 0), f)

    for p in FUNCIONALES:
        add(p, frecuencia(p, 1200))
    for p in limpio(NOMBRES_TECH):
        add(p, frecuencia(p, 700))
        add(plural(p), frecuencia(plural(p), 600))
    for p in limpio(NOMBRES):
        add(p, frecuencia(p))
        add(plural(p), frecuencia(plural(p)))
    for a in limpio(ADJETIVOS):
        for f in formas_adjetivo(a):
            add(f, frecuencia(f, 100))
    for v in limpio(VERBOS_AR) + limpio(VERBOS_ER) + limpio(VERBOS_IR):
        for f in formas_verbo(v):
            add(f, frecuencia(f))

    with open("diccionario.txt", "w", encoding="ascii") as fh:
        for p in sorted(d):
            fh.write(f"{p} {d[p]}\n")
    print(f"diccionario.txt generado con {len(d)} palabras")


if __name__ == "__main__":
    main()
