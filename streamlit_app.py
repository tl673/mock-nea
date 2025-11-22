import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import calendar as c
import os
import random

st.set_page_config(page_title="Judd Trips App", layout="wide")


from database import (getAllTrips,getTeachers,getTrip,createTrip,updateTrip,deleteTrip,getEnrolledStudents)


def displayTripsData(trips):
    data = [{
        'ID': t['tripID'],
        'Title': t['title'],
        'Destination': t['destination'],
        'Lead Teacher': f"{t['first']} {t['last']}",
        'Start Date': t['startDate'],
        'End Date': t['endDate'],
        'Type': t['tripType'],
        'Active': 'Yes' if t['activeStatus'] == 1 else 'No',
        'Subject': t['subject'],
        'National': 'Yes' if t['national'] == 1 else 'No'
    } for t in trips]
    return pd.DataFrame(data)
demoUser = {"email": "admin@judd.kent.sch.uk", "password": "admin123"}

if "isLoggedIn" not in st.session_state:
    st.session_state.isLoggedIn = False
if "page" not in st.session_state:
    st.session_state.page = "Home"

st.markdown("""
    <style>
    .stApp {background-color: #c6c5c6;}
    .subtitle {font-size: 2rem;color: #1f3b4d;margin-bottom: 2rem;}
    .main-header {color: #1f3b4d; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

def loginPage():
    with st.container():
        st.title(":red[The] :blue[Judd School] :grey[Trips App]")
        with st.form(key="my_form"): #this groups the widgets together
            email = st.text_input("School Email", placeholder="name@judd.kent.sch.uk")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            loginButton = st.form_submit_button("Log in")
            if loginButton:
                if email == demoUser["email"] and password == demoUser["password"]:
                    st.session_state.isLoggedIn = True
                    st.rerun()
                else:
                    st.error("Invalid email or password")

def sidebar():
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/5/5a/The_Judd_School_Crest.png", width=80)
    st.sidebar.title("The Judd School")
    st.sidebar.markdown("---")
    if st.sidebar.button("Home"):
        st.session_state.page = "Home"
    if st.sidebar.button("Calendar"):
        st.session_state.page = "Calendar"
    if st.sidebar.button("Information"):
        st.session_state.page = "Information"
    if st.sidebar.button("Trips"):
        st.session_state.page = "Trips"
    st.sidebar.markdown("---")
    if st.sidebar.button("Log Out"):
        st.session_state.isLoggedIn = False
        st.session_state.page = "Home"
        st.rerun()

        

def calendarPage():
    st.title("Calendar")
    st.session_state.tripCalendar = {} 
    trips = getAllTrips()
    for trip in trips:
        try:
            startDate = datetime.strptime(trip['startDate'], '%Y-%m-%d').date()
            endDate = datetime.strptime(trip['endDate'], '%Y-%m-%d').date()
            currentDate = startDate
            while currentDate <= endDate:
                st.session_state.tripCalendar[currentDate] = trip['title']
                currentDate += timedelta(days=1)
        except:
            continue

    today = date.today()
    yearSelected = st.session_state.get("calYear", today.year)
    monthSelected = st.session_state.get("calMonth", today.month)
    col1, col2, col3 = st.columns(3)

    if col1.button("<-- Previous Month"):
        if monthSelected == 1:
            monthSelected = 12
            yearSelected -= 1
        else:
            monthSelected -= 1

    if col3.button("Next Month -->"):
        if monthSelected == 12:
            monthSelected = 1
            yearSelected += 1
        else:
            monthSelected += 1

    st.session_state.calYear = yearSelected
    st.session_state.calMonth = monthSelected
    st.subheader(f"{c.month_name[monthSelected]} {yearSelected}")

    monthCal = c.monthcalendar(yearSelected, monthSelected)

    st.markdown("""
    <style>
.calendarTable {width: 100%; border-collapse: collapse;}
.calendarTable th {padding: 8px; text-align: center; background: #1f3b4d; color: white;}
.calendarTable td {padding: 12px; text-align: center; border: 2px solid #ddd; background-color: inherit;}
.tripDay {background-color: #ffd54f;}
.dayNumber {font-weight: 900; color: black;}
    </style>
    """, unsafe_allow_html=True)

    calendarHtml = "<table class='calendarTable'><tr>" + "".join(f"<th>{d}</th>" for d in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]) + "</tr>"
    for week in monthCal:
        calendarHtml += "<tr>"
        for day in week:
            if day == 0:
                calendarHtml += "<td></td>"
            else:
                dateKey = date(yearSelected, monthSelected, day)
                tripTitle = st.session_state.tripCalendar.get(dateKey)
                classes = "tripDay" if tripTitle else ""
                content = f"<span class='dayNumber'>{day}</span>"
                if tripTitle:
                    content += f"<div style='font-size: 0.75rem;'>{tripTitle}</div>"
                calendarHtml += f"<td class='{classes}'>{content}</td>"
        calendarHtml += "</tr>"
    calendarHtml += "</table>"

    st.markdown(calendarHtml, unsafe_allow_html=True)

def informationPage():
    st.title("Information page X")

def homePage():
    st.title("Welcome to The Judd School Trips App")
    st.subheader("Trip Administrator Dashboard")
    st.image("https://search.brave.com/images?q=the+judd+school", use_container_width=True)

# --- Helpers ---
def getTripOptionsNumbered():
    """Return a dict of numbered trip display name -> tripID, sorted by tripID."""
    trips = getAllTrips()
    trips.sort(key=lambda x: x['tripID'])
    options = {f"{i+1}. {t['title']}": t['tripID'] for i, t in enumerate(trips)}
    return options, trips

def getTeacherOptions():
    teachers = getTeachers()
    return {f"{t['first']} {t['second']} (ID: {t['teacherID']})": t['teacherID'] for t in teachers}, teachers


# --- Tabs ---

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


# ------------------ Tabs ------------------

def createTripTab():
    st.subheader("Plan a New School Trip")
    teacherOptions, _ = getTeacherOptions()

    with st.form("create_trip_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Trip Title", max_chars=100)
            destination = st.text_input("Destination")
            subject = st.selectbox("Subject Area", [
                "Maths", "English", "Religious Studies", "Physics", "Chemistry", "Biology",
                "Geography","History","Music","Design and Technology", "Computer Science",
                "PE","German","French","Latin","Classics","Art","Economics","Politics","Philosophy"
            ])
            keys = list(teacherOptions.keys())
            if not keys:
                st.warning("No teachers found.")
                teacherId = None
            else:
                teacherName = st.selectbox("Lead Teacher", options=keys, key="create_teacher_select")
                teacherId = teacherOptions.get(teacherName)

        with col2:
            startDate = st.date_input("Start Date")
            endDate = st.date_input("End Date", min_value=startDate)
            tripType = st.selectbox("Trip Type", ["Day Trip", "Residential (UK)", "Residential (Overseas)"], key="create_trip_type")
            national = st.checkbox("National (UK-based)", value=True)
            activeStatus = st.checkbox("Active Status", value=True)

        if st.form_submit_button("Create Trip"):
            if not title or not destination or not subject:
                st.error("Missing fields.")
            elif not teacherId:
                st.error("Teacher missing.")
            else:
                createTrip(
                    teacherID=teacherId,
                    destination=destination,
                    startDate=startDate.isoformat(),
                    endDate=endDate.isoformat(),
                    tripType=tripType,
                    activeStatus=1 if activeStatus else 0,
                    title=title,
                    subject=subject,
                    national=1 if national else 0
                )
                st.success(f"Trip '{title}' created.")
                st.rerun()


def editTripTab():
    st.subheader("Modify Existing Trip Details")
    tripOptions, _ = getTripOptionsNumbered()
    if not tripOptions:
        st.info("No trips available.")
        return

    selected = st.selectbox("Select Trip", tripOptions.keys(), key="edit_trip_select")
    tripId = tripOptions[selected]
    trip = getTrip(tripId)
    if not trip:
        st.warning("Trip not found.")
        return

    currentStart = datetime.strptime(trip['startDate'], '%Y-%m-%d').date()
    currentEnd = datetime.strptime(trip['endDate'], '%Y-%m-%d').date()
    teacherOptions, _ = getTeacherOptions()

    with st.form("edit_trip_form"):
        col1, col2 = st.columns(2)
        with col1:
            newTitle = st.text_input("Trip Title", value=trip['title'])
            newDestination = st.text_input("Destination", value=trip['destination'])
            newSubject = st.text_input("Subject Area", value=trip['subject'])
            teacherKeys = list(teacherOptions.keys())
            idx = next((i for i, k in enumerate(teacherKeys) if teacherOptions[k] == trip['teacherID']), 0)
            newTeacher = st.selectbox("Lead Teacher", options=teacherKeys, index=idx, key="edit_teacher_select")
            newTeacherId = teacherOptions[newTeacher]

        with col2:
            newStart = st.date_input("Start Date", value=currentStart)
            newEnd = st.date_input("End Date", value=currentEnd, min_value=newStart)
            tripTypes = ["Day Trip", "Residential (UK)", "Residential (Overseas)"]
            idx = tripTypes.index(trip['tripType']) if trip['tripType'] in tripTypes else 0
            newType = st.selectbox("Trip Type", tripTypes, index=idx, key="edit_trip_type")

        c1, c2 = st.columns(2)
        with c1: newNational = st.checkbox("National", value=(trip['national'] == 1))
        with c2: newActive = st.checkbox("Active", value=(trip['activeStatus'] == 1))

        if st.form_submit_button("Save Changes"):
            updateTrip(
                tripID=tripId,
                teacherID=newTeacherId,
                destination=newDestination,
                startDate=newStart.isoformat(),
                endDate=newEnd.isoformat(),
                tripType=newType,
                activeStatus=1 if newActive else 0,
                title=newTitle,
                subject=newSubject,
                national=1 if newNational else 0
            )
            st.success("Trip updated.")
            st.rerun()


def deleteTripTab():
    st.subheader("Permanently Delete a Trip")
    tripOptions, _ = getTripOptionsNumbered()
    if not tripOptions:
        st.info("No trips available.")
        return

    selected = st.selectbox("Select Trip to Delete", tripOptions.keys(), key="delete_trip_select")
    tripId = tripOptions[selected]
    title = selected.split(". ", 1)[1]

    st.warning(f"Delete '{title}'?")
    if st.button("Confirm Delete", key="delete_confirm_button"):
        deleteTrip(tripId)
        st.success("Deleted.")
        st.rerun()


def cloneAnnualTripTab():
    st.subheader("Clone an Existing Trip")
    tripOptions, _ = getTripOptionsNumbered()
    if not tripOptions:
        st.info("No trips available.")
        return

    selected = st.selectbox("Select Source Trip", tripOptions.keys(), key="clone_trip_select")
    tripId = tripOptions[selected]
    trip = getTrip(tripId)
    if not trip:
        st.warning("Trip not found.")
        return

    start = datetime.strptime(trip['startDate'], '%Y-%m-%d').date()
    end = datetime.strptime(trip['endDate'], '%Y-%m-%d').date()

    try:
        newStart = start.replace(year=start.year + 1)
        newEnd = end.replace(year=end.year + 1)
    except ValueError:
        newStart = date(start.year + 1, start.month, 1)
        newEnd = date(end.year + 1, end.month, 1)

    with st.form("clone_trip_form", clear_on_submit=True):
        newTitle = st.text_input("New Title", value=f"Annual {trip['title']} ({newStart.year})")
        col1, col2 = st.columns(2)
        with col1:
            newSD = st.date_input("Start Date", value=newStart)
            newNat = st.checkbox("National", value=(trip['national'] == 1))
        with col2:
            newED = st.date_input("End Date", value=newEnd, min_value=newSD)
            newAct = st.checkbox("Active", value=True)

        if st.form_submit_button("Clone Trip"):
            createTrip(
                teacherID=trip['teacherID'],
                destination=trip['destination'],
                startDate=newSD.isoformat(),
                endDate=newED.isoformat(),
                tripType=trip['tripType'],
                title=newTitle,
                subject=trip['subject'],
                national=1 if newNat else 0,
                activeStatus=1 if newAct else 0
            )
            st.success("Trip cloned.")
            st.rerun()


def viewEnrollmentTab():
    st.subheader("View Enrollment")
    tripOptions, _ = getTripOptionsNumbered()
    if not tripOptions:
        st.info("No trips available.")
        return

    selected = st.selectbox("Select Trip", tripOptions.keys(), key="view_enrollment_select")
    tripId = tripOptions[selected]
    enrolled = getEnrolledStudents(tripId)

    if enrolled:
        data = [{
            'First Name': s['first'],
            'Last Name': s['last'],
            'Year': s['year'],
            'House': s['house'],
            'Dietary Requirements': s.get('dietaryRequirements') or 'None',
            'Medical Info': s.get('medicalInfo') or 'None',
            'Consent Given': 'Yes' if s.get('consent') == 1 else 'No'
        } for s in enrolled]
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.warning("No students enrolled.")
        
def tripsPage():
    st.title("Trips Management")
    allTrips = getAllTrips()
    if allTrips:
        df = displayTripsData(allTrips)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No trips found.")

    st.markdown("---")
    create, edit, delete, clone, view = st.tabs([
        "Create New Trip",
        "Edit Trip",
        "Delete Trip",
        "Clone / Annual Trip",
        "View Enrollment"
    ])
    with create: createTripTab()
    with edit: editTripTab()
    with delete: deleteTripTab()
    with clone: cloneAnnualTripTab()
    with view: viewEnrollmentTab()

def renderPage():
    if st.session_state.page == "Home":
        homePage()
    elif st.session_state.page == "Calendar":
        calendarPage()
    elif st.session_state.page == "Information":
        informationPage()
    elif st.session_state.page == "Trips":
        tripsPage()

if st.session_state.isLoggedIn:
    sidebar()
    renderPage()
else:
    loginPage()

