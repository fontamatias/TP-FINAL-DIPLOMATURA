from __future__ import annotations


class Eventos:
    # Login / Auth
    LOGIN_SUBMIT = "login_submit"
    REGISTRO_REQUESTED = "registro_requested"
    CAMBIAR_CONTRASENA_REQUESTED = "cambiar_contrasena_requested"
    ELIMINAR_USUARIO_REQUESTED = "eliminar_usuario_requested"

    REGISTRO_SUBMIT = "registro_submit"
    CAMBIAR_CONTRASENA_SUBMIT = "cambiar_contrasena_submit"
    ELIMINAR_USUARIO_SUBMIT = "eliminar_usuario_submit"

    # Producción
    PRODUCCION_CIERRE_DIA = "produccion_cierre_dia"

    # Inspección Final
    INSPECCION_MARCAR_OK = "inspeccion_marcar_ok"
    INSPECCION_MARCAR_NO_OK = "inspeccion_marcar_no_ok"
    INSPECCION_CIERRE_DIA = "inspeccion_cierre_dia"

    # Mecánica
    MECANICA_DAR_ALTA = "mecanica_dar_alta"
    MECANICA_CIERRE_DIA = "mecanica_cierre_dia"

    # Distribución
    DISTRIBUCION_CREAR_PEDIDO = "distribucion_crear_pedido"
    DISTRIBUCION_AGREGAR_A_PEDIDO = "distribucion_agregar_a_pedido"
    DISTRIBUCION_FINALIZAR_PEDIDO = "distribucion_finalizar_pedido"
    DISTRIBUCION_CIERRE_DIA = "distribucion_cierre_dia"


class Sectores:
    LINEA_PRODUCCION = "Linea de produccion"
    INSPECCION_FINAL = "Inspeccion final"
    MECANICA = "Mecanica"
    DISTRIBUCION = "Distribucion"