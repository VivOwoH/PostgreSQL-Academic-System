# Importing the Flask Framework

from typing import Union, List, Tuple
from modules import *
from flask import *
import database
import configparser
import datetime


page = {}
session = {}

# Initialise the FLASK application
app = Flask(__name__)
app.secret_key = 'SoMeSeCrEtKeYhErE'


# Debug = true if you want debug output on error ; change to false if you dont
app.debug = True


# Read my unikey to show me a personalised app
config = configparser.ConfigParser()
config.read('config.ini')
unikey = config['DATABASE']['user']
portchoice = config['FLASK']['port']

#####################################################
##  INDEX
#####################################################

def coalesce(string: Union[str, None], default: str = '') -> str:
    return string if string != None else default

# What happens when we go to our website
@app.route('/')
def index():
    # If the user is not logged in, then make them go to the login page
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('newsfeed'))

################################################################################
# Login Page
################################################################################

# This is for the login
# Look at the methods [post, get] that corresponds with form actions etc.
@app.route('/login', methods=['POST', 'GET'])
def login():
    page = {'title' : 'Login', 'unikey' : unikey}
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get our login value
        val = database.check_login(request.form['sid'], request.form['password'])

        # If our database connection gave back an error
        if(val == None):
            flash("""Error with the database connection. Please check your terminal
            and make sure you updated your INI files.""")
            return redirect(url_for('login'))

        # If it's null, or nothing came up, flash a message saying error
        # And make them go back to the login screen
        if(val is None or len(val) < 1):
            flash('There was an error logging you in')
            return redirect(url_for('login'))
        # If it was successful, then we can log them in :)
        session['name'] = val[1]
        session['sid'] = request.form['sid']
        session['logged_in'] = True
        return redirect(url_for('index'))
    else:
        # Else, they're just looking at the page :)
        if('logged_in' in session and session['logged_in'] == True):
            return redirect(url_for('index'))
        return render_template('index.html', page=page)


################################################################################
# Logout Endpoint
################################################################################

@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You have been logged out')
    return redirect(url_for('index'))


################################################################################
# Transcript Page
################################################################################

@app.route('/transcript')
def transcript():
    # TODO
    # Now it's your turn to add to this ;)
    # Good luck!
    #   Look at the function below
    #   Look at database.py
    #   Look at units.html and transcript.html
    transcript = database.get_transcript(session['sid'])
    
    if (transcript is None):
        # Set it to an empty list and show error message
        transcript = []
        flash('Error, there are no transcript')
    page['title'] = 'Transcript'
    return render_template('transcript.html', page=page, session=session, transcript=transcript)


################################################################################
# List Units page
################################################################################

# List the units of study
@app.route('/list-units')
def list_units():
    # Go into the database file and get the list_units() function
    units = database.list_units()

    # What happens if units are null?
    if (units is None):
        # Set it to an empty list and show error message
        units = []
        flash('Error, there are no units of study')
    page['title'] = 'Units of Study'
    return render_template('units.html', page=page, session=session, units=units)


################################################################################
# Academic Staff page
################################################################################

# List all the academicstaff [but not the password or salary!]).
@app.route('/academicstaff/list-academicstaff')
def list_academicstaff():
    # Go into the database file and get the list_academicstaff() function
    academicstaff = database.list_academicstaff()

    if (academicstaff is None):
        # Set it to an empty list and show error message
        academicstaff = []
        flash('Error, there are no staff')
    page['title'] = 'Academic Staff'
    return render_template('academicstaff/list-academicstaff.html', page=page, 
                        session=session, academicstaff=academicstaff)

# Seach for all academicstaff in the department
@app.route('/academicstaff/search-academicstaff')
def search_academicstaff():
    academicstaff = []
        # Get use input deptid value
    dept = request.args.get('department')
    print(dept)
    academicstaff = database.search_academicstaff(dept)
    if (academicstaff is None or academicstaff == -1):
        # Set it to an empty list and show error message
        academicstaff = []
        flash('Error, there are no academic staff with that department name')
     
    page['title'] = 'Search Academic Staff'
    return render_template('academicstaff/search-academicstaff.html', page=page, 
                                    session=session, academicstaff=academicstaff)

# Count Academic Stuff
@app.route('/academicstaff/count-academicstaff')
def count_academicstaff():
    academicstaff = database.count_academicstaff()

    if (academicstaff is None):
        # Set it to an empty list and show error message
        academicstaff = []
        flash('Error, there are no staff')
    page['title'] = 'Count Academic Staff'
    return render_template('/academicstaff/count-academicstaff.html', page=page, session=session, academicstaff=academicstaff)

