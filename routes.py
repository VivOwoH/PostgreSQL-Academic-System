# Importing the Flask Framework

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
    try:
        lectures = database.lectures("list")
    except Exception as e: flash('Error retrieving existing lectures')
    # print(lectures)
    dict = {
        'code':request.args.get('code'),
        'sem':request.args.get('sem'),
        'year':request.args.get('year'),
        'time':request.args.get('time'),
        'id':request.args.get('id')
        }
    lectures = database.lectures("add", **dict)

    if (lectures is None):
        # Set it to an empty list and show error message
        lectures = []
        flash('Error, there are no lectures')
    page['title'] = 'Lectures'
    return render_template('/lectures/add-lectures.html', page=page, session=session, lectures=lectures)

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
        classrooms = database.classroom_summary()
    except Exception as e: flash('Error accessing the classroom summary')

    # prepare the template to display for the page
    page['title'] = 'Classroom Summary'
    return render_template('/classrooms/classroom-summary.html', page=page, session=session, classrooms=classrooms)

# add a new classroom to the database
@app.route('/classroom/add')
def add_classroom():
    # attempt to retrieve the classroom summary from the database
    classrooms = []
    try:
        classrooms = database.classroom_registry()
    except Exception as e: flash('Error retrieving classroom registry')

    # attempt to create the classroom if one is specified
    try: 
        classroom_id = request.args.get('id')
        seats = request.args.get('seats')
        classroom_type = request.args.get('type')
        if classroom_id != None and seats and seats.isdigit() and classroom_type != None:
            if database.add_classroom(classroom_id, int(seats), classroom_type):
                flash(f"Successfully created classroom '{classroom_id}'")
                return redirect("/classroom/registry")
            else: flash('Error creating classroom')
    except Exception as e:
        print(e)
        flash('Error creating classroom')

    # prepare the template to display for the page
    page['title'] = 'Classroom Summary'
    return render_template('/classrooms/add-classroom.html', page=page, session=session, classrooms=classrooms)

# search the classrooms stored in the database
@app.route('/classroom/search')
def search_classrooms():
    # attempt to retrieve the classroom summary from the database
    seats = request.args.get('seats')
    classrooms = []
    try:
        if seats == None or not seats.isdigit():
            if seats != None and not seats.isdigit():
                flash('Invalid number of seats')
            classrooms = database.classroom_registry()
        else: classrooms = database.search_classroom(int(seats))
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
    semester = request.args.get('semester') if request.args.get('semester') else current_semester()
    year = request.args.get('year') if request.args.get('year') else current_year()
    unit = request.args.get('unit') if request.args.get('unit') != None else ''
    announcements = []
    previous_year = None
    next_year = None
    try:
        if not semester or not semester.isdigit():
            flash(f"Invalid semester provided '{semester}'")
        elif not year or not year.isdigit():
            flash(f"Invalid year provided '{year}'")
        else:
            previous_year = str(int(year) - 1)
            next_year = str(int(year) + 1)
            announcements = database.list_announcements(int(semester), int(year), unit)
    except Exception as e: flash(str(e))

    # build a dictionary with all the unique units that appear the query
    units = {}
    for announcement in announcements:
        units[announcement.unitCode] = announcement.unitName

    # prepare the template to display for the page
    page['title'] = 'Classroom Summary'
    print(semester, year)
    return render_template(
        '/newsfeed.html',
        page=page,
        session=session,
        announcements=announcements,
        units=units,
        active_unit=unit,
        semester=semester,
        year=year,
        previous_year=previous_year,
        next_year=next_year
    )
