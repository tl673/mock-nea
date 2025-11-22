import streamlit as st
from datetime import date, datetime
import pandas as pd

def createTripTab():
    st.subheader("Plan a New School Trip")
    teachers = getTeachers()
    teacherOptions = {f"{t['first']} {t['second']} (ID: {t['teacherID']})": t['teacherID'] for t in teachers}

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
                teacherName = st.selectbox("Lead Teacher", options=keys)
                teacherId = teacherOptions.get(teacherName)
        with col2:
            startDate = st.date_input("Start Date", min_value=date.today())
            endDate = st.date_input("End Date", min_value=startDate)
            tripType = st.selectbox("Trip Type", ["Day Trip", "Residential (UK)", "Residential (Overseas)", "Remote Learning"])
            national = st.checkbox("National (UK-based)", value=True)
            activeStatus = st.checkbox("Active Status", value=True)

        submitted = st.form_submit_button("Create Trip")
        if submitted:
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
    allTrips = getAllTrips()
    if not allTrips:
        st.info("No trips available.")
        return

    tripOptions = {f"{t['title']} (ID: {t['tripID']})": t['tripID'] for t in allTrips}
    selected = st.selectbox("Select Trip", tripOptions.keys(), key="edit_trip_select")
    tripId = tripOptions[selected]
    trip = getTrip(tripId)
    if not trip:
        st.warning("Trip not found.")
        return

    currentStart = datetime.strptime(trip['startDate'], '%Y-%m-%d').date()
    currentEnd = datetime.strptime(trip['endDate'], '%Y-%m-%d').date()

    teachers = getTeachers()
    teacherOptions = {f"{t['first']} {t['second']} (ID: {t['teacherID']})": t['teacherID'] for t in teachers}

    with st.form("edit_trip_form"):
        col1, col2 = st.columns(2)
        with col1:
            newTitle = st.text_input("Trip Title", value=trip['title'])
            newDestination = st.text_input("Destination", value=trip['destination'])
            newSubject = st.text_input("Subject Area", value=trip['subject'])
            teacherKeys = list(teacherOptions.keys())
            idx = next((i for i, k in enumerate(teacherKeys) if teacherOptions[k] == trip['teacherID']), 0)
            newTeacher = st.selectbox("Lead Teacher", options=teacherKeys, index=idx)
            newTeacherId = teacherOptions[newTeacher]
        with col2:
            newStart = st.date_input("Start Date", value=currentStart)
            newEnd = st.date_input("End Date", value=currentEnd, min_value=newStart)
            tripTypes = ["Day Trip", "Residential (UK)", "Residential (Overseas)", "Remote Learning"]
            idx = tripTypes.index(trip['tripType']) if trip['tripType'] in tripTypes else 0
            newType = st.selectbox("Trip Type", tripTypes, index=idx, key="edit_trip_type")

        c1, c2 = st.columns(2)
        with c1:
            newNational = st.checkbox("National", value=(trip['national'] == 1))
        with c2:
            newActive = st.checkbox("Active", value=(trip['activeStatus'] == 1))

        submitted = st.form_submit_button("Save Changes")
        if submitted:
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
    allTrips = getAllTrips()
    if not allTrips:
        st.info("No trips available.")
        return

    tripOptions = {f"{t['title']} (ID: {t['tripID']})": t['tripID'] for t in allTrips}
    selected = st.selectbox("Select Trip to Delete", tripOptions.keys(), key="delete_trip_select")
    tripId = tripOptions[selected]
    title = selected.split(" (ID:")[0]

    st.warning(f"Delete '{title}'?")
    if st.button("Confirm Delete", key="confirm_delete_button"):
        deleteTrip(tripId)
        st.success("Deleted.")
        st.rerun()


def viewEnrollmentTab():
    st.subheader("View Enrollment")
    allTrips = getAllTrips()
    if not allTrips:
        st.info("No trips available.")
        return

    tripOptions = {f"{t['title']} (ID: {t['tripID']})": t['tripID'] for t in allTrips}
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

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download CSV",
            df.to_csv(index=False).encode('utf-8'),
            f"enrollment_trip_{tripId}.csv",
            "text/csv",
            key="download_enrollment"
        )
    else:
        st.warning("No students enrolled.")

