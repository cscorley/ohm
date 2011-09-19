CREATE OR REPLACE VIEW change_data_all AS SELECT
                project.id project_id,
                project.name project_name,
                revision.id revision_id,
                revision.number revision_number,
                owner.id owner_id,
                owner.name owner_name,
                block.id block_id,
                block.full_name block_full_name,
                block.name block_name,
                block.type block_type,
                change.additions,
                change.deletions
            FROM
                change
            INNER JOIN
                block 
            ON
                block.id = change.block
            INNER JOIN
                revision
            ON 
                revision.id = change.revision
            INNER JOIN
                owner
            ON
                owner.id = change.owner
            INNER JOIN
                project
            ON
                project.id = change.project
            ORDER BY
                project.id,
                revision.number;

CREATE OR REPLACE VIEW change_data_method AS SELECT
                *
            FROM
                change_data_all
            WHERE
                block_type = 'Method';

CREATE OR REPLACE VIEW change_data_class AS SELECT
                *
            FROM
                change_data_all
            WHERE
                block_type = 'Class';
    
CREATE OR REPLACE VIEW change_data_file AS SELECT
                *
            FROM
                change_data_all
            WHERE
                block_type = 'File';
    
CREATE OR REPLACE VIEW change_data_sums AS
SELECT block_id, owner_id, sum(additions + deletions) AS sum
    FROM change_data_all
    GROUP BY block_id, owner_id
    ORDER BY block_id, owner_id;