# add a new academicstaff member to the dataset
@app.route('/academicstaff/add-academicstaff', methods=['POST', 'GET'])
def add_academicstaff():
    academicstaff = []
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        entry = database.add_academicstaff(request.form['id'], request.form['name'], request.form['deptid'], request.form['password'], request.form['address'], request.form['salary'] )

        if (entry is None):
            flash('Academic Staff is not added')
            return redirect(url_for('add_academicstaff'))
        #flash('A new prerequisite {} is added for {}'.format(entry[0][1], entry[0][0]))
        return redirect(url_for('list_academicstaff'))
    
    else:
        page['title'] = 'Add Academic Staff'
        return render_template('/academicstaff/add-academicstaff.html', page=page, 
                                    session=session)

# Extensions for academic staff page 
# List all the academicstaff and their salary
@app.route('/academicstaff/salary-academicstaff')
def salary_academicstaff():
    # Go into the database file and get the list_academicstaff() function
    academicstaff = database.salary_academicstaff()

    if (academicstaff is None):
        # Set it to an empty list and show error message
        academicstaff = []
        flash('Error, there are no staff')
    page['title'] = 'Salary Academic Staff'
    return render_template('academicstaff/salary-academicstaff.html', page=page, 
                        session=session, academicstaff=academicstaff)
    
################################################################################
# Prerequisites page
################################################################################

# List the prerequisite units
@app.route('/prerequisites/list-prerequisites')
def list_prerequisites():
    # Go into the database file and get the list_prerequisites() function
    prerequisites = database.list_prerequisites()

    if (prerequisites is None):
        # Set it to an empty list and show error message
        prerequisites = []
        flash('Error, there are no prerequisites')
    page['title'] = 'Prerequisites'
    return render_template('/prerequisites/prerequisites.html', page=page, 
                        session=session, prerequisites=prerequisites)

# Seach for all prerequisites of a unit
@app.route('/prerequisites/search-prerequisites', methods=['POST', 'GET'])
def search_prerequisites():
    prerequisites = []
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get use input uoscode value
        prerequisites = database.search_prerequisites(request.form['uoscode'])

        # If our database connection gave back code -1
        if(prerequisites == -1):
            flash("We cannot find this unit. Check the list below for available unit.")
            return redirect(url_for('list_units'))

        else:
            if (prerequisites is None):
                # Set it to an empty list and show error message
                prerequisites = []
                flash('Error, there are no prerequisites')
            elif (prerequisites == ()): # no prerequisites
                prerequisites = []
                flash('There are no prerequisites for the given unit')
            page['title'] = 'Search prerequisites'
            return render_template('/prerequisites/searchPrerequisites.html', page=page, 
                                    session=session, prerequisites=prerequisites)
    else:
        page['title'] = 'Search prerequisites'
        return render_template('/prerequisites/searchPrerequisites.html', page=page, 
                                    session=session, prerequisites=prerequisites)

# Report the number of prerequisite for each UOS
@app.route('/prerequisites/report-prerequisites')
def report_prerequisites():
    # Go into the database file and get the list_prerequisites() function
    prerequisites = database.report_prerequisites()

    if (prerequisites is None):
        # Set it to an empty list and show error message
        prerequisites = []
        flash('There are no UOS entries')
    page['title'] = 'Report prerequisites'
    return render_template('/prerequisites/reportPrerequisites.html', page=page, 
                        session=session, prerequisites=prerequisites)

# Add a new pair of prerequisites
@app.route('/prerequisites/add-prerequisites', methods=['POST', 'GET'])
def add_prerequisites():
    prerequisites = []
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get use input uoscode value
        entry = database.add_prerequisites(request.form['uos'], request.form['prereq'])

        if (entry is None):
            flash('Prerequisite not added')
            return redirect(url_for('add_prerequisites'))
        flash('A new prerequisite {} is added for {}'.format(entry[0][1], entry[0][0]))
        return redirect(url_for('list_prerequisites'))
    
    else:
        page['title'] = 'Add prerequisites'
        return render_template('/prerequisites/addPrerequisites.html', page=page, 
                                    session=session)

# List all prohibitions
@app.route('/prerequisites/list-prohibitions')
def list_prohibitions():
    # Go into the database file and get the list_prerequisites() function
    prohibitions = database.list_prohibitions()

    if (prohibitions is None):
        # Set it to an empty list and show error message
        prohibitions = []
        flash('Error, there are no prohibitions')
    page['title'] = 'Prohibitions'
    return render_template('/prerequisites/prohibitions.html', page=page, 
                        session=session, prohibitions=prohibitions)

