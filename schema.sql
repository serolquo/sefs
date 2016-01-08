drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  hashed_key text not null,
  salt text not null,
  s3_object text not null,
  date_uploaded text not null,
  uploaded integer not null
);

create index s3obj_index on entries (s3_object);
