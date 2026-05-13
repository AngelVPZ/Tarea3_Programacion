"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas
Empresa: Software FJ
Curso: Programación 213023 - UNAD
"""

from abc import ABC, abstractmethod
from datetime import datetime
import os

# ============================================================
# SISTEMA DE LOGS
# ============================================================

LOG_FILE = "softwarefj_logs.txt"

def registrar_log(tipo, mensaje):
    """Registra eventos y errores en archivo de logs."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] [{tipo}] {mensaje}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(linea)
    except Exception as e:
        print(f"Error al escribir log: {e}")


# ============================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================

class ErrorSistema(Exception):
    """Excepción base del sistema."""
    pass

class ErrorClienteInvalido(ErrorSistema):
    """Se lanza cuando los datos del cliente son inválidos."""
    pass

class ErrorServicioInvalido(ErrorSistema):
    """Se lanza cuando los datos del servicio son inválidos."""
    pass

class ErrorReservaInvalida(ErrorSistema):
    """Se lanza cuando la reserva no puede realizarse."""
    pass

class ErrorDisponibilidad(ErrorSistema):
    """Se lanza cuando hay conflicto de horarios."""
    pass

class ErrorEstadoInvalido(ErrorSistema):
    """Se lanza cuando se intenta una transición de estado inválida."""
    pass


# ============================================================
# CLASE ABSTRACTA BASE
# ============================================================

class EntidadBase(ABC):
    """Clase abstracta base para todas las entidades del sistema."""

    @abstractmethod
    def validar(self):
        pass

    @abstractmethod
    def describir(self):
        pass


# ============================================================
# CLASE CLIENTE
# ============================================================

class Cliente(EntidadBase):
    """Representa un cliente del sistema con encapsulación de datos personales."""

    def __init__(self, nombre, cc, ciudad, email):
        self._nombre = None
        self._cc = None
        self._ciudad = None
        self._email = None
        self.nombre = nombre
        self.cc = cc
        self.ciudad = ciudad
        self.email = email

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ErrorClienteInvalido("El nombre debe tener al menos 2 caracteres.")
        self._nombre = valor.strip()

    @property
    def cc(self):
        return self._cc

    @cc.setter
    def cc(self, valor):
        if not str(valor).isdigit() or len(str(valor)) < 6:
            raise ErrorClienteInvalido("La cédula debe ser numérica y tener al menos 6 dígitos.")
        self._cc = str(valor)

    @property
    def ciudad(self):
        return self._ciudad

    @ciudad.setter
    def ciudad(self, valor):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ErrorClienteInvalido("La ciudad debe tener al menos 2 caracteres.")
        self._ciudad = valor.strip()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        if not valor or "@" not in valor or "." not in valor:
            raise ErrorClienteInvalido("El email no es válido.")
        self._email = valor.strip()

    def validar(self):
        return all([self._nombre, self._cc, self._ciudad, self._email])

    def describir(self):
        return f"  [{self._cc}] {self._nombre} | {self._ciudad} | {self._email}"


# ============================================================
# CLASE ABSTRACTA SERVICIO
# ============================================================

