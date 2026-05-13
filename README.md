# Sistema Integral de Gestión de Clientes, Servicios y Reservas
**Empresa:** Software FJ  
**Curso:** Programación - Código 213023  
**Universidad:** Universidad Nacional Abierta y a Distancia (UNAD)  

---

## Descripción
Sistema orientado a objetos desarrollado en Python que gestiona clientes, servicios y reservas para la empresa Software FJ, sin uso de bases de datos. Toda la información se maneja en memoria mediante objetos y listas.

---

## Estructura del proyecto
```
├── sistema_softwarefj.py   # Código fuente principal
├── softwarefj_logs.txt     # Generado automáticamente al ejecutar
└── README.md
```

---

## Arquitectura

### Clases principales
| Clase | Tipo | Descripción |
|---|---|---|
| `EntidadBase` | Abstracta | Clase base del sistema |
| `Cliente` | Concreta | Gestiona datos del cliente con validaciones |
| `Servicio` | Abstracta | Base para los servicios especializados |
| `Sala` | Concreta | Servicio de reserva de salas |
| `Equipo` | Concreta | Servicio de alquiler de equipos |
| `Asesoria` | Concreta | Servicio de asesorías especializadas |
| `Reserva` | Concreta | Integra cliente y servicio con estados |
| `SistemaReservas` | Concreta | Gestiona listas en memoria |

### Excepciones personalizadas
- `ErrorSistema` → base de todas las excepciones
- `ErrorClienteInvalido` → datos de cliente inválidos
- `ErrorServicioInvalido` → datos de servicio inválidos
- `ErrorReservaInvalida` → reserva no puede realizarse
- `ErrorDisponibilidad` → conflicto de horarios
- `ErrorEstadoInvalido` → transición de estado no permitida

---

## Requisitos
- Python 3.8 o superior
- No requiere librerías externas

---

## Ejecución
```bash
python sistema_softwarefj.py
```

Al ejecutar se generará automáticamente el archivo `softwarefj_logs.txt` con el registro de todos los eventos y errores.

---

## Operaciones demostradas
1. Registro de cliente válido
2. Registro de cliente con email inválido
3. Registro de cliente con cédula duplicada
4. Registro de segundo cliente válido
5. Creación de servicios válidos (Sala, Equipo, Asesoría)
6. Creación de servicio con horas inválidas
7. Creación y confirmación de reserva exitosa
8. Intento de reserva sobre servicio no disponible
9. Cálculo de costos con descuento e IVA
10. Cancelación de reserva y transición de estado inválida

---

## Conceptos POO aplicados
- **Abstracción** → `EntidadBase`, `Servicio`
- **Herencia** → `Sala`, `Equipo`, `Asesoria` heredan de `Servicio`
- **Polimorfismo** → `calcular_costo()` implementado diferente en cada servicio
- **Encapsulación** → atributos privados con getters y setters en `Cliente`
- **Manejo de excepciones** → `try/except`, `try/except/finally`, excepciones personalizadas y encadenadas
