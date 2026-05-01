-- TSIS1 stored procedures and search function

create or replace procedure add_phone(p_contact_name varchar, p_phone varchar, p_type varchar)
language plpgsql as $$
declare
    v_contact_id integer;
begin
    select id into v_contact_id from contacts where name = p_contact_name;
    if not found then
        raise exception 'Contact % not found', p_contact_name;
    end if;
    if p_type not in ('home', 'work', 'mobile') then
        raise exception 'Phone type must be home, work, or mobile';
    end if;
    insert into phones(contact_id, phone, type) values (v_contact_id, p_phone, p_type);
end;
$$;

create or replace procedure move_to_group(p_contact_name varchar, p_group_name varchar)
language plpgsql as $$
declare
    v_group_id integer;
begin
    if p_group_name is null or trim(p_group_name) = '' then
        raise exception 'Group name must not be empty';
    end if;
    insert into groups(name) values (trim(p_group_name)) on conflict (name) do nothing;
    select id into v_group_id from groups where name = trim(p_group_name);
    update contacts set group_id = v_group_id where name = p_contact_name;
    if not found then
        raise exception 'Contact % not found', p_contact_name;
    end if;
end;
$$;

create or replace function search_contacts(p_query text)
returns table (
    id integer,
    name varchar,
    email varchar,
    birthday date,
    group_name varchar,
    created_at timestamp
)
language sql as $$
    select distinct c.id, c.name, c.email, c.birthday, g.name, c.created_at
    from contacts c
    left join groups g on g.id = c.group_id
    left join phones p on p.contact_id = c.id
    where c.name ilike '%' || p_query || '%'
       or c.email ilike '%' || p_query || '%'
       or p.phone ilike '%' || p_query || '%'
    order by c.name;
$$;

create or replace function get_contacts_page(
    p_limit integer,
    p_offset integer,
    p_group_name varchar default null,
    p_email_search varchar default null,
    p_sort varchar default 'name'
)
returns table (
    id integer,
    name varchar,
    email varchar,
    birthday date,
    group_name varchar,
    created_at timestamp
)
language sql as $$
    select c.id, c.name, c.email, c.birthday, g.name, c.created_at
    from contacts c
    left join groups g on g.id = c.group_id
    where (p_group_name is null or g.name = p_group_name)
      and (p_email_search is null or c.email ilike '%' || p_email_search || '%')
    order by
      case when p_sort = 'birthday' then c.birthday end nulls last,
      case when p_sort = 'date' then c.created_at end nulls last,
      case when p_sort = 'name' then c.name end nulls last
    limit p_limit offset p_offset;
$$;
