drop table if exists keys;
create table keys
(
  user_id varchar primary key,
  api bytea,
  can_run boolean,
  can_read_result boolean
);
