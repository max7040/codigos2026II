// main.cpp - WordWise: corrector ortográfico y autocompletado
// Proyecto del curso Análisis y Diseño de Algoritmos (SIS214) - Unidad I
//
// Compilar:  g++ -O2 -std=c++17 main.cpp -o wordwise
// Ejecutar:  ./wordwise                (menú interactivo; requiere diccionario.txt en la misma carpeta)
//            ./wordwise --benchmark    (ejecuta todos los benchmarks y guarda resultados_benchmark.csv)
//            ./wordwise --benchmark --completo   (incluye los O(n^2) con n = 50 000 y 100 000: tarda minutos)
#include <iostream>
#include <iomanip>
#include <string>
#include <vector>
#include "utils.hpp"
#include "hash_table.hpp"
#include "trie.hpp"
#include "heap.hpp"
#include "sorting.hpp"
#include "edit_distance.hpp"
#include "search.hpp"
#include "corrector.hpp"
#include "benchmark.hpp"

using namespace std;

// ---------- Estado de la aplicación ----------
struct WordWise {
    vector<Palabra> dic;
    TablaHash tabla;
    Trie trie;

    bool cargar(const string& ruta) {
        dic = cargarDiccionario(ruta);
        for (const Palabra& p : dic) {
            tabla.insertar(p.texto, p.freq);
            trie.insertar(p.texto, p.freq);
        }
        return !dic.empty();
    }
};

static string leerLinea(const string& mensaje) {
    cout << mensaje;
    string s;
    if (!getline(cin, s)) { cout << "\n"; exit(0); }
    return s;
}

// ---------- Opciones del menú ----------
static void verificar(const WordWise& w) {
    string p = normalizar(leerLinea("Palabra a verificar: "));
    if (p.empty()) { cout << "  (entrada vacia)\n"; return; }
    int f = w.tabla.frecuencia(p);
    if (f >= 0) cout << "  [OK] \"" << p << "\" existe en el diccionario (frecuencia " << f << ")\n";
    else        cout << "  [X] \"" << p << "\" NO existe. Pruebe la opcion 3 para ver correcciones.\n";
}

static void autocompletar(const WordWise& w) {
    string p = normalizar(leerLinea("Prefijo: "));
    if (p.empty()) { cout << "  (entrada vacia)\n"; return; }
    auto sug = w.trie.autocompletar(p, 5);
    if (sug.empty()) { cout << "  Sin sugerencias para \"" << p << "\"\n"; return; }
    cout << "  Sugerencias (las 5 mas frecuentes):\n";
    for (const auto& s : sug) cout << "    - " << s.palabra << "  (frecuencia " << s.freq << ")\n";
}

static void corregirPalabra(const WordWise& w) {
    string p = normalizar(leerLinea("Palabra a corregir: "));
    if (p.empty()) { cout << "  (entrada vacia)\n"; return; }
    if (w.tabla.contiene(p)) { cout << "  [OK] \"" << p << "\" esta bien escrita.\n"; return; }
    auto sug = corregir(p, w.dic, 5, 2);
    if (sug.empty()) { cout << "  No se encontraron correcciones cercanas (distancia <= 2).\n"; return; }
    cout << "  Quiso decir:\n";
    for (const auto& s : sug)
        cout << "    - " << s.palabra << "  (distancia de edicion " << s.distancia << ")\n";
}

static void mostrarMatriz() {
    string a = normalizar(leerLinea("Palabra 1: ")), b = normalizar(leerLinea("Palabra 2: "));
    if (a.empty() || b.empty() || a.size() > 15 || b.size() > 15) {
        cout << "  Use palabras de 1 a 15 letras.\n";
        return;
    }
    auto d = matrizDistancia(a, b);
    cout << "\n  Matriz de programacion dinamica (filas: \"" << a << "\", columnas: \"" << b << "\")\n\n      ";
    cout << setw(3) << "-";
    for (char c : b) cout << setw(3) << c;
    cout << "\n";
    for (size_t i = 0; i <= a.size(); ++i) {
        cout << "    " << setw(2) << (i == 0 ? '-' : a[i - 1]);
        for (size_t j = 0; j <= b.size(); ++j) cout << setw(3) << d[i][j];
        cout << "\n";
    }
    cout << "\n  Distancia de edicion = " << d[a.size()][b.size()] << " (esquina inferior derecha)\n";
}

