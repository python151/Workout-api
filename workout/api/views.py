from django.http import JsonResponse
from django.contrib.auth import authenticate, login as log
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_exempt

import json

from .models import Workout, Exercise, Set, Muscel

def getSessionFromReq(request):
    data = request.GET.dict()
    sessKey = data.get('session-key')
    obj = Session.objects.filter(session_key=sessKey).get()
    return obj.get_decoded()

def getSessionKey(request):
    return request.session.session_key

def login(request):
    if request.method != "GET":
        return JsonResponse({"success": False, 'message': "invalid request method"})
    
    data = request.GET.dict()

    username, password = data['username'], data['password']

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"success": False, 'message': "authentication failed"})
    
    log(request, user)
    
    return JsonResponse({
        "success": True,
        "sessionKey": getSessionKey(request),
    })

@csrf_exempt
def signup(request):
    if request.method != "POST":
        return JsonResponse({"success": False, 'message': "invalid request method"})
    
    data = request.body
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)

    username, password, email, firstName, lastName = data['username'], data['password'], data['email'], data['firstName'], data['lastName']

    user = User.objects.create_user(email=email, username=username, password=password, first_name=firstName, last_name=lastName)
    user.save()

    print(user.username)

    user = authenticate(username=username, password=password)
    log(request, user)
    
    return JsonResponse({
        "success": True,
        "session-key": getSessionKey(request),
    })
    
def getMyExercises(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "invalid request method"
        })
    
    session = getSessionFromReq(request)
    
    workouts = Workout.objects.filter(users__id=session['_auth_user_id'])
    if not workouts.exists():
        return JsonResponse({
            "success": False,
            "message": "No workouts found"
        })
    workouts = workouts.all()

    exercises = []

    for index, workout in enumerate(workouts):
        for set in workout.sets.all():
            musc = []
            for muscel in set.muscelOrMuscelGroup.all():
                musc.append(muscel.name)
            exercises.append({
                "id": set.id,
                "name": set.name,
                "type": set.type,
                "muscel": musc
            })
    
    return JsonResponse({
        "success": True,
        "exercises": exercises
    })

def getMyWorkouts(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "invalid request method"
        })
    
    session = getSessionFromReq(request)
    
    workouts = Workout.objects.filter(users__id=session['_auth_user_id'])
    if not workouts.exists():
        return JsonResponse({
            "success": False,
            "message": "No workouts found"
        })
    workouts = workouts.all()

    ret = []

    for index, workout in enumerate(workouts):
        sets = []
        for set in workout.sets.all():
            sets.append(set.name)
        ret.append({
            "sets": sets,
            "id": workout.id,
        })
        
    
    return JsonResponse({
        "success": True,
        "workouts": ret
    })

@csrf_exempt
def addWorkout(request):
    session = getSessionFromReq(request)
    if request.method != "POST":
        return JsonResponse({"success": False, 'message': "invalid request method"})
    
    data = request.body
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    
    workout = Workout.objects.create()
    workout.save()
    workout.users.add(User.objects.filter(id=session['_auth_user_id']).get())
    workout.save()

    for setv in data['sets']:
        for i in range(setv['numOfSets']):
            set = Set.objects.create(amountOfExercise=setv['setSize'], name=setv['name'])
            set.save()
            muscel = Muscel.objects.create(name=setv['muscel'])
            set.muscelOrMuscelGroup.add(muscel)
            set.save()
            workout.sets.add(set)
            workout.save()
    
    return JsonResponse({
        "success": True,
        "id": workout.id,
    })

def getWorkout(request, id):
    session = getSessionFromReq(request)
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "invalid request method"
        })
    
    workout = Workout.objects.filter(users__id=session.get('_auth_user_id'), id=id)
    
    if not workout.exists():
        return JsonResponse({
            "success": False,
            "message": "You do not have permissions or it does not exist"
        })

    workout = workout.get()
    rSets = []

    sets = workout.sets.all()
    users = workout.users.all()

    for set in sets:
        hasSet = False

        for s in rSets:
            if s['name'] == set.name:
                hasSet = True
                s['howMany'] += 1

        if not hasSet:
            rSets.append({
                "name": set.name,
                "setSize": set.amountOfExercise,
                "howMany": 1,
            })

    rUsers = [user.username for user in users]

    return JsonResponse({
        "success": True,
        "workout": {
            "sets": rSets,
            "users": rUsers,
        }
    })
            

    

    