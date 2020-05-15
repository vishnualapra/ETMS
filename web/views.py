from django.shortcuts import render,loader
from django.http import HttpResponse, HttpResponseRedirect
import requests
from urllib.parse import urlencode
import json

# Create your views here.

def superuser_validation(fun):
    def wrapper(request, *args, **kwargs):
        try:
            user = request.session['user']
            if user["user"]["is_superuser"] is True:
                return fun(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('/dashboard/')
        except:
            return HttpResponseRedirect('/login/')
        return HttpResponseRedirect('/login/')
    return wrapper


def user_validation(fun):
    def wrapper(request, *args, **kwargs):
        try:
            user = request.session['user']
            return fun(request, *args, **kwargs)
        except:
            return HttpResponseRedirect('/login/')
        return HttpResponseRedirect('/login/')
    return wrapper


@user_validation
def index(request):
    return HttpResponseRedirect('/dashborad/')

    
def login(request):
    host = request.get_host()
    msg = ''
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('pass')
        data = {'username':username,'password':password}
        url = str(request.scheme)+"://"+ host +"/api/login/"
        print(url)
        payload = urlencode(data)
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.request("POST", url, headers=headers, data = payload)

        data = json.loads(response.text)
        if data["success"] is True:
            request.session['user'] = data['data']
            return HttpResponseRedirect('/dashboard/')
        else:
            msg = "wrong credentials"

    template = loader.get_template('master/login.html')
    return HttpResponse(template.render({"msg":msg},request))

@user_validation
def logout(request):
    
    try:
        user = request.session['user']
        host = request.get_host()
        url = str(request.scheme)+"://"+ host +"/api/logout/"

        payload = ""
        headers = {
            'Authorization': "token "+ user["token"],
            'cache-control': "no-cache",
            }
        
        response = requests.request("GET", url, data=payload, headers=headers)
        
        data = json.loads(response.text)
        if data['success'] is True:
            del request.session['user']
            return HttpResponseRedirect('/login/')
        else:
            del request.session['user']
            return HttpResponseRedirect('/login/')
    except:
        return HttpResponseRedirect('/login/')
    

@user_validation
def dashboard(request):
    url = str(request.scheme)+"://"+ request.get_host() +"/api/count/"

    payload = {}
    headers = {
    'Authorization': 'token '+ str(request.session['user']['token']),
    }

    response = requests.request("GET", url, headers=headers, data = payload)

    data = json.loads(response.text)
    template = loader.get_template('master/dashboard.html')
    return HttpResponse(template.render({"page":"dashboard",'data':data},request))


@superuser_validation
def team(request):
    msg = ""
    addmsg = ""
    host = request.get_host()
    if request.method == "POST" and 'email' in request.POST:
        try:
            email = request.POST.get('email')
            name = request.POST.get('name')
            password = request.POST.get('password')
            dat = {'username':email,"email":email,"password":password,"is_active":True,"first_name":name}
            url = str(request.scheme)+"://"+ host +"/api/user/"
            payload = urlencode(dat)
            headers = {
            'Authorization': 'token '+ str(request.session['user']['token']),
            'Content-Type': 'application/x-www-form-urlencoded',
            }

            response = requests.request("POST", url, headers=headers, data = payload)

            dat = json.loads(response.text)
            if 'id' in dat.keys():
                addmsg = "success"
            else:
                addmsg = "failed"

        except:
            addmsg = "failed"
    try:
        url = str(request.scheme)+"://"+ host +"/api/listusers/"
        payload = {}
        headers = {
        'Authorization': 'token ' +  str(request.session["user"]["token"]),
        }

        response = requests.request("GET", url, headers=headers, data = payload)
        data = json.loads(response.text)
        msg = ''
    except:
        msg = "errorload"
        data = None
    template = loader.get_template('master/team.html')
    return HttpResponse(template.render({"page":"team","data":data,"msg":msg,"addmsg":addmsg},request))


@user_validation
def project(request):
    msg = ''
    addmsg = ''
    data = []

    if request.method == "POST" and 'name' in request.POST:
        try:
            name = request.POST.get('name')
            details = request.POST.get('details')
            dat = {'project_name':name,"project_details":details}
            url = str(request.scheme)+"://"+ request.get_host() +"/api/project/"
            payload = urlencode(dat)
            headers = {
            'Authorization': 'token '+ str(request.session['user']['token']),
            'Content-Type': 'application/x-www-form-urlencoded',
            }

            response = requests.request("POST", url, headers=headers, data = payload)

            dat = json.loads(response.text)
            print(dat,'****')
            if 'id' in dat.keys():
                addmsg = "success"
            else:
                addmsg = "failed"

        except Exception as e:
            print(str(e))
            addmsg = "failed"
    url = str(request.scheme)+"://"+ request.get_host() +"/api/project/"
    payload = {}
    headers = {
    'Authorization': 'token ' +  str(request.session["user"]["token"]),
    }
    response = requests.request("GET", url, headers=headers, data = payload)
    data = json.loads(response.text)
    template = loader.get_template('master/projects.html')
    return HttpResponse(template.render({"page":"project","data":data,"msg":msg,"addmsg":addmsg},request))


@user_validation
def sproject(request,id):
    msg = ''
    data = []
    addmsg = ''
    addtask = ''
    stmsg = ''
    if request.method == 'POST' and 'complete' in request.POST:
        url = str(request.scheme)+"://"+ request.get_host() +"/api/projectstatus/"+str(id)+"/"
        payload = {}
        headers = {
        'Authorization': 'token ' +  str(request.session["user"]["token"]),
        }

        response = requests.request("PUT", url, headers=headers, data = payload)
        res = json.loads(response.text)
        if res['success'] is True:
            stmsg = "success"
        else:
            stmsg = res['msg']
    if request.method == "POST" and 'team' in request.POST:
        team = request.POST.get('team')
        url = str(request.scheme)+"://"+ request.get_host() +"/api/team/"
        dat = { 'project':id,"team_member":team }
        payload = urlencode(dat)
        headers = {
        'Authorization': 'token ' +  str(request.session["user"]["token"]),
        'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.request("POST", url, headers=headers, data = payload)

        ateam = json.loads(response.text)
        if 'id' in ateam.keys():
            addmsg = "success"
        else:
            addmsg = "failed"
    if request.method == "POST" and 'name' in request.POST:
        title = request.POST.get('name')
        details = request.POST.get('details')
        teamm = request.POST.get('steam')
        url = str(request.scheme)+"://"+ request.get_host() +"/api/task/"
        dat = {'title':title,'description':details,'project_team':teamm}
        payload = urlencode(dat)
        headers = {
        'Authorization': 'token ' +  str(request.session["user"]["token"]),
        'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.request("POST", url, headers=headers, data = payload)
        atask = json.loads(response.text)
        if 'id' in atask.keys():
            addtask = "success"
        else:
            addtask = "failed"
    
    if request.session['user']['user']['is_superuser'] is True:
        url = str(request.scheme)+"://"+ request.get_host() +"/api/task/?project=" + str(id)
    else:
        url = str(request.scheme)+"://"+ request.get_host() +"/api/task/?project=" + str(id) + "&team=" + str(request.session['user']['user']['id'])
    payload = {}
    headers = {
        'Authorization': 'token ' +  str(request.session["user"]["token"]),
    }

    response = requests.request("GET", url, headers=headers, data = payload)

    tasks = json.loads(response.text)

    url = str(request.scheme)+"://"+ request.get_host() +"/api/team/?project=" + str(id)
    payload = {}
    headers = {
    'Authorization': 'token ' +  str(request.session["user"]["token"]),
    }

    response = requests.request("GET", url, headers=headers, data = payload)

    projectteam = json.loads(response.text)

    url = str(request.scheme)+"://"+ request.get_host() +"/api/project/" + str(id) +"/"

    payload = {}
    headers = {
    'Authorization': 'token '+ str(request.session['user']['token']),
    }

    response = requests.request("GET", url, headers=headers, data = payload)
    project = json.loads(response.text)

    url = str(request.scheme)+"://"+  request.get_host() +"/api/listusers/"
    payload = {}
    headers = {
        'Authorization': 'token ' +  str(request.session["user"]["token"]),
        }

    response = requests.request("GET", url, headers=headers, data = payload)
    team = json.loads(response.text)

    template = loader.get_template('master/project.html')
    return HttpResponse(template.render({"page":"project","data":data,"msg":msg,"addmsg":addmsg,"project":project,'team':team,
    'projectteam':projectteam,'tasks':tasks,'stmsg':stmsg},request))


@user_validation
def task(request,id,tid):
    msg = ''
    data = []
    addmsg = ''
    addtask = ''
    if request.method == "POST" and 'changestat' in request.POST:
        stat = request.POST.get('changestat')
        url = str(request.scheme)+"://"+ request.get_host() +"/api/gettask/"+str(tid)+"/"+stat+"/"

        payload = {}
        headers = {
        'Authorization': 'token ' +  str(request.session["user"]["token"]),
        }

        response = requests.request("PUT", url, headers=headers, data = payload)

        astat = json.loads(response.text)
        if astat['success'] is True:
            addmsg = "success"
        else:
            addmsg = "failed"
    if request.method == "POST" and 'comment' in request.POST:
        
        details = request.POST.get('comment')
        url = str(request.scheme)+"://"+ request.get_host() +"/api/comment/"
        dat = {'comment':details,'user':request.session['user']['user']['id'],'task':tid}
        payload = urlencode(dat)
        headers = {
        'Authorization': 'token ' +  str(request.session["user"]["token"]),
        'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.request("POST", url, headers=headers, data = payload)
        atask = json.loads(response.text)
        if 'id' in atask.keys():
            addtask = "success"
        else:
            addtask = "failed"
    url = str(request.scheme)+"://"+ request.get_host() +"/api/gettask/"+str(tid)+"/"
    payload = {}
    headers = {
    'Authorization': 'token ' +  str(request.session["user"]["token"]),
    }

    response = requests.request("GET", url, headers=headers, data = payload)
    task = json.loads(response.text)

    url = str(request.scheme)+"://"+ request.get_host() +"/api/project/" + str(id) +"/"

    payload = {}
    headers = {
    'Authorization': 'token '+ str(request.session['user']['token']),
    }

    response = requests.request("GET", url, headers=headers, data = payload)
    project = json.loads(response.text)

    url = str(request.scheme)+"://"+ request.get_host() +"/api/comment/?task=" + str(tid) 

    payload = {}
    headers = {
    'Authorization': 'token '+ str(request.session['user']['token']),
    }

    response = requests.request("GET", url, headers=headers, data = payload)
    comments = json.loads(response.text)
    template = loader.get_template('master/task.html')
    return HttpResponse(template.render({"page":"project","data":data,"msg":msg,"addmsg":addmsg,"project":project,
    'task':task,'comments':comments},request))


@superuser_validation
def reports(request):
    msg = ""
    addmsg = ""
    host = request.get_host()
    try:
        url = str(request.scheme)+"://"+ request.get_host() +"/api/reports/"

        payload = {}
        headers = {
        'Authorization': 'token '+ str(request.session['user']['token']),
        }

        response = requests.request("GET", url, headers=headers, data = payload)

        print(response.text.encode('utf8'))
        data = json.loads(response.text)
        msg = ''
    except:
        msg = "errorload"
        data = None
    template = loader.get_template('master/reports.html')
    return HttpResponse(template.render({"page":"reports","data":data,"msg":msg,"addmsg":addmsg},request))


def job(request):
    try:
        
        url = str(request.scheme)+"://"+ request.get_host() +"/api/report/"
        payload = {}
        headers = {
        }
        response = requests.request("GET", url, headers=headers, data = payload)
        msg = True
    except Exception as e:
        msg = str(e)
    return HttpResponse(msg)