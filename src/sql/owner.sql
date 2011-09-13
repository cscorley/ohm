-- if any duplicate full_names exist
 select b.full_name, count(b.full_name) from block b group by full_name having (count(b.full_name) > 1) order by count;


select project, name, count from owner, (SELECT owner_id, count(DISTINCT method_id) from change_data group by owner_id order by owner_id) AS ot where ot.owner_id = owner.id;

-- how many revisions and unique owners a method has
SELECT method_id, count(revision_number) revisions, count(DISTINCT owner_id) uniq_owners from change_data group by method_id order by method_id;

-- how many methods have x uniq_owners
select count(DISTINCT method_id), uniq_owners from (SELECT method_id, count(revision_number) revisions, count(DISTINCT owner_id) uniq_owners from change_data group by method_id order by method_id) as t group by uniq_owners order by uniq_owners;

-- how many methods have x revisions
select count(DISTINCT method_id), revisions FROM (SELECT method_id, count(revision_number) revisions from change_data group by id order by revisions desc) as tmp group by revisions;

-- how many methods a unique owner has the mode() of changes (ie, the most touches to method)
select owner.project, owner_id, owner.name, count(DISTINCT method_id) method_count from (select method_id, mode(owner_id) owner_id from change_data group by method_id) as t inner join owner on owner_id=owner.id group by owner_id, owner.name, owner.project order by owner_id;
select owner.project, owner_id, owner.name, count(DISTINCT class_id) class_count from (select class_id, mode(owner_id) owner_id from change_data group by class_id) as t inner join owner on owner_id=owner.id group by owner_id, owner.name, owner.project order by owner_id;
select owner.project, owner_id, owner.name, count(DISTINCT file_id) file_count from (select file_id, mode(owner_id) owner_id from change_data group by file_id) as t inner join owner on owner_id=owner.id group by owner_id, owner.name, owner.project order by owner_id;

-- same as above, but excludes the methods with "0" current length
select owner_id, owner.name, count(method_id) from (select change_data.method_id, mode(owner_id) owner_id from change_data inner join (select *, sum_a-sum_d current_length from (select method_id, sum(additions) as sum_a, sum(deletions) as sum_d from change_data group by method_id) as sums where sum_a-sum_d > 0 group by method_id, sum_a, sum_d, current_length order by method_id) as t on change_data.method_id=t.method_id group by change_data.method_id) as what inner join owner on owner_id=owner.id group by owner_id order by owner_id;


-- the view for below
create or replace view change_data_sums as (select method_id, owner_id, sum(additions + deletions) from change_data group by method_id, owner_id order by method_id);
select method_id, owner_id, sum(additions + deletions) from change_data group by method_id, owner_id order by method_id
select class_id, owner_id, sum(additions + deletions) from change_data group by class_id, owner_id order by class_id
select file_id, owner_id, sum(additions + deletions) from change_data group by file_id, owner_id order by file_id

-- which owner has the most contributinos (sum of additions/deletions) on a method
select t1.method_id, t1.owner_id, t1.sum 
from (select method_id, owner_id, sum(additions + deletions) from change_data group by method_id, owner_id order by method_id) as t1 
left outer join	(select method_id, owner_id, sum(additions + deletions) from change_data group by method_id, owner_id order by method_id) as t2
on (t1.method_id = t2.method_id and t1.sum < t2.sum)
where t2.method_id is null 
order by method_id;

select t1.class_id, t1.owner_id, t1.sum 
from (select class_id, owner_id, sum(additions + deletions) from change_data group by class_id, owner_id order by class_id) as t1 
left outer join (select class_id, owner_id, sum(additions + deletions) from change_data group by class_id, owner_id order by class_id) as t2
on (t1.class_id = t2.class_id and t1.sum < t2.sum)
where t2.class_id is null 
order by class_id;

select t1.file_id, t1.owner_id, t1.sum 
from (select file_id, owner_id, sum(additions + deletions) from change_data group by file_id, owner_id order by file_id) as t1 
left outer join (select file_id, owner_id, sum(additions + deletions) from change_data group by file_id, owner_id order by file_id) as t2
on (t1.file_id = t2.file_id and t1.sum < t2.sum)
where t2.file_id is null 
order by file_id;

-- above, but methods which have more than 1, ie, have ties
select count(method_id), method_id from (select t1.method_id, t1.owner_id, t1.sum from change_data_sums as t1 left outer join change_data_sums as t2 on (t1.method_id = t2.method_id and t1.sum < t2.sum) where t2.method_id is null order by method_id) as sumz where count(method_id) > 1 group by method_id;

