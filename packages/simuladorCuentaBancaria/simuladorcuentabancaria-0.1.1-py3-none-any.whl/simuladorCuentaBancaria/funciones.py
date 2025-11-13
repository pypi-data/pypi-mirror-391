import datetime
import random

def iniciarSimulacion():
    cuentas = {
    "ES123412": {"titular": "Nico","password": "1234", "saldo": 500},
    "ES456432": {"titular": "Ana","password": "1111", "saldo": 1000}
    }
    historial = {
        "Nico":[
            {"msg":"Registro completado en el banco.", "fecha": "2025-11-12 10:10:00"}
            ],
        "Ana": [
            {"msg": "Registro completado en el banco.", "fecha": "2025-11-12 10:10:00"}
            ]

    }
    mostrarMenuLoggin(cuentas,historial)

def iniciarSesion(cuentas,historial):
    titular = input("Introduce el nombre del titular (Enter para cancelar): ")
    if titular=="":
        print("↩️ Operación cancelada.")
        return
    password = input("introduce la contraseña: ")
    for cuentaBancaria, datos in cuentas.items():
        if datos["titular"]==titular and datos["password"]==password:
            print(f"🪪 Bienvenido {titular}, tu numero de cuenta es {cuentaBancaria}")
            mostrarMenu(cuentas,cuentaBancaria,historial)
            return
    else:
        print("❌ Usuario o contraseña incorrectos.")


def registro(cuentas,historial):
    try:
        titular = input("Introduce el nombre del titular (Enter para cancelar): ")
        if titular=="":
                print("↩️ Operación cancelada.")
                return
        for cuentaBancaria, datos in cuentas.items():
            if datos["titular"]==titular:
                print("🚫 Usuario existente. Intente con otro nombre")
                return
        password = input("Introduce la contraseña: ")
        saldo = float(input("Introduce el saldo inicial: "))
        cuentaBancaria = generarNumBancario(cuentas) 
        cuentas[cuentaBancaria]={
            "titular":titular,
            "password":password,
            "saldo":saldo
        }
        historial[titular] = []
        historial[titular].append(crearAccion("Registro completado en el banco."))
        print(f"✅ Registro completado con exito.\n🪪  Bienvenido {titular}! Su numero de cuenta es {cuentaBancaria}")
        mostrarMenu(cuentas,cuentaBancaria,historial)
    except ValueError:
        print("❌ El saldo debe ser un número válido.")

def generarNumBancario(cuentas):
    while True:
        numBancario = str(random.randint(100000,999999))
        cuenta = "ES"+numBancario
        if cuenta not in cuentas:
            return cuenta

def mostrarMenuLoggin(cuentas,historial):
    while True:
        try:
            optionInicial = int(input("🏦 BIENVENIDO A TU BANCO DE CONFIANZA 🏦\n1.🔑 Iniciar sesión\n2.📝 Registrarse\n3.🚪 Salir\n"))
            if optionInicial==1:
                iniciarSesion(cuentas,historial)
            elif optionInicial==2:        
                registro(cuentas,historial)
            elif optionInicial==3:
                print("👋 Saliendo...")
                break
            else:
               print("🚫 Opción no válida.")
        except ValueError:
            print("🚫 Introduce un valor válido.")

def mostrarMenu(cuentas,cuentaBancaria,historial):
    while True:
        try:
            opcion = int(input(f"🏧 Menu para {cuentas[cuentaBancaria]["titular"]}\n1.💵 Ingresar dinero\n2.💸 Retirar dinero\n3.💰 Ver saldo\n4.👤 Ver información personal\n5.📤 Realizar transferencia\n6.📥 Pedir préstamo\n7.📜 Ver historial\n8.🚪 Salir\n"))
            match opcion:
                case 1:
                    ingresarDinero(cuentas, cuentaBancaria,historial)
                case 2:
                    retirarDinero(cuentas, cuentaBancaria,historial)
                case 3:
                    verSaldo(cuentas, cuentaBancaria)
                case 4:
                    verInfoPersonal(cuentas, cuentaBancaria)
                case 5:
                    realizarTransferencia(cuentas,cuentaBancaria,historial)
                case 6:
                    pedirPrestamo(cuentas,cuentaBancaria,historial)
                case 7:
                    verHistorial(cuentas[cuentaBancaria]["titular"],historial)
                case 8:
                    print(f"👋 ¡Hasta pronto, {cuentas[cuentaBancaria]["titular"]}!")
                    break
                case _:
                    print("🚫 Introduce una opcion correcta.")
        except ValueError:
            print("🚫 Introduce una opcion correcta.")
