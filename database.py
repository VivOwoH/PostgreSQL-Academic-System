#!/usr/bin/env python3

from typing import Callable, Union, List, Tuple
from modules import pg8000
import configparser


################################################################################
# Connect to the database
#   - This function reads the config file and tries to connect
#   - This is the main "connection" function used to set up our connection
################################################################################

def database_connect():
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create a connection to the database
    connection = None
    try:
        '''
        This is doing a couple of things in the back
        what it is doing is:

        connect(database='y12i2120_unikey',
            host='soit-db-pro-2.ucc.usyd.edu.au,
            password='password_from_config',
            user='y19i2120_unikey')
        '''
        connection = pg8000.connect(database=config['DATABASE']['user'],
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    except Exception as e:
        print(e)

    # Return the connection to use
    return connection

################################################################################
# Login Function
#   - This function performs a "SELECT" from the database to check for the
#       student with the same unikey and password as given.
#   - Note: This is only an exercise, there's much better ways to do this
################################################################################

def check_login(sid, pwd):
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT *
                 FROM unidb.student
                 WHERE studid=%s AND password=%s"""
        cur.execute(sql, (sid, pwd))
        r = cur.fetchone()              # Fetch the first row
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error Invalid Login")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


################################################################################
# List Units
#   - This function performs a "SELECT" from the database to get the unit
#       of study information.
#   - This is useful for your part when we have to make the page.
################################################################################

def list_units():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if (conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT uosCode, uosName, credits, year, semester
                        FROM UniDB.UoSOffering JOIN UniDB.UnitOfStudy USING (uosCode)
                        ORDER BY uosCode, year, semester""")
        val = cur.fetchall()
    except Exception as e:
        # If there were any errors, we print error details and return a NULL value
        print("Error fetching from database {}".format(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val


################################################################################
# Get transcript function
#   - Your turn now!
#   - What do you have to do?
#       1. Connect to the database and set up the cursor.
#       2. You're given an SID - get the transcript for the SID.
#       3. Close the cursor and the connection.
#       4. Return the information we need.
################################################################################

def get_transcript(sid):
    # TODO
    # Get the students transcript from the database
    # You're given an SID as a variable 'sid'
    # Return the results of your query :)
    conn = database_connect()
    if (conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        cur.execute("""SELECT uosCode, uosName, credits, year, semester, grade
                        FROM UniDB.transcript JOIN UniDB.UnitOfStudy USING (uosCode)
                        WHERE studid = %s
                        ORDER BY uosCode, year, semester""", (sid,))
        val = cur.fetchall()
    except Exception as e:
        # If there were any errors, we print error details and return a NULL value
        print("Error fetching from database {}".format(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val


################################################################################
# Prerequisites
#   1. UoSCodes	and	names of the two units,	and enforce date
#   2. Allow user to search for all the units which are prerequisites of a given unit.
#   3. Produce a report showing how many prerequisites there are, for each unit of study
#   4. Allow user to add a new (prerequities, unit) pair to the dataset
################################################################################

# run query function
def query_result(sql):
     # Get the database connection and set up the cursor
    conn = database_connect()
    if (conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        cur.execute(sql)
        val = cur.fetchall()
        conn.commit()
    except Exception as e:
        # If there were any errors, we print error details and return a NULL value
        print("Error fetching from database {}".format(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

# Extension: prohibitions table -> list prohibition + check uos eligibility
def list_prohibitions():
    list_sql = """SELECT DISTINCT a.uoscode, a.uosname, a.prohibuoscode, b.prohibuosname, a.enforcedsince
                        FROM (SELECT uoscode, uosname, prohibuoscode, enforcedsince
                                FROM UniDB.Prohibitions NATURAL JOIN UniDB.UnitOfStudy) a
                        Join
                            (SELECT prohibuoscode, uosname as prohibuosname, enforcedsince
                                FROM UniDB.Prohibitions JOIN UniDB.UnitOfStudy A ON (prohibuoscode=A.uoscode)) b 
	                    ON a.prohibuoscode = b.prohibuoscode AND a.enforcedsince=b.enforcedsince
						ORDER BY a.uoscode, a.prohibuoscode"""
    return query_result(list_sql)

def check_uos_eligibility(uoscode, sid):
    # Get the database connection and set up the cursor
    conn = database_connect()
    conn.autocommit = True
    if (conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        cur.execute("""SELECT prohibuoscode
                    FROM UniDB.Prohibitions
                    WHERE %s = uoscode
                    AND prohibuoscode IN (SELECT uosCode
                                FROM UniDB.transcript
                                WHERE studid = %s AND grade != 'F')""", (uoscode,sid))
        val = cur.fetchall()
        if len(val) > 0:
            return False # have finished a unit that is in prohib list

        cur.execute("""SELECT prerequoscode
                    FROM UniDB.Requires
                    WHERE %s = uoscode
                    AND prerequoscode NOT IN (SELECT uosCode
                                FROM UniDB.transcript
                                WHERE studid = %s AND grade != 'F')""", (uoscode,sid))
        val = cur.fetchall()
        if len(val) > 0:
            return False # have not finished all prerequisites

        return True # pass both prohib and prereq check, can choose this unit

    except Exception as e:
        # If there were any errors, we print error details and return a NULL value
        print("Error fetching from database {}".format(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val
    

#   1. UoSCodes	and	names of the two units,	and enforce date
def list_prerequisites():
    list_sql = """SELECT DISTINCT a.uoscode, a.uosname, a.prerequoscode, b.prerequosname, a.enforcedsince
                        FROM (SELECT uoscode, uosname, prerequoscode, enforcedsince
                                FROM UniDB.Requires NATURAL JOIN UniDB.UnitOfStudy) a
                        Join
                            (SELECT prerequoscode, uosname as prerequosname, enforcedsince
                                FROM UniDB.Requires JOIN UniDB.UnitOfStudy A ON (prerequoscode=A.uoscode)) b 
	                    ON a.prerequoscode = b.prerequoscode AND a.enforcedsince=b.enforcedsince
						ORDER BY a.uoscode, a.prerequoscode"""
    return query_result(list_sql)

#   2. Allow user to search for all the units which are prerequisites of a given unit.
def search_prerequisites(uoscode):
    # Only search using uoscode: case insensitive
    # Get the database connection and set up the cursor
    conn = database_connect()
    conn.autocommit = True
    if (conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        cur.execute("""SELECT uoscode 
                        FROM UniDB.UnitOfStudy
                        WHERE LOWER(uoscode) = LOWER(%s)""", (uoscode,))
        val = cur.fetchall()
        if val is None or len(val) < 1:
            return -1 # we cannot find this given unit

        cur.execute("""SELECT prerequoscode, B.uosname as prerequosname, enforcedsince
                        FROM UniDB.Requires A JOIN UniDB.UnitOfStudy B ON (prerequoscode=B.uoscode)
                        WHERE LOWER(A.uoscode) = LOWER(%s)""", (uoscode,))
        val = cur.fetchall()
    except Exception as e:
        # If there were any errors, we print error details and return a NULL value
        print("Error fetching from database {}".format(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val


#   3. Produce a report showing how many prerequisites there are, for each unit of study
def report_prerequisites():
    count_sql = """SELECT uoscode, COUNT(prerequoscode) as num_of_prerequisites
                        FROM UniDB.Requires
                        GROUP BY uoscode"""
    return query_result(count_sql)


#   4. Allow user to add a new (prerequities, unit) pair to the dataset
# (uoscode, prereqcode) -> must be in unitOfStudy table already
def add_prerequisites(uos, prereq):
    add_sql = """INSERT INTO UniDB.Requires
                        VALUES (%s, %s, CURRENT_DATE) 
                        RETURNING uoscode, prerequoscode""", (uos, prereq)
    return query_result(add_sql)
    

################################################################################
# Lectures
################################################################################

def lectures(func, **kwargs):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:

        if func == "list":
            cur.execute("""SELECT uoscode, uosname, semester, year, classtime, classroomid 
                            FROM unidb.lecture
                            JOIN unidb.unitofstudy 
                            USING (uoscode)""")
            val = cur.fetchall()

        if func == "count":
            cur.execute("""SELECT classroomid, COUNT(*) 
                            FROM unidb.lecture
                            GROUP BY classroomid
                            ORDER BY COUNT(*) 
                            DESC""")
            val = cur.fetchall()

        if func == "search":
            time = kwargs['time']
            if time != "" and time is not None:
                cur.execute("""SELECT uoscode, uosname, semester, year, classtime, classroomid 
                            FROM unidb.lecture
                            JOIN unidb.unitofstudy USING (uoscode)
                            WHERE classtime LIKE %s""", 
                            (time, ))
            else:
                cur.execute("""SELECT uoscode, uosname, semester, year, classtime, classroomid 
                            FROM unidb.lecture
                            JOIN unidb.unitofstudy 
                            USING (uoscode)""")
            val = cur.fetchall()
        
        if func == "timing":
            cur.execute("""SELECT classtime 
                            FROM unidb.lecture
                            GROUP BY classtime
                            ORDER BY classtime""")
            val = cur.fetchall()

        if func == "add":
            flag = True
            for k, v in kwargs.items():
                if kwargs[k] is None or kwargs[k] == "":
                    flag = False
            if flag == True:
                code = kwargs['code']
                sem = kwargs['sem']
                year = kwargs['year']
                time = kwargs['time']
                id = kwargs['id']
                cur.execute("""INSERT INTO lecture 
                                VALUES (
                                    %s
                                    %s
                                    %s
                                    %s
                                    %s
                                )""", 
                            (code, sem, year, time, id))
            else:
                cur.execute("""SELECT uoscode, uosname, semester, year, classtime, classroomid 
                            FROM unidb.lecture
                            JOIN unidb.unitofstudy 
                            USING (uoscode)""")
            val = cur.fetchall()

    except Exception as e:
        # If there were any errors, we print error details and return a NULL value
        print("Error fetching from database {}".format(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

################################################################################
# Classrooms
################################################################################

# helper functions to execute queries and mutations

DefaultResolver = lambda c: list(c.fetchall())

def connect() -> pg8000.Connection:
    config = configparser.ConfigParser()
    config.read('config.ini')
    return pg8000.connect(
        database=config['DATABASE']['user'],
        user=config['DATABASE']['user'],
        password=config['DATABASE']['password'],
        host=config['DATABASE']['host']
    )

def execute_query(sql: str, resolver = DefaultResolver) -> Union[List[tuple], Tuple]:
    # attempt to connect and then attempt to execute the provided query
    connection = connect()
    cursor = connection.cursor()
    cursor.execute(sql)
    results = resolver(cursor)

    # close the connection to the database before returning the results
    cursor.close()
    connection.close()
    return results

def classroom_registry():
    return execute_query("SELECT classroomid, seats, type FROM unidb.classroom")

def classroom_summary():
    return execute_query("SELECT type, COUNT(*) FROM unidb.classroom GROUP BY type")

def search_classroom(seats: int):
    return execute_query(f"SELECT classroomid, seats, type FROM unidb.classroom WHERE seats > {seats}")

def add_classroom(classroom_id: str, seats: int, classroom_type: str) -> bool:
    connection = connect()
    cursor = connection.cursor()
    success = True
    try: 
        cursor.execute(f"INSERT INTO unidb.classroom VALUES ('{classroom_id}', {seats}, '{classroom_type}')")
        connection.commit()
    except Exception: success = False

    connection.close()
    cursor.close()
    return success


#####################################################
#  Python code if you run it on it's own as 2tier
#####################################################


if (__name__ == '__main__'):
    print("{}\n{}\n{}".format(
        "=" * 50, "Welcome to the 2-Tier Python Database", "=" * 50))
    print("""
This file is to interact directly with the database.
We're using the unidb (make sure it's in your database)

Try to execute some functions:
check_login('3070799133', 'random_password')
check_login('3070088592', 'Green')
list_units()""")
