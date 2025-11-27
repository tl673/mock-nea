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
    reader = csv.DictReader(file)

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
            INSERT OR IGNORE INTO student (
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
           INSERT OR IGNORE INTO teacher (
               teacherID, first, last
           ) VALUES (
               :teacherID, :first, :last
           )
       """, row)


#save changes
connection.commit()


print("teachers imported") #confirmation message for when running/testing the code and can be removed later


#importing trips from csv
cursor.execute("SELECT COUNT(*) FROM trip")
trip_count = cursor.fetchone()[0]

if trip_count == 0:
    path3 = "csvFiles/trips.csv"
    with open(path3, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row['activeStatus'] = 1 if row['activeStatus'].lower().strip() == 'active' else 0
            row['national'] = 1 if row['national'].lower().strip() == 'national' else 0

            cursor.execute("""
                INSERT INTO trip (
                    teacherID, destination, startDate, endDate, tripType, activeStatus, title, subject, national
                ) VALUES (
                    :teacherID, :destination, :startDate, :endDate, :tripType, :activeStatus, :title, :subject, :national
                )
            """, row)

    connection.commit()
    print("Trips imported")


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
   password = random.randint(100000, 999999) 
   cursor.execute("""
       INSERT OR REPLACE INTO user (teacherID, username, password)
       VALUES (?, ?, ?)
   """, (teacherID, username, str(password)))
#save changes
connection.commit()
connection.close()

print("user accounts created") 


