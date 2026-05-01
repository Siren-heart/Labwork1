import csv
import json
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

from config import load_config

VALID_PHONE_TYPES = {'home', 'work', 'mobile'}
PAGE_SIZE = 5
SORT_OPTIONS = {
    'name': 'name',
    'birthday': 'birthday',
    'date': 'created_at',
}
ORDER_OPTIONS = {
    'name': 'c.name',
    'birthday': 'c.birthday',
    'date': 'c.created_at',
}


def connect_db():
    return psycopg2.connect(**load_config())


def ensure_schema():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
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
            """)
        conn.commit()


def normalize_phone_type(value):
    if not value:
        return None
    normalized = value.strip().lower()
    if normalized in VALID_PHONE_TYPES:
        return normalized
    if normalized.startswith('h'):
        return 'home'
    if normalized.startswith('w'):
        return 'work'
    if normalized.startswith('m'):
        return 'mobile'
    return None


def parse_date(value):
    if not value:
        return None
    for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f'Unsupported date format: {value}')


def get_group_id(cur, group_name):
    if not group_name:
        return None
    normalized = group_name.strip()
    if normalized == '':
        return None
    cur.execute("insert into groups(name) values (%s) on conflict (name) do nothing", (normalized,))
    cur.execute("select id from groups where name = %s", (normalized,))
    row = cur.fetchone()
    return row[0] if row else None


def create_contact(conn, name, email=None, birthday=None, group_name=None, phones=None):
    if not name or name.strip() == '':
        raise ValueError('Contact name is required')
    phones = phones or []
    with conn.cursor() as cur:
        cur.execute('select id from contacts where name = %s', (name,))
        if cur.fetchone():
            raise ValueError(f'Contact {name} already exists')
        group_id = get_group_id(cur, group_name)
        cur.execute(
            'insert into contacts(name, email, birthday, group_id) values (%s, %s, %s, %s) returning id',
            (name, email, birthday, group_id),
        )
        contact_id = cur.fetchone()[0]
        for phone in phones:
            phone_value = phone.get('phone')
            phone_type = normalize_phone_type(phone.get('type'))
            if phone_value and phone_type:
                cur.execute(
                    'insert into phones(contact_id, phone, type) values (%s, %s, %s)',
                    (contact_id, phone_value.strip(), phone_type),
                )
        conn.commit()
    return contact_id


def update_contact(conn, name, email=None, birthday=None, group_name=None, phones=None):
    with conn.cursor() as cur:
        cur.execute('select id from contacts where name = %s', (name,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f'Contact {name} not found')
        contact_id = row[0]
        group_id = get_group_id(cur, group_name)
        cur.execute(
            'update contacts set email = %s, birthday = %s, group_id = %s where id = %s',
            (email, birthday, group_id, contact_id),
        )
        if phones is not None:
            cur.execute('delete from phones where contact_id = %s', (contact_id,))
            for phone in phones:
                phone_value = phone.get('phone')
                phone_type = normalize_phone_type(phone.get('type'))
                if phone_value and phone_type:
                    cur.execute(
                        'insert into phones(contact_id, phone, type) values (%s, %s, %s)',
                        (contact_id, phone_value.strip(), phone_type),
                    )
        conn.commit()
    return contact_id


def add_phone_to_contact(conn, contact_name, phone_value, phone_type):
    with conn.cursor() as cur:
        cur.execute('select id from contacts where name = %s', (contact_name,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f'Contact {contact_name} not found')
        normalized_type = normalize_phone_type(phone_type)
        if not normalized_type:
            raise ValueError('Phone type must be one of home, work, mobile')
        cur.execute(
            'insert into phones(contact_id, phone, type) values (%s, %s, %s)',
            (row[0], phone_value.strip(), normalized_type),
        )
        conn.commit()


def move_contact_to_group(conn, contact_name, group_name):
    with conn.cursor() as cur:
        cur.execute('select id from contacts where name = %s', (contact_name,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f'Contact {contact_name} not found')
        group_id = get_group_id(cur, group_name)
        cur.execute('update contacts set group_id = %s where id = %s', (group_id, row[0]))
        conn.commit()


def delete_contact(conn, contact_name):
    with conn.cursor() as cur:
        cur.execute('select id from contacts where name = %s', (contact_name,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f'Contact {contact_name} not found')
        cur.execute('delete from contacts where id = %s', (row[0],))
        conn.commit()


def get_groups(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('select name from groups order by name')
        return [row['name'] for row in cur.fetchall()]


def fetch_phones(conn, contact_ids):
    if not contact_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            'select contact_id, phone, type from phones where contact_id = any(%s) order by id',
            (contact_ids,),
        )
        result = {}
        for contact_id, phone, type_name in cur.fetchall():
            result.setdefault(contact_id, []).append({'phone': phone, 'type': type_name})
        return result


def fetch_page(conn, group_filter=None, email_search=None, sort_by='name', page=0):
    order_field = ORDER_OPTIONS.get(sort_by, 'c.name')
    email_filter = f'%{email_search}%' if email_search else None
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"""
            select c.id, c.name, c.email, c.birthday, g.name as group_name, c.created_at
            from contacts c
            left join groups g on g.id = c.group_id
            where (%s is null or g.name = %s)
              and (%s is null or c.email ilike %s)
            order by {order_field} nulls last
            limit %s offset %s
            """,
            (group_filter, group_filter, email_search, email_filter, PAGE_SIZE, page * PAGE_SIZE),
        )
        contacts = cur.fetchall()
        contact_ids = [row['id'] for row in contacts]
        phones = fetch_phones(conn, contact_ids)
        for row in contacts:
            row['phones'] = phones.get(row['id'], [])
        return contacts


def search_contacts(conn, query, sort_by='name', page=0):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('select * from search_contacts(%s)', (query,))
        rows = cur.fetchall()
        field = SORT_OPTIONS.get(sort_by, 'name')
        if field in ('birthday', 'created_at'):
            rows.sort(key=lambda row: row.get(field) or datetime.min)
        else:
            rows.sort(key=lambda row: row.get(field) or '')
        start = page * PAGE_SIZE
        selected = rows[start:start + PAGE_SIZE]
        contact_ids = [row['id'] for row in selected]
        phones = fetch_phones(conn, contact_ids)
        for row in selected:
            row['phones'] = phones.get(row['id'], [])
        return selected, len(rows)


def print_contacts(rows, page=1, total=None):
    if not rows:
        print('No contacts found.')
        return
    print(f'\nContacts (page {page}{" of " + str(total) if total is not None else ""}):')
    for row in rows:
        print('---')
        print(f"Name: {row['name']}")
        print(f"Group: {row.get('group_name') or 'None'}")
        print(f"Email: {row.get('email') or 'None'}")
        print(f"Birthday: {row.get('birthday') or 'None'}")
        print(f"Added: {row.get('created_at')}")
        if row.get('phones'):
            print('Phones:')
            for phone in row['phones']:
                print(f"  - {phone['phone']} ({phone['type']})")
        else:
            print('Phones: None')
    print('')


def build_phone_list(row):
    phones = []
    for suffix in ['', '1', '2', '3', '4', '5']:
        phone_key = f'phone{suffix}' if suffix else 'phone'
        type_key = f'type{suffix}' if suffix else 'type'
        phone_value = row.get(phone_key) or row.get(phone_key.lower())
        phone_type = row.get(type_key) or row.get(type_key.lower())
        if phone_value:
            phones.append({'phone': phone_value.strip(), 'type': normalize_phone_type(phone_type) or 'mobile'})
    return phones


def import_contacts_from_csv(conn, filepath):
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f'CSV file not found: {path}')

    with path.open(newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        imported = 0
        for row in reader:
            name = (row.get('name') or '').strip()
            if not name:
                continue
            email = (row.get('email') or '').strip() or None
            birthday = None
            if row.get('birthday'):
                try:
                    birthday = parse_date(row['birthday'])
                except ValueError as exc:
                    print(f'Warning: skipping invalid birthday for {name}: {exc}')
            group_name = (row.get('group') or '').strip() or None
            phones = build_phone_list(row)
            with conn.cursor() as cur:
                cur.execute('select id from contacts where name = %s', (name,))
                if cur.fetchone():
                    action = prompt_duplicate_action(name)
                    if action == 'skip':
                        continue
                    update_contact(conn, name, email=email, birthday=birthday, group_name=group_name, phones=phones)
                else:
                    create_contact(conn, name, email=email, birthday=birthday, group_name=group_name, phones=phones)
            imported += 1
    print(f'Imported {imported} contacts from CSV.')


def export_contacts_to_json(conn, filepath):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            select c.id, c.name, c.email, c.birthday, g.name as group_name, c.created_at
            from contacts c
            left join groups g on g.id = c.group_id
            order by c.name
            """
        )
        contacts = cur.fetchall()
        phones = fetch_phones(conn, [row['id'] for row in contacts])
        payload = []
        for row in contacts:
            payload.append({
                'name': row['name'],
                'email': row.get('email'),
                'birthday': row['birthday'].isoformat() if row.get('birthday') else None,
                'group': row.get('group_name'),
                'phones': phones.get(row['id'], []),
            })
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
    print(f'Exported {len(payload)} contacts to {filepath}')


