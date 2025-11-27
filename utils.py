import sqlite3
from datetime import datetime

def getConnection():
    return sqlite3.connect("trips.db", check_same_thread=False)

def loginCheck(username,password): #checking for the username and password is stored in the database
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM user WHERE username = ?", (username, ))
    storedPassword = (cursor.fetchone())[0]
    connection.close()

    if storedPassword is None:
        return False
    if storedPassword == password:
        return True
    else:
        return False

def resetTripsandIDs(): #to reset the trips table, used to debug the SQL logic
    connection = getConnection()
    cursor = connection.cursor()
    
    cursor.execute("DELETE FROM tripEnrollment")
    cursor.execute("DELETE FROM trip")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='trip'")  # reset AUTOINCREMENT
    
    connection.commit()
    connection.close()
    print("Trips cleared and IDs reset")

def resetTripEnrollment():
    connection = sqlite3.connect("trips.db")  # replace with your DB path
    cursor = connection.cursor()
    
    cursor.execute("DELETE FROM trip")  # removes all rows
    connection.commit()
    connection.close()

def getTeachers(): #retrieves details of teachers
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM teacher")
    info = cursor.fetchall()
    connection.close()
    teachers = []
    for i in info:
        teachers.append({"teacherID": i[0], "first" : i[1], "second": i[2]})
    print(teachers)
    return teachers

def getTrip(tripID): #retrieves details of ONE specific trip using its trip ID
    connection = getConnection()
    cursor = connection.cursor()    
    cursor.execute("SELECT * FROM trip WHERE tripID = ?", (tripID, ))
    info = cursor.fetchone()
    connection.close()
    if info:
        trip = {
            "tripID": info[0],
            "teacherID": info[1],
            "destination": info[2],
            "startDate": info[3],
            "endDate": info[4],
            "tripType": info[5],
            "activeStatus": info[6],
            "title": info[7],
            "subject": info[8],
            "national": info[9]
        }
        print(trip)
        return trip
    else:
        return None 
    
def createTrip(teacherID,destination,startDate,endDate,tripType,activeStatus,title,subject,national): 
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO trip (
            teacherID, destination, startDate, endDate, tripType, activeStatus, title, subject, national
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (teacherID, destination, startDate, endDate, tripType, activeStatus, title, subject, national))
    connection.commit()
    tripID = cursor.lastrowid
    connection.close()
    return tripID

def updateTrip(tripID,teacherID,destination,startDate,endDate,tripType,activeStatus,title,subject,national):
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE trip
        SET teacherID = ?, destination = ?, startDate = ?, endDate = ?,
            tripType = ?, activeStatus = ?, title = ?, subject = ?, national = ?
        WHERE tripID = ?
    """, (teacherID, destination, startDate, endDate, tripType,
          activeStatus, title, subject, national, tripID))

    connection.commit()
    connection.close()

def deleteTrip(tripID):
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM trip WHERE tripID = ?", (tripID, ))
    connection.commit()
    connection.close()

def getEnrolledStudents(tripID):
    connection = getConnection()
    cursor = connection.cursor()
    
    # Join tripEnrollment with student to get full details
    cursor.execute("""
        SELECT s.studentID, s.first, s.last, s.DOB, s.medicalInfo, s.consent, s.year, s.house, s.dietaryRequirements
        FROM tripEnrollment te
        JOIN student s ON te.studentID = s.studentID
        WHERE te.tripID = ?
    """, (tripID,))
    
    rows = cursor.fetchall()
    connection.close()
    
    # Convert rows to a list of dictionaries for easier use
    students = []
    for row in rows:
        students.append({
            "studentID": row[0],
            "first": row[1],
            "last": row[2],
            "DOB": row[3],
            "medicalInfo": row[4],
            "consent": row[5],
            "year": row[6],
            "house": row[7],
            "dietaryRequirements": row[8]
        })
    
    return students

def getAllTrips():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT t.tripID, t.teacherID, t.destination, t.startDate, t.endDate, t.tripType,
               t.activeStatus, t.title, t.subject, t.national,
               tr.first, tr.last
        FROM trip t
        JOIN teacher tr ON t.teacherID = tr.teacherID
        ORDER BY t.startDate
    """)
    
    rows = cursor.fetchall()
    connection.close()
    
    trips = []
    for row in rows:
        trips.append({
            "tripID": row[0],
            "teacherID": row[1],
            "destination": row[2],
            "startDate": row[3],
            "endDate": row[4],
            "tripType": row[5],
            "activeStatus": row[6],
            "title": row[7],
            "subject": row[8],
            "national": row[9],
            "first": row[10],
            "last": row[11]
        })
    
    return trips

def getActiveTrips():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT tripID, title FROM trip WHERE activeStatus = 1")
    rows = cursor.fetchall()
    connection.close()
    trips = [{"tripID": row[0], "title": row[1]} for row in rows]
    return trips

def displayTripTable(): #to show what is in the trips table
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM trip")
    print(cursor.fetchall())  
    connection.close()

def displayTripEnrollmentTable(): #to show what is in the trips table
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tripEnrollment")
    print(cursor.fetchall())  
    connection.close()
    
def displayStudentTable(): #to show what is in the students table
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM student")
    print(cursor.fetchall())  
    connection.close()

def displayTeacherTable():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM teacher")
    print(cursor.fetchall())  
    connection.close()

def displayUserTable():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user")
    print(cursor.fetchall())  
    connection.close()

def getTeacherOptions():
    teachers = getTeachers()
    teacherOptions = {f"{t['first']} {t['second']} (ID: {t['teacherID']})": t['teacherID'] for t in teachers}
    return teacherOptions, teachers

def getTripOptionsNumbered():
    allTrips = getAllTrips()
    if not allTrips:
        return {}, []
    sortedTrips = sorted(allTrips, key=lambda x: x['tripID'])
    tripOptions = {f"{i+1}. {t['title']}": t['tripID'] for i, t in enumerate(sortedTrips)}
    return tripOptions, sortedTrips

def inORactiveTrips():
    connection =getConnection()
    cursor = connection.cursor()
    today = datetime.today().date()
    cursor.execute("SELECT tripID, endDate FROM trip WHERE activeStatus = 1")
    trips = cursor.fetchall()
    for num in trips:
        tripID, endDateStr = num
        # Convert endDate string to date
        endDate = datetime.strptime(endDateStr, "%Y-%m-%d").date()
        
        # If the trip has ended, set activeStatus to 0
        if endDate < today:
            cursor.execute("UPDATE trip SET activeStatus = 0 WHERE tripID = ?", (tripID,))
    
    # Commit changes and close the connection
    connection.commit()
    connection.close()


displayTripTable()
displayUserTable()
