from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time
from bson import json_util

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/', connect=False)

# Choose database
db = client['InfoSys']

# Choose collections
students = db['Students']
users = db['Users']

# Initiate Flask App
app = Flask(__name__)

users_sessions = {}

def create_session(username):
  user_uuid = str(uuid.uuid1())
  users_sessions[user_uuid] = (username, time.time())
  return user_uuid  

def is_session_valid(user_uuid):
  return user_uuid in users_sessions


# ΕΡΩΤΗΜΑ 1: Δημιουργία χρήστη
@app.route('/createUser', methods=['POST'])
def create_user():
  # Request JSON data
  data = None
  try:
    data = json.loads(request.data)
  except Exception as e:
    return Response("bad json content",status=500,mimetype='application/json')
  if data == None:
    return Response("bad request",status=500,mimetype='application/json')
  if not "username" in data or not "password" in data:
    return Response("Information incomplete",status=500,mimetype="application/json")

  
  if users.find({"username": data['username']}).count()==0:
    users.insert_one({"username": data['username'], "password": data['password']})
    return Response(data['username']+" was added to the MongoDB", status=200 , mimetype='application/json')
  else:
    return Response("A user with the given name already exists",status=400 , mimetype='application/json')


# ΕΡΩΤΗΜΑ 2: Login στο σύστημα
@app.route('/login', methods=['POST'])
def login():
  # Request JSON data
  data = None 
  try:
    data = json.loads(request.data)
  except Exception as e:
    return Response("bad json content",status=500,mimetype='application/json')
  if data == None:
    return Response("bad request",status=500,mimetype='application/json')
  if not "username" in data or not "password" in data:
    return Response("Information incomplete",status=500,mimetype="application/json")


  # Έλεγχος δεδομένων username / password
    
  # Αν η αυθεντικοποίηση είναι επιτυχής. 
  
  if users.find({"username": data['username'] , "password": data['password']}).count()!=0: 
    user_uuid=create_session(data['username'])
    res = {"uuid": user_uuid, "username": data['username']}
    return Response(json.dumps(res), mimetype='application/json', status=200) # ΠΡΟΣΘΗΚΗ STATUS
  else:
    # Μήνυμα λάθους (Λάθος username ή password)
    return Response("Wrong username or password.",mimetype='application/json',status=400) 
  
# ΕΡΩΤΗΜΑ 3: Επιστροφή φοιτητή βάσει email 
@app.route('/getStudent', methods=['GET'])
def get_student():
  # Request JSON data
  data = None 
  try:
    data = json.loads(request.data)
  except Exception as e:
    return Response("bad json content",status=500,mimetype='application/json')
  if data == None:
    return Response("bad request",status=500,mimetype='application/json')
  if not "email" in data:
    return Response("Information incomplete",status=500,mimetype="application/json")

    
  uuid = request.headers.get('authorization')
   
  if is_session_valid(uuid):
    para=students.find_one({"email":data['email']})
    student=json.loads(json_util.dumps(para))
    if students.find({"email":data['email']}).count()==1:
      return Response(json.dumps(student), mimetype='application/json', status=200)
    else:
      return Response("There is no user with that email" , status=400, mimetype="application/json") 
  else:
    return Response("Non authenticated user" , status=401, mimetype="application/json")  

   



 # Η παρακάτω εντολή χρησιμοποιείται μόνο στη περίπτωση επιτυχούς αναζήτησης φοιτητών (δηλ. υπάρχει φοιτητής με αυτό το email).
 #return Response(json.dumps(student), status=200, mimetype='application/json')

# ΕΡΩΤΗΜΑ 4: Επιστροφή όλων των φοιτητών που είναι 30 ετών
@app.route('/getStudents/thirties', methods=['GET'])
def get_students_thirty():
    
    uuid = request.headers.get('authorization')
    if is_session_valid(uuid):
      res=students.find({"yearOfBirth":1991})
      if students.find({"yearOfBirth":1991}).count()==0:
        return Response("no users of the age of 30 were found", status=400, mimetype='application/json')
      else:
        arr=[]
        for results in res:
          results['_id'] = None
          arr.append(results)
        return Response(json.dumps(arr), status=200, mimetype='application/json')
    else:
      return Response("non authenticated user", status=401, mimetype='application/json')

# ΕΡΩΤΗΜΑ 5: Επιστροφή όλων των φοιτητών που είναι τουλάχιστον 30 ετών
@app.route('/getStudents/oldies', methods=['GET'])
def get_students_overThirty():
    
  uuid = request.headers.get('authorization')
  if is_session_valid(uuid):
    res=students.find({"yearOfBirth" : {"$lte" : 1991} })
    if students.find({"yearOfBirth" : 1991}).count()==0:
      return Response("no users over the age of 30 were found", status=400, mimetype='application/json')
    else:
      arr=[]
      for results in res:
        results['_id'] = None
        arr.append(results)
      return Response(json.dumps(arr), status=200, mimetype='application/json')
  else:
    return Response("non authenticated user", status=401, mimetype='application/json')

