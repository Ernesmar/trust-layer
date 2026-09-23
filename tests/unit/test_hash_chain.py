import dataclasses

import pytest

from src.domain.hash_chain import CadenaAlteradaError, verificar_cadena
from src.domain.servicios import RegistrarAccionAuditable, VerificarIdentidadAgente
from src.infrastructure.adaptadores_memoria import (
    FirmadorMemoria,
    RepositorioAgentesMemoria,
    RepositorioRegistrosMemoria,
)


def _construir_cadena_de_tres_registros():
    repo_agentes = RepositorioAgentesMemoria()
    repo_registros = RepositorioRegistrosMemoria()
    firmador = FirmadorMemoria()
    verificar_identidad = VerificarIdentidadAgente(repo_agentes)
    registrar_accion = RegistrarAccionAuditable(repo_agentes, repo_registros, firmador)

    agente = verificar_identidad.ejecutar("Acme SRL", "procesar pagos", [])
    for accion, objetivo in [("leer", "api/saldo"), ("escribir", "api/pago/1"), ("leer", "api/confirmacion")]:
        registrar_accion.ejecutar(agente.agente_id, accion, objetivo)

    return agente.agente_id, repo_registros, firmador


def test_cadena_intacta_verifica_correctamente():
    agente_id, repo_registros, firmador = _construir_cadena_de_tres_registros()
    historial = repo_registros.historial_de(agente_id)

    verificar_cadena(historial, firmador.clave_secreta())  # no debe lanzar


def test_alterar_una_accion_es_detectado():
    """Este es el test central: demuestra que el sistema SÍ detecta manipulación,
    la propiedad de la que depende toda la promesa de 'notario verificable'."""
    agente_id, repo_registros, firmador = _construir_cadena_de_tres_registros()
    historial = repo_registros.historial_de(agente_id)

    # Se simula un atacante (o un bug) reescribiendo el contenido de un registro
    # sin volver a firmar ni recalcular el hash — exactamente lo que pasaría si
    # alguien intentara un UPDATE directo saltándose la aplicación.
    historial_manipulado = list(historial)
    historial_manipulado[1] = dataclasses.replace(historial_manipulado[1], objetivo="api/pago/1-MODIFICADO")

    with pytest.raises(CadenaAlteradaError):
        verificar_cadena(historial_manipulado, firmador.clave_secreta())


def test_reordenar_registros_es_detectado():
    agente_id, repo_registros, firmador = _construir_cadena_de_tres_registros()
    historial = repo_registros.historial_de(agente_id)

    historial_reordenado = [historial[1], historial[0], historial[2]]

    with pytest.raises(CadenaAlteradaError):
        verificar_cadena(historial_reordenado, firmador.clave_secreta())
