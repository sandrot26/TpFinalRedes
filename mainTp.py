import requests
from requests import Session
from lxml import etree, html
from DatabaseHelper import DatabaseHelper
import socket
from datetime import datetime


s = Session()

s.get("http://www.bcra.gob.ar/PublicacionesEstadisticas/Evolucion_moneda.asp")
Monedas = [
    {"nombre": "Peso", "codigo": 5,"id_moneda":1},
    {"nombre": "Real", "codigo": 12,"id_moneda":2},
    {"nombre": "Dólar estadounidense", "codigo": 2,"id_moneda":3},
    {"nombre": "Peso Chileno", "codigo": 11,"id_moneda":4},
    
]

dbh = DatabaseHelper()

for moneda in Monedas:
    payload = {
        "Fecha": "2023.07.1",
        "Moneda": moneda['codigo']
    }
    r = s.post(url="http://www.bcra.gob.ar/PublicacionesEstadisticas/Evolucion_moneda_2.asp", data=payload)

    tree = html.fromstring(r.text)
    filas = tree.xpath("//table/tr")
    for fila in filas:
        arrayValores = []
        arrayValores.append({"fecha": fila[0].text.replace("\r", "").replace("\n", "")})
        arrayValores.append({"nombre": moneda['nombre']})
        arrayValores.append({"id_moneda": moneda["id_moneda"]})
        arrayValores.append({"equivausd": fila[1].text})
        arrayValores.append({"equivapeso": fila[2].text})
        
        dbh.DBQuery(dbh.constructorInsert("cotizacion_historico", arrayValores))
        ##print("Insertado: " + str(fila[0].text.replace("\r", "").replace("\n", "")) + "  " + moneda['nombre'])

dbh.commit()

