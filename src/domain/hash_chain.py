"""Integridad criptográfica: hash-chain + firma.

GENESIS_HASH es el ancla de la cadena para el primer registro de cada agente.
Cualquiera puede recalcular la cadena completa y detectar alteraciones
retroactivas sin confiar en el operador del sistema — esa es la propiedad
que hace esto un "notario verificable" y no una base de datos común.
"""
from __future__ import annotations

import hashlib
import hmac

GENESIS_HASH = "0" * 64


def calcular_hash(payload_canonico: str, hash_anterior: str) -> str:
    contenido = f"{hash_anterior}:{payload_canonico}".encode()
    return hashlib.sha256(contenido).hexdigest()


def firmar(payload_canonico: str, hash_actual: str, clave_secreta: bytes) -> str:
    mensaje = f"{hash_actual}:{payload_canonico}".encode()
    return hmac.new(clave_secreta, mensaje, hashlib.sha256).hexdigest()


def verificar_firma(payload_canonico: str, hash_actual: str, firma: str, clave_secreta: bytes) -> bool:
    esperada = firmar(payload_canonico, hash_actual, clave_secreta)
    return hmac.compare_digest(esperada, firma)


class CadenaAlteradaError(Exception):
    """Se lanza cuando la verificación de una cadena de registros falla."""


def verificar_cadena(registros_en_orden: list, clave_secreta: bytes) -> None:
    """Recalcula hash y firma de cada registro en orden y compara.

    registros_en_orden: lista de RegistroAuditable, más antiguo primero.
    Lanza CadenaAlteradaError con el detalle del primer registro corrupto.
    """
    hash_esperado = GENESIS_HASH
    for registro in registros_en_orden:
        if registro.hash_anterior != hash_esperado:
            raise CadenaAlteradaError(
                f"registro {registro.registro_id}: hash_anterior no coincide con la cadena"
            )
        hash_recalculado = calcular_hash(registro.payload_canonico, registro.hash_anterior)
        if hash_recalculado != registro.hash_actual:
            raise CadenaAlteradaError(
                f"registro {registro.registro_id}: el contenido fue alterado (hash no coincide)"
            )
        firma_valida = verificar_firma(
            registro.payload_canonico, registro.hash_actual, registro.firma, clave_secreta
        )
        if not firma_valida:
            raise CadenaAlteradaError(
                f"registro {registro.registro_id}: firma inválida"
            )
        hash_esperado = registro.hash_actual
