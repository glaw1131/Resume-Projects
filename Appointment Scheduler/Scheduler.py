from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)
    promptmenu()


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)
    promptmenu()


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False 


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient
    promptmenu()


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver
    promptmenu()


def search_caregiver_schedule(tokens):
    # search_caregiver_schedule <date>
    # check 1: if nobody is logged-in, they need to log in first
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
        
    # check 2: the length for tokens needs to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return 
    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    try:
        date_tokens = date.split("-")
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int (date_tokens[2])
    except Exception as e:
        print("Please try again!")
        print("Error:", e)

    cm = ConnectionManager()
    conn = cm.create_connection()

    select_available_caregivers = "SELECT Caregiver FROM Availabilities Join Caregivers ON Availabilities.Caregiver = Caregivers.Username WHERE Date = %s ORDER BY Caregiver ASC"
    #select_caregiver_count = "SELECT COUNT(Caregiver) AS count FROM Availabilities Join Caregivers ON Availabilities.Caregiver = Caregivers.Username WHERE Date = %s"
    select_vaccines = "SELECT * FROM Vaccines"
    try:
        d = datetime.datetime(year, month, day)
        cursor = conn.cursor(as_dict=True)
        #cursor.execute(select_caregiver_count, d)
        #for row in cursor:
        #    print(row['count'])
        
        cursor.execute(select_available_caregivers, d)
        
        print("Available caregivers on %s: " % (str(month)+"-"+str(day)+"-"+str(year)))
        for row in cursor:
            print(row['Caregiver'])
        print("")
        print("Vaccines Available: ")
        cursor.execute(select_vaccines)
        for row in cursor:
            print(row['Name'] + " | " + str(row['Doses']))
    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()
    promptmenu()


def reserve(tokens):
    # reserve <date> <vaccine>
    # check 1: if nobody is logged-in, they need to log in first
    global current_caregiver 
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    # check 2: if the current user logged in is a caregiver, they need to log in as a patient
    if current_patient is None:
        print("Please login as a patient!")
        return

    # check 3: the length for tokens needs to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return 
    date = tokens[1]
    vaccine_name = tokens[2] # MAKE SURE INPUTS ARE VALID
        
    # assume input is hyphenated in the format mm-dd-yyyy
    try:
        date_tokens = date.split("-")
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    
    cm = ConnectionManager()
    conn = cm.create_connection()

    vaccine = None 
    select_doses_vaccine = "SELECT Doses FROM Vaccines WHERE Name = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_doses_vaccine, vaccine_name)
        doses = None
        for row in cursor:
            doses = row['Doses']
            break
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error: ", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e) 

    if vaccine is None:
        print("Please try again!")
        return

    select_available_caregivers = "SELECT Caregiver FROM Availabilities Join Caregivers ON Availabilities.Caregiver = Caregivers.Username WHERE Date = %s ORDER BY Caregiver ASC"
    select_caregiver_count = "SELECT COUNT(Caregiver) AS count FROM Availabilities Join Caregivers ON Availabilities.Caregiver = Caregivers.Username WHERE Date = %s"
    #select_doses_vaccine = "SELECT Doses FROM Vaccines WHERE Name = %s"
    add_appointment = "INSERT INTO Appointments (Date, Vaccine, Caregiver, Patient) VALUES (%s, %s, %s, %s)"
    remove_availability = "DELETE FROM Availabilities WHERE Caregiver = %s AND Date = %s"
    try:
        d = datetime.datetime(year, month, day)
        cursor = conn.cursor(as_dict=True)
        # Check for available caregiver on given date
        cursor.execute(select_caregiver_count, d)
        #row = cursor.fetchone()
        #print(row[0])
       # if row[0] == 0:
        #    print("No Caregiver is available!")
        #    return
        for row in cursor:
            if row['count'] == 0:
                print("No Caregiver is available!")
                return 
            break
        
        # Obtain a caregiver for the appointment
        cursor.execute(select_available_caregivers, d)
        #row = cursor.fetchone()
        #print(row[0])
        #app_caregiver = row[0]
        #print(app_caregiver)
        app_caregiver = None 
        for row in cursor: # theres gotta be a better way to do this
            app_caregiver = row['Caregiver']
            break
        
        # Check for valid caregiver and add appointment
        if app_caregiver is None:
            print("Please try again!")
            return
        app_patient = current_patient.get_username()
        vaccine.decrease_available_doses(1)
        cursor.execute(add_appointment, (d, vaccine_name, app_caregiver, app_patient))
        cursor.execute(remove_availability, (app_caregiver, d))
        conn.commit()


        print("Appointment ID: " + str(cursor.lastrowid) + ", Caregiver username: " + app_caregiver)

    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error: ", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()
    promptmenu()

    """
    TODO: Part 2
    """
    


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")
    promptmenu()


def cancel(tokens):
    # cancel <appointment_id>
    # check 1: if nobody is logged-in, they need to log in first
    global current_caregiver 
    global current_patient 
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return 
    
    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    app_id = tokens[1]

    cm = ConnectionManager()
    conn = cm.create_connection()

    select_appointment = "SELECT * FROM Appointments WHERE Appointment_id = %s"
    add_availability = "INSERT INTO Availabilities VALUES (%s , %s)"
    remove_appointment = "DELETE FROM Appointments WHERE Appointment_id = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_appointment, app_id)
        d = None
        app_caregiver = None
        for row in cursor:
            d = row['Date']
            app_caregiver = row['Caregiver']
            break
        cursor.execute(add_availability, (d, app_caregiver))
        cursor.execute(remove_appointment, app_id)
        conn.commit()
        
    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error: ", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()

    print("Appointment canceled!")
    promptmenu()

    """
    TODO: Extra Credit
    """
    


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")
    promptmenu()


def show_appointments(tokens):
    # show_appointments
    # check 1: if nobody is logged-in, they need to log in first
    global current_caregiver
    global current_patient 
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return 
    
    # check 2: the length for tokens needs to be exactly 1 to include all information (with the operation name)
    if len(tokens) != 1:
        print("Please try again!")
        return 
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    select_appointments_caregiver = "SELECT * FROM Appointments WHERE Caregiver = %s"
    select_appointments_patient = "SELECT * FROM Appointments WHERE Patient = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        if current_caregiver is not None:
            cursor.execute(select_appointments_caregiver, current_caregiver.get_username())
        if current_patient is not None:
            cursor.execute(select_appointments_patient, current_patient.get_username())
        print("Appointments: ")
        for row in cursor:
            print('Appointment ID: '+str(row['Appointment_id'])+' | Date: '+str(row['Date'])+' | Vaccine: '+row['Vaccine']+' | Caregiver: '+row['Caregiver']+' | Patient '+row['Patient'])
        
    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()
    promptmenu()

    '''
    TODO: Part 2
    '''
    


def logout(tokens):
    # logout
    # check 1: if nobody is logged-in, they need to log in first
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first.")
        return

    # check 2: the length for tokens need to be exactly 1 to include all information (with the operation name)
    if len(tokens) != 1:
        print("Please try again!")
        return 
    try:
        current_patient = None 
        current_caregiver = None
    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
        return

    # check if the logout was successful
    if current_patient is not None or current_caregiver is not None:
        print("Please try again!")
    else:
        print("Successfully logged out!")
        promptmenu()


def start():
    stop = False
    
    promptmenu()

    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")

def promptmenu():
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
