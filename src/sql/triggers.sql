CREATE OR REPLACE FUNCTION propagate_rename(newrow rename) RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    IF newrow.ratio >= 0.6
    THEN
        UPDATE change SET block = newrow.target WHERE
        block = newrow.original; 
        UPDATE block SET block = newrow.target WHERE
        block = newrow.original;
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION propagate_rename_trg() RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
        PERFORM propagate_rename(NEW);
        RETURN NEW;
END;
$$;

CREATE TRIGGER propagate_rename AFTER INSERT ON rename FOR EACH ROW
    EXECUTE PROCEDURE propagate_rename_trg();


create or replace function full_name(next_id INT) RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    block_row block%ROWTYPE;
BEGIN
    SELECT * into block_row from block where id=next_id;
    IF block_row.block is NULL
    THEN
        RETURN block_row.name;
    ELSE
        IF block_row.type = 'file'
        THEN
            RETURN full_name(block_row.block);
        ELSIF block_row.type = 'package'
        THEN
            RETURN block_row.block || '.';
        ELSE
            RETURN trim(both '.' from full_name(block_row.block) || '.' || block_row.name);
        END IF;
    END IF;
END;
$$;

