import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Lagrange: desventajas", layout="wide")

# ----------------------------------------------------------------------------
# Utilidades matemáticas
# ----------------------------------------------------------------------------
def fmt(v: float) -> str:
    s = f"{v:.4g}"
    return f"({s})" if v < 0 else s


def lagrange_eval(xs, ys, x):
    x = np.asarray(x, dtype=float)
    total = np.zeros_like(x)
    for i in range(len(xs)):
        Li = np.ones_like(x)
        for j in range(len(xs)):
            if j != i:
                Li *= (x - xs[j]) / (xs[i] - xs[j])
        total += ys[i] * Li
    return total


def lagrange_coeffs(xs, ys):
    n = len(xs)
    poly = np.zeros(n)
    for i in range(n):
        others = [xs[j] for j in range(n) if j != i]
        num = np.poly(others) if others else np.array([1.0])
        den = np.prod([xs[i] - xs[j] for j in range(n) if j != i])
        poly += ys[i] * num / den
    return poly


def poly_latex(c):
    deg = len(c) - 1
    out = ""
    for k, a in enumerate(c):
        p = deg - k
        if abs(a) < 1e-12:
            continue
        sign = "-" if a < 0 else "+"
        mag = f"{abs(a):.4g}"
        mon = "" if p == 0 else ("x" if p == 1 else f"x^{{{p}}}")
        if mon and mag == "1":
            term = mon
        else:
            term = mag + mon
        out += (f" {sign} " if out else ("-" if a < 0 else "")) + term
    return out or "0"


def denominators(xs):
    return [float(np.prod([xs[i] - xs[j] for j in range(len(xs)) if j != i])) for i in range(len(xs))]


def op_count(n):
    """Operaciones aritméticas para evaluar g(x) en UN valor de x."""
    per_term = 4 * (n - 1) + 2  # (n-1) restas y mults arriba, (n-1) restas y mults abajo, 1 división, 1 mult por f_i
    return {"restas": 2 * n * (n - 1), "multiplicaciones": 2 * n * (n - 1) + n,
            "divisiones": n, "total": n * per_term}


# ----------------------------------------------------------------------------
# Estado de la sesión
# ----------------------------------------------------------------------------
ss = st.session_state
ss.setdefault("points", None)       # DataFrame con columnas x, y
ss.setdefault("editor_v", 0)        # versión del editor (para reiniciarlo)
ss.setdefault("last_sig", None)     # firma de los datos ya calculados
ss.setdefault("prev_points", None)  # puntos de la versión anterior
ss.setdefault("log", [])            # historial de recálculos
ss.setdefault("pending", "Creación inicial")
ss.setdefault("total_ops", 0)


def create_table(n):
    xs = np.arange(n, dtype=float)
    ss.points = pd.DataFrame({"x": xs, "y": np.zeros(n)})
    ss.editor_v += 1
    ss.pending = f"Tabla creada con {n} puntos"


EXAMPLES = {
    "Ejemplo 1 · Densidad del sodio (T = 251 °C)": {
        "x": [94.0, 205.0, 371.0], "y": [929.0, 902.0, 860.0], "x_star": 251.0},
    "Ejemplo 2 · {(-1,2),(2,8),(5,-3),(8,10)} (x = 4)": {
        "x": [-1.0, 2.0, 5.0, 8.0], "y": [2.0, 8.0, -3.0, 10.0], "x_star": 4.0},
    "Ejercicio propuesto (x = 4)": {
        "x": [1.5, 2.7, 5.6, 7.2], "y": [-5.0, 2.0, -2.0, 10.0], "x_star": 4.0},
}


def load_example(name):
    ex = EXAMPLES[name]
    ss.points = pd.DataFrame({"x": ex["x"], "y": ex["y"]})
    ss.x_star = ex["x_star"]
    ss.editor_v += 1
    ss.pending = f"📚 Cargado: {name}"


# Carga por defecto: Ejemplo 1
if ss.points is None:
    load_example(list(EXAMPLES)[0])


def add_point():
    df = ss.points
    xmax = pd.to_numeric(df["x"], errors="coerce").max()
    nx = float(xmax + 1) if pd.notna(xmax) and np.isfinite(xmax) else 0.0
    ss.points = pd.concat([df, pd.DataFrame({"x": [nx], "y": [0.0]})], ignore_index=True)
    ss.editor_v += 1
    ss.pending = "➕ Punto añadido"


def remove_point():
    idx = ss.get("del_idx")
    if idx in ss.points.index and len(ss.points) > 2:   # índice válido y mínimo 2 puntos
        ss.points = ss.points.drop(index=idx).reset_index(drop=True)
        ss.editor_v += 1
        ss.pending = f"➖ Punto eliminado (fila {idx})"