# ΕΡΩΤΗΜΑ 6: Επιστροφή φοιτητή που έχει δηλώσει κατοικία βάσει email 
@app.route('/getStudentAddress', methods=['GET'])
def get_student_Address():
  # Request JSON data
  data = None 
  try:
    data = json.loads(request.data)
  except Exception as e:
    return Response("bad json content",status=500,mimetype='application/json')
  if data == None:
    return Response("bad request",status=500,mimetype='application/json')
  if not "email" in data:
    return Response("Information incomplete",status=500,mimetype="application/json")

  uuid = request.headers.get('authorization')
  if is_session_valid(uuid):
    para=students.find_one({"email":data['email']})
    student=json.loads(json_util.dumps(para))
    if students.find({"email":data['email']}).count()==1:
      dict={}
      dict['name']=student['name']
      dict['address'] = student['address'][0]['street']
      dict['postcode']=student['address'][0]['postcode']
      return Response(json.dumps(dict), status=200, mimetype='application/json')
    else:
      return Response("There is no user with that email or that address" , status=400, mimetype="application/json") 
      
  else:
    return Response("non authenticated user", status=401, mimetype='application/json')
    

# ΕΡΩΤΗΜΑ 7: Διαγραφή φοιτητή βάσει email 
@app.route('/deleteStudent', methods=['DELETE'])
def delete_student():
 # Request JSON data
  data = None 
  try:
    data = json.loads(request.data)
  except Exception as e:
    return Response("bad json content",status=500,mimetype='application/json')
  if data == None:
    return Response("bad request",status=500,mimetype='application/json')
  if not "email" in data:
    return Response("Information incomplete",status=500,mimetype="application/json")

  uuid = request.headers.get('authorization')
   
  if is_session_valid(uuid):
    if students.find({"email":data['email']}).count()==1:
      students.delete_one({"email":data['email']})
      return Response("student has been succesfully deleted", mimetype='application/json', status=200)
    else:
      return Response("There is no user with that email" , status=400, mimetype="application/json") 
  else:
    return Response("Non authenticated user" , status=401, mimetype="application/json")  

# ΕΡΩΤΗΜΑ 8: Εισαγωγή μαθημάτων σε φοιτητή βάσει email 
@app.route('/addCourses', methods=['PATCH'])
def add_courses():
  # Request JSON data
  data = None 
  try:
    data = json.loads(request.data)
  except Exception as e:
    return Response("bad json content",status=500,mimetype='application/json')
  if data == None:
    return Response("bad request",status=500,mimetype='application/json')
  if not "email" in data or not "courses" in data:
    return Response("Information incomplete",status=500,mimetype="application/json")

  uuid = request.headers.get('authorization')
   
  if is_session_valid(uuid):
    if students.find({"email":data['email']}).count()==1:
      students.update_one({"email": data['email']} , {'$set' : { "courses" : data['courses']}})
      return Response("student with the given email has been succesfully updated", status=200 , mimetype='application/json')
    else:
      return Response("There is no user with that email" , status=400, mimetype="application/json") 
  else:
    return Response("Non authenticated user" , status=401, mimetype="application/json") 

# ΕΡΩΤΗΜΑ 9: Επιστροφή περασμένων μαθημάτων φοιτητή βάσει email
@app.route('/getPassedCourses', methods=['GET'])
def get_courses():
  # Request JSON data
  data = None 
  try:
    data = json.loads(request.data)
  except Exception as e:
    return Response("bad json content",status=500,mimetype='application/json')
  if data == None:
    return Response("bad request",status=500,mimetype='application/json')
  if not "email" in data:
    return Response("Information incomplete",status=500,mimetype="application/json")

  uuid = request.headers.get('authorization')

  if is_session_valid(uuid):
    if students.find({"$and":[{"email" : data['email']}, {"courses": { "$exists": True }}]}).count()!=0:
      para=students.find_one({"email":data['email']})
      student=json.loads(json_util.dumps(para))
      courses_list=student['courses']
      
      arr={}
      for course in range(len(courses_list)):
        arr.update(courses_list[course])
        
      arr2={}
      for i in arr:
        if arr[i]>=5:
          arr2[i]=arr[i]

      return Response(json.dumps(arr2) , status=200, mimetype="application/json")
    else:
      return Response("There is no user with that email" , status=400, mimetype="application/json") 
  else:
    return Response("Non authenticated user" , status=401, mimetype="application/json") 



# Εκτέλεση flask service σε debug mode, στην port 5000. 

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=5000)