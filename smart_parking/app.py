from flask import Flask, render_template, redirect, url_for
import random
from datetime import datetime
import pyrebase

app = Flask(__name__)

# Firebase configuration
firebaseConfig = {
    'apiKey': "M7Srx179SFSu7aGSt2uLwdg20aMOnb9iRCCy45Ka",
    'authDomain': "smartparkingsystemiot.firebaseapp.com",
    'databaseURL': "https://smartparkingsystemiot-default-rtdb.firebaseio.com/",
    'projectId': "YOUR_PROJECT_ID",
    'storageBucket': "YOUR_PROJECT_ID.appspot.com",
    'messagingSenderId': "YOUR_SENDER_ID",
    'appId': "YOUR_APP_ID",
    'measurementId': "YOUR_MEASUREMENT_ID"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# Initialize parking slots data if database empty
def initialize_slots():
    slots = db.child("parking_slots").get().val()
    if not slots:
        parking_slots = [
            {'id': 1, 'status': 'Vacant', 'selected_time': ''},
            {'id': 2, 'status': 'Occupied', 'selected_time': ''},
            {'id': 3, 'status': 'Vacant', 'selected_time': ''},
            {'id': 4, 'status': 'Occupied', 'selected_time': ''},
            {'id': 5, 'status': 'Vacant', 'selected_time': ''}
        ]
        for slot in parking_slots:
            db.child("parking_slots").child(str(slot['id'])).set({
                'id': slot['id'],
                'status': slot['status'],
                'selected_time': slot['selected_time'],
                'occupied_datetime': '',
                'vacate_datetime': ''
            })

@app.route('/')
def index():
    initialize_slots()
    slots = db.child("parking_slots").get().val()
    slots_list = []
    if slots:
        if isinstance(slots, dict):
            valid_keys = [k for k in slots.keys() if k is not None and str(k).isdigit()]
            for key in sorted(valid_keys, key=lambda x: int(x)):
                slots_list.append(slots[key])
        elif isinstance(slots, list):
            # slots is a list
            for slot in slots:
                if slot:  # skip None entries
                    slots_list.append(slot)
    return render_template('index.html', slots=slots_list)





@app.route('/select/<int:slot_id>')
def select(slot_id):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    slots = db.child("parking_slots").get().val()
    if slots:
        if isinstance(slots, dict):
            for key in slots:
                slot = slots[key]
                if int(slot['id']) == slot_id and slot['status'] == 'Vacant':
                    db.child("parking_slots").child(key).update({
                        'status': 'Occupied',
                        'selected_time': current_time,
                        'occupied_datetime': current_time,
                        'vacate_datetime': ''
                    })
                    break
        elif isinstance(slots, list):
            for index, slot in enumerate(slots):
                if slot and int(slot['id']) == slot_id and slot['status'] == 'Vacant':
                    db.child("parking_slots").child(str(index)).update({
                        'status': 'Occupied',
                        'selected_time': current_time,
                        'occupied_datetime': current_time,
                        'vacate_datetime': ''
                    })
                    break
    return redirect(url_for('index'))


@app.route('/make_all_available')
def make_all_available():
    slots = db.child("parking_slots").get().val()
    vacate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if slots:
        for key in slots:
            db.child("parking_slots").child(key).update({
                'status': 'Vacant',
                'selected_time': '',
                'vacate_datetime': vacate_time
            })
    return redirect(url_for('index'))

@app.route('/simulate')
def simulate():
    slots = db.child("parking_slots").get().val()
    if slots:
        for key in slots:
            status = random.choice(['Vacant', 'Occupied'])
            db.child("parking_slots").child(key).update({
                'status': status,
                'selected_time': '',
                'occupied_datetime': '',
                'vacate_datetime': ''
            })
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

