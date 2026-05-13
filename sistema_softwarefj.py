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
    print(linea.strip())


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
        """Valida los datos de la entidad."""
        pass

    @abstractmethod
    def describir(self):
        """Retorna una descripción de la entidad."""
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
        # Usamos setters para validar desde el inicio
        self.nombre = nombre
        self.cc = cc
        self.ciudad = ciudad
        self.email = email

    # --- Getters y Setters ---

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
        return f"Cliente: {self._nombre} | CC: {self._cc} | Ciudad: {self._ciudad} | Email: {self._email}"


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
        """Calcula el costo del servicio con parámetros opcionales."""
        pass

    def validar(self):
        return self._hora_inicio < self._hora_fin and self._precio_por_hora > 0

    def describir(self):
        return (f"Servicio [{self._id}]: {self._nombre} | "
                f"Horario: {self._hora_inicio}:00 - {self._hora_fin}:00 | "
                f"Precio/hora: ${self._precio_por_hora:,.0f}")


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
        """Calcula costo de la sala. Acepta descuento (%) e IVA opcional."""
        horas = self._hora_fin - self._hora_inicio
        costo = horas * self._precio_por_hora
        costo -= costo * (descuento / 100)
        if aplicar_iva:
            costo *= 1.19
        return round(costo, 2)

    def describir(self):
        base = super().describir()
        return f"{base} | Capacidad: {self._capacidad} personas | Tipo: Sala"


class Equipo(Servicio):
    """Servicio de alquiler de equipos tecnológicos."""

    def __init__(self, id_servicio, nombre, hora_inicio, hora_fin, modelo, marca, precio_por_hora):
        super().__init__(id_servicio, nombre, hora_inicio, hora_fin, precio_por_hora)
        if not modelo or not marca:
            raise ErrorServicioInvalido("El modelo y la marca son obligatorios.")
        self._modelo = modelo
        self._marca = marca

    def calcular_costo(self, descuento=0, aplicar_iva=False):
        """Calcula costo del equipo. Acepta descuento (%) e IVA opcional."""
        horas = self._hora_fin - self._hora_inicio
        costo = horas * self._precio_por_hora
        costo -= costo * (descuento / 100)
        if aplicar_iva:
            costo *= 1.19
        return round(costo, 2)

    def describir(self):
        base = super().describir()
        return f"{base} | Equipo: {self._marca} {self._modelo} | Tipo: Equipo"


class Asesoria(Servicio):
    """Servicio de asesoría especializada."""

    def __init__(self, id_servicio, nombre, hora_inicio, hora_fin, tema, precio_por_hora):
        super().__init__(id_servicio, nombre, hora_inicio, hora_fin, precio_por_hora)
        if not tema:
            raise ErrorServicioInvalido("El tema de la asesoría es obligatorio.")
        self._tema = tema

    def calcular_costo(self, descuento=0, aplicar_iva=False):
        """Calcula costo de asesoría. Las asesorías tienen recargo del 10% por especialización."""
        horas = self._hora_fin - self._hora_inicio
        costo = horas * self._precio_por_hora * 1.10  # recargo especialización
        costo -= costo * (descuento / 100)
        if aplicar_iva:
            costo *= 1.19
        return round(costo, 2)

    def describir(self):
        base = super().describir()
        return f"{base} | Tema: {self._tema} | Tipo: Asesoría"


# ============================================================
# CLASE RESERVA
# ============================================================