class MainProgram:
    def __init__(self):
        # Inicializar la base de datos y otros elementos necesarios
        self.dbh = DatabaseHelper()
        self.s = Session()

    def menu(self):
        # Implementar un menú interactivo para acceder a los diferentes métodos
        while True:
            print("\n------------------------------------------------------------------------")
            print("\nMenú:")
            print("\n-------------------------------")
            print("1. Histórico")
            print("2. Actualización")
            print("3. Consulta Específica")
            print("4. Consulta por Rango")
            print("5. Diferencia")
            print("6. Servidor")
            print("7. Salir")
            print("-------------------------------")
            
            choice = input("\nSeleccione una opción: ")

            if choice == '1':
                self.historico()
            elif choice == '2':
                self.actualizacion()
            elif choice == '3':
                self.consulta_especifica()
            elif choice == '4':
                self.consulta_rango()
            elif choice == '5':
                self.diferencia()
            elif choice == '6':
                self.servidor()
            elif choice == '7':
                print("Saliendo del programa.")
                break
            else:
                print("Opción no válida. Intente de nuevo.")

    def historico(self):
        start_date = input("Ingrese la fecha de inicio (dd/mm/aaaa): ")
        ##end_date = input("Ingrese la fecha de fin (dd/mm/aaaa): ")
        for moneda in Monedas:
            payload = {
                "Fecha": start_date,
                "Moneda": moneda['codigo']
            }
            r = self.s.post(url="http://www.bcra.gob.ar/PublicacionesEstadisticas/Evolucion_moneda_2.asp", data=payload)

            tree = html.fromstring(r.text)
            filas = tree.xpath("//table/tr")
            for fila in filas:
                arrayValores = []
                arrayValores.append({"fecha": fila[0].text.replace("\r", "").replace("\n", "")})
                arrayValores.append({"nombre": moneda['nombre']})
                arrayValores.append({"id_moneda": moneda["id_moneda"]})
                arrayValores.append({"equivausd": fila[1].text})
                arrayValores.append({"equivapeso": fila[2].text})

                # Guardar el registro en la base de datos
                self.dbh.DBQuery(self.dbh.constructorInsert("cotizacion_historico", arrayValores))
                print("Insertado: " + str(fila[0].text.replace("\r", "").replace("\n", "")) + "  " + moneda['nombre'])

        self.dbh.commit()

    def actualizacion(self):
        for moneda in Monedas:
            payload = {
                "Fecha": datetime.now().strftime("%Y.%m.%d"),
                "Moneda": moneda['codigo']
            }
            r = self.s.post(url="http://www.bcra.gob.ar/PublicacionesEstadisticas/Evolucion_moneda_2.asp", data=payload)

            tree = html.fromstring(r.text)
            filas = tree.xpath("//table/tr")
            for fila in filas:
                arrayValores = []
                arrayValores.append({"fecha": fila[0].text.replace("\r", "").replace("\n", "")})
                arrayValores.append({"nombre": moneda['nombre']})
                arrayValores.append({"id_moneda": moneda["id_moneda"]})
                arrayValores.append({"equivausd": fila[1].text})
                arrayValores.append({"equivapeso": fila[2].text})

                # Guardar el registro en la base de datos
                self.dbh.DBQuery(self.dbh.constructorInsert("cotizacion_historico", arrayValores))
                print("Insertado: " + str(fila[0].text.replace("\r", "").replace("\n", "")) + "  " + moneda['nombre'])

        self.dbh.commit()

    def consulta_especifica(self):
        date = input("Ingrese la fecha (dd/mm/aaaa): ")
        print("\nPeso: 1, Real: 2, Dólar estadounidense: 3, Peso Chileno: 4")
        currency_type = int(input("Ingrese el id_moneda: "))    

        # Llamar a la función correspondiente de la base de datos
        value = self.dbh.consulta_especifica(date, currency_type)

        if value is not None:
            print(f"Valor para id_moneda {currency_type} en la fecha {date} (equivausd): {value}")
        else:
            print(f"No hay datos disponibles para id_moneda {currency_type} en la fecha {date}.")


    def consulta_rango(self):
        start_date = input("Ingrese la fecha de inicio (dd/mm/aaaa): ")
        end_date = input("Ingrese la fecha de fin (dd/mm/aaaa): ")
        print("\nPeso: 1, Real: 2, Dólar estadounidense: 3, Peso Chileno: 4")
        currency_type = int(input("Ingrese el id_moneda: "))

        # Llamar a la función correspondiente de la base de datos
        values = self.dbh.consulta_rango(start_date, end_date, currency_type)

        if values:
            print(f"Valores para id_moneda {currency_type} en el rango de fechas {start_date} a {end_date}:")
            for value in values:
                print(f"Fecha: {value['fecha']}, EquivaUSD: {value['equivausd']}, EquivaPeso: {value['equivapeso']}")
        else:
            print(f"No hay datos disponibles para id_moneda {currency_type} en el rango de fechas {start_date} a {end_date}.")


    def diferencia(self):
        start_date = input("Ingrese la fecha de inicio (dd/mm/aaaa): ")
        end_date = input("Ingrese la fecha de fin (dd/mm/aaaa): ")
        print("\nPeso: 1, Real: 2, Dólar estadounidense: 3, Peso Chileno: 4")
        currency_type = int(input("Ingrese el id_moneda: "))

        # Llamar a la función correspondiente de la base de datos
        diff = self.dbh.diferencia(start_date, end_date, currency_type)

        if diff is not None:
            print(f"Diferencia porcentual para id_moneda {currency_type} entre {start_date} y {end_date}: {diff:.2f}%")
        else:
            print(f"No hay datos disponibles para id_moneda {currency_type} en el rango de fechas {start_date} a {end_date}.")


    def servidor(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 2345))
        server_socket.listen(1)

        print("Servidor esperando conexiones en el puerto 2345...")

        while True:
            client_socket, client_address = server_socket.accept()
            print("Conexión establecida desde:", client_address)

            # Recibir la fecha del cliente
            date_str = client_socket.recv(1024).decode('utf-8')

            # Llamar a la función correspondiente de la base de datos
            value = self.dbh.valor_por_fecha(date_str)

            # Enviar el valor de vuelta al cliente
            client_socket.send(str(value).encode('utf-8'))

            client_socket.close()

# Lista de monedas
Monedas = [
    {"nombre": "Peso", "codigo": 5, "id_moneda": 1},
    {"nombre": "Real", "codigo": 12, "id_moneda": 2},
    {"nombre": "Dólar estadounidense", "codigo": 2, "id_moneda": 3},
    {"nombre": "Peso Chileno", "codigo": 11, "id_moneda": 4},
]

# Instanciar la clase y ejecutar el menú
main_program = MainProgram()
main_program.menu()