# ----------------------------------------------------------------------------
# Barra lateral: ingreso de datos
# ----------------------------------------------------------------------------
st.title("Interpolación de Lagrange · Demostración de desventajas")

with st.sidebar:
    st.header("1. Datos")
    st.radio("Ejemplos de la presentación", list(EXAMPLES), key="example_sel", index=0,
             on_change=lambda: load_example(ss.example_sel))
    st.caption("O crea una tabla propia:")
    n0 = st.number_input("Cantidad inicial de puntos (N)", min_value=2, max_value=20, value=4, step=1)
    st.button("Crear tabla vacía", on_click=create_table, args=(int(n0),), use_container_width=True)

    st.header("2. Editar puntos")
    edited = st.data_editor(
        ss.points, key=f"editor_{ss.editor_v}", num_rows="fixed",
        use_container_width=True, hide_index=False,
        column_config={"x": st.column_config.NumberColumn("x", format="%.4f"),
                       "y": st.column_config.NumberColumn("f(x)", format="%.4f")},
    )
    ss.points = edited

    b1, b2 = st.columns(2)
    b1.button("➕ Añadir punto", on_click=add_point, use_container_width=True)
    b2.button("➖ Eliminar", on_click=remove_point, use_container_width=True,
              disabled=len(ss.points) <= 2)
    st.selectbox("Punto a eliminar", list(ss.points.index), key="del_idx",
                 format_func=lambda i: f"P{i}")

    st.header("3. Evaluación")
    x_star = st.number_input("Evaluar g(x) en x =", key="x_star", format="%.4f")

# ----------------------------------------------------------------------------
# Validación
# ----------------------------------------------------------------------------
raw = ss.points.copy()
for col in ("x", "y"):
    raw[col] = pd.to_numeric(raw[col], errors="coerce")        
raw = raw.replace([np.inf, -np.inf], np.nan)                    
bad = raw[["x", "y"]].isna().any(axis=1)

# (3) Campos vacíos / no numéricos / infinitos: se avisa y se ignoran esas filas
if bad.any():
    filas = ", ".join(f"P{i}" for i in raw.index[bad])
    st.warning(f" Filas ignoradas por tener campos vacíos o no numéricos: **{filas}**. "
               "Complétalas para incluirlas en el polinomio (la numeración i del desglose "
               "se cuenta solo con las filas válidas).")
df = raw[~bad]

# (2) Cantidad mínima de puntos
if len(df) < 2:
    st.error(f" Se necesitan al menos **2 puntos completos** para interpolar "
             f"(ahora hay {len(df)}). Completa o añade puntos.")
    st.stop()

xs = df["x"].to_numpy(float)
ys = df["y"].to_numpy(float)
labels = [f"P{i}" for i in df.index]
n = len(xs)

# (1) X duplicados exactos -> x_i - x_j = 0 (división por cero)
dup_mask = df["x"].duplicated(keep=False)
if dup_mask.any():
    detalle = "; ".join(f"x = {v:g} en {', '.join(f'P{i}' for i in df.index[df['x'] == v])}"
                        for v in sorted(df.loc[dup_mask, "x"].unique()))
    st.error(f"⛔ Hay valores de x repetidos ({detalle}). La fórmula de Lagrange divide entre "
             "(x_i − x_j), que sería 0. Cambia o elimina uno de los puntos.")
    st.stop()

# (1b) X casi iguales -> denominadores ~0, resultados sin sentido
gaps = np.diff(np.sort(xs))
if gaps.min() <= 1e-9 * max(1.0, np.abs(xs).max()):
    st.error("⛔ Hay dos valores de x prácticamente idénticos (diferencia < 1e-9): "
             "los denominadores serían casi 0 y el resultado numérico no es confiable.")
    st.stop()
if gaps.min() < 1e-6 * max(xs.max() - xs.min(), 1.0):
    st.warning("⚠️ Hay valores de x muy próximos entre sí: el polinomio puede tener valores "
               "enormes y perder precisión numérica.")

# Magnitudes extremas (evita overflow)
if max(np.abs(xs).max(), np.abs(ys).max()) > 1e100:
    st.error("⛔ Hay valores demasiado grandes (> 1e100); causarían desbordamiento numérico.")
    st.stop()
if n >= 12:
    st.warning(f"⚠️ Con N = {n} puntos el polinomio es de grado {n-1}: es normal ver oscilaciones "
               "fuertes (fenómeno de Runge) y pérdida de precisión.")

# Valor a evaluar
if x_star is None or not np.isfinite(x_star):
    st.warning("⚠️ El valor 'Evaluar g(x) en x' es inválido; se usa el promedio de las x.")
    x_star = float(xs.mean())

sig = (tuple(np.round(xs, 10)), tuple(np.round(ys, 10)))

