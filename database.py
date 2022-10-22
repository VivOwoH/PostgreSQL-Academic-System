#!/usr/bin/env python3

from typing import Callable, Union, List, Tuple
from modules import pg8000
import configparser
import datetime
import re

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
        connection = pg8000.connect(database=config['DATABASE']['database'],
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
# Academic Staff
#   1. List all the academicstaff (showing the id, name, department, address [but not the password or salary!]).
#   2. Allow the user to search for staff in a particular department.
#   3. One page should produce a report showing how many staff there are, in each department.
#   4. Allow the user to add a new academicstaff member to the dataset.
################################################################################

#   1. List all the academicstaff (showing the id, name, department, address [but not the password or salary!]).
def list_academicstaff():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if (conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        cur.execute("""Select id, name, deptid as department, address
                        from unidb.academicstaff
                        ORDER BY id""")
        val = cur.fetchall()
    except Exception as e:
        # If there were any errors, we print error details and return a NULL value
        print("Error fetching from database {}".format(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

#   2. Allow the user to search for staff in a particular department.
def search_academicstaff(deptid):
    # Only search using deptid: case insensitive
    # Get the database connection and set up the cursor
    conn = database_connect()
    conn.autocommit = True
    if (conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        cur.execute("""SELECT id, name, deptid 
                        FROM unidb.academicstaff
                        WHERE LOWER(deptid) = LOWER(%s)""", (deptid,))
        val = cur.fetchall()
        if val is None:
            return -1 # we cannot find this given unit
        
    except Exception as e:
        # If there were any errors, we print error details and return a NULL value
        print("Error fetching from database {}".format(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

#   3. One page should produce a report showing how many staff there are, in each department.
def count_academicstaff():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if (conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        cur.execute("""SELECT deptid, COUNT(id) as num_of_academicstaff
                        FROM unidb.academicstaff
                        GROUP BY deptid""")
        val = cur.fetchall()
    except Exception as e:
        # If there were any errors, we print error details and return a NULL value
        print("Error fetching from database {}".format(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

#   4. Allow the user to add a new academicstaff member to the dataset.
def add_academicstaff(staff_id, staff_name, deptid, password, address, salary):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if (conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        cur.execute("""INSERT INTO unidb.academicstaff
                        VALUES (%s, %s, %s, %s, %s, %s) 
                        RETURNING id, name, deptid, password""", (staff_id, staff_name, deptid, password, address, salary))
        
        val = cur.fetchall()
        conn.commit()
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
        cur.execute("""SELECT uoscode 
                        FROM UniDB.UnitOfStudy
                        WHERE LOWER(uoscode) = LOWER(%s)""", (uoscode,))
        val = cur.fetchall()
        if val is None or len(val) < 1:
            return -1 # invalid input: we cannot find this given unit

        cur.execute("""SELECT prohibuoscode
                    FROM UniDB.Prohibitions
                    WHERE %s = uoscode
                    AND prohibuoscode IN (SELECT uosCode
                                FROM UniDB.transcript
                                WHERE studid = %s AND grade != 'F')""", (uoscode,sid))
        val = cur.fetchall()
        if len(val) > 0:
            return 0 # have finished a unit that is in prohib list

        cur.execute("""SELECT prerequoscode
                    FROM UniDB.Requires
                    WHERE %s = uoscode
                    AND prerequoscode NOT IN (SELECT uosCode
                                FROM UniDB.transcript
                                WHERE studid = %s AND grade != 'F')""", (uoscode,sid))
        val = cur.fetchall()
        if len(val) > 0:
            return 0 # have not finished all prerequisites

        return 1 # pass both prohib and prereq check, can choose this unit

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
    # Get the database connection and set up the cursor
    conn = database_connect()
    if (conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        if uos == prereq:
            return val # reject same input as prerequisites
        cur.execute("""INSERT INTO UniDB.Requires
                        VALUES (%s, %s, CURRENT_DATE) 
                        RETURNING uoscode, prerequoscode""", (uos, prereq))
        val = cur.fetchall()
        conn.commit()
    except Exception as e:
        # If there were any errors, we print error details and return a NULL value
        print("Error fetching from database {}".format(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val
    

################################################################################
# Lectures
#   1. Display all lecture locations.
#   2. Enable the user to search for lectures at a specific time.
#   3. Produce a report illustrating how many classes take place in each room.
#   4. Provide functionality to add a new lecture to the dataset.
################################################################################

def lectures(func, **kwargs):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    val = None
    try:
        # Query => Listing all lectures
        if func == "list":
            cur.execute("""SELECT uoscode, uosname, semester, year, classtime, classroomid 
                            FROM unidb.lecture
                            JOIN unidb.unitofstudy 
                            USING (uoscode)
                            ORDER BY uoscode""")
            val = cur.fetchall()

        # Query => Counting number of lectures in each classroom
        if func == "count":
            cur.execute("""SELECT classroomid, COUNT(*) 
                            FROM unidb.lecture
                            GROUP BY classroomid
                            ORDER BY COUNT(*) 
                            DESC""")
            val = cur.fetchall()

        # Query => Enable the user to search classtimes
        if func == "search":
            time = kwargs['time'] # Access the optional dictionary
            if not ValidString.match(time) and time != "": 
                raise ValueError(f"Invalid code '{time}'")
            if time is not None: # If a time has been selected, return lectures that run at that classtime
                cur.execute("""SELECT uoscode, uosname, semester, year, classtime, classroomid 
                            FROM unidb.lecture
                            JOIN unidb.unitofstudy USING (uoscode)
                            WHERE classtime LIKE %s""", 
                            (time, ))
            else: # If time has not been selected, return all
                cur.execute("""SELECT uoscode, uosname, semester, year, classtime, classroomid 
                            FROM unidb.lecture
                            JOIN unidb.unitofstudy 
                            USING (uoscode)""")
            val = cur.fetchall()
        
        # Query => Return all unique classtimes
        if func == "timing":
            cur.execute("""SELECT classtime 
                            FROM unidb.lecture
                            GROUP BY classtime
                            ORDER BY classtime""")
            val = cur.fetchall()

        # Query => Return all unique classrooms
        if func == "classid_fkey":
            cur.execute("""SELECT classroomid 
                            FROM unidb.classroom
                            ORDER BY classroomid""")
            val = cur.fetchall()
        
        # Query => Return all unique lectures (uoscode-semester-year)
        if func == "uoscode_fkey":
            cur.execute("""SELECT uoscode, semester, year
                            FROM unidb.lecture
                            GROUP BY uoscode, semester, year
                            ORDER BY uoscode""")
            val = cur.fetchall()

        # Query => Add new classroom for an existing lecture
        if func == "add":
            code = kwargs['code']
            sem = kwargs['sem']
            year = kwargs['year']
            time = kwargs['time']
            id = kwargs['id']
            if not ValidString.match(code): raise ValueError(f"Invalid code '{code}'")
            if not ValidString.match(sem): raise ValueError(f"Invalid semester '{sem}'")
            if not NaturalNumber.match(year): raise ValueError(f"Invalid year '{year}'")
            if not ValidString.match(time): raise ValueError(f"Invalid code '{time}'")
            if not ValidString.match(id): raise ValueError(f"Invalid code '{id}'")
            success = True
            try:
                cur.execute(f"INSERT INTO unidb.lecture VALUES ('{code}', '{sem}', '{year}', '{time}', '{id}')")
                conn.commit()
            except Exception: 
                success = False
                cur.close()
                conn.close()
            return success

        # Extension: Query => Display lecture duration
        if func == "duration":
            cur.execute("""SELECT uoscode, semester, year, duration
                            FROM unidb.lecture lecture
                            JOIN unidb.duration duration
                            ON duration.uoscode = lecture.uoscode
                            AND duration.semester = lecture.semester
                            AND duration.year = lecture.year
                            """)
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

def connect() -> pg8000.Connection:
    config = configparser.ConfigParser()
    config.read('config.ini')
    return pg8000.connect(
        database=config['DATABASE']['database'],
        user=config['DATABASE']['user'],
        password=config['DATABASE']['password'],
        host=config['DATABASE']['host']
    )

DefaultResolver = lambda c: list(c.fetchall())
NaturalNumber = re.compile('^[1-9]+[0-9]*$')
ValidString = re.compile('^[A-z0-9_-]+$')

def execute_query(sql: str, resolver = DefaultResolver) -> Union[List[tuple], Tuple]:
    connection = connect()
    results = None
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        results = resolver(cursor)
        cursor.close()
    finally: connection.close()
    return results

def classroom_registry():
    return execute_query("SELECT classroomid, seats, type FROM unidb.classroom")

def classroom_summary():
    return execute_query("SELECT type, COUNT(*) FROM unidb.classroom GROUP BY type")

def search_classroom(seats: str):
    if not NaturalNumber.match(seats): raise ValueError(f"Invalid number of seats '{seats}'")
    return execute_query(f"SELECT classroomid, seats, type FROM unidb.classroom WHERE seats > {seats}")

def add_classroom(classroom_id: str, seats: str, classroom_type: str):
    if not ValidString.match(classroom_id): raise ValueError(f"Invalid classroom identifier '{classroom_id}'")
    if not NaturalNumber.match(seats): raise ValueError(f"Invalid number of seats '{seats}'")
    if classroom_type != '' and not ValidString.match(classroom_type):
        raise ValueError(f"Invalid type of classroom '{classroom_type}'")

    connection = connect()
    cursor = connection.cursor()
    try: 
        cursor.execute(f"INSERT INTO unidb.classroom VALUES ('{classroom_id}', {seats}, '{classroom_type}')")
        connection.commit()
    except pg8000.ProgrammingError as error:
        if error.args[2] == '22001': raise ValueError('Classroom type exceeds 7 letter limit')
        if error.args[2] == '23505': raise ValueError('Classroom with id already exists')
        raise error
    finally:
        connection.close()
        cursor.close()

################################################################################
# Announcements
################################################################################


class Announcement:
    def __init__(self, row: Tuple[str, datetime.datetime, str, str, str, str]):
        self.title = row[0]
        self.date = row[1].strftime("%A %B %d %H:%M:%S %Y")
        self.author = row[2]
        self.unitCode = row[3]
        self.unitName = row[4]
        self.details = row[5].replace('\\n', '\n')

def list_announcements(semester: str, year: str) -> List[Announcement]:
    if not NaturalNumber.match(semester): raise ValueError(f"Invalid semester '{semester}'")
    if not NaturalNumber.match(year): raise ValueError(f"Invalid year '{year}'")
    sql_query = f"""
    SELECT title, date, name as author, uoSCode as code, uosname as unit, details
      FROM unidb.Announcement as A                                               
        INNER JOIN unidb.UnitOfStudy as U USING (uoScode)                        
        INNER JOIN unidb.AcademicStaff ON (author = id)                          
    WHERE CASE                              
      WHEN {semester} = 1 THEN EXTRACT(month FROM date) <= 7                
      WHEN {semester} = 2 THEN EXTRACT(month FROM Date) >= 7                
      ELSE TRUE                                                                  
    END AND EXTRACT(year FROM date) = {year}
    ORDER BY date DESC, title ASC, code ASC
    """
    return [ Announcement(row) for row in execute_query(sql_query) ]

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
