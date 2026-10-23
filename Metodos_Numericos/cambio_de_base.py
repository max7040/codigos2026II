def convertir_base(numero_str, base_origen, base_destino):
  """Convierte un número entero de cualquier base (2 a 36) a otra."""
  try:

    decimal = int(numero_str, base_origen)

    if base_destino == 10:
      return str(decimal)

    if decimal == 0:
      return "0"

    caracteres = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    res = ""
    while decimal > 0:
      res = caracteres[decimal % base_destino] + res
      decimal //= base_destino
    return res

  except ValueError:
    return (
        f"❌ Error: El número '{numero_str}' no es válido para la base"
        f" {base_origen}."
    )


if __name__ == "__main__":
  print("=======================================")
  print("     CONVERSOR DE BASES NUMÉRICAS      ")
  print("=======================================")

  num_input = input("Ingresa el número que quieres convertir: ").strip()

  try:
    b_origen = int(input("Ingresa la base de origen (ej. 2, 8, 10, 16): "))
    b_destino = int(input("Ingresa la base de destino (ej. 2, 8, 10, 16): "))

    if 2 <= b_origen <= 36 and 2 <= b_destino <= 36:
      resultado = convertir_base(num_input, b_origen, b_destino)
      print("\n---------------------------------------")
      print(f"Resultado: El número **{num_input}** en base **{b_origen}**")
      print(f"equivale a: **{resultado}** en base **{b_destino}**")
      print("---------------------------------------")
    else:
      print("❌ Error: Las bases deben estar estrictamente entre 2 y 36.")

  except ValueError:
    print("❌ Error: Las bases deben ser números enteros.")