# ----------------------------------------------------------------------------
# Detección de cambios -> RECÁLCULO COMPLETO
# ----------------------------------------------------------------------------
changed = sig != ss.last_sig
if changed:
    prev = ss.last_sig
    ss.prev_points = None if prev is None else (np.array(prev[0]), np.array(prev[1]))
    ops = op_count(n)
    ss.total_ops += ops["total"]
    label = ss.pending if ss.pending else "✏️ Valor modificado"
    ss.log.append({"#": len(ss.log) + 1, "Evento": label, "N": n, "Grado": n - 1,
                   "Términos L_i recalculados": n, "Términos reutilizados": 0,
                   "Operaciones": ops["total"]})
    ss.last_sig = sig
    ss.pending = ""
    recomputed = True
else:
    recomputed = False

# ----------------------------------------------------------------------------
# Disposición: izquierda = gráfica / derecha = cálculos
# ----------------------------------------------------------------------------
left, right = st.columns([1.1, 1], gap="large")

# ---------------------------- PANEL IZQUIERDO -------------------------------
with left:
    st.subheader("📈 Visualización")
    span_x = xs.max() - xs.min()
    xx = np.linspace(xs.min() - 0.15 * span_x, xs.max() + 0.15 * span_x, 800)
    with np.errstate(all="ignore"):
        yy = lagrange_eval(xs, ys, xx)
    if not np.all(np.isfinite(yy)):
        st.warning("⚠️ Algunos valores de la curva no son finitos; se omiten en la gráfica.")
        yy = np.where(np.isfinite(yy), yy, np.nan)

    fig = go.Figure()
    if ss.prev_points is not None and (not np.array_equal(ss.prev_points[0], xs)
                                       or not np.array_equal(ss.prev_points[1], ys)):
        px, py = ss.prev_points
        with np.errstate(all="ignore"):
            y_prev = lagrange_eval(px, py, xx)
        fig.add_trace(go.Scatter(x=xx, y=y_prev, mode="lines",
                                 name="Curva anterior", line=dict(color="gray", dash="dash", width=2)))
    fig.add_trace(go.Scatter(x=xx, y=yy, mode="lines", name=f"g(x), grado {n-1}",
                             line=dict(color="#4B2E91", width=3)))
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers+text", name="Puntos",
        text=labels, textposition="top center",
        textfont=dict(size=14, color="#E4572E"),
        customdata=[[l] for l in labels],
        hovertemplate="<b>%{customdata[0]}</b><br>x = %{x}<br>f(x) = %{y}<extra></extra>",
        marker=dict(size=12, color="#E4572E", line=dict(width=2, color="white"))))
    with np.errstate(all="ignore"):
        gx = float(lagrange_eval(xs, ys, np.array([x_star]))[0])
    fig.add_trace(go.Scatter(x=[x_star], y=[gx], mode="markers", name=f"g({x_star:g}) = {gx:.4g}",
                             marker=dict(size=14, symbol="star", color="#2A9D8F")))

    span_y = max(ys.max() - ys.min(), 1.0)
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=30, b=10),
                      xaxis_title="x", yaxis_title="g(x)",
                      yaxis=dict(range=[ys.min() - 1.5 * span_y, ys.max() + 1.5 * span_y]),
                      legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("La línea gris discontinua es la curva de la versión anterior: al añadir, quitar o mover "
               "un punto la curva completa cambia (con muchos puntos aparecen oscilaciones tipo Runge). "
               "El eje Y se recorta para que la gráfica siga siendo legible.")

    st.markdown("#### 🧮 Tabla de datos vigente")
    st.dataframe(pd.DataFrame({"Punto": labels, "i": range(n), "x_i": xs, "f_i": ys}), hide_index=True,
                 use_container_width=True)