# Check unit eligibility
@app.route('/prerequisites/check_uos_eligibility', methods=['POST', 'GET'])
def check_uos_eligibility():
    prerequisites = []
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get use input uoscode value
        check_result = database.check_uos_eligibility(request.form['uoscode'], session['sid'])

        if (check_result == -1):
            flash("We cannot find this unit. Check the list below for available unit.")
            return redirect(url_for('list_units'))
            
        elif(check_result == 0):
            flash("You are not eligible to choose this unit. Check Prerequisites and Prohibitions requirement.")
            return redirect(url_for('check_uos_eligibility'))

        elif (check_result == 1):
            flash('You can choose this UOS.')
            return redirect(url_for('check_uos_eligibility'))
    else:
        page['title'] = 'Search prerequisites'
        return render_template('/prerequisites/checkUOSEligibility.html', page=page, session=session)

                                    
################################################################################
# Lectures
################################################################################

# List lectures
@app.route('/lectures/list-lectures')
def list_lectures():
    lectures = database.lectures("list")

    if (lectures is None):
        # Set it to an empty list and show error message
        lectures = []
        flash('Error, there are no lectures')
    page['title'] = 'Lectures'
    return render_template('/lectures/list-lectures.html', page=page, session=session, lectures=lectures)

# Count lectures
@app.route('/lectures/count-lectures')
def count_lectures():
    lectures = database.lectures("count")

    if (lectures is None):
        # Set it to an empty list and show error message
        lectures = []
        flash('Error, there are no lectures')
    page['title'] = 'Count Lectures'
    return render_template('/lectures/count-lectures.html', page=page, session=session, lectures=lectures)

# Add lectures
@app.route('/lectures/add-lectures')
def add_lectures():
    # Retrieve existing lectures
    lectures = []
    classid_fkey = database.lectures('classid_fkey')
    uoscode_fkey = database.lectures('uoscode_fkey')
    timing = database.lectures('timing')
    try: 
        codeSemYear = request.args.get('code').split('-') 
        dict = {
            'code':codeSemYear[0],
            'sem':codeSemYear[1],
            'year':codeSemYear[2],
            'time':request.args.get('time'),
            'id':request.args.get('id')
            }
        if database.lectures("add", **dict):
            flash(f"Successfully Added New Lecture '{dict['code']}' '{dict['sem']}' '{dict['year']}' '{dict['time']}' '{dict['id']}'")
        else:
            flash(f"Could Not Add New Lecture '{dict['code']}' '{dict['sem']}' '{dict['year']}' '{dict['time']}' '{dict['id']} - You Cannot Have The Same Lecture In The Same Classroom Location (Albeit Different Times)'")
    except Exception as e:
        # This occurs on page refresh
        pass
    if (lectures is None):
        # Set it to an empty list and show error message
        lectures = []
        flash('Error, there are no lectures')
    page['title'] = 'Lectures'
    return render_template('/lectures/add-lectures.html', page=page, session=session, lectures=lectures, classid_fkey=classid_fkey, uoscode_fkey=uoscode_fkey, timing=timing)

# Search lectures
@app.route('/lectures/search-lectures')
def search_lectures():
    timing = database.lectures('timing')
    # print(timing)
    time = {'time':request.args.get('time')}
    print(time)
    lectures = database.lectures('search', **time)
    if (lectures is None):
        # Set it to an empty list and show error message
        lectures = []
        flash('Error, there are no lectures')
    page['title'] = 'Lectures'
    return render_template('/lectures/search-lectures.html', page=page, session=session, lectures=lectures, timing=timing)

################################################################################
# Classrooms
################################################################################

# list all of the classrooms stored in the database
@app.route('/classroom/registry')
def classroom_registry():
    # attempt to retrieve the classroom registry from the database
    classrooms = []
    try:
        classrooms = database.classroom_registry()
    except Exception as e: flash('Error accessing the classroom registry')

    # prepare the template to display for the page
    page['title'] = 'Classroom Registry'
    return render_template('/classrooms/classroom-registry.html', page=page, session=session, classrooms=classrooms)

# display the number of classrooms by type
@app.route('/classroom/summary')
def classroom_summary():
    # attempt to retrieve the classroom summary from the database
    classrooms = []
    try:
        classrooms = database.clasrooms_by_type()
    except Exception as e: flash('Error accessing the classroom summary')

    # prepare the template to display for the page
    page['title'] = 'Classroom Summary'
    return render_template('/classrooms/classroom-summary.html', page=page, session=session, classrooms=classrooms)

# add a new classroom to the database
@app.route('/classroom/add', methods=['POST', 'GET'])
def add_classroom():
    if request.method == 'POST':
        try: 
            classroom_type = coalesce(request.form.get('type'))
            classroom_id = coalesce(request.form.get('id'))
            seats = coalesce(request.form.get('seats'))
            database.add_classroom(classroom_id, seats, classroom_type)
            flash(f"Successfully created classroom '{classroom_id}'")
            return redirect("/classroom/registry")
        except Exception as e:
            print(e.with_traceback)
            flash(str(e))

    page['title'] = 'Classroom Summary'
    return render_template('/classrooms/add-classroom.html', page=page, session=session)

