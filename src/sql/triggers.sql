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



--

CREATE OR REPLACE FUNCTION propagate_data(change) RETURNS void
LANGUAGE SQL
AS $$
        INSERT INTO r_change VALUES ($1.additions, $1.deletions, 
        $1.project, $1.revision, $1.owner, $1.block);
$$;

CREATE TRIGGER propagate_data_trg AFTER INSERT ON change FOR EACH ROW
    EXECUTE PROCEDURE propagate_data(ROW);


CREATE OR REPLACE FUNCTION propagate_rename(rename) RETURNS void
LANGUAGE SQL
AS $$
        UPDATE r_change SET block = $1.target WHERE
        block = $1.original AND $1.ratio >= 0.6; 
$$;

CREATE TRIGGER propagate_rename_trg AFTER INSERT ON rename FOR EACH ROW
    EXECUTE PROCEDURE propagate_rename(ROW);