# ---------------------------- PANEL DERECHO ---------------------------------
with right:
    st.subheader("🧾 Desglose matemático")

    if recomputed:
        st.warning(f"🔄 **¡Cambio detectado!** El polinomio se **recalculó desde cero**: "
                   f"los {n} términos L_i(x) se reconstruyeron. Reutilizados: **0**.")
    else:
        st.info("Sin cambios en los datos desde el último cálculo.")

    ops = op_count(n)
    m1, m2, m3 = st.columns(3)
    m1.metric("Términos L_i", n)
    m2.metric("Operaciones / evaluación", ops["total"])
    m3.metric("Reutilizados", 0)

    tab1, tab2, tab3 = st.tabs(["Fórmula y evaluación", "¿Se puede reutilizar?", "Historial de recálculos"])

    # --- Tab 1: fórmula paso a paso ------------------------------------------
    with tab1:
        st.markdown("**Fórmula general**")
        st.latex(r"g(x)=\sum_{i=0}^{%d} f_i\,L_i(x),\qquad L_i(x)=\prod_{\substack{j=0\\ j\ne i}}^{%d}\frac{x-x_j}{x_i-x_j}"
                 % (n - 1, n - 1))

        st.markdown("**Fórmula con los datos actuales**")
        terms = []
        for i in range(n):
            num = "".join(f"(x-{fmt(xs[j])})" for j in range(n) if j != i)
            den = "".join(f"({fmt(xs[i])}-{fmt(xs[j])})" for j in range(n) if j != i)
            terms.append(r"\frac{%s}{%s}\,%s" % (num, den, fmt(ys[i])))
        st.latex("g(x)=" + " + ".join(terms))

        st.markdown(f"**Sustitución en x = {x_star:g}** (cada término se vuelve a calcular)")
        total = 0.0
        for i in range(n):
            nums = [x_star - xs[j] for j in range(n) if j != i]
            dens = [xs[i] - xs[j] for j in range(n) if j != i]
            Li = float(np.prod(nums) / np.prod(dens))
            total += ys[i] * Li
            with st.expander(f"Término i = {i}:  L_{i}({x_star:g}) · f_{i}", expanded=(n <= 5)):
                st.latex(r"L_{%d}=\prod\frac{x-x_j}{x_{%d}-x_j}=%s" % (
                    i, i,
                    r"\cdot".join(r"\frac{%s}{%s}" % (fmt(a), fmt(b)) for a, b in zip(nums, dens))))
                st.latex(r"\text{Prod. numerador}=%.6g,\quad \text{Prod. denominador}=%.6g"
                         % (np.prod(nums), np.prod(dens)))
                st.latex(r"L_{%d}=%.6g\;\Rightarrow\; L_{%d}\cdot f_{%d}=%.6g\cdot%s=%.6g"
                         % (i, Li, i, i, Li, fmt(ys[i]), Li * ys[i]))
        st.success(f"g({x_star:g}) = Σ L_i·f_i = **{total:.6g}**")

        st.markdown("**Polinomio expandido (potencias de x)**")
        st.latex("g(x)=" + poly_latex(lagrange_coeffs(xs, ys)))

    # --- Tab 2: comparación con la versión anterior ---------------------------
    with tab2:
        st.markdown("Comparación de los denominadores $\\prod_{j\\ne i}(x_i-x_j)$ "
                    "entre la versión anterior y la actual:")
        if ss.prev_points is None or not recomputed:
            st.info("Modifica, añade o elimina un punto para ver la comparación.")
        else:
            px, py = ss.prev_points
            old_den = dict(zip(np.round(px, 10), denominators(px)))
            new_den = denominators(xs)
            rows = []
            for i in range(n):
                key = round(xs[i], 10)
                od = old_den.get(key)
                if od is None:
                    rows.append({"x_i": xs[i], "Denominador anterior": "— (punto nuevo)",
                                 "Denominador actual": new_den[i], "¿Reutilizable?": "❌ se calcula de cero"})
                else:
                    same = np.isclose(od, new_den[i])
                    rows.append({"x_i": xs[i], "Denominador anterior": od, "Denominador actual": new_den[i],
                                 "¿Reutilizable?": "✅ (solo cambió f_i)" if same else "❌ cambió → recalcular"})
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
            removed = [x for x in px if round(x, 10) not in {round(v, 10) for v in xs}]
            if removed:
                st.caption(f"Puntos eliminados / movidos: {[float(v) for v in removed]}. "
                           "Al desaparecer un nodo, el factor correspondiente desaparece de TODOS los productos.")
            st.caption("Al añadir o quitar un nodo x_k, cada L_i gana o pierde el factor (x−x_k)/(x_i−x_k), "
                       "así que ningún término previo sirve tal cual. "
                       "Si únicamente se cambia un valor f_i (no las x), las L_i podrían guardarse, "
                       "pero el algoritmo de la presentación las reconstruye igualmente.")
        st.markdown("**Costo de evaluar g(x) en un solo valor de x**")
        st.table(pd.DataFrame([ops]).rename(columns=str.capitalize))
        st.caption("Evaluar en *otro* x vuelve a costar lo mismo: no hay nada que reaprovechar entre evaluaciones.")

    # --- Tab 3: historial -----------------------------------------------------
    with tab3:
        st.markdown("Cada fila es un **recálculo completo** provocado por un cambio:")
        st.dataframe(pd.DataFrame(ss.log).iloc[::-1], hide_index=True, use_container_width=True)
        st.metric("Operaciones acumuladas (solo reconstrucciones)", ss.total_ops)
        if st.button("Limpiar historial"):
            ss.log = []
            ss.total_ops = 0
            st.rerun()

st.divider()
st.markdown(
    "**Desventajas ilustradas:** (1) el número de cálculos crece como O(N²) por evaluación; "
    "(2) otro valor de x exige repetir todo; (3) al aumentar o disminuir los datos no se aprovechan "
    "cálculos previos; (4) el error es difícil de evaluar y la curva puede oscilar con muchos nodos."
)

