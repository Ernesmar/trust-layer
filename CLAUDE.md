# CLAUDE.md — Registro de Confianza para Agentes

Este archivo es contexto de arranque para Claude Code. Léelo completo antes
de tocar código: define la filosofía del proyecto, lo que ya está hecho y
verificado, y las reglas que no se negocian.

## Qué es esto

Servidor MCP que actúa como **notario verificable** de agentes de IA:
registra identidad y acciones en un log inmutable y criptográficamente
verificable. NO certifica ni juzga si un agente cumple ninguna normativa —
solo registra hechos objetivos, de forma pública y auditable por cualquiera.

Ver `docs/adr/0001-hash-chain-en-vez-de-blockchain.md` para el razonamiento
de la decisión técnica central.

## Regla de oro (no romper nunca)

En todo texto de cara al usuario (docstrings de herramientas MCP, mensajes
de error, README, comunicación pública): la promesa es *"registramos de
forma pública y verificable lo que los agentes hacen"*, nunca *"certificamos
/ verificamos que un agente es confiable"*. La autoridad se gana con
histórico y transparencia, no se autodeclara. Si una tarea pide agregar
lenguaje de "certificación" o "compliance garantizado", frénala y pregunta.

## Estado actual (verificado, no asumido)

- Dominio completo: `src/domain/` (modelos, hash-chain, puertos, dos casos
  de uso) — 100% aislado de infraestructura, sin dependencias externas.
- Adaptadores en memoria: `src/infrastructure/adaptadores_memoria.py` —
  usados por el servidor MCP hoy.
- Esquema Postgres: `src/infrastructure/postgres_schema.sql` — escrito,
  **NO conectado todavía**. No existe `RepositorioAgentesPostgres` ni
  `RepositorioRegistrosPostgres`.
- Servidor MCP: `src/mcp_server/servidor.py` — tres herramientas
  (`verificar_identidad_agente`, `registrar_accion_auditable`,
  `verificar_historial`), corriendo sobre adaptadores en memoria.
- Tests: 10 pasan (`tests/unit/`, `tests/contract/`), 96% cobertura.
  `tests/integration/` existe pero está **vacía** — depende del adaptador
  Postgres que aún no existe.
- CI: `.github/workflows/ci.yml` define 4 gates (lint, tests, escaneo de
  dependencias, build). No verificado corriendo en GitHub Actions real
  todavía — solo localmente.
- SDK MCP: usa `mcp[cli]>=2.0.0` (API `MCPServer`, no `FastMCP` — eso es
  la v1, no lo reintroduzcas).

## Reglas de ingeniería que no se negocian

1. **Arquitectura hexagonal estricta.** Nada en `src/domain/` importa de
   `src/infrastructure/` ni de `src/mcp_server/`. Si una tarea te empuja a
   romper esto, para y replantea el puerto en `src/domain/ports.py`.
2. **Append-only real.** Ningún código nuevo debe hacer UPDATE/DELETE
   sobre registros auditables — ni siquiera para "corregir" datos de
   prueba. El trigger de Postgres ya lo bloquea a nivel de motor; el
   código de aplicación debe respetarlo igual.
3. **Nada llega a `main` sin pasar los 4 gates del pipeline.** Antes de
   dar por terminada cualquier tarea: `ruff check .` limpio y
   `pytest --cov=src --cov-fail-under=85` en verde.
4. **Todo cambio de diseño relevante = un ADR nuevo** en `docs/adr/`,
   siguiendo el formato del 0001.
5. **Nunca inventar autoridad.** Ver "Regla de oro" arriba.

## Cómo correr esto

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/ruff check .
.venv/bin/pytest tests/unit tests/contract --cov=src --cov-report=term-missing
python -m src.mcp_server.servidor   # levanta el servidor
```

## Próximas tareas, en orden

1. **Publicación mínima (prioridad actual).** Empujar este repo a GitHub
   público, confirmar que `ci.yml` corre en verde en Actions real, listar
   en MCP Registry y MCPBundles. Ningún cambio de código requerido para
   esto — es un paso de distribución, no de ingeniería.
2. **Validar con la comunidad antes de seguir construyendo.** No avanzar
   a la tarea 3 hasta tener señal real de adopción (ver plan de
   validación en la especificación original del proyecto — comunidades
   de MCP Registry, Indie Hackers, marketplaces de agentes como Kenwea
   o indie.money).
3. **Adaptador Postgres real**, solo si hay señal de la tarea 2:
   - Implementar `RepositorioAgentesPostgres` y
     `RepositorioRegistrosPostgres` cumpliendo los puertos existentes en
     `src/domain/ports.py`, sin tocar el dominio.
   - Llenar `tests/integration/` corriendo contra un contenedor Postgres
     real (docker-compose de test), reusando los mismos casos de uso que
     ya pasan en memoria — deben comportarse igual.
   - Añadir el job de integración al pipeline de CI (hoy está comentado
     ahí porque requiere un servicio de base de datos).
4. **Fase 2 — pagos** (no empezar antes de validar Fase 1): módulo de
   pagos cripto agente-a-agente sobre x402/AP2, que dispare automáticamente
   un registro de auditoría por cada pago. Diseño pendiente de detallar.

## Qué NO hacer sin preguntar primero

- No agregar blockchain real / ledger distribuido (ver ADR 0001).
- No agregar lenguaje de "certificación" o "compliance garantizado".
- No saltarse `tests/integration/` vacío como si Postgres ya estuviera
  conectado — sigue pendiente hasta que la tarea 3 se haga explícitamente.
- No monetizar ni agregar cobros antes de completar la validación de la
  tarea 2.
