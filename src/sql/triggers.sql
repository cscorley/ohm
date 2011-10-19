CREATE OR REPLACE FUNCTION propagate_data(newrow change) RETURNS void
LANGUAGE plpgsql 
AS $$
BEGIN
        INSERT INTO r_change(additions, deletions, project, revision, owner, block)
        VALUES (newrow.additions, newrow.deletions, 
        newrow.project, newrow.revision, newrow.owner, newrow.block);
END;
$$;

CREATE OR REPLACE FUNCTION propagate_data_trg() RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
        PERFORM propagate_data(NEW);
        RETURN NEW;
END;
$$;

CREATE TRIGGER propagate_data AFTER INSERT ON change FOR EACH ROW
    EXECUTE PROCEDURE propagate_data_trg();


CREATE OR REPLACE FUNCTION propagate_rename(newrow rename) RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
        UPDATE r_change SET block = newrow.target WHERE
        block = newrow.original AND newrow.ratio >= 0.6; 
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
    IF block_row.type = 'file'
    THEN
        RETURN '';
    ELSIF block_row.type = 'package'
    THEN
        RETURN block_row.block || '.';
    ELSIF block_row.block is NULL
    THEN
        RETURN block_row.name;
    ELSE
        RETURN trim(both '.' from full_name(block_row.block) || '.' || block_row.name);
    END IF;
END;
$$;
