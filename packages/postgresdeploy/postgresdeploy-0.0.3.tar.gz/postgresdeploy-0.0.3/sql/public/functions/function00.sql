create or replace function function00()
returns trigger
language plpgsql
as $$
begin
    insert into public.deployed_table_00
    (new.col1)
    values
    ('text');
	
    return new;
end;
$$