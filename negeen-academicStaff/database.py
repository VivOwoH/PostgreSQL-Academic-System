#!/usr/bin/env python3

from modules import pg8000
import configparser
import sys
import random


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
        'y22s2i2120_weha7612'
        connect(database='y12i2120_unikey',
            host='soitpw11d59.shared.sydney.edu.au',
            password='pB5N2jyA',
            user='y22s2i2120_ndau3314')
        '''
        connection = pg8000.connect(database='y22s2i2120_weha7612',
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
    if(conn is None):
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
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute(""" SELECT uosCode, uosName, credits, year, semester
                        FROM unidb.UoSOffering JOIN unidb.UnitOfStudy USING (uosCode)
                        ORDER BY uosCode, year, semester""")
        val = cur.fetchall()
    except Exception as e:
        # If there were any errors, we print something nice and return a NULL value
        print(e)
        print("Error fetching from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

################################################################################
# List Academic Staff
#   - This function performs a "SELECT" from the database to get the academic
#       staff information.
################################################################################

def list_academic_staff():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    staff_and_units = {}
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT id, name, deptid, address
                        FROM UniDB.AcademicStaff
                        ORDER BY name, deptid""")
        val = cur.fetchall()
        for staff in val:
            staff_and_units[tuple(staff)] = get_staff_unit(staff[1])
        print(staff_and_units)
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val, staff_and_units

def list_tutors():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    tutors_and_units = {}
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT tutorid, tutorname, studentid, deptid
                        FROM UniDB.Tutor join UniDB.TutorUOSO ON (tutorid = tutor) join UniDB.UnitOfStudy USING (UOSCode)
                        ORDER BY tutorname, uoscode""")
        val = cur.fetchall()
        for tutor in val:
            tutors_and_units[tuple(tutor)] = get_tutor_unit(tutor[1])
        print(tutors_and_units)
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val, tutors_and_units

def get_staff_unit(staff):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT uoscode, uosname, semester, year
                        FROM UniDB.AcademicStaff join UniDB.UOSOffering on (id = instructorid) join UniDB.UnitOfStudy using (uoscode)
                        WHERE name = %s
                        ORDER BY uosCode, year, semester""", (staff,))
        val = cur.fetchall()
        
    except Exception as e:
        # If there were any errors, we print something nice and return a NULL value
        print(e)
        print("Error fetching from database")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

def get_tutor_unit(tutor):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT uoscode, uosname, semester, year
                        FROM UniDB.Tutor join UniDB.TutorUOSO ON (tutorid = tutor) join UniDB.UnitOfStudy USING (UOSCode)
                        WHERE tutorname = %s
                        ORDER BY tutorname, uoscode""", (tutor,))
        val = cur.fetchall()
    except Exception as e:
        # If there were any errors, we print something nice and return a NULL value
        print(e)
        print("Error fetching from database")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val


################################################################################
# List Staff By Department
#   - This function performs a "SELECT" from the database to get the academic
#       staff information.
################################################################################

def staff_by_department():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # column ordering is IMPORTANT
        cur.execute("""SELECT deptid, count(*) as yeet
                        from UniDB.AcademicStaff
                        group by deptid
                        order by yeet desc""")
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")

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
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT uosCode, uosName, credits, year, semester, grade
                        FROM UniDB.Transcript NATURAL JOIN UniDB.UnitOfStudy
                        WHERE studid = %s
                        ORDER BY uosCode, year, semester""", (sid,))
        val = cur.fetchall()
    except Exception as e:
        # If there were any errors, we print something nice and return a NULL value
        print(e)
        print("Error fetching from database")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val


################################################################################
# Generate unique Staff ID
################################################################################
def generate_id():
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        cur.execute("""select id from unidb.academicstaff""")
        val = cur.fetchall()
        valid = False
        while valid == False:
            staffid = ''
            i = 0
            while i < 7:
                num = str(random.randint(0, 9))
                staffid += num
                i += 1
            for ls in val:
                if staffid == ls[0].strip():
                    continue
            valid = True
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error")
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return staffid

################################################################################
# List Staff in a Department
#   - This function performs a "SELECT" from the database to get the academic
#       staff information from a specific Department.
################################################################################
def find_staff_by_department(searchterm):
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        cur.execute("""SELECT id, name, address
                    FROM UniDB.AcademicStaff
                    WHERE lower(deptID) = lower(%s)
                    ORDER BY name""", (searchterm,))
        val = cur.fetchall()
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Staff from this department:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

################################################################################
# Add Staff Function
#   - This function performs a "INSERT" to the database to add a new staff 
#       member with the same information given
################################################################################
def add_staff(name,department,temppass,address,salary):
    staff_id = generate_id()
    sql = """INSERT INTO unidb.academicstaff VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, name, deptid, password, address, salary;"""
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()    
    val = None
    try:
        # execute the INSERT statement
        cur.execute(sql, (staff_id, name, department, temppass, address, salary))
        # get the generated id back
        val = cur.fetchall()
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a staff member:", sys.exc_info()[0])
        raise    
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

#####################################################
#  Python code if you run it on it's own as 2tier
#####################################################


if (__name__ == '__main__'):
    print("{}\n{}\n{}".format("=" * 50, "Welcome to the 2-Tier Python Database", "=" * 50))
    print("""
This file is to interact directly with the database.
We're using the unidb (make sure it's in your database)

Try to execute some functions:
check_login('3070799133', 'random_password')
check_login('3070088592', 'Green')
list_units()""")