def prompt_duplicate_action(name):
    while True:
        choice = input(f'Contact "{name}" already exists. [S]kip or [O]verwrite? ').strip().lower()
        if choice.startswith('s'):
            return 'skip'
        if choice.startswith('o'):
            return 'overwrite'
        print('Enter S or O.')


def import_contacts_from_json(conn, filepath):
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f'JSON file not found: {path}')

    with path.open(encoding='utf-8') as file:
        data = json.load(file)
    imported = 0
    for item in data:
        name = (item.get('name') or '').strip()
        if not name:
            continue
        email = (item.get('email') or '').strip() or None
        birthday = None
        if item.get('birthday'):
            birthday = parse_date(item['birthday'])
        group_name = (item.get('group') or '').strip() or None
        phones = item.get('phones') or []
        with conn.cursor() as cur:
            cur.execute('select id from contacts where name = %s', (name,))
            exists = cur.fetchone() is not None
            if exists:
                action = prompt_duplicate_action(name)
                if action == 'skip':
                    continue
                update_contact(conn, name, email=email, birthday=birthday, group_name=group_name, phones=phones)
            else:
                create_contact(conn, name, email=email, birthday=birthday, group_name=group_name, phones=phones)
        imported += 1
    print(f'Imported {imported} contacts from JSON.')


