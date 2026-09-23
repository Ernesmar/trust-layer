# ADR 0001: Hash-chain simple en vez de blockchain real

## Estado
Aceptado

## Contexto
El sistema necesita que cualquier tercero pueda verificar que un registro
de auditoría no fue alterado retroactivamente, sin tener que confiar
ciegamente en el operador de la base de datos.

## Decisión
Se implementa un hash-chain simple (cada registro incluye el hash del
anterior + firma HMAC) en vez de un ledger distribuido / blockchain real.

## Razones
- Un blockchain real resuelve un problema que no tenemos todavía: consenso
  entre múltiples partes que no confían entre sí. En Fase 1 hay un solo
  operador — el problema es integridad verificable, no descentralización.
- Complejidad operativa mucho menor: sin nodos, sin gas, sin minería.
- La propiedad de "tamper-evident" (se detecta la alteración) se cumple
  igual con hash-chain + firma que con blockchain, para este caso de uso.

## Consecuencias
- Si en el futuro se requiere descentralización real (ej. que ni el propio
  operador pueda alterar el historial sin ser detectado por terceros
  independientes), esto requerirá revisar esta decisión.
- El esquema de Postgres (`postgres_schema.sql`) refuerza esto con un
  trigger que prohíbe UPDATE/DELETE a nivel de motor de base de datos.
