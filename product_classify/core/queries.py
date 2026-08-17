class ClassStructQueries:
    FIND_GR_GR = "SELECT * FROM find_gr_gr(%s);"
    GET_TERMINAL_CLASSES = "SELECT * FROM get_terminal_classes(%s);"
    DELETE_CLASS_AND_DESCENDANTS = "SELECT * FROM delete_class_and_descendants(%s);"
    CHECK_CYCLE = "SELECT * FROM check_class_struct_cycles(%s, %s);"
    IS_PARENT_PROD = "SELECT * FROM is_parent_prod(%s);"
    TOTAL_COST_RATIO = "SELECT * FROM total_cost_ratio(%s, %s);"
    GET_CHANGE_LOG = "SELECT * FROM get_changelog(%s);"
    CREATE_SPECIFICATION = "SELECT * FROM create_specification(%s, %s, %s);"
    PRODUCT_SPECIFICATION = "SELECT * FROM product_specification(%s);"


class DatabaseFunctions:
    CHECK_CYCLE = """
        CREATE OR REPLACE FUNCTION check_class_struct_cycles(cls_id integer, main_cls_id integer) RETURNS boolean
            LANGUAGE plpgsql
        AS
        $$
            DECLARE
                rec RECORD;
                visited INTEGER[];      -- массив для хранения посещённых идентификаторов
                parent_id INTEGER;      -- текущий родительский идентификатор
            BEGIN
        
            CREATE TEMP TABLE TEMP_CLASS_STRUCT(
                CLASS_ID INTEGER PRIMARY KEY,
                MAIN_CLASS INTEGER,
                FOREIGN KEY (MAIN_CLASS) REFERENCES TEMP_CLASS_STRUCT(CLASS_ID)
            ) ON COMMIT DROP;
            
            INSERT INTO TEMP_CLASS_STRUCT 
            SELECT classes_classstruct.id, classes_classstruct.main_class_id FROM classes_classstruct;
        
            UPDATE TEMP_CLASS_STRUCT
            SET MAIN_CLASS = MAIN_CLS_ID
            WHERE TEMP_CLASS_STRUCT.CLASS_ID = CLS_ID;
            
                -- перебираем все записи таблицы
                FOR rec IN SELECT class_id, main_class FROM TEMP_CLASS_STRUCT LOOP
                        visited := ARRAY[rec.class_id];  -- начинаем с текущего класса
                        parent_id := rec.main_class;
        
                        -- идём по цепочке родителей, пока не достигнем конца (NULL)
                        WHILE parent_id IS NOT NULL LOOP
                                -- если родитель уже встречался, значит, обнаружен цикл
                                IF parent_id = ANY(visited) THEN
                                    RETURN TRUE;
                                END IF;
        
                                -- добавляем родителя в массив посещённых
                                visited := visited || parent_id;
        
                                -- переходим к следующему родителю
                                SELECT main_class INTO parent_id
                                FROM TEMP_CLASS_STRUCT
                                WHERE class_id = parent_id;
                            END LOOP;
                    END LOOP;
        
                -- если цикл не найден, возвращаем false
                RETURN FALSE;
            END;
        $$;
    """
    DELETE_CLASS_AND_DESCENDANTS = """
        CREATE OR REPLACE FUNCTION delete_class_and_descendants(_node_id integer) RETURNS integer
            LANGUAGE plpgsql
        AS
        $$
        DECLARE
            deleted_count INTEGER;
        BEGIN
            -- Проверяем, что класс с данным идентификатором существует
            IF NOT EXISTS (SELECT 1 FROM classes_classstruct WHERE classes_classstruct.id = _node_id) THEN
                RAISE EXCEPTION 'Класс с идентификатором % не найден', _node_id;
            END IF;
        
            -- С помощью рекурсии собираем идентификаторы всех классов,
            -- которые являются потомками указанного класса, включая его самого.
            WITH RECURSIVE subtree AS (
                SELECT classes_classstruct.id
                FROM classes_classstruct
                WHERE classes_classstruct.id = _node_id
        
                UNION ALL
        
                SELECT child.id
                FROM classes_classstruct child
                            INNER JOIN subtree parent ON child.main_class_id = parent.id
            )
            -- Удаляем все записи, идентификаторы которых найдены в поддереве
            DELETE FROM classes_classstruct
            WHERE classes_classstruct.id IN (SELECT classes_classstruct.id FROM subtree);
        
            -- Получаем количество удалённых строк
            GET DIAGNOSTICS deleted_count = ROW_COUNT;
            RETURN deleted_count;
        END;
        $$;
    """
    FIND_GR_GR = """
        CREATE OR REPLACE FUNCTION find_gr_gr(prod_class_id integer)
            RETURNS TABLE(class_id bigint, main_class bigint, name character varying, base_ei bigint)
            LANGUAGE plpgsql
        AS
        $$
        BEGIN
            IF NOT EXISTS(SELECT 1 FROM classes_classstruct
                                WHERE classes_classstruct.id = prod_class_id) THEN
            RAISE EXCEPTION 'Такого класса не существует!';
        ELSE
            RETURN QUERY
                SELECT classes_classstruct.id, classes_classstruct.main_class_id, classes_classstruct.name, classes_classstruct.base_ei_id
                FROM classes_classstruct
                WHERE classes_classstruct.id = prod_class_id
                UNION
                (
                    WITH RECURSIVE r AS(
                        SELECT classes_classstruct.id, classes_classstruct.main_class_id, classes_classstruct.name, classes_classstruct.base_ei_id
                        FROM classes_classstruct
                        WHERE classes_classstruct.main_class_id = prod_class_id
        
                        UNION
        
                        SELECT classes_classstruct.id, classes_classstruct.main_class_id, classes_classstruct.name, classes_classstruct.base_ei_id
                        FROM classes_classstruct
                                    JOIN r
                                        ON classes_classstruct.main_class_id = r.id
                    )
                    SELECT * FROM r);
            end if;
        end;
        $$;
    """
    GET_TERMINAL_CLASSES = """
        CREATE OR REPLACE FUNCTION get_terminal_classes(_start_class integer) RETURNS SETOF classes_classstruct
            LANGUAGE plpgsql
        AS
        $$
        BEGIN
            -- Проверяем, существует ли заданный класс
            IF NOT EXISTS (SELECT 1 FROM classes_classstruct WHERE classes_classstruct.id = _start_class) THEN
                RAISE EXCEPTION 'Класс с идентификатором % не найден', _start_class;
            END IF;
        
            RETURN QUERY
                WITH RECURSIVE class_tree AS (
                    -- Начало рекурсии: выбран заданный класс
                    SELECT *
                    FROM classes_classstruct
                    WHERE classes_classstruct.id = _start_class
        
                    UNION ALL
        
                    -- Рекурсивное добавление: ищем потомков текущих вершин
                    SELECT child.*
                    FROM classes_classstruct child
                                INNER JOIN class_tree parent ON child.MAIN_CLASS_ID = parent.id
                )
                -- Выбираем те вершины, у которых нет потомков
                SELECT ct.*
                FROM class_tree ct
                WHERE NOT EXISTS (
                    SELECT 1 FROM classes_classstruct c
                    WHERE c.MAIN_CLASS_id = ct.id
                );
        END;
        $$;
    """
    ADD_PARAMETR_TO_CLASS = """
        CREATE OR REPLACE FUNCTION to_add_parametr_to_class(cls_id integer, parametr_id integer, min_val double precision, max_val double precision) RETURNS integer
            LANGUAGE plpgsql
        AS
        $$
            DECLARE 
            f_result INTEGER;
            parametr_record RECORD;
            parametr_tp INTEGER;
            enum_parent_node_id INTEGER;
            product_classes_parent_node_id INTEGER;
            cls_ids integer[];
            BEGIN
            enum_parent_node_id := 14;
            IF NOT EXISTS(SELECT * FROM classes_classstruct WHERE classes_classstruct.id = cls_id) THEN
                f_result := 0;
                RAISE EXCEPTION 'Класса с ID=% не существует!', cls_id;
                RETURN f_result;
            END IF;
            IF NOT EXISTS(SELECT * FROM parametr_parametr WHERE parametr_parametr.id = parametr_id) THEN
                f_result := 0;
                RAISE EXCEPTION 'Параметра с ID=% не существует!', parametr_id;
                RETURN f_result;
            END IF;
            product_classes_parent_node_id := 1;
            SELECT class_id FROM find_gr_Gr(product_classes_parent_node_id) INTO cls_ids;
            -- IF NOT EXISTS(SELECT class_id FROM find_gr_gr(product_classes_parent_node_id) WHERE products_prod.class_field_id=cls_id) THEN
                -- RAISE EXCEPTION 'Элемент с ID=% не является изделием!', cls_id;
            -- END IF;
            IF NOT EXISTS(SELECT * FROM products_prod WHERE products_prod.class_field_id = cls) THEN
                RAISE EXCEPTION 'Элемент с ID=% не является изделием!', cls_id;
            END IF;
            SELECT * INTO parametr_record FROM parametr_parametr WHERE 
            parametr.id = parametr_id;
            parametr_tp := parametr_record.parametr_type_id;
            IF EXISTS(SELECT class_id FROM find_gr_gr(enum_parent_node_id) WHERE products_prod.class_id = parametr_tp) THEN
                IF min_val != 0.0 OR max_val != 0.0 THEN
                f_result := 0;
                RAISE EXCEPTION 'Нельзя присваивать параметру-перечислению значения MIN_VALUE и MAX_VALUE!';
                RETURN f_result;
                END IF;
                f_result := 1;
                INSERT INTO classes_parclass VALUES(cls_id, parametr_id, NULL, NULL);
                RETURN f_result;
            ELSE
                f_result := 1;
                INSERT INTO classes_parclass VALUES(cls_id, parametr_id, min_val, max_val);
                RETURN f_result;
            END IF;
            END;
        $$;
    """
    IS_PARENT_PROD = """
        CREATE OR REPLACE FUNCTION is_parent_prod(product_id integer) RETURNS INTEGER
            LANGUAGE plpgsql
        AS
        $$
        BEGIN
            IF EXISTS(SELECT 1 FROM specifications_prodcomponent sp WHERE sp.parent_prod_id = PRODUCT_ID) THEN
                RETURN 1;
            ELSE
                RETURN 0;
            END IF;
        END;
        $$;
    """
    TOTAL_COST_RATIO = """
        CREATE OR REPLACE FUNCTION total_cost_ratio(root_prod integer, num_of_products double precision)
            RETURNS TABLE(
                parent_id bigint,
                parent_prod_name character varying,
                child_id bigint,
                child_prod_name character varying,
                quantity double precision,
                ei_short_name character varying,
                total_cost double precision,
                level integer
            )
            LANGUAGE plpgsql
        as
        $$
        BEGIN
            RETURN QUERY
                WITH RECURSIVE r AS (
                    SELECT
                        pc.id AS pair_id,
                        pc.parent_prod_id AS parent_id,
                        pc.component_id AS child_id,
                        pc.num AS prod_num,
                        pc.quantity AS quantity,
                        1 AS level
                    FROM specifications_prodcomponent pc
                    WHERE pc.parent_prod_id = ROOT_PROD

                    UNION

                    SELECT
                        pc2.id AS pair_id,
                        pc2.parent_prod_id AS parent_id,
                        pc2.component_id AS child_id,
                        pc2.num AS prod_num,
                        pc2.quantity AS quantity,
                        r.LEVEL + 1 AS level
                    FROM specifications_prodcomponent pc2
                            JOIN r ON pc2.parent_prod_id = r.child_id
                    WHERE pc2.num = r.prod_num
                ),
                grouped_r as (
                SELECT
                    r.parent_id AS gr_parent_id,
                    r.child_id AS gr_child_id,
                    r.level AS gr_level,
                    AVG(r.quantity) as gr_quantity
                FROM r
                GROUP BY r.parent_id, r.child_id, r.level
                )
                SELECT
                    parent_prod.id AS parent_id,
                    parent_prod."name" AS parent_prod_name,
                    child_prod.id AS child_id,
                    child_prod."name" AS child_prod_name,
                    grouped_r.gr_quantity AS quantity,
                    e.short_name AS ei_short_name,
                    ROUND((child_prod.cost * grouped_r.gr_quantity * NUM_OF_PRODUCTS)::NUMERIC, 2)::DOUBLE PRECISION AS total_cost,
                    grouped_r.gr_level AS level
                FROM grouped_r
                JOIN products_prod parent_prod ON grouped_r.gr_parent_id = parent_prod.id
                JOIN products_prod child_prod ON grouped_r.gr_child_id = child_prod.id
                JOIN ei_ei e ON child_prod.ei_id = e.id
                ORDER BY grouped_r.gr_level;
        END;
        $$;
    """
    GET_CHANGE_LOG = """
        CREATE OR REPLACE FUNCTION get_changelog(target_product_id integer)
            returns table(
                log_id bigint,
                parent_id bigint,
                comp_id bigint,
                updated_at timestamp with time zone,
                log_string text
            )
            language plpgsql
        as
        $$
        BEGIN
            RETURN QUERY
                WITH RECURSIVE component_tree AS (
                    SELECT
                        id AS pair_id,
                        parent_prod_id,
                        component_id,
                        quantity,
                        1 as level,
                        num,
                        ARRAY[parent_prod_id] as path,
                        parent_prod_id::text || '->' || component_id::text as relation_path
                    FROM specifications_prodcomponent
                    WHERE parent_prod_id = TARGET_PRODUCT_ID

                    UNION ALL

                    SELECT
                        pc.id,
                        pc.parent_prod_id,
                        pc.component_id,
                        pc.quantity,
                        ct.level + 1 as level,
                        ct.num,
                        ct.path || pc.parent_prod_id,
                        ct.relation_path || '->' || pc.component_id::text
                    FROM component_tree ct
                    INNER JOIN specifications_prodcomponent pc ON pc.parent_prod_id = ct.component_id
                    WHERE NOT (pc.component_id = ANY(ct.path)) AND ct.num  = pc.num
                ), pairs AS (
                    SELECT
                        pair_id
                    FROM component_tree
                    GROUP BY pair_id
                )
                SELECT
                    sl.id,
                    pc.parent_prod_id,
                    pc.component_id,
                    sl.updated_at,
                    'Количество изделия "' || p2.name || '" для изделия "' || p3.name || '" изменилось с ' || sl.old_quantity || ' на ' || sl.new_quantity
                FROM specifications_specificationlogs sl
                JOIN specifications_prodcomponent pc ON sl.pair_id = pc.id
                JOIN products_prod p2 ON pc.component_id = p2.id
                JOIN products_prod p3 ON pc.parent_prod_id = p3.id
                WHERE sl.pair_id IN (SELECT pair_id FROM pairs);
        END;
        $$;
    """
    CREATE_SPECIFICATION = """
        CREATE OR REPLACE FUNCTION create_specification(base_product_id integer, modified_product_name character varying, modified_product_short_name character varying) returns bigint
            language plpgsql
        as
        $$
        DECLARE
            MOD_CLASS_ID bigint;
            MOD_COST DOUBLE PRECISION;
            MOD_EI bigint;
            MOD_POSITION INTEGER;
            MOD_IMAGE VARCHAR;
            COMPONENT_REC RECORD;
            new_prod_id bigint;
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM products_prod WHERE id = BASE_PRODUCT_ID) THEN
                RAISE EXCEPTION 'Error product_id: %', BASE_PRODUCT_ID;
            END IF;

            SELECT count(*) + 1 INTO MOD_POSITION
            FROM products_prod
            WHERE modification_id = BASE_PRODUCT_ID;

            SELECT class_field_id, IMAGE, COST, ei_id
            INTO MOD_CLASS_ID, MOD_IMAGE, MOD_COST, MOD_EI
            FROM products_prod
            WHERE id = BASE_PRODUCT_ID;

            INSERT INTO products_prod
            VALUES (default, MODIFIED_PRODUCT_SHORT_NAME, MODIFIED_PRODUCT_NAME, MOD_IMAGE, MOD_CLASS_ID, MOD_COST, BASE_PRODUCT_ID, MOD_EI)
            RETURNING id INTO new_prod_id;

            FOR COMPONENT_REC IN
                WITH RECURSIVE component_tree AS (
                    SELECT
                        new_prod_id as parent_prod,
                        component_id,
                        quantity,
                        1 as level,
                        ARRAY[parent_prod_id] as path,
                        parent_prod_id::text || '->' || component_id::text as relation_path
                    FROM specifications_prodcomponent
                    WHERE parent_prod_id = BASE_PRODUCT_ID

                    UNION ALL

                    SELECT
                        pc.parent_prod_id as parent_prod,
                        pc.component_id,
                        pc.quantity,
                        ct.level + 1 as level,
                        ct.path || pc.parent_prod_id,
                        ct.relation_path || '->' || pc.component_id::text
                    FROM component_tree ct
                            INNER JOIN specifications_prodcomponent pc ON pc.parent_prod_id = ct.component_id
                    WHERE NOT (pc.component_id = ANY(ct.path))
                )
                SELECT
                    level,
                    parent_prod,
                    component_id,
                    SUM(quantity) / COUNT(*) as quantity
                FROM component_tree
                GROUP BY parent_prod, component_id, level
                ORDER BY level, parent_prod, component_id
                LOOP
                    INSERT INTO specifications_prodcomponent
                    VALUES (default, MOD_POSITION, COMPONENT_REC.quantity, COMPONENT_REC.component_id, COMPONENT_REC.parent_prod);
                END LOOP;
            RETURN new_prod_id;
        END;
        $$;
    """
    PRODUCT_SPECIFICATION = """
        CREATE OR REPLACE FUNCTION product_specification(root_prod integer)
            returns TABLE(
                pair_id bigint,
                parent_id bigint,
                child_id bigint,
                prod_num smallint,
                quantity double precision
            )
            language plpgsql
        as
        $$
        BEGIN
            RETURN QUERY
                WITH RECURSIVE r AS (
                    SELECT
                        pc.id AS pair_id,
                        pc.parent_prod_id AS parent_id,
                        pc.component_id AS child_id,
                        pc.num as prod_num,
                        pc.quantity AS quantity
                    FROM specifications_prodcomponent pc
                    WHERE pc.parent_prod_id = ROOT_PROD

                    UNION

                    SELECT
                        pc2.id AS pair_id,
                        pc2.parent_prod_id AS parent_id,
                        pc2.component_id AS child_id,
                        pc2.num as prod_num,
                        pc2.quantity AS quantity
                    FROM specifications_prodcomponent pc2
                            JOIN r ON pc2.parent_prod_id = r.child_id
                    WHERE pc2.num = r.prod_num
                )
                SELECT * FROM r;
        END;
        $$;
    """

    DROP_CHECK_CYCLE = "DROP FUNCTION check_class_struct_cycles(integer, integer);"
    DROP_DELETE_CLASS_AND_DESCENDANTS = "DROP FUNCTION delete_class_and_descendants(integer);"
    DROP_FIND_GR_GR = "DROP FUNCTION find_gr_gr(integer);"
    DROP_GET_TERMINAL_CLASSES = "DROP FUNCTION get_terminal_classes(integer);"
    DROP_ADD_PARAMETR_TO_CLASS = "DROP FUNCTION add_parametr_to_class(integer, integer, double precision, double precision);"
    DROP_IS_PARENT_PROD = "DROP FUNCTION is_parent_prod(integer);"
    DROP_TOTAL_COST_RATIO = "DROP FUNCTION total_cost_ratio(root_prod integer, num_of_products double precision);"
    DROP_GET_CHANGE_LOG = "DROP FUNCTION get_changelog(target_product_id integer);"
    DROP_CREATE_SPECIFICATION = "DROP FUNCTION create_specification(base_product_id integer, modified_product_name character varying, modified_product_short_name character varying);"
    DROP_PRODUCT_SPECIFICATION = "DROP FUNCTION product_specification(root_prod integer);"
