-- TSIS1 schema for enhanced contact management

create table if not exists groups (
    id serial primary key,
    name varchar(50) unique not null
);

create table if not exists contacts (
    id serial primary key,
    name varchar(100) unique not null,
    email varchar(100),
    birthday date,
    group_id integer references groups(id),
    created_at timestamp default now()
);

create table if not exists phones (
    id serial primary key,
    contact_id integer references contacts(id) on delete cascade,
    phone varchar(20) not null,
    type varchar(10) check (type in ('home', 'work', 'mobile'))
);

alter table if exists contacts add column if not exists email varchar(100);
alter table if exists contacts add column if not exists birthday date;
alter table if exists contacts add column if not exists group_id integer references groups(id);
alter table if exists contacts add column if not exists created_at timestamp default now();

insert into groups(name) values ('Family'), ('Work'), ('Friend'), ('Other')
    on conflict (name) do nothing;