static void estadisticas(const WordWise& w) {
    cout << "\n  --- Estadisticas de las estructuras ---\n";
    cout << "  Palabras en el diccionario : " << w.dic.size() << "\n";
    cout << "  Tabla hash: cubetas " << w.tabla.numCubetas() << ", factor de carga " << fixed << setprecision(2)
         << w.tabla.factorCarga() << ", cubetas vacias " << w.tabla.cubetasVacias()
         << ", cadena mas larga " << w.tabla.cadenaMasLarga() << "\n";
    size_t letras = 0;
    for (const Palabra& p : w.dic) letras += p.texto.size();
    cout << "  Trie: " << w.trie.numNodos() << " nodos para " << letras << " letras en total (comparte prefijos)\n";
}

static void menu() {
    cout << "\n=========== WordWise - Corrector y Autocompletado ===========\n"
         << " 1. Verificar palabra            (tabla hash)\n"
         << " 2. Autocompletar                (Trie + heap)\n"
         << " 3. Corregir palabra             (distancia de edicion + heap)\n"
         << " 4. Ver matriz de distancia      (programacion dinamica)\n"
         << " 5. Benchmark de ordenamiento    (EV1)\n"
         << " 6. Benchmark distancia de edicion (recursiva vs DP)\n"
         << " 7. Benchmark de busqueda        (lineal, binaria, hash, trie)\n"
         << " 8. Estadisticas de estructuras\n"
         << " 0. Salir\n";
}

static void ejecutarBenchmarks(const WordWise& w, bool completo) {
    ofstream csv("resultados_benchmark.csv");
    csv << "categoria,algoritmo,caso,n,ms\n";
    benchmarkOrdenamiento(w.dic, completo, csv);
    benchmarkDistancia(csv);
    benchmarkBusqueda(w.dic, csv);
    cout << "\nResultados guardados en resultados_benchmark.csv\n";
}

int main(int argc, char** argv) {
    WordWise w;
    if (!w.cargar("diccionario.txt")) {
        cerr << "No se pudo leer diccionario.txt (debe estar en la misma carpeta que el programa).\n"
             << "Generelo con:  python generar_diccionario.py\n";
        return 1;
    }
    bool soloBench = false, completo = false;
    for (int i = 1; i < argc; ++i) {
        string a = argv[i];
        if (a == "--benchmark") soloBench = true;
        if (a == "--completo") completo = true;
    }
    if (soloBench) { ejecutarBenchmarks(w, completo); return 0; }

    cout << "Diccionario cargado: " << w.dic.size() << " palabras.\n";
    for (;;) {
        menu();
        string op = leerLinea("Opcion: ");
        if (op == "1") verificar(w);
        else if (op == "2") autocompletar(w);
        else if (op == "3") corregirPalabra(w);
        else if (op == "4") mostrarMatriz();
        else if (op == "5") {
            string r = leerLinea("Incluir O(n^2) con n=50000 y 100000? Tarda varios minutos (s/n): ");
            ofstream csv("resultados_benchmark.csv");
            csv << "categoria,algoritmo,caso,n,ms\n";
            benchmarkOrdenamiento(w.dic, !r.empty() && (r[0] == 's' || r[0] == 'S'), csv);
        }
        else if (op == "6") { ofstream csv("resultados_distancia.csv"); csv << "categoria,algoritmo,caso,n,ms\n"; benchmarkDistancia(csv); }
        else if (op == "7") { ofstream csv("resultados_busqueda.csv"); csv << "categoria,algoritmo,caso,n,ms\n"; benchmarkBusqueda(w.dic, csv); }
        else if (op == "8") estadisticas(w);
        else if (op == "0") { cout << "Hasta luego.\n"; break; }
        else cout << "  Opcion no valida.\n";
    }
    return 0;
}
