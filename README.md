# Registro de Confianza para Agentes

Servidor MCP que actúa como **notario verificable** de agentes de IA:
registra su identidad y cada acción relevante en un log inmutable y
criptográficamente verificable — sin certificar ni juzgar si esas
acciones cumplen ninguna normativa.

Ver la especificación completa (arquitectura, modelo de datos, plan de
validación) en el documento de diseño del proyecto.

## Estructura

```
src/
  domain/            # lógica de negocio pura, sin dependencias externas
    models.py        # AgenteIA, RegistroAuditable
    hash_chain.py     # integridad criptográfica: hash-chain + firma
    ports.py          # interfaces que la infraestructura implementa
    servicios.py       # casos de uso: VerificarIdentidadAgente, RegistrarAccionAuditable
  infrastructure/
    adaptadores_memoria.py   # implementación en memoria (tests, Fase 1)
    postgres_schema.sql      # esquema para cuando se conecte Postgres real
  mcp_server/
    servidor.py        # expone los casos de uso como herramientas MCP
tests/
  unit/          # dominio puro, sin DB
  integration/   # (pendiente: contra Postgres real)
  contract/      # garantiza el schema que ve cualquier cliente MCP
docs/adr/        # decisiones de arquitectura, con su razonamiento
```

## Uso

```bash
pip install -e ".[dev]"
pytest                          # corre toda la suite
python -m src.mcp_server.servidor   # levanta el servidor MCP
```

## Estado

Fase 1, primera versión: `verificar_identidad_agente` +
`registrar_accion_auditable` + `verificar_historial`, con adaptadores en
memoria. Sin pagos, sin certificación normativa — ver ADR 0001 y el
documento de diseño para el porqué de cada decisión.
