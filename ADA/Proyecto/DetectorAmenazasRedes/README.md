# Detector de Amenazas en Redes

Proyecto académico (Análisis y Diseño de Algoritmos, Unidad 1). Modela una red **simulada** como grafo,
detecta patrones sospechosos con reglas explicables y muestra los resultados con Streamlit, NetworkX y Plotly.
No escanea redes reales ni usa inteligencia artificial.

## Requisitos
Windows 11, Python 3.10 o superior y Visual Studio Code.

## Instalación y ejecución (PowerShell)

1. **Comprobar Python** (debe mostrar la versión):
   ```powershell
   python --version
   ```
   Si falla, prueba `py --version`; si tampoco funciona, instala Python desde python.org marcando *Add python.exe to PATH*.
2. **Abrir la carpeta en VS Code:** `Archivo > Abrir carpeta...` y elige `DetectorAmenazasRedes`.
   Abre la terminal con `Ctrl + ñ` (debe ser *PowerShell*; si no, elígela en el menú desplegable de la terminal).
3. **Crear el entorno virtual** (aísla las bibliotecas del proyecto):
   ```powershell
   python -m venv .venv
   ```
4. **Activarlo:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   Verás `(.venv)` al inicio de la línea. En **CMD** el comando sería `.venv\Scripts\activate.bat`.
5. **Instalar dependencias:**
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
6. **Ejecutar las pruebas:**
   ```powershell
   pytest
   ```
7. **Iniciar la aplicación:**
   ```powershell
   streamlit run app.py
   ```
8. **Abrir en el navegador:** se abre sola; si no, entra a http://localhost:8501. Para detenerla: `Ctrl + C` en la terminal.

## Problemas frecuentes
| Problema | Solución |
|---|---|
| `Activate.ps1 no se puede cargar porque la ejecución de scripts está deshabilitada` | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` y vuelve a activar. |
| `python` no se reconoce | Usa `py` o reinstala Python marcando *Add to PATH*. |
| `ModuleNotFoundError` | Activa el entorno `(.venv)` y repite `pip install -r requirements.txt`. |
| `streamlit` no se reconoce | Usa `python -m streamlit run app.py`. |
| El puerto 8501 está ocupado | `streamlit run app.py --server.port 8502`. |
| VS Code usa otro intérprete | `Ctrl+Shift+P` > *Python: Select Interpreter* > el de `.venv`. |
| Aviso de `use_container_width` obsoleto | Es solo una advertencia de versiones nuevas de Streamlit; no afecta el funcionamiento. |

## Estructura
- `app.py`: punto de entrada (menú lateral).
- `interfaz/`: una página de Streamlit por módulo (Inicio, Constructor, Visualización, Detector, Laboratorio, Estadísticas, Ayuda) y el estado compartido.
- `algoritmos/`: ordenamiento, búsqueda, recursión, divide y vencerás, voraces, programación dinámica.
- `estructuras/`: tabla hash, árbol binario de búsqueda, grafo (lista de adyacencia propia).
- `analisis/`: detector de reglas, métricas de grafo y benchmark de ordenamiento.
- `visualizacion/`: grafo con NetworkX + Plotly y gráficos estadísticos.
- `utils/validaciones.py`: importación/exportación JSON y CSV con errores comprensibles.
- `pruebas/`: pruebas con pytest · `data/ejemplo_red.json`: red de ejemplo.

## Formato de importación
- JSON: `{"dirigido": true, "nodos": [{"id": "pc-01", "tipo": "equipo"}], "conexiones": [{"origen": "pc-01", "destino": "srv-web", "peso": 1, "frecuencia": 30, "eventos": 12}]}`
- CSV: nodos `id,tipo`; conexiones `origen,destino,peso,frecuencia,eventos`. Tipos: equipo, servidor, cuenta.