class Reserva:
    """Integra cliente, servicio y estado. Maneja el ciclo de vida de una reserva."""

    ESTADOS_VALIDOS = ["pendiente", "confirmada", "cancelada", "finalizada"]
    TRANSICIONES = {
        "pendiente":   ["confirmada", "cancelada"],
        "confirmada":  ["finalizada", "cancelada"],
        "cancelada":   [],
        "finalizada":  []
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
        """Controla las transiciones de estado válidas."""
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
        """Obtiene el costo del servicio asociado con parámetros opcionales."""
        return self._servicio.calcular_costo(descuento, aplicar_iva)

    def describir(self):
        return (f"Reserva [{self._id}] | Estado: {self._estado} | "
                f"Cliente: {self._cliente.nombre} | "
                f"Servicio: {self._servicio.nombre} | "
                f"Costo: ${self.obtener_costo():,.0f} | "
                f"Creada: {self._fecha_creacion}")


# ============================================================
# SISTEMA DE GESTIÓN
# ============================================================

class SistemaReservas:
    """Gestiona clientes, servicios y reservas en memoria."""

    def __init__(self):
        self._clientes = []
        self._servicios = []
        self._reservas = []
        registrar_log("INFO", "Sistema Software FJ iniciado.")

    def registrar_cliente(self, cliente):
        try:
            # Verificar cédula duplicada
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

    def crear_reserva(self, id_reserva, cliente, servicio):
        try:
            # Verificar conflicto de horarios
            for r in self._reservas:
                if (r._servicio.id == servicio.id and
                        r._estado not in ["cancelada", "finalizada"]):
                    raise ErrorDisponibilidad(
                        f"El servicio '{servicio.nombre}' ya tiene una reserva activa."
                    )
            reserva = Reserva(id_reserva, cliente, servicio)
            self._reservas.append(reserva)
            registrar_log("INFO", f"Reserva {id_reserva} creada: {cliente.nombre} -> {servicio.nombre}")
            return reserva
        except (ErrorReservaInvalida, ErrorDisponibilidad) as e:
            registrar_log("ERROR", f"Error al crear reserva: {e}")
            raise

    def listar_clientes(self):
        if not self._clientes:
            print("No hay clientes registrados.")
            return
        for c in self._clientes:
            print(c.describir())

    def listar_servicios(self):
        if not self._servicios:
            print("No hay servicios registrados.")
            return
        for s in self._servicios:
            print(s.describir())

    def listar_reservas(self):
        if not self._reservas:
            print("No hay reservas registradas.")
            return
        for r in self._reservas:
            print(r.describir())


# ============================================================
# MAIN - 10 OPERACIONES COMPLETAS
# ============================================================

def main():
    print("=" * 60)
    print("   SISTEMA DE GESTIÓN SOFTWARE FJ")
    print("=" * 60)

    sistema = SistemaReservas()

    # ----------------------------------------------------------
    # OPERACIÓN 1: Registrar cliente válido
    # ----------------------------------------------------------
    print("\n--- OP 1: Registrar cliente válido ---")
    try:
        c1 = Cliente("Ana Torres", "1023456789", "Bogotá", "ana@email.com")
        sistema.registrar_cliente(c1)
    except ErrorClienteInvalido as e:
        registrar_log("ERROR", str(e))

    # ----------------------------------------------------------
    # OPERACIÓN 2: Registrar cliente con datos inválidos
    # ----------------------------------------------------------
    print("\n--- OP 2: Registrar cliente con email inválido ---")
    try:
        c_invalido = Cliente("Pedro", "987654", "Cali", "correo-invalido")
        sistema.registrar_cliente(c_invalido)
    except ErrorClienteInvalido as e:
        registrar_log("ERROR", f"Cliente inválido capturado: {e}")
    finally:
        registrar_log("INFO", "Operación 2 finalizada.")

    # ----------------------------------------------------------
    # OPERACIÓN 3: Registrar cliente con cédula duplicada
    # ----------------------------------------------------------
    print("\n--- OP 3: Registrar cliente duplicado ---")
    try:
        c_dup = Cliente("Ana Duplicada", "1023456789", "Medellín", "otra@email.com")
        sistema.registrar_cliente(c_dup)
    except ErrorClienteInvalido as e:
        registrar_log("ERROR", f"Duplicado capturado: {e}")

    # ----------------------------------------------------------
    # OPERACIÓN 4: Registrar segundo cliente válido
    # ----------------------------------------------------------
    print("\n--- OP 4: Registrar segundo cliente válido ---")
    try:
        c2 = Cliente("Carlos Ruiz", "9876543210", "Medellín", "carlos@email.com")
        sistema.registrar_cliente(c2)
    except ErrorClienteInvalido as e:
        registrar_log("ERROR", str(e))

    # ----------------------------------------------------------
    # OPERACIÓN 5: Crear servicios válidos
    # ----------------------------------------------------------
    print("\n--- OP 5: Crear servicios válidos ---")
    try:
        sala1 = Sala(1, "Sala Innovación", 8, 12, 10, 50000)
        equipo1 = Equipo(2, "Laptop HP", 9, 11, "Pavilion 15", "HP", 30000)
        asesoria1 = Asesoria(3, "Asesoría Fintech", 14, 16, "Finanzas Digitales", 80000)
        sistema.registrar_servicio(sala1)
        sistema.registrar_servicio(equipo1)
        sistema.registrar_servicio(asesoria1)
    except ErrorServicioInvalido as e:
        registrar_log("ERROR", str(e))

    # ----------------------------------------------------------
    # OPERACIÓN 6: Crear servicio con horas inválidas
    # ----------------------------------------------------------
    print("\n--- OP 6: Crear servicio con horas inválidas ---")
    try:
        sala_invalida = Sala(4, "Sala Error", 15, 10, 5, 40000)
        sistema.registrar_servicio(sala_invalida)
    except ErrorServicioInvalido as e:
        registrar_log("ERROR", f"Servicio inválido capturado: {e}")
    finally:
        registrar_log("INFO", "Operación 6 finalizada.")

    # ----------------------------------------------------------
    # OPERACIÓN 7: Crear reserva exitosa
    # ----------------------------------------------------------
    print("\n--- OP 7: Crear y confirmar reserva exitosa ---")
    try:
        r1 = sistema.crear_reserva(1, c1, sala1)
        r1.confirmar()
        print(r1.describir())
    except (ErrorReservaInvalida, ErrorDisponibilidad, ErrorEstadoInvalido) as e:
        registrar_log("ERROR", str(e))

    # ----------------------------------------------------------
    # OPERACIÓN 8: Intentar reservar servicio no disponible
    # ----------------------------------------------------------
    print("\n--- OP 8: Reservar servicio ya ocupado ---")
    try:
        r2 = sistema.crear_reserva(2, c2, sala1)
    except ErrorDisponibilidad as e:
        registrar_log("ERROR", f"Conflicto de disponibilidad: {e}")

    # ----------------------------------------------------------
    # OPERACIÓN 9: Calcular costos con descuento e IVA
    # ----------------------------------------------------------
    print("\n--- OP 9: Calcular costos con variantes ---")
    try:
        costo_base = asesoria1.calcular_costo()
        costo_descuento = asesoria1.calcular_costo(descuento=10)
        costo_iva = asesoria1.calcular_costo(aplicar_iva=True)
        costo_completo = asesoria1.calcular_costo(descuento=10, aplicar_iva=True)
        print(f"Costo base:              ${costo_base:,.0f}")
        print(f"Con 10% descuento:       ${costo_descuento:,.0f}")
        print(f"Con IVA:                 ${costo_iva:,.0f}")
        print(f"Con descuento e IVA:     ${costo_completo:,.0f}")
        registrar_log("INFO", f"Cálculos de costo realizados para {asesoria1.nombre}")
    except Exception as e:
        registrar_log("ERROR", f"Error en cálculo de costos: {e}")

    # ----------------------------------------------------------
    # OPERACIÓN 10: Cancelar reserva e intentar transición inválida
    # ----------------------------------------------------------
    print("\n--- OP 10: Cancelar reserva y transición inválida ---")
    try:
        r3 = sistema.crear_reserva(3, c2, equipo1)
        r3.confirmar()
        r3.cancelar()
        # Intentar cancelar de nuevo (transición inválida)
        r3.cancelar()
    except ErrorEstadoInvalido as e:
        registrar_log("ERROR", f"Transición inválida capturada: {e}")
    except (ErrorReservaInvalida, ErrorDisponibilidad) as e:
        registrar_log("ERROR", str(e))

    # ----------------------------------------------------------
    # RESUMEN FINAL
    # ----------------------------------------------------------
    print("\n" + "=" * 60)
    print("   RESUMEN DEL SISTEMA")
    print("=" * 60)
    print("\n--- Clientes registrados ---")
    sistema.listar_clientes()
    print("\n--- Servicios registrados ---")
    sistema.listar_servicios()
    print("\n--- Reservas registradas ---")
    sistema.listar_reservas()
    print(f"\nLogs guardados en: {os.path.abspath(LOG_FILE)}")


if __name__ == "__main__":
    main()
