import ast
import math
import operator

import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Interpolación lineal", layout="wide")

EPS = 1e-12# = 0.000000000001


# ----------------------------------------------------------------------------
# Evaluador seguro de expresiones numéricas (sin usar eval)
# ----------------------------------------------------------------------------
_BIN_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Pow: operator.pow,
}
_UN_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_CONSTANTES = {"pi": math.pi, "π": math.pi, "e": math.e}


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
            and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.Name) and node.id in _CONSTANTES:
        return _CONSTANTES[node.id]
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UN_OPS:
        return _UN_OPS[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        izq, der = _eval_node(node.left), _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(der) > 100:
            raise OverflowError("exponente demasiado grande")
        return _BIN_OPS[type(node.op)](izq, der)
    raise ValueError("expresión no permitida")


def parse_number(raw, nombre):
   
    if raw is None or str(raw).strip() == "":
        return None, f"El campo **{nombre}** está vacío."

    texto = str(raw).strip().replace(",", ".").replace("^", "**")
    try:
        valor = float(_eval_node(ast.parse(texto, mode="eval")))
    except (SyntaxError, ValueError, TypeError, RecursionError):
        return None, f"El campo **{nombre}** no es un número válido: «{raw}»."
    except (ZeroDivisionError, OverflowError):
        return None, f"El campo **{nombre}** produce una operación inválida o demasiado grande: «{raw}»."

    if not math.isfinite(valor):  
        return None, f"El campo **{nombre}** debe ser un número finito (no se admite inf ni NaN)."

    return valor, None


def fmt(v):
    """Número -> texto LaTeX (los negativos van entre paréntesis)."""
    s = f"{v:.6g}"
    return f"({s})" if v < 0 else s


# ----------------------------------------------------------------------------
# Catálogo de funciones
# ----------------------------------------------------------------------------
NINGUNA = "Nada (ingreso manual)"


def construir_funciones(grados):
    a_rad = math.radians if grados else (lambda t: t)
    return {
        "ln(x)":    (math.log, r"\ln"),
        "log10(x)": (math.log10, r"\log_{10}"),
        "log2(x)":  (math.log2, r"\log_{2}"),
        "sen(x)":   (lambda t: math.sin(a_rad(t)), r"\operatorname{sen}"),
        "cos(x)":   (lambda t: math.cos(a_rad(t)), r"\cos"),
        "tan(x)":   (lambda t: math.tan(a_rad(t)), r"\tan"),
        "exp(x)":   (math.exp, r"e^{x}\ \text{en}"),
        "√x":       (math.sqrt, r"\sqrt{\ }"),
        "x²":       (lambda t: t ** 2, r"(\cdot)^2"),
        "1/x":      (lambda t: 1.0 / t, r"1/"),
    }


def evaluar(func, x):
    try:
        y = func(x)
    except ValueError:
        return None, f"x = {x:g} está fuera del dominio de la función."
    except ZeroDivisionError:
        return None, f"La función no está definida en x = {x:g} (división entre cero)."
    except OverflowError:
        return None, f"El valor de la función en x = {x:g} es demasiado grande."
    if not math.isfinite(y) or abs(y) > 1e12:
        return None, f"La función no está definida (o diverge) en x = {x:g}."
    return y, None


def curva_real(func, xs):
    ys = np.full(len(xs), np.nan)
    for i, xv in enumerate(xs):
        y, err = evaluar(func, float(xv))
        if err is None:
            ys[i] = y
    ys[np.abs(ys) > 1e6] = np.nan
    return ys


# ----------------------------------------------------------------------------
# Interfaz: entrada de datos (todo como texto para controlar los errores nosotros)
# ----------------------------------------------------------------------------
st.title("Interpolación lineal · Simulador")
st.caption("Se calcula la recta que pasa por P1 = (x1, y1) y P2 = (x2, y2) y se evalúa en el valor x indicado.")

with st.sidebar:
    st.header("0. Función")
    grados = False
    nombre_funcion = st.selectbox(
        "Función a usar",
        [NINGUNA] + list(construir_funciones(False).keys()),
        key="funcion",
        help="Si eliges una función, y1 e y2 se calculan solos a partir de x1 y x2.",
    )
    usa_funcion = nombre_funcion != NINGUNA

    if nombre_funcion in ("sen(x)", "cos(x)", "tan(x)"):
        unidad = st.radio("Ángulos en", ["Radianes", "Grados"], horizontal=True, key="unidad")
        grados = unidad == "Grados"

    func = None
    latex_func = ""
    if usa_funcion:
        func, latex_func = construir_funciones(grados)[nombre_funcion]

    st.header("1. Puntos conocidos")
    c1, c2 = st.columns(2)
    raw_x1 = c1.text_input("x1", value="1", key="x1")
    raw_x2 = c1.text_input("x2", value="5", key="x2")

    errores_funcion = []
    if usa_funcion:
        ys_auto = []
        for raw_x, nombre_x, nombre_y in ((raw_x1, "x1", "y1"), (raw_x2, "x2", "y2")):
            xv, err_x = parse_number(raw_x, nombre_x)
            texto_y = ""
            if err_x is None:
                yv, err_y = evaluar(func, xv)
                if err_y is None:
                    texto_y = f"{yv:.10g}"
                else:
                    errores_funcion.append(f"**{nombre_y}**: {err_y}")
            ys_auto.append((texto_y, nombre_y))
        raw_y1 = c2.text_input(f"y1 = {nombre_funcion.replace('x', 'x1')}", value=ys_auto[0][0],
                               disabled=True, placeholder="—")
        raw_y2 = c2.text_input(f"y2 = {nombre_funcion.replace('x', 'x2')}", value=ys_auto[1][0],
                               disabled=True, placeholder="—")
    else:
        raw_y1 = c2.text_input("y1 = f(x1)", value="2", key="y1")
        raw_y2 = c2.text_input("y2 = f(x2)", value="10", key="y2")

    st.header("2. Valor a interpolar")
    raw_x = st.text_input("x =", value="3", key="x_eval")
    st.caption("Puedes usar coma o punto decimal, y expresiones como pi/2, e**2 o 3^2. "
               "Los campos vacíos o con texto se detectan automáticamente.")

# ----------------------------------------------------------------------------
# Validación 4: campos vacíos o no numéricos
# ----------------------------------------------------------------------------
campos = [
    (raw_x1, "x1"), (raw_y1, "y1"),
    (raw_x2, "x2"), (raw_y2, "y2"),
    (raw_x, "x (valor a interpolar)"),
]
valores, errores = [], []
for raw, nombre in campos:
    v, err = parse_number(raw, nombre)
    valores.append(v)
    
    if err and not (usa_funcion and nombre in ("y1", "y2")):
        errores.append(err)
errores.extend(errores_funcion)

if errores:
    st.error(" No se puede calcular todavía. Corrige lo siguiente:")
    for e in errores:
        st.markdown(f"- {e}")
    st.stop()  

x1, y1, x2, y2, x_eval = valores

# ----------------------------------------------------------------------------
# Validación 1: x1 != x2 (división por cero)
# ----------------------------------------------------------------------------
if abs(x2 - x1) < EPS: 
    st.error(
        " **x1 y x2 son iguales.** No se puede formar un intervalo válido ni calcular la "
        "pendiente m = (y2 − y1)/(x2 − x1), porque se dividiría entre cero. "
        "Ingresa dos valores de x distintos."
    )
    st.stop()

# ----------------------------------------------------------------------------
# Validación 2: orden del intervalo (x1 < x2) -> se corrige intercambiando los puntos
# ----------------------------------------------------------------------------
if x1 > x2:
    st.warning(
        f"↔ Ingresaste x1 = {x1:g} > x2 = {x2:g}. Se intercambiaron automáticamente los puntos "
        "P1 y P2 para que x1 < x2 (la recta resultante es exactamente la misma)."
    )
    x1, y1, x2, y2 = x2, y2, x1, y1

# ----------------------------------------------------------------------------
# Cálculo protegido
# ----------------------------------------------------------------------------
try:
    m = (y2 - y1) / (x2 - x1)          
    y_eval = y1 + m * (x_eval - x1)    
    if not (math.isfinite(m) and math.isfinite(y_eval)):
        raise OverflowError("El resultado excede el rango numérico representable.")
except (OverflowError, ZeroDivisionError, FloatingPointError) as exc:
    st.error(f" No se pudo completar el cálculo: {exc} Prueba con valores de menor magnitud.")
    st.stop()


y_real, err_real = (None, None)
if usa_funcion:
    y_real, err_real = evaluar(func, x_eval)


err_abs = abs(y_real - y_eval) if y_real is not None else None
err_rel = (err_abs / abs(y_real) * 100) if (y_real is not None and abs(y_real) > EPS) else None

# ----------------------------------------------------------------------------
# Validación 3: alerta de extrapolación
# ----------------------------------------------------------------------------
es_extrapolacion = x_eval < x1 or x_eval > x2
if es_extrapolacion:
    distancia = (x1 - x_eval) if x_eval < x1 else (x_eval - x2)
    st.warning(
        f" **Extrapolación:** x = {x_eval:g} está fuera del intervalo [{x1:g}, {x2:g}] "
        f"(a {distancia:g} unidades del extremo más cercano). Los datos no cubren ese valor, "
        "por lo que el resultado tiene un **mayor margen de error** y debe tomarse con cautela."
    )
else:
    st.success(f" Interpolación: x = {x_eval:g} está dentro del intervalo [{x1:g}, {x2:g}].")

# ----------------------------------------------------------------------------
# Resultados
# ----------------------------------------------------------------------------
izq, der = st.columns([1.1, 1], gap="large")

with izq:
    st.subheader(" Visualización")

    # Rango del gráfico: cubre los puntos y el valor evaluado, con un margen del 15 %
    xmin, xmax = min(x1, x2, x_eval), max(x1, x2, x_eval)
    margen = 0.15 * (xmax - xmin)
    xs_plot = np.array([xmin - margen, xmax + margen])

    fig = go.Figure()

    # Curva real de la función (solo si se eligió una)
    if usa_funcion:
        xs_curva = np.linspace(xmin - margen, xmax + margen, 400)
        fig.add_trace(go.Scatter(
            x=xs_curva, y=curva_real(func, xs_curva), mode="lines",
            name=f"Curva real {nombre_funcion}",
            line=dict(color="#264653", width=2, dash="dot"),
            connectgaps=False))

        # Zona de error sombreada: diferencia entre la curva real y la recta en [x1, x2]
        xs_in = np.linspace(x1, x2, 300)
        fig.add_trace(go.Scatter(
            x=xs_in, y=y1 + m * (xs_in - x1), mode="lines",
            line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(
            x=xs_in, y=curva_real(func, xs_in), mode="lines",
            line=dict(width=0), fill="tonexty", fillcolor="rgba(214,40,40,0.18)",
            name="Zona de error en [x1, x2]", hoverinfo="skip"))

    fig.add_trace(go.Scatter(
        x=xs_plot, y=y1 + m * (xs_plot - x1), mode="lines",
        name="Recta extendida (extrapolación)",
        line=dict(color="gray", dash="dash", width=2)))
    fig.add_trace(go.Scatter(
        x=[x1, x2], y=[y1, y2], mode="lines",
        name="Intervalo [x1, x2]", line=dict(color="#4B2E91", width=4)))
    fig.add_trace(go.Scatter(
        x=[x1, x2], y=[y1, y2], mode="markers+text", name="Puntos conocidos",
        text=["P1", "P2"], textposition="top center",
        marker=dict(size=12, color="#E4572E", line=dict(width=2, color="white"))))
    fig.add_trace(go.Scatter(
        x=[x_eval], y=[y_eval], mode="markers",
        name=f"f({x_eval:g}) ≈ {y_eval:.6g}",
        marker=dict(size=16, symbol="star",
                    color="#F4A261" if es_extrapolacion else "#2A9D8F")))
    if y_real is not None:
        fig.add_trace(go.Scatter(
            x=[x_eval], y=[y_real], mode="markers",
            name=f"Valor real = {y_real:.6g}",
            marker=dict(size=11, symbol="x", color="#D62828", line=dict(width=2))))
        etiqueta_err = f"Error = {err_abs:.3g}" + (f" ({err_rel:.3g} %)" if err_rel is not None else "")
        fig.add_trace(go.Scatter(
            x=[x_eval, x_eval], y=[y_eval, y_real], mode="lines",
            name=f"Margen de error: {etiqueta_err.replace('Error = ', '')}",
            line=dict(color="#D62828", width=3)))
        fig.add_annotation(
            x=x_eval, y=(y_eval + y_real) / 2, text=etiqueta_err,
            showarrow=True, arrowhead=0, ax=60, ay=-30,
            font=dict(color="#D62828", size=12), bgcolor="rgba(255,255,255,0.85)",
            bordercolor="#D62828", borderwidth=1)

    fig.update_layout(height=500, margin=dict(l=10, r=10, t=30, b=10),
                      xaxis_title="x", yaxis_title="f(x)",
                      legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, use_container_width=True)

with der:
    st.subheader(" Desglose matemático")

    m1, m2 = st.columns(2)
    m1.metric("Pendiente m", f"{m:.6g}")
    m2.metric("f(x) estimado", f"{y_eval:.6g}",
              delta="extrapolado" if es_extrapolacion else "interpolado",
              delta_color="off")

    if usa_funcion:
        st.markdown(f"**Función elegida:** `{nombre_funcion}`"
                    + (" (ángulos en grados)" if grados else
                       " (ángulos en radianes)" if nombre_funcion in ("sen(x)", "cos(x)", "tan(x)") else ""))
        if y_real is not None:
            e1, e2 = st.columns(2)
            e1.metric("Valor real", f"{y_real:.6g}")
            err_abs = abs(y_real - y_eval)
            e2.metric("Error absoluto", f"{err_abs:.3g}",
                      delta=(f"{err_abs / abs(y_real) * 100:.3g} % relativo" if abs(y_real) > EPS else None),
                      delta_color="off")
        else:
            st.info(f"No se puede comparar con el valor real: {err_real}")

    st.markdown("**Fórmula general**")
    st.latex(r"f(x)\approx y_1+\frac{y_2-y_1}{x_2-x_1}\,(x-x_1)")

    st.markdown("**Paso 1 · Pendiente**")
    st.latex(rf"m=\frac{{{fmt(y2)}-{fmt(y1)}}}{{{fmt(x2)}-{fmt(x1)}}}"
             rf"=\frac{{{fmt(y2 - y1)}}}{{{fmt(x2 - x1)}}}={m:.6g}")

    st.markdown(f"**Paso 2 · Evaluación en x = {x_eval:g}**")
    st.latex(rf"f({x_eval:g})\approx {fmt(y1)}+({m:.6g})\cdot\left({fmt(x_eval)}-{fmt(x1)}\right)"
             rf"={y_eval:.6g}")

    st.markdown("**Ecuación de la recta**")
    ordenada = y1 - m * x1  # f(x) = m x + b
    signo = "+" if ordenada >= 0 else "-"
    st.latex(rf"f(x)={m:.6g}\,x\;{signo}\;{abs(ordenada):.6g}")

    if es_extrapolacion:
        st.info("El punto resultado se muestra en naranja porque proviene de una extrapolación.")

st.divider()
st.caption("Nota: la interpolación lineal supone que f(x) se comporta como una recta entre x1 y x2; "
           "fuera de ese intervalo el error puede crecer rápidamente.")