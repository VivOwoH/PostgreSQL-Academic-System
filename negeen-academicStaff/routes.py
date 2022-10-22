# Importing the Flask Framework

from modules import *
from flask import *
import database
import configparser


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
    if( 'logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    page['unikey'] = unikey
    page['title'] = 'Welcome'
    return render_template('welcome.html', session=session, page=page)

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
    transcript = database.get_transcript(session.get('sid'))
    if (transcript is None):
        # Set it to an empty list and show error message
        transcript = []
        flash('Error, there are no records in your transcript')
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
# List Academic Staff page
################################################################################

# List the academic staff
@app.route('/academic-staff/lecturers')
def list_academic_staff():
    # Go into the database file and get the list_units() function
    staff, staffUnits = database.list_academic_staff()
    
    # What happens if units are null?
    if (staff is None):
        # Set it to an empty list and show error message
        staff = []
        flash('There are no Lecturers to display')
    if (staffUnits is None):
        staffUnits = []
    page['title'] = 'Academic Staff - Lecturers'
    return render_template('staff.html', page=page, session=session, staff=staff, staffUnits=staffUnits)

@app.route('/academic-staff/tutors')
def list_tutors():
    # Go into the database file and get the list_units() function
    staff, tutorUnits = database.list_tutors()
    # What happens if units are null?
    if (staff is None):
        # Set it to an empty list and show error message
        staff = []
        flash('There are no Tutors to display')
    if (tutorUnits is None):
        tutorUnits = []
    page['title'] = 'Academic Staff - Tutors'
    return render_template('tutors.html', page=page, session=session, staff=staff, tutorUnits=tutorUnits)


################################################################################
# List Department Page
################################################################################

# List the academic staff
@app.route('/staff-by-department')
def staff_by_department():
    # Go into the database file and get the list_units() function
    sbd = database.staff_by_department()
    # What happens if units are null?
    if (sbd is None):
        # Set it to an empty list and show error message
        sbd = []
        flash('Error, there is no available information')
    page['title'] = 'Department Staff'
    return render_template('sbd.html', page=page, session=session, sbd=sbd)

################################################################################
# Staff in Department Page
################################################################################
@app.route('/<department_id>')
def department_staff(department_id):

    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'Department Staff'

    # Get a list of all tvshows by tvshow_id from the database
    staff = None
    staff = database.find_staff_by_department(department_id)

    # Data integrity checks
    if staff == None:
        staff = []
    return render_template('departmentStaff.html',
                           session=session,
                           page=page,
                           staff=staff,
                           department_id=department_id.upper())

################################################################################
# Search Staff by Department Page
################################################################################
@app.route('/search-staff', methods=['POST', 'GET'])
def search_staff_by_department():

    # Check if the user is logged in, if not: back to login.
    if ('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'Staff Search by Department'

    # Get a list of matching staff from the database
    staff = None
    if (request.method == 'POST'):
        staff = database.find_staff_by_department(request.form['searchterm'])

    # Data integrity checks
    if staff is None or staff == []:
        staff = []
        page['bar'] = False
        # flash("No staff found for this department, please try again")
    else:
        page['bar'] = True
        if len(staff) == 0:
            flash("No staff found for this department, please try again")
        else:
            flash('Found ' + str(len(staff)) + ' results!')
        session['logged_in'] = True

    return render_template('search_staff.html',
                           session=session,
                           page=page,
                           staff=staff)

################################################################################
# Add Staff Member
################################################################################
@app.route('/add-staff', methods=['POST', 'GET'])
def add_staff():
    # # Check if the user is logged in, if not: back to login.
    if ('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'Add Staff to DataBase'

    newstaff = None
    print("request form is: ")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if (request.method == 'POST'):
        
        if ('name' not in request.form):
            newdict['name'] = 'N/A'
        else:
            newdict['name'] = request.form['name']
            print("We have a value: ", newdict['name'])

        if ('department' not in request.form):
            newdict['department'] = 'Empty department field'
        else:
            newdict['department'] = request.form['department']
            print("We have a value: ", newdict['department'])

        if ('password' not in request.form):
            newdict['password'] = 'Empty password field'
        else:
            newdict['password'] = request.form['password']
            print("We have a value: ", newdict['password'])

        if ('address' not in request.form):
            newdict['address'] = 'N/A'
        else:
            newdict['address'] = request.form['address']
            print("We have a value: ", newdict['address'])
            
        if ('salary' not in request.form):
            newdict['salary'] = '0'
        else:
            newdict['salary'] = request.form['salary']
            print("We have a value: ", newdict['salary'])

        print('newdict is:')
        print(newdict)
        
        print(database.generate_id())

        for key, value in newdict.items():
            if key == 'salary':
                if not value.isnumeric():
                    return render_template('addStaffFailed.html',
                        session=session,
                        page=page)
                elif int(value) < 0:
                    return render_template('addStaffFailed.html',
                        session=session,
                        page=page)
            elif key == 'department':
                if  len(value) != 3:
                    return render_template('addStaffFailed.html',
                        session=session,
                        page=page)
            else:
                if value == "":
                    return render_template('addStaffFailed.html',
                        session=session,
                        page=page)

        # forward to the database to manage insert
        staff = database.add_staff(newdict['name'], newdict['department'], newdict['password'], newdict['address'], newdict['salary'])

#         max_staff_id = database.get_last_staff()[0]['staff_id']
#         print(staff)
#         if staff is not None:
#             max_staff_id = staff[0]

        # ideally this would redirect to your newly added staff
        flash("Successfully added "+newdict['name']+" to database!")
        return render_template('addStaff.html',
                               session=session,
                               page=page)
    else:
        return render_template('addStaff.html',
                               session=session,
                               page=page)
