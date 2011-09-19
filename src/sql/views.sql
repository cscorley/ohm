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

 create or replace view change_data_sums_owner as (select t1.block_id, t1.owner_id, t1.sum 
from change_data_sums as t1 
left outer join change_data_sums as t2
on (t1.block_id = t2.block_id and t1.sum < t2.sum)
where t2.block_id is null 
order by block_id);