def interactive_page_loop(conn, group_filter=None, email_search=None, sort_by='name'):
    page = 0
    while True:
        rows = fetch_page(conn, group_filter=group_filter, email_search=email_search, sort_by=sort_by, page=page)
        print_contacts(rows, page=page + 1)
        command = input('[N]ext, [P]rev, [Q]uit: ').strip().lower()
        if command.startswith('n'):
            page += 1
        elif command.startswith('p') and page > 0:
            page -= 1
        elif command.startswith('q'):
            break
        else:
            print('Please enter N, P, or Q.')


def interactive_search_loop(conn):
    query = input('Search query: ').strip()
    page = 0
    while True:
        results, total = search_contacts(conn, query, sort_by='name', page=page)
        print_contacts(results, page=page + 1, total=(total + PAGE_SIZE - 1) // PAGE_SIZE)
        command = input('[N]ext, [P]rev, [Q]uit: ').strip().lower()
        if command.startswith('n'):
            page += 1
        elif command.startswith('p') and page > 0:
            page -= 1
        elif command.startswith('q'):
            break
        else:
            print('Please enter N, P, or Q.')


def prompt_new_contact(conn):
    name = input('Name: ').strip()
    email = input('Email: ').strip() or None
    birthday = input('Birthday (YYYY-MM-DD): ').strip() or None
    if birthday:
        birthday = parse_date(birthday)
    group_name = input('Group (Family, Work, Friend, Other): ').strip() or None
    phones = []
    while True:
        phone = input('Phone number (or leave blank to finish): ').strip()
        if not phone:
            break
        phone_type = input('Phone type (home, work, mobile): ').strip()
        phones.append({'phone': phone, 'type': phone_type})
        more = input('Add another phone? [y/N]: ').strip().lower()
        if more != 'y':
            break
    create_contact(conn, name, email=email, birthday=birthday, group_name=group_name, phones=phones)
    print(f'Contact "{name}" saved.')


def main():
    ensure_schema()
    with connect_db() as conn:
        while True:
            print('\nPhonebook menu:')
            print('1. Add contact')
            print('2. Add phone to contact')
            print('3. Move contact to group')
            print('4. Delete contact')
            print('5. Search contacts')
            print('6. Filter by group')
            print('7. Search by email')
            print('8. Export contacts to JSON')
            print('9. Import contacts from JSON')
            print('10. Import contacts from CSV')
            print('0. Quit')
            choice = input('Choose an option: ').strip()
            try:
                if choice == '1':
                    prompt_new_contact(conn)
                elif choice == '2':
                    name = input('Contact name: ').strip()
                    phone_number = input('Phone number: ').strip()
                    phone_type = input('Phone type (home, work, mobile): ').strip()
                    add_phone_to_contact(conn, name, phone_number, phone_type)
                    print(f'Phone added to {name}.')
                elif choice == '3':
                    name = input('Contact name: ').strip()
                    group_name = input('New group: ').strip()
                    move_contact_to_group(conn, name, group_name)
                    print(f'{name} moved to {group_name}.')
                elif choice == '4':
                    name = input('Contact name to delete: ').strip()
                    confirm = input(f'Are you sure you want to delete "{name}"? [y/N]: ').strip().lower()
                    if confirm == 'y':
                        delete_contact(conn, name)
                        print(f'Contact "{name}" deleted.')
                    else:
                        print('Delete canceled.')
                elif choice == '5':
                    interactive_search_loop(conn)
                elif choice == '6':
                    groups = get_groups(conn)
                    print('Available groups:', ', '.join(groups))
                    group_name = input('Group to filter by: ').strip() or None
                    sort_by = input('Sort by (name, birthday, date): ').strip().lower() or 'name'
                    if sort_by not in SORT_OPTIONS:
                        sort_by = 'name'
                    interactive_page_loop(conn, group_filter=group_name, sort_by=sort_by)
                elif choice == '7':
                    email_query = input('Email search query: ').strip() or None
                    sort_by = input('Sort by (name, birthday, date): ').strip().lower() or 'name'
                    if sort_by not in SORT_OPTIONS:
                        sort_by = 'name'
                    interactive_page_loop(conn, email_search=email_query, sort_by=sort_by)
                elif choice == '8':
                    filename = input('JSON filename to export: ').strip() or 'contacts_export.json'
                    export_contacts_to_json(conn, filename)
                elif choice == '9':
                    filename = input('JSON filename to import: ').strip() or 'contacts_import.json'
                    import_contacts_from_json(conn, filename)
                elif choice == '10':
                    filename = input('CSV filename to import: ').strip() or 'contacts.csv'
                    import_contacts_from_csv(conn, filename)
                elif choice == '0':
                    print('Goodbye!')
                    break
                else:
                    print('Invalid choice, try again.')
            except Exception as exc:
                print(f'Error: {exc}')


if __name__ == '__main__':
    main()