class Servicio(EntidadBase, ABC):
    """Clase abstracta que representa un servicio genérico de Software FJ."""

    def __init__(self, id_servicio, nombre, hora_inicio, hora_fin, precio_por_hora):
        if not isinstance(hora_inicio, int) or not isinstance(hora_fin, int):
            raise ErrorServicioInvalido("Las horas deben ser números enteros.")
        if hora_inicio < 0 or hora_fin > 24:
            raise ErrorServicioInvalido("Las horas deben estar entre 0 y 24.")
        if hora_inicio >= hora_fin:
            raise ErrorServicioInvalido("La hora de inicio debe ser menor a la hora de fin.")
        if precio_por_hora <= 0:
            raise ErrorServicioInvalido("El precio por hora debe ser mayor a 0.")

        self._id = id_servicio
        self._nombre = nombre
        self._hora_inicio = hora_inicio
        self._hora_fin = hora_fin
        self._precio_por_hora = precio_por_hora
        self._disponible = True

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def hora_inicio(self):
        return self._hora_inicio

    @property
    def hora_fin(self):
        return self._hora_fin

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = valor

    @abstractmethod
    def calcular_costo(self, descuento=0, aplicar_iva=False):
        pass

    def validar(self):
        return self._hora_inicio < self._hora_fin and self._precio_por_hora > 0

    def describir(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return (f"  [{self._id}] {self._nombre} | "
                f"{self._hora_inicio}:00 - {self._hora_fin}:00 | "
                f"${self._precio_por_hora:,.0f}/hora | {estado}")


# ============================================================
# SERVICIOS ESPECIALIZADOS
# ============================================================

class Sala(Servicio):
    """Servicio de reserva de sala de reuniones."""

    def __init__(self, id_servicio, nombre, hora_inicio, hora_fin, capacidad, precio_por_hora):
        super().__init__(id_servicio, nombre, hora_inicio, hora_fin, precio_por_hora)
        if capacidad <= 0:
            raise ErrorServicioInvalido("La capacidad debe ser mayor a 0.")
        self._capacidad = capacidad

    def calcular_costo(self, descuento=0, aplicar_iva=False):
        horas = self._hora_fin - self._hora_inicio
        costo = horas * self._precio_por_hora
        costo -= costo * (descuento / 100)
        if aplicar_iva:
            costo *= 1.19
        return round(costo, 2)

    def describir(self):
        base = super().describir()
        return f"{base} | Cap: {self._capacidad} personas | [SALA]"


class Equipo(Servicio):
    """Servicio de alquiler de equipos tecnológicos."""

    def __init__(self, id_servicio, nombre, hora_inicio, hora_fin, modelo, marca, precio_por_hora):
        super().__init__(id_servicio, nombre, hora_inicio, hora_fin, precio_por_hora)
        if not modelo or not marca:
            raise ErrorServicioInvalido("El modelo y la marca son obligatorios.")
        self._modelo = modelo
        self._marca = marca

    def calcular_costo(self, descuento=0, aplicar_iva=False):
        horas = self._hora_fin - self._hora_inicio
        costo = horas * self._precio_por_hora
        costo -= costo * (descuento / 100)
        if aplicar_iva:
            costo *= 1.19
        return round(costo, 2)

    def describir(self):
        base = super().describir()
        return f"{base} | {self._marca} {self._modelo} | [EQUIPO]"


class Asesoria(Servicio):
    """Servicio de asesoría especializada."""

    def __init__(self, id_servicio, nombre, hora_inicio, hora_fin, tema, precio_por_hora):
        super().__init__(id_servicio, nombre, hora_inicio, hora_fin, precio_por_hora)
        if not tema:
            raise ErrorServicioInvalido("El tema de la asesoría es obligatorio.")
        self._tema = tema

    def calcular_costo(self, descuento=0, aplicar_iva=False):
        horas = self._hora_fin - self._hora_inicio
        costo = horas * self._precio_por_hora * 1.10
        costo -= costo * (descuento / 100)
        if aplicar_iva:
            costo *= 1.19
        return round(costo, 2)

    def describir(self):
        base = super().describir()
        return f"{base} | Tema: {self._tema} | [ASESORÍA]"


# ============================================================
# CLASE RESERVA
# ============================================================

class Reserva:
    """Integra cliente, servicio y estado. Maneja el ciclo de vida de una reserva."""

    TRANSICIONES = {
        "pendiente":  ["confirmada", "cancelada"],
        "confirmada": ["finalizada", "cancelada"],
        "cancelada":  [],
        "finalizada": []
    }

    def __init__(self, id_reserva, cliente, servicio):
        if not isinstance(cliente, Cliente):
            raise ErrorReservaInvalida("El cliente no es válido.")
        if not isinstance(servicio, Servicio):
            raise ErrorReservaInvalida("El servicio no es válido.")
        if not servicio.disponible:
            raise ErrorDisponibilidad(f"El servicio '{servicio.nombre}' no está disponible.")

        self._id = id_reserva
        self._cliente = cliente
        self._servicio = servicio
        self._estado = "pendiente"
        self._fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _cambiar_estado(self, nuevo_estado):
        if nuevo_estado not in self.TRANSICIONES[self._estado]:
            raise ErrorEstadoInvalido(
                f"No se puede pasar de '{self._estado}' a '{nuevo_estado}'."
            )
        self._estado = nuevo_estado

    def confirmar(self):
        try:
            self._cambiar_estado("confirmada")
            self._servicio.disponible = False
            registrar_log("INFO", f"Reserva {self._id} confirmada para {self._cliente.nombre}")
        except ErrorEstadoInvalido as e:
            registrar_log("ERROR", f"Reserva {self._id}: {e}")
            raise

    def cancelar(self):
        try:
            self._cambiar_estado("cancelada")
            self._servicio.disponible = True
            registrar_log("INFO", f"Reserva {self._id} cancelada para {self._cliente.nombre}")
        except ErrorEstadoInvalido as e:
            registrar_log("ERROR", f"Reserva {self._id}: {e}")
            raise

    def finalizar(self):
        try:
            self._cambiar_estado("finalizada")
            registrar_log("INFO", f"Reserva {self._id} finalizada para {self._cliente.nombre}")
        except ErrorEstadoInvalido as e:
            registrar_log("ERROR", f"Reserva {self._id}: {e}")
            raise

    def obtener_costo(self, descuento=0, aplicar_iva=False):
        return self._servicio.calcular_costo(descuento, aplicar_iva)

    def describir(self):
        return (f"  [{self._id}] {self._cliente.nombre} -> {self._servicio.nombre} | "
                f"Estado: {self._estado} | "
                f"Costo: ${self.obtener_costo():,.0f} | "
                f"Fecha: {self._fecha_creacion}")


# ============================================================
# SISTEMA DE GESTIÓN
# ============================================================

class SistemaReservas:
    """Gestiona clientes, servicios y reservas en memoria."""

    def __init__(self):
        self._clientes = []
        self._servicios = []
        self._reservas = []
        self._id_reserva = 1
        registrar_log("INFO", "Sistema Software FJ iniciado.")

    def registrar_cliente(self, cliente):
        try:
            for c in self._clientes:
                if c.cc == cliente.cc:
                    raise ErrorClienteInvalido(f"Ya existe un cliente con CC {cliente.cc}.")
            self._clientes.append(cliente)
            registrar_log("INFO", f"Cliente registrado: {cliente.nombre} (CC: {cliente.cc})")
        except ErrorClienteInvalido as e:
            registrar_log("ERROR", f"Error al registrar cliente: {e}")
            raise

    def registrar_servicio(self, servicio):
        try:
            for s in self._servicios:
                if s.id == servicio.id:
                    raise ErrorServicioInvalido(f"Ya existe un servicio con ID {servicio.id}.")
            self._servicios.append(servicio)
            registrar_log("INFO", f"Servicio registrado: {servicio.nombre}")
        except ErrorServicioInvalido as e:
            registrar_log("ERROR", f"Error al registrar servicio: {e}")
            raise

    def crear_reserva(self, cliente, servicio):
        try:
            for r in self._reservas:
                if (r._servicio.id == servicio.id and
                        r._estado not in ["cancelada", "finalizada"]):
                    raise ErrorDisponibilidad(
                        f"El servicio '{servicio.nombre}' ya tiene una reserva activa."
                    )
            reserva = Reserva(self._id_reserva, cliente, servicio)
            self._reservas.append(reserva)
            registrar_log("INFO", f"Reserva {self._id_reserva} creada: {cliente.nombre} -> {servicio.nombre}")
            self._id_reserva += 1
            return reserva
        except (ErrorReservaInvalida, ErrorDisponibilidad) as e:
            registrar_log("ERROR", f"Error al crear reserva: {e}")
            raise

    def buscar_cliente_por_cc(self, cc):
        for c in self._clientes:
            if c.cc == str(cc):
                return c
        return None

    def buscar_servicio_por_id(self, id_servicio):
        for s in self._servicios:
            if s.id == id_servicio:
                return s
        return None

    def buscar_reserva_por_id(self, id_reserva):
        for r in self._reservas:
            if r._id == id_reserva:
                return r
        return None

    def listar_clientes(self):
        if not self._clientes:
            print("  No hay clientes registrados.")
            return
        for c in self._clientes:
            print(c.describir())

    def listar_servicios(self):
        if not self._servicios:
            print("  No hay servicios registrados.")
            return
        for s in self._servicios:
            print(s.describir())

    def listar_reservas(self):
        if not self._reservas:
            print("  No hay reservas registradas.")
            return
        for r in self._reservas:
            print(r.describir())


# ============================================================
# MENÚ INTERACTIVO
# ============================================================

def separador():
    print("\n" + "=" * 55)

def pausar():
    input("\n  Presiona Enter para continuar...")

def menu_clientes(sistema):
    while True:
        separador()
        print("  GESTIÓN DE CLIENTES")
        separador()
        print("  1. Registrar cliente")
        print("  2. Listar clientes")
        print("  0. Volver")
        opcion = input("\n  Opción: ").strip()

        if opcion == "1":
            separador()
            print("  REGISTRAR CLIENTE")
            try:
                nombre  = input("  Nombre:  ")
                cc      = input("  Cédula:  ")
                ciudad  = input("  Ciudad:  ")
                email   = input("  Email:   ")
                cliente = Cliente(nombre, cc, ciudad, email)
                sistema.registrar_cliente(cliente)
                print(f"\n  ✓ Cliente '{nombre}' registrado exitosamente.")
            except ErrorClienteInvalido as e:
                print(f"\n  ✗ Error: {e}")
            finally:
                pausar()

        elif opcion == "2":
            separador()
            print("  CLIENTES REGISTRADOS")
            sistema.listar_clientes()
            pausar()

        elif opcion == "0":
            break


def menu_servicios(sistema):
    while True:
        separador()
        print("  GESTIÓN DE SERVICIOS")
        separador()
        print("  1. Registrar Sala")
        print("  2. Registrar Equipo")
        print("  3. Registrar Asesoría")
        print("  4. Listar servicios")
        print("  0. Volver")
        opcion = input("\n  Opción: ").strip()

        if opcion == "1":
            separador()
            print("  REGISTRAR SALA")
            try:
                id_s        = int(input("  ID:              "))
                nombre      = input("  Nombre:          ")
                hora_inicio = int(input("  Hora inicio:     "))
                hora_fin    = int(input("  Hora fin:        "))
                capacidad   = int(input("  Capacidad:       "))
                precio      = float(input("  Precio por hora: "))
                sala = Sala(id_s, nombre, hora_inicio, hora_fin, capacidad, precio)
                sistema.registrar_servicio(sala)
                print(f"\n  ✓ Sala '{nombre}' registrada exitosamente.")
            except ErrorServicioInvalido as e:
                print(f"\n  ✗ Error: {e}")
            except ValueError:
                print("\n  ✗ Error: Ingresa valores numéricos donde corresponde.")
            finally:
                pausar()

        elif opcion == "2":
            separador()
            print("  REGISTRAR EQUIPO")
            try:
                id_s        = int(input("  ID:              "))
                nombre      = input("  Nombre:          ")
                hora_inicio = int(input("  Hora inicio:     "))
                hora_fin    = int(input("  Hora fin:        "))
                modelo      = input("  Modelo:          ")
                marca       = input("  Marca:           ")
                precio      = float(input("  Precio por hora: "))
                equipo = Equipo(id_s, nombre, hora_inicio, hora_fin, modelo, marca, precio)
                sistema.registrar_servicio(equipo)
                print(f"\n  ✓ Equipo '{nombre}' registrado exitosamente.")
            except ErrorServicioInvalido as e:
                print(f"\n  ✗ Error: {e}")
            except ValueError:
                print("\n  ✗ Error: Ingresa valores numéricos donde corresponde.")
            finally:
                pausar()

        elif opcion == "3":
            separador()
            print("  REGISTRAR ASESORÍA")
            try:
                id_s        = int(input("  ID:              "))
                nombre      = input("  Nombre:          ")
                hora_inicio = int(input("  Hora inicio:     "))
                hora_fin    = int(input("  Hora fin:        "))
                tema        = input("  Tema:            ")
                precio      = float(input("  Precio por hora: "))
                asesoria = Asesoria(id_s, nombre, hora_inicio, hora_fin, tema, precio)
                sistema.registrar_servicio(asesoria)
                print(f"\n  ✓ Asesoría '{nombre}' registrada exitosamente.")
            except ErrorServicioInvalido as e:
                print(f"\n  ✗ Error: {e}")
            except ValueError:
                print("\n  ✗ Error: Ingresa valores numéricos donde corresponde.")
            finally:
                pausar()

        elif opcion == "4":
            separador()
            print("  SERVICIOS REGISTRADOS")
            sistema.listar_servicios()
            pausar()

        elif opcion == "0":
            break


def menu_reservas(sistema):
    while True:
        separador()
        print("  GESTIÓN DE RESERVAS")
        separador()
        print("  1. Crear reserva")
        print("  2. Confirmar reserva")
        print("  3. Cancelar reserva")
        print("  4. Finalizar reserva")
        print("  5. Ver costo de reserva")
        print("  6. Listar reservas")
        print("  0. Volver")
        opcion = input("\n  Opción: ").strip()

        if opcion == "1":
            separador()
            print("  CREAR RESERVA")
            try:
                cc          = input("  Cédula del cliente: ")
                id_servicio = int(input("  ID del servicio:    "))
                cliente = sistema.buscar_cliente_por_cc(cc)
                if not cliente:
                    print("\n  ✗ Cliente no encontrado.")
                    pausar()
                    continue
                servicio = sistema.buscar_servicio_por_id(id_servicio)
                if not servicio:
                    print("\n  ✗ Servicio no encontrado.")
                    pausar()
                    continue
                reserva = sistema.crear_reserva(cliente, servicio)
                print(f"\n  ✓ Reserva creada (ID: {reserva._id}).")
                print(f"  Costo estimado: ${reserva.obtener_costo():,.0f}")
            except (ErrorReservaInvalida, ErrorDisponibilidad) as e:
                print(f"\n  ✗ Error: {e}")
            except ValueError:
                print("\n  ✗ Error: El ID debe ser un número.")
            finally:
                pausar()

        elif opcion == "2":
            separador()
            print("  CONFIRMAR RESERVA")
            try:
                id_r = int(input("  ID de la reserva: "))
                reserva = sistema.buscar_reserva_por_id(id_r)
                if not reserva:
                    print("\n  ✗ Reserva no encontrada.")
                else:
                    reserva.confirmar()
                    print(f"\n  ✓ Reserva {id_r} confirmada.")
            except ErrorEstadoInvalido as e:
                print(f"\n  ✗ Error: {e}")
            except ValueError:
                print("\n  ✗ Error: El ID debe ser un número.")
            finally:
                pausar()

        elif opcion == "3":
            separador()
            print("  CANCELAR RESERVA")
            try:
                id_r = int(input("  ID de la reserva: "))
                reserva = sistema.buscar_reserva_por_id(id_r)
                if not reserva:
                    print("\n  ✗ Reserva no encontrada.")
                else:
                    reserva.cancelar()
                    print(f"\n  ✓ Reserva {id_r} cancelada.")
            except ErrorEstadoInvalido as e:
                print(f"\n  ✗ Error: {e}")
            except ValueError:
                print("\n  ✗ Error: El ID debe ser un número.")
            finally:
                pausar()

        elif opcion == "4":
            separador()
            print("  FINALIZAR RESERVA")
            try:
                id_r = int(input("  ID de la reserva: "))
                reserva = sistema.buscar_reserva_por_id(id_r)
                if not reserva:
                    print("\n  ✗ Reserva no encontrada.")
                else:
                    reserva.finalizar()
                    print(f"\n  ✓ Reserva {id_r} finalizada.")
            except ErrorEstadoInvalido as e:
                print(f"\n  ✗ Error: {e}")
            except ValueError:
                print("\n  ✗ Error: El ID debe ser un número.")
            finally:
                pausar()

        elif opcion == "5":
            separador()
            print("  CALCULAR COSTO DE RESERVA")
            try:
                id_r      = int(input("  ID de la reserva:      "))
                descuento = float(input("  Descuento % (0 si no): "))
                iva       = input("  ¿Aplicar IVA? (s/n):   ").strip().lower() == "s"
                reserva   = sistema.buscar_reserva_por_id(id_r)
                if not reserva:
                    print("\n  ✗ Reserva no encontrada.")
                else:
                    costo = reserva.obtener_costo(descuento, iva)
                    print(f"\n  Costo calculado: ${costo:,.0f}")
            except ValueError:
                print("\n  ✗ Error: Ingresa valores numéricos donde corresponde.")
            finally:
                pausar()

        elif opcion == "6":
            separador()
            print("  RESERVAS REGISTRADAS")
            sistema.listar_reservas()
            pausar()

        elif opcion == "0":
            break


def demo_automatica(sistema):
    """Ejecuta 10 operaciones automáticas para demostrar el sistema."""
    separador()
    print("  DEMO AUTOMÁTICA - 10 OPERACIONES")
    separador()

    sala1 = equipo1 = asesoria1 = None

    # OP 1
    print("\n[1] Registrar cliente válido")
    try:
        c1 = Cliente("Ana Torres", "1023456789", "Bogotá", "ana@email.com")
        sistema.registrar_cliente(c1)
        print("  ✓ Ana Torres registrada.")
    except ErrorClienteInvalido as e:
        print(f"  ✗ {e}")

    # OP 2
    print("\n[2] Registrar cliente con email inválido")
    try:
        c2 = Cliente("Pedro", "987654", "Cali", "correo-invalido")
        sistema.registrar_cliente(c2)
    except ErrorClienteInvalido as e:
        print(f"  ✗ Error esperado: {e}")
    finally:
        print("  → Bloque finally ejecutado.")

    # OP 3
    print("\n[3] Registrar cliente con cédula duplicada")
    try:
        c3 = Cliente("Ana Copia", "1023456789", "Medellín", "copia@email.com")
        sistema.registrar_cliente(c3)
    except ErrorClienteInvalido as e:
        print(f"  ✗ Error esperado: {e}")

    # OP 4
    print("\n[4] Registrar segundo cliente válido")
    try:
        c4 = Cliente("Carlos Ruiz", "9876543210", "Medellín", "carlos@email.com")
        sistema.registrar_cliente(c4)
        print("  ✓ Carlos Ruiz registrado.")
    except ErrorClienteInvalido as e:
        print(f"  ✗ {e}")

    # OP 5
    print("\n[5] Registrar servicios válidos")
    try:
        sala1     = Sala(101, "Sala Innovación", 8, 12, 10, 50000)
        equipo1   = Equipo(102, "Laptop HP", 9, 11, "Pavilion 15", "HP", 30000)
        asesoria1 = Asesoria(103, "Asesoría Fintech", 14, 16, "Finanzas Digitales", 80000)
        sistema.registrar_servicio(sala1)
        sistema.registrar_servicio(equipo1)
        sistema.registrar_servicio(asesoria1)
        print("  ✓ 3 servicios registrados.")
    except ErrorServicioInvalido as e:
        print(f"  ✗ {e}")

    # OP 6
    print("\n[6] Registrar servicio con horas inválidas")
    try:
        sala_err = Sala(104, "Sala Error", 15, 10, 5, 40000)
        sistema.registrar_servicio(sala_err)
    except ErrorServicioInvalido as e:
        print(f"  ✗ Error esperado: {e}")
    finally:
        print("  → Bloque finally ejecutado.")

    # OP 7
    print("\n[7] Crear y confirmar reserva exitosa")
    try:
        c1_ref = sistema.buscar_cliente_por_cc("1023456789")
        r1 = sistema.crear_reserva(c1_ref, sala1)
        r1.confirmar()
        print(f"  ✓{r1.describir().strip()}")
    except (ErrorReservaInvalida, ErrorDisponibilidad, ErrorEstadoInvalido) as e:
        print(f"  ✗ {e}")

    # OP 8
    print("\n[8] Intentar reservar servicio ya ocupado")
    try:
        c4_ref = sistema.buscar_cliente_por_cc("9876543210")
        sistema.crear_reserva(c4_ref, sala1)
    except ErrorDisponibilidad as e:
        print(f"  ✗ Error esperado: {e}")

    # OP 9
    print("\n[9] Calcular costos con descuento e IVA")
    try:
        print(f"  Base:            ${asesoria1.calcular_costo():,.0f}")
        print(f"  10% descuento:   ${asesoria1.calcular_costo(descuento=10):,.0f}")
        print(f"  Con IVA:         ${asesoria1.calcular_costo(aplicar_iva=True):,.0f}")
        print(f"  Desc. + IVA:     ${asesoria1.calcular_costo(descuento=10, aplicar_iva=True):,.0f}")
    except Exception as e:
        print(f"  ✗ {e}")

    # OP 10
    print("\n[10] Cancelar reserva y transición inválida")
    try:
        c4_ref = sistema.buscar_cliente_por_cc("9876543210")
        r3 = sistema.crear_reserva(c4_ref, equipo1)
        r3.confirmar()
        r3.cancelar()
        r3.cancelar()  # debe fallar
    except ErrorEstadoInvalido as e:
        print(f"  ✗ Error esperado: {e}")

    print("\n  Demo finalizada. Revisa el archivo de logs.")
    pausar()


def main():
    sistema = SistemaReservas()

    while True:
        separador()
        print("  SISTEMA DE GESTIÓN - SOFTWARE FJ")
        separador()
        print("  1. Gestión de Clientes")
        print("  2. Gestión de Servicios")
        print("  3. Gestión de Reservas")
        print("  4. Ver resumen general")
        print("  5. Ejecutar demo automática")
        print("  0. Salir")
        separador()
        opcion = input("  Opción: ").strip()

        if opcion == "1":
            menu_clientes(sistema)
        elif opcion == "2":
            menu_servicios(sistema)
        elif opcion == "3":
            menu_reservas(sistema)
        elif opcion == "4":
            separador()
            print("  RESUMEN GENERAL")
            separador()
            print("\n  Clientes:")
            sistema.listar_clientes()
            print("\n  Servicios:")
            sistema.listar_servicios()
            print("\n  Reservas:")
            sistema.listar_reservas()
            print(f"\n  Logs en: {os.path.abspath(LOG_FILE)}")
            pausar()
        elif opcion == "5":
            demo_automatica(sistema)
        elif opcion == "0":
            registrar_log("INFO", "Sistema cerrado por el usuario.")
            print("\n  ¡Hasta luego!\n")
            break
        else:
            print("\n  Opción inválida.")


if __name__ == "__main__":
    main()
