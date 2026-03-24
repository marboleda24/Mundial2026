from aplicacion import crear_aplicacion

app = crear_aplicacion()

if __name__ == '__main__':
    print("Iniciando Plataforma Polla Mundial 2026 (Esquema V2)...")
    app.run(debug=True)