-- how many methods a unique owner has the mode of changes based on contributions
select owner.project, owner_id, owner.name, count(DISTINCT method_id) method_count
from (
	select t1.method_id, mode(t1.owner_id) owner_id
	from (
		select method_id, owner_id, sum(additions + deletions) from change_data group by method_id, owner_id order by method_id
	) as t1
	left outer join (
		select method_id, owner_id, sum(additions + deletions) from change_data group by method_id, owner_id order by method_id
	)as t2
	on (t1.method_id = t2.method_id and t1.sum < t2.sum)
	where t2.method_id is null
	group by t1.method_id order by method_id
) as t 
inner join owner
on owner_id=owner.id 
group by owner_id, owner.name, owner.project order by owner_id;

select owner.project, owner_id, owner.name, count(DISTINCT class_id) class_count
from (
	select t1.class_id, mode(t1.owner_id) owner_id
	from (
		select class_id, owner_id, sum(additions + deletions) from change_data group by class_id, owner_id order by class_id
	) as t1
	left outer join (
		select class_id, owner_id, sum(additions + deletions) from change_data group by class_id, owner_id order by class_id
	)as t2
	on (t1.class_id = t2.class_id and t1.sum < t2.sum)
	where t2.class_id is null
	group by t1.class_id order by class_id
) as t 
inner join owner
on owner_id=owner.id 
group by owner_id, owner.name, owner.project order by owner_id;

select owner.project, owner_id, owner.name, count(DISTINCT file_id) file_count
from (
	select t1.file_id, mode(t1.owner_id) owner_id
	from (
		select file_id, owner_id, sum(additions + deletions) from change_data group by file_id, owner_id order by file_id
	) as t1
	left outer join (
		select file_id, owner_id, sum(additions + deletions) from change_data group by file_id, owner_id order by file_id
	)as t2
	on (t1.file_id = t2.file_id and t1.sum < t2.sum)
	where t2.file_id is null
	group by t1.file_id order by file_id
) as t 
inner join owner
on owner_id=owner.id 
group by owner_id, owner.name, owner.project order by owner_id;


-- this one will show you how much you are wrong (aka, how many methods have negative changes
select *, sum_a-sum_d current_length from (select method_id, sum(additions) as sum_a, sum(deletions) as sum_d from change_data group by method_id) as sums where sum_a-sum_d < 0 group by method_id, sum_a, sum_d, current_length order by method_id;

-- interesting
-- above, but methods which have more than 1, ie, have ties
select count(method_id), method_id from (select t1.method_id, t1.owner_id, t1.sum from change_data_sums as t1 left outer join change_data_sums as t2 on (t1.method_id = t2.method_id and t1.sum < t2.sum) where t2.method_id is null order by method_id) as sumz where count(method_id) > 1 group by method_id;

-- how many methods a unique owner has the mode of changes based on contributions
select owner_id, owner.name, count(DISTINCT method_id) method_count from (select t1.method_id, mode(t1.owner_id) owner_id from change_data_sums as t1 left outer join change_data_sums as t2 on (t1.method_id = t2.method_id and t1.sum < t2.sum) where t2.method_id is null group by t1.method_id order by method_id) as t inner join owner on owner_id=owner.id group by owner_id, owner.name order by owner_id;


-- this one will show you how much you are wrong (aka, how many methods have negative changes
select *, sum_a-sum_d current_length from (select method_id, sum(additions) as sum_a, sum(deletions) as sum_d from change_data group by method_id) as sums where sum_a-sum_d < 0 group by method_id, sum_a, sum_d, current_length order by method_id;

-- interesting
select * from change inner join revision on change.revision=revision.id inner join method on change.method=method.id where method=289 order by revision;
select c.revision, c.file, c.method, c.additions, c.deletions, r.number, r.owner, m.signature, c.project from change c inner join revision r on c.revision=r.id inner join method m on c.method=m.id where c.method=53493 order by r.number;

-- gets min and max revisions for given revision numbers
select t.method_id, min(number), max(number) from (select m.id method_id, r.number from change c inner join revision r on c.revision=r.id inner join method m on c.method=m.id group by r.number, m.id order by r.number) as t inner join (select method_name, additions, deletions, revision_number, method_id from change_data va inner join revision r on r.number=va.revision_number where project=1 and revision_number = 10156 or revision_number = 10165 or revision_number = 10172 order by revision_number, method_id) as s on t.method_id=s.method_id group by t.method_id order by t.method_id;

select method_name, method_id from (select s.method_name, t.method_id, min(number) = 10156 a1, min(number) =10165 a2, min(number)=10172 a3, max(number)=10156 d1, max(number)=10165 d2, max(number)=10172 d3 from (select m.id method_id, r.number from change c inner join revision r on c.revision=r.id inner join method m on c.method=m.id group by r.number, m.id order by r.number) as t inner join (select method_name, additions, deletions, revision_number, method_id from change_data va inner join revision r on r.number=va.revision_number where project=1 and revision_number = 10156 or revision_number = 10165 or revision_number = 10172 order by revision_number, method_id) as s on t.method_id=s.method_id group by t.method_id, s.method_name order by t.method_id) as what where a1='t';
