create trigger trg_function00
after insert on deployed_table_00
for each row
execute function function00()