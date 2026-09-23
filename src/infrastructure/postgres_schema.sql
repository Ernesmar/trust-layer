-- Append-only por diseño: no hay UPDATE ni DELETE permitidos sobre registros_auditables.
-- El trigger abajo lo hace cumplir a nivel de base de datos, no solo de código de aplicación.

CREATE TABLE IF NOT EXISTS agentes (
    agente_id UUID PRIMARY KEY,
    empresa_propietaria TEXT NOT NULL,
    proposito_declarado TEXT NOT NULL,
    permisos TEXT[] NOT NULL DEFAULT '{}',
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS registros_auditables (
    registro_id UUID PRIMARY KEY,
    agente_id UUID NOT NULL REFERENCES agentes(agente_id),
    accion TEXT NOT NULL,
    objetivo TEXT NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL,
    hash_anterior CHAR(64) NOT NULL,
    hash_actual CHAR(64) NOT NULL,
    firma TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_registros_agente_ts
    ON registros_auditables (agente_id, "timestamp");

-- Hace cumplir la inmutabilidad a nivel de motor de base de datos:
-- ni un bug de aplicación ni un acceso directo a la DB pueden alterar el log.
CREATE OR REPLACE FUNCTION prohibir_update_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'registros_auditables es append-only: % no permitido', TG_OP;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_no_update ON registros_auditables;
CREATE TRIGGER trg_no_update
    BEFORE UPDATE OR DELETE ON registros_auditables
    FOR EACH ROW EXECUTE FUNCTION prohibir_update_delete();