# search the classrooms stored in the database
@app.route('/classroom/search')
def search_classrooms():
    # attempt to retrieve the classroom summary from the database
    seats = request.args.get('seats')
    classrooms = []
    try:
        if coalesce(seats) != '':
            classrooms = database.search_classroom(coalesce(seats))
        else: classrooms = database.classroom_registry()
    except ValueError as e: flash(str(e))
    except Exception: flash('Error searching for classrooms')

    # prepare the template to display for the page
    page['title'] = 'Classroom Summary'
    return render_template('/classrooms/search-classrooms.html', page=page, session=session, classrooms=classrooms)

################################################################################
# Announcements
################################################################################

def current_semester() -> str: return ('2' if datetime.date.today().month > 7 else '1')
def current_year() -> str: return str(datetime.date.today().year)

# search the classrooms stored in the database
@app.route('/newsfeed')
def newsfeed():
    # attempt to retrieve the classroom summary from the database
    semester = coalesce(request.args.get('semester'), current_semester())
    year = coalesce(request.args.get('year'), current_year())
    unit = coalesce(request.args.get('unit'))
    announcements = []
    previous_year = None
    next_year = None
    try:
        announcements = database.list_announcements(semester, year)
        previous_year = str(int(year) - 1)
        next_year = str(int(year) + 1)
    except Exception as e: flash(str(e))

    # build a dictionary with all the unique units that appear the query
    units = {}
    for announcement in announcements:
        units[announcement.unitCode] = announcement.unitName

    # prepare the template to display for the page
    page['title'] = 'Classroom Summary'
    return render_template(
        '/newsfeed.html',
        page=page,
        session=session,
        announcements=[ a for a in announcements if not unit or a.unitCode == unit ],
        units=units,
        active_unit=unit,
        semester=semester,
        year=year,
        previous_year=previous_year,
        next_year=next_year
    )

################################################################################
# Textbooks
################################################################################

# List uos and textbooks
@app.route('/textbooks/list')
def list_textbooks():
    units = []
    try:
        units = database.list_textbooks()
    except Exception as e:
        print(e.with_traceback)
        flash(str(e))

    # prepare the template to display for the page
    page['title'] = 'List of Textbooks'
    return render_template('/textbooks/list-textbooks.html', page=page, session=session, units=units)

# Report the number of uos for each txtbook
@app.route('/textbooks/summary')
def units_by_textbook():
    # attempt to retrieve the classroom registry from the database
    units = []
    try:
        units = database.units_by_textbook()
    except Exception as e:
        print(e.with_traceback)
        flash(str(e))

    # prepare the template to display for the page
    page['title'] = 'Textbook Summary'
    return render_template('/textbooks/textbook-summary.html', page=page, session=session, units=units)

# Seach for all uos by given textbook
@app.route('/textbook/search-textbook', methods=['POST', 'GET'])
def search_textbook():
    uos = []
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get use input uoscode value
        uos = database.search_textbook(request.form['textbook'])

        # If our database connection gave back code -1
        if(uos == -1):
            flash("We cannot find this book. Or there are no uos using this textbook.")
            return redirect(url_for('list_textbooks'))

        else:
            if (uos is None):
                # Set it to an empty list and show error message
                uos = []
                flash('Error, there are no uos offering.')
            page['title'] = 'Search UOS by Textbook'
            return render_template('/textbooks/searchTextbook.html', page=page, 
                                    session=session, uos=uos)
    else:
        page['title'] = 'Search UOS by Textbook'
        return render_template('/textbooks/searchTextbook.html', page=page, 
                                    session=session, uos=uos)

# Update a textbook for a given unit
@app.route('/textbooks/update-textbook', methods=['POST', 'GET'])
def update_textbook():
    textbook = []
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get use input uoscode value
        entry = database.update_textbook(request.form['uos'], request.form['textbook'])

        # If our database connection gave back code -1
        if(entry == -1):
            flash("We cannot find this book. Or there are no uos using this textbook.")
            return redirect(url_for('update_textbook'))

        elif (entry is None):
            flash('Textbook not updated')
            return redirect(url_for('update_textbook'))

        flash('A new textbook {} is updated for {}'.format(entry[0][1], entry[0][0]))
        return redirect(url_for('list_textbooks'))
    
    else:
        page['title'] = 'Add prerequisites'
        return render_template('/textbooks/updateTextbook.html', page=page, 
                                    session=session)
