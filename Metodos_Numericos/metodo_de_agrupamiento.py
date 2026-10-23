def probar_error_redondeo():
    valor_inicial = 1.0
    incremento = 0.00001
    iteraciones = 10000

    suma = valor_inicial
    
    # Sumar 0.00001 diez mil veces
    for _ in range(iteraciones):
        suma += incremento

    valor_teorico = 1.1
    error_absoluto = abs(suma - valor_teorico)

    print("=" * 40)
    print("DEMOSTRACIÓN DE ERROR DE REDONDEO")
    print("=" * 40)
    print(f"Valor inicial: {valor_inicial}")
    print(f"Incremento: {incremento}")
    print(f"Número de iteraciones: {iteraciones}")
    print(f"Resultado esperado (teórico): {valor_teorico}")
    print(f"Resultado obtenido en la PC:   {suma}")
    print(f"Diferencia (Error absoluto):  {error_absoluto}")
    print("=" * 40)

if __name__ == "__main__":
    probar_error_redondeo()