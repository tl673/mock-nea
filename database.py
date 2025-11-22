#importing libraries
import sqlite3
import csv
import random


#opening connection
connection = sqlite3.connect("trips.db",check_same_thread=False)
cursor = connection.cursor()


#tables
#teacher table, primary key is teacherID
cursor.execute("""
CREATE TABLE IF NOT EXISTS teacher (
   teacherID INTEGER PRIMARY KEY,
   first TEXT NOT NULL,
   last TEXT NOT NULL
)
""")
#user table, primary key is teacherID as each teacher has one account. possibly need to change password to hash later
cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
   teacherID INTEGER NOT NULL PRIMARY KEY,
   username TEXT NOT NULL,
   password TEXT NOT NULL, 
   FOREIGN KEY(teacherID) REFERENCES teacher(teacherID)           
)
""")
#trips table, primary key is tripID
cursor.execute("""
CREATE TABLE IF NOT EXISTS trip (
   tripID INTEGER PRIMARY KEY AUTOINCREMENT,
   teacherID INTEGER NOT NULL,
   destination TEXT NOT NULL,
   startDate TEXT NOT NULL,
   endDate TEXT NOT NULL,
   tripType TEXT NOT NULL,
   activeStatus INTEGER NOT NULL,
   title TEXT NOT NULL,
   subject TEXT NOT NULL,
   national INTEGER NOT NULL,
   FOREIGN KEY(teacherID) REFERENCES teacher(teacherID)
)
""")
#student table, primary key is studentID
cursor.execute("""
CREATE TABLE IF NOT EXISTS student (
   studentID INTEGER PRIMARY KEY,
   first TEXT NOT NULL,
   last TEXT NOT NULL,
   DOB TEXT NOT NULL,
   medicalInfo TEXT,
   consent INTEGER NOT NULL,
   year INTEGER NOT NULL,
   house TEXT NOT NULL,
   dietaryRequirements TEXT   
)            
""")
#tripEnrollment table, composite primary key of tripID and studentID              
cursor.execute("""
CREATE TABLE IF NOT EXISTS tripEnrollment(
   tripID INTEGER NOT NULL,
   studentID INTEGER NOT NULL,
   PRIMARY KEY (tripID, studentID),
   FOREIGN KEY(tripID) REFERENCES trip(tripID),
   FOREIGN KEY(studentID) REFERENCES student(studentID)
)
""")


#save changes and close the connection
connection.commit()
connection.close()
print("\n\ndatabase created") #confirmation message for when running/testing the code and can be removed later


#reopen connection
connection = sqlite3.connect("trips.db",check_same_thread=False)
cursor = connection.cursor()

path1 = "csvFiles/students.csv"
with open(path1, newline="") as file:
   reader = csv.DictReader(file) #using dictreader to make a dictionary from each row using the headers for easier insertion
  
   #looping thru each row in the csv and inserting into table using reader which stores each row as a dictionary
   for row in reader:
       if row['consent'].lower().strip() == 'yes':
           row['consent'] = 1
       else:
           row['consent'] = 0
       row['year'] = int(row['year'])
       if 'medicalInfo' not in row:
           row['medicalInfo'] = None
       if 'dietaryRequirements' not in row:
           row['dietaryRequirements'] = None
           cursor.execute("""
               INSERT INTO student (
                   studentID, first, last, DOB, medicalInfo, consent, year, house, dietaryRequirements
               ) VALUES (
                   :studentID, :first, :last, :DOB, :medicalInfo, :consent, :year, :house, :dietaryRequirements
               )
           """, row)


#save changes
connection.commit()


print("students imported") #confirmation message for when running/testing the code and can be removed later

path2 = "csvFiles/teachers.csv"
with open(path2, newline="") as file:
   reader = csv.DictReader(file) #using dictreader to make a dictionary from each row using the headers for easier insertion
   #looping thru each row in the csv and inserting into table using reader which stores each row as a dictionary
   for row in reader:
       cursor.execute("""
           INSERT OR REPLACE INTO teacher (
               teacherID, first, last
           ) VALUES (
               :teacherID, :first, :last
           )
       """, row)


#save changes
connection.commit()


print("teachers imported") #confirmation message for when running/testing the code and can be removed later


#importing trips from csv
path3 = "csvFiles/trips.csv"
with open(path3, newline="" ) as file:
   reader = csv.DictReader(file) #using dictreader to make a dictionary from each row using the headers for easier insertion
   #looping thru each row in the csv and inserting into table using reader which stores each row as a dictionary
   for row in reader:
       if row['activeStatus'].lower().strip() == 'active':
           row['activeStatus'] = 1
       else:
           row['activeStatus'] = 0
      
       if row['national'].lower().strip() ==  'national':
           row['national'] = 1
       else:
           row['national'] = 0
      


       cursor.execute("""
           INSERT INTO trip (
               teacherID, destination, startDate, endDate, tripType, activeStatus, title, subject, national
           ) VALUES (
               :teacherID, :destination, :startDate, :endDate, :tripType, :activeStatus, :title, :subject, :national
           )
       """, row)
#save changes
connection.commit()


print("trips imported") #confirmation message for when running/testing the code and can be removed later


cursor.execute("SELECT studentID FROM student")
students = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT tripID FROM trip")
trips = [row[0] for row in cursor.fetchall()]      


#randomly enrolling students in trips - change later to actual enrollment system
for studentID in students:
   assignedTrips = random.sample(trips, k=random.randint(1, 3))
   for tripID in assignedTrips:
       cursor.execute("""
           INSERT OR IGNORE INTO tripEnrollment (tripID, studentID)
           VALUES (?, ?)
       """, (tripID, studentID))
#save changes


connection.commit()


print("students enrolled in trips") #confirmation message for when running/testing the code and can be removed later


cursor.execute("SELECT teacherID, first, last FROM teacher")
teachers = cursor.fetchall()
for teacherID, first, last in teachers:
   cursor.execute("SELECT * FROM user WHERE teacherID = ?", (teacherID,))
   existing = cursor.fetchone()
   if existing:
       continue  # Skip if user already exists
   username = last.lower() + first[0].lower()
   password = random.randint(100000, 999999)  # temporary simple password generation
   cursor.execute("""
       INSERT OR REPLACE INTO user (teacherID, username, password)
       VALUES (?, ?, ?)
   """, (teacherID, username, str(password)))
#save changes
connection.commit()
connection.close()

print("user accounts created") #confirmation message for when running/testing the code and can be removed later


def getConnection():
    return sqlite3.connect("trips.db", check_same_thread=False)


# Fetch teachers from CSV (no DB needed)
def getTeachers(): 
    path = "csvFiles/teachers.csv"
    with open(path, newline="") as file:
        return list(csv.DictReader(file))  # Convert to list for easier use


# Fetch all trips with teacher info
def getAllTrips():
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            trip.tripID,
            trip.title,
            trip.destination,
            trip.startDate,
            trip.endDate,
            trip.tripType,
            trip.activeStatus,
            trip.subject,
            trip.national,
            teacher.first,
            teacher.last,
            teacher.teacherID
        FROM trip
        JOIN teacher ON trip.teacherID = teacher.teacherID
        ORDER BY trip.startDate
    """)

    rows = cursor.fetchall()
    conn.close()

    fieldNames = [
        "tripID", "title", "destination", "startDate", "endDate",
        "tripType", "activeStatus", "subject", "national",
        "first", "last", "teacherID"
    ]

    return [dict(zip(fieldNames, row)) for row in rows]