def ingresarDinero(cuentas, cuentaBancaria,historial):
    while True:
        try:
            saldoAIngresarStr = input("¿Cuanto dinero quieres ingresar a la cuenta? (Enter para cancelar)\n")
            if saldoAIngresarStr=="":
                print("↩️ Operación cancelada.")
                break
            saldoAIngresar = float(saldoAIngresarStr)
            if saldoAIngresar < 0:
                print("🚫 Ingresa una cantidad positiva")
                continue

        except ValueError:
            print("🚫 Ingrese un dato válido")
        else:
            cuentas[cuentaBancaria]["saldo"] += saldoAIngresar
            print("✅ Dinero ingresado con EXITO")
            historial[cuentas[cuentaBancaria]["titular"]].append(crearAccion(f"Ingreso de $ {saldoAIngresar}."))
            break

def retirarDinero(cuentas, cuentaBancaria,historial):
    while True:
        try:
            saldoARetirarStr = input("¿Cuanto dinero quieres retirar de la cuenta? (Enter para cancelar)\n")
            if saldoARetirarStr=="":
                print("↩️ Operación cancelada.")
                break
            saldoARetirar = float(saldoARetirarStr)
            if saldoARetirar < 0:
                print("🚫 Ingresa una cantidad positiva")
                continue

            if saldoARetirar > cuentas[cuentaBancaria]["saldo"]:
                print("🚫 No tienes suficiente saldo en tu cuenta")
                verSaldo(cuentas, cuentaBancaria)
                continue

        except ValueError:
            print("🚫 Ingrese un dato válido")
        else:
            cuentas[cuentaBancaria]["saldo"] -= saldoARetirar
            print("✅ Dinero retirado con EXITO")
            historial[cuentas[cuentaBancaria]["titular"]].append(crearAccion(f"Retiro de $ {saldoARetirar}."))
            break


def verSaldo(cuentas, cuentaBancaria):
    print("💰 Tu saldo actual es de: $",cuentas[cuentaBancaria]["saldo"])
    input("\nPresiona Enter para volver al menú...")


def verInfoPersonal(cuentas,cuentaBancaria):
    print(f"\n💳 Número de cuenta bancaria: {cuentaBancaria}\n👤 Nombre de usuario: {cuentas[cuentaBancaria]['titular']}\n🔒 Contraseña: {cuentas[cuentaBancaria]['password']}\n💰 Saldo disponible: $ {cuentas[cuentaBancaria]["saldo"]}")
    input("\nPresiona Enter para volver al menú...")


def realizarTransferencia(cuentas,cuentaBancaria,historial):
    while True:
        try:
            usuarioTransferencia = input("Introduce la cuenta bancaria del usuario al que desea transferir el dinero (Enter para cancelar): ")
            if usuarioTransferencia == "":
                print("↩️ Transferencia cancelada.")
                break
            dineroTransferido = float(input("Introduce la cantidad que desea transferir: "))
            if dineroTransferido < 0:
                print("🚫 Ingresa una cantidad positiva")
                continue
            if dineroTransferido > cuentas[cuentaBancaria]["saldo"]:
                print("❌ No tienes suficiente saldo en tu cuenta")
                verSaldo(cuentas, cuentaBancaria)
                continue
        except ValueError:
            print("❌ Cantidad ingresada no válida.")
            break
        if usuarioTransferencia == cuentaBancaria:
                print("🚫 No puedes transferirte dinero a ti mismo.")
                continue
        if usuarioTransferencia in cuentas:
            cuentas[usuarioTransferencia]['saldo'] += dineroTransferido
            cuentas[cuentaBancaria]['saldo'] -= dineroTransferido
            print(f"✅ ¡Transferencia realizada! ${dineroTransferido} a {cuentas[usuarioTransferencia]['titular']}")
            historial[cuentas[cuentaBancaria]["titular"]].append(crearAccion(f"Transferencia realizada de $ {dineroTransferido} a {cuentas[usuarioTransferencia]["titular"]}."))
            historial[cuentas[usuarioTransferencia]["titular"]].append(crearAccion(f"Has recibido $ {dineroTransferido} de {cuentas[cuentaBancaria]["titular"]}."))
            break
        else:
            print("❌ ¡Fallo en la transferencia! Usuario no encontrado.")
            break


def pedirPrestamo(cuentas, cuentaBancaria,historial):
    while True:
        try:
            cantidadStr = input("Introduce la cantidad del préstamo (Enter para cancelar): ")
            if cantidadStr=="":
                print("↩️ Operación cancelada.")
                break
            cantidad = float(cantidadStr)
            if cantidad <= 0:
                print("🚫 La cantidad debe ser positiva.")
                continue
        except ValueError:
            print("❌ Introduce un valor válido.")
        else:
            cuentas[cuentaBancaria]["saldo"] += cantidad
            print("✅ Préstamo concedido.")
            historial[cuentas[cuentaBancaria]["titular"]].append(crearAccion(f"Te han aceptado un préstamo de $ {cantidad}."))
            break


def verHistorial(titular,historial):
    print(f"📜 Historial de {titular}")
    for accion in historial[titular]:
        print(f"  - [ {accion["fecha"]} ] {accion["msg"]}")
    input("\nPresiona Enter para volver al menú...")


def crearAccion(msg):
    return {"msg":msg,
            "fecha":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
