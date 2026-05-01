-- Practice 8: PostgreSQL procedures for PhoneBook
-- Assumes a table with this structure:
-- contacts(id SERIAL PRIMARY KEY, first_name VARCHAR, last_name VARCHAR, phone VARCHAR)

CREATE OR REPLACE PROCEDURE upsert_contact(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM contacts
        WHERE first_name = p_first_name
          AND last_name = p_last_name
    ) THEN
        UPDATE contacts
        SET phone = p_phone
        WHERE first_name = p_first_name
          AND last_name = p_last_name;
    ELSE
        INSERT INTO contacts(first_name, last_name, phone)
        VALUES (p_first_name, p_last_name, p_phone);
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_first_names TEXT[],
    p_last_names TEXT[],
    p_phones TEXT[],
    INOUT p_invalid_data TEXT[] DEFAULT ARRAY[]::TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i INTEGER;
    current_first_name TEXT;
    current_last_name TEXT;
    current_phone TEXT;
BEGIN
    IF array_length(p_first_names, 1) IS DISTINCT FROM array_length(p_last_names, 1)
       OR array_length(p_first_names, 1) IS DISTINCT FROM array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'Input arrays must have the same length';
    END IF;

    FOR i IN 1..COALESCE(array_length(p_first_names, 1), 0) LOOP
        current_first_name := p_first_names[i];
        current_last_name := p_last_names[i];
        current_phone := p_phones[i];

        IF current_phone !~ '^\+?[0-9 ()-]{7,20}$' THEN
            p_invalid_data := array_append(
                p_invalid_data,
                current_first_name || ' ' || current_last_name || ': ' || current_phone
            );
        ELSE
            CALL upsert_contact(current_first_name, current_last_name, current_phone);
        END IF;
    END LOOP;
END;
$$;


CREATE OR REPLACE PROCEDURE delete_contact(p_value VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM contacts
    WHERE phone = p_value
       OR first_name = p_value
       OR last_name = p_value
       OR CONCAT(first_name, ' ', last_name) = p_value;
END;
$$;
