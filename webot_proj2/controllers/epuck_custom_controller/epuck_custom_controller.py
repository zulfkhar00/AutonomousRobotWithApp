"""line_follower_custom controller."""

from controller import Robot, Motor
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('cadt-c6e62-firebase-adminsdk-5s3x0-c79d2728bf.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

doc_ref = db.collection(u'Actions').document(u'Main')

doc = doc_ref.get()
print(doc)
doc_ref.set({u'status': u'waiting', u'needed_item': u'nothing'})
needed_item = doc.to_dict()['needed_item']
while needed_item[-4:] != 'item':
    doc = doc_ref.get()
    needed_item = doc.to_dict()['needed_item']
doc_ref.update({u'status': u'in process'})
'''for doc in docs:
    needed_item = dict(doc.to_dict())['status']
    while needed_item[-4:] != 'item':
        db = firestore.client()
        docs = db.collection("Actions").stream()
        needed_item = dict(doc.to_dict())['status']
'''

MAX_SPEED = 6.28
speed = 0.5 * MAX_SPEED
counter = 0
# create the Robot instance.
robot = Robot()
timestep = 32

states = ["forward", "turn_right", "turn_left"]
current_state = states[0]

gs = []
gsNames = ["gs0", "gs1", "gs2", "gs-left-0", "gs-left-1", "gs-right-0", "gs-right-1"]

for i in range(7):
    gs.append(robot.getDistanceSensor(gsNames[i]))
    gs[i].enable(timestep)

leftMotor = robot.getMotor("left wheel motor")
rightMotor = robot.getMotor("right wheel motor")
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))
leftMotor.setVelocity(0.0)
rightMotor.setVelocity(0.0)

left_mark_seen = False
right_mark_seen = False
left_junction = False
right_junction = False
full_junction = False

#needed_item = 'third_item'
is_first_run = True
x_count = 0
junctions = []

while robot.step(timestep) != -1:
    gsValues = []
    for gsSensor in gs:
        gsValues.append(gsSensor.getValue())
    leftSensor = gsValues[0]
    midSensor = gsValues[1]
    rightSensor = gsValues[2]
    gsLeftSensor0 = gsValues[3]
    gsLeftSensor1 = gsValues[4]
    gsRightSensor0 = gsValues[5]
    gsRightSensor1 = gsValues[6]

    if needed_item == 'second_item':
        if len(junctions) > 2 and junctions[1] == 'left_junction' and junctions[2] == 'left_junction':
            leftMotor.setVelocity(0)
            rightMotor.setVelocity(speed)
            if x_count == 30:
                needed_item = ''
            x_count += 1
            continue

    line_right = leftSensor > 600
    line_left = rightSensor > 600
    left_junction = gsLeftSensor0 < 580 and gsLeftSensor1 < 580 and gsRightSensor1 > 650
    right_junction = gsRightSensor0 < 580 and gsRightSensor1 < 580 and gsLeftSensor1 > 650
    full_junction = gsLeftSensor1 < 580 and gsRightSensor1 < 580

    if not left_junction and not right_junction and not full_junction:
        if gsLeftSensor0 > 650 and gsLeftSensor1 < 580:
            left_mark_seen = True
            right_mark_seen = False
        elif gsRightSensor0 > 650 and gsRightSensor1 < 580:
            right_mark_seen = True
            left_mark_seen = False

    #print(leftSensor, "-", midSensor, "-", rightSensor)
    #print(gsLeftSensor1, gsLeftSensor0, " - ", gsRightSensor0, gsRightSensor1)
    #print("leftMark:", left_mark_seen, " rightMark:", right_mark_seen)
    #print("leftJ:", left_junction, "rightJ:", right_junction, "fullJ:", full_junction)
    if len(junctions) > 3:
        junctions = junctions[-3:]
        is_first_run = False
    #print(junctions)
    #print(' ')

    if left_junction:
        #print("LEFT_JUNCTION")
        junctions.append('left_junction')
        if needed_item == 'second_item':
            leftMotor.setVelocity(speed)
            rightMotor.setVelocity(MAX_SPEED)
            continue
        if left_mark_seen:
            current_state = states[2]
        else:
            current_state = states[0]
    elif right_junction:
        #print("RIGHT_JUNCTION")
        junctions.append('right_junction')
        if right_mark_seen:
            current_state = states[1]
        else:
            current_state = states[0]
    elif full_junction:
        #print("FULL_JUNCTION")
        junctions.append('full_junction')
        if left_mark_seen:
            current_state = states[2]
        elif right_mark_seen:
            current_state = states[1]
        else:
            current_state = states[0]
        if needed_item == 'first_item':
            current_state = states[2]
        elif needed_item == 'second_item' or needed_item == 'third_item':
            current_state = states[1]
    else:
        left_junction = False
        right_junction = False
        full_junction = False
        current_state = states[0]

    if current_state == states[0]:
        leftSpeed = speed
        rightSpeed = speed

        if line_right and not line_left:
            current_state = states[1]
            counter = 0
        elif line_left and not line_right:
            current_state = states[2]
            counter = 0
        elif line_left and line_right:
            if leftSensor < rightSensor:
                current_state = states[2]
                counter = 0
            elif leftSensor > rightSensor:
                current_state = states[1]
                counter = 0
        if not is_first_run and gsLeftSensor1 > 650 and gsRightSensor1 > 650 and midSensor > 650 and leftSensor > 650 and rightSensor > 650:
            leftMotor.setVelocity(0)
            rightMotor.setVelocity(0)
            doc_ref.update({u'status': u'Done!'})
            break

    if current_state == states[1]:
        leftSpeed = 1.5 * speed
        rightSpeed = 0.2 * speed
        if counter == 30:
            current_state = states[0]

    if current_state == states[2]:
        leftSpeed = 0.2 * speed
        rightSpeed = 1.5 * speed
        if counter == 30:
            current_state = states[0]

    counter += 1
    leftMotor.setVelocity(leftSpeed)
    rightMotor.setVelocity(rightSpeed)
# Enter here exit cleanup code.