# Fetch a single trip by ID
def getTripById(tripId):
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM trip WHERE tripID = ?", (tripId,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    fieldNames = [
        "tripID", "teacherID", "destination", "startDate",
        "endDate", "tripType", "activeStatus", "title",
        "subject", "national"
    ]

    return dict(zip(fieldNames, row))


# Create a new trip
def createNewTrip(teacherId, destination, startDate, endDate,
                  tripType, title, subject, national, activeStatus):
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO trip 
        (teacherID, destination, startDate, endDate, tripType, activeStatus, title, subject, national)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (teacherId, destination, startDate, endDate, tripType,
          activeStatus, title, subject, national))

    conn.commit()
    trip_id = cursor.lastrowid
    conn.close()
    return trip_id


# Update an existing trip
def updateTripDetails(tripId, destination, startDate, endDate,
                      tripType, activeStatus, title, subject, national):
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE trip
        SET destination = ?, startDate = ?, endDate = ?, tripType = ?,
            activeStatus = ?, title = ?, subject = ?, national = ?
        WHERE tripID = ?
    """, (destination, startDate, endDate, tripType,
          activeStatus, title, subject, national, tripId))

    conn.commit()
    conn.close()


# Delete a trip and its enrollments
def deleteTrip(tripId):
    conn = getConnection()
    cursor = conn.cursor()

    # Remove enrollment records first
    cursor.execute("DELETE FROM tripEnrollment WHERE tripID = ?", (tripId,))
    # Remove the trip itself
    cursor.execute("DELETE FROM trip WHERE tripID = ?", (tripId,))

    conn.commit()
    conn.close()


# Get all students enrolled in a trip
def getEnrolledStudents(tripId):
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student.*
        FROM student
        JOIN tripEnrollment ON student.studentID = tripEnrollment.studentID
        WHERE tripEnrollment.tripID = ?
    """, (tripId,))

    rows = cursor.fetchall()
    conn.close()

    fieldNames = [
        "studentID", "first", "last", "DOB",
        "medicalInfo", "consent", "year", "house",
        "dietaryRequirements"
    ]

    return [dict(zip(fieldNames, row)) for row in rows]