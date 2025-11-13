# Simulador de Banco

Este robusto simulador bancario incluye tanto un proceso de identificación en el que podrás registrarte y si ya tienes cuentas podrás iniciar sesión. Gracias a ello tendrás tus propias credenciales.
Una vez dentro de la cuenta podrás realizar todo tipo de acciones bancarias.

## Acciones permitidas 

 - **Ingresar dinero**
 - **Retirar dinero**
 - **Ver saldo**
 - **Ver información personal**
 - **Realizar transferencia**
 - **Pedir préstamo**
 - **Ver historial de movimientos**

## Valores por defecto:
```
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
```
**Estos valores te permitirán realizar pruebas sin necesidad de crear nuevos usuarios.**

## Función inicial

Para iniciar la simulación deberás llamar a la función **iniciarSimulacion()**.
```
def iniciarSimulacion():
```

## Importaciones de módulos

- **datetime** : Para recoger la fecha y hora exacta actual.
- **random** : Para generar números aleatorios en un rango determinado.