import psycopg2

# Function to insert variables into the table
def insert_into_function_table(function_name, api_name):
    # Connection parameters - replace these with your database connection info
    # Connection parameters
    dbname = "Project"
    user = "postgres"
    password = "hunt"
    host = "localhost"  # localhost if it's running on your local machine
    port = "5432"  # default PostgreSQL port

    # Establishing the connection
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    
    # Create a new cursor
    cur = conn.cursor()

    
    # SQL statement to check for the value
    sql_query = """SELECT EXISTS(SELECT 1 FROM public."API" WHERE api_name = %s);"""
    # Execute the SQL statement
    cur.execute(sql_query, (api_name,))

    # Fetch the result
    exists = cur.fetchone()[0]

    if exists:
        
        # SQL statement to check for the function_name
        sql_query = """SELECT EXISTS(SELECT 1 FROM public."function" WHERE function_name = %s);"""
        cur.execute(sql_query, (function_name,))
        exists_in_function_table = cur.fetchone()[0]

        if not (exists_in_function_table):
            # SQL statement for inserting data
            sql_insert_query = """
            INSERT INTO public."function" (function_name, api_name)
            VALUES (%s, %s);
            """
            
            try:
                # Execute the SQL statement with provided variables
                cur.execute(sql_insert_query, (function_name, api_name))
                
                # Commit the changes
                conn.commit()
                print(f"{function_name} inserted successfully into function table\n")
                
            except Exception as e:
                # Rollback in case there is any error
                conn.rollback()
                print(f"An error occurred: {e}")
                
        else:
            print(f"{function_name} already inserted in table \n")
    else:
        print(f"{api_name} does not exist \n")


    cur.close()
    conn.close()


# Function to insert variables into the table
def insert_into_API_function_specific_table(function_name, api_name, api_context, api_topic, function_context,  function_topic, llm_expert_API, sim_expert_API, llm_expert_function, sim_expert_function):
    # Connection parameters
    dbname = "Project"
    user = "postgres"
    password = "hunt"
    host = "localhost"  # localhost if it's running on your local machine
    port = "5432"  # default PostgreSQL port

    # Establishing the connection
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    
    # Create a new cursor
    cur = conn.cursor()

    # SQL statement to check for the value
    sql_query = """SELECT EXISTS(SELECT 1 FROM public."function" WHERE function_name = %s);"""
    # Execute the SQL statement
    cur.execute(sql_query, (function_name,))

    # Fetch the result
    exists = cur.fetchone()[0]

    if exists:
        # SQL statement for inserting data
        sql_insert_query = """
        INSERT INTO public."API_function_specific" (function_name, api_name, api_context, api_topic, function_context, function_topic, llm_expert_API, sim_expert_API, llm_expert_function, sim_expert_function)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        # SQL statement to check for the function_name
        sql_query = """SELECT EXISTS(SELECT 1 FROM public."API_function_specific" WHERE function_name = %s);"""
        cur.execute(sql_query, (function_name,))
        exists_in_function_table = cur.fetchone()[0]

        if not (exists_in_function_table):
            
            try:
                # Execute the SQL statement with provided variables
                cur.execute(sql_insert_query, (function_name, api_name, api_context, api_topic, function_context,  function_topic, llm_expert_API, sim_expert_API, llm_expert_function, sim_expert_function))
                
                # Commit the changes
                conn.commit()
                print(f"{function_name} inserted successfully into API_function_specific table\n")
                        
            except Exception as e:
                # Rollback in case there is any error
                conn.rollback()
                print(f"An error occurred: {e}")
        else: print(f"{function_name} is already inserted in table")

    else:
        print("No function_name found in function table \n")

    cur.close()
    conn.close()


# Function to insert variables into the table
def wipeDB():
    # Connection parameters - replace these with your database connection info
    # Connection parameters
    dbname = "Project"
    user = "postgres"
    password = "hunt"
    host = "localhost"  # localhost if it's running on your local machine
    port = "5432"  # default PostgreSQL port

    # Establishing the connection
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    
    # Create a new cursor
    cur = conn.cursor()

    # SQL statement to delete all rows
    sql_delete_query = f"""DELETE FROM public."function";"""
    
    try:
        # Execute the SQL statement
        cur.execute(sql_delete_query)
        # Commit the changes to the database
        conn.commit()
        
    except Exception as e:
        # If an error occurs, print the error and rollback any changes
        conn.rollback()
        print(f"An error occurred: {e}")
    
        # SQL statement to delete all rows
    sql_delete_query = f"""DELETE FROM public."API_function_specific";"""
    
    try:
        # Execute the SQL statement
        cur.execute(sql_delete_query)
        # Commit the changes to the database
        conn.commit()
        
    except Exception as e:
        # If an error occurs, print the error and rollback any changes
        conn.rollback()
        print(f"An error occurred: {e}")

    cur.close()
    conn.close()
