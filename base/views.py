import random, time, datetime, openai, json, os

from django.shortcuts import render, redirect
from django.http import JsonResponse
from agora_token_builder import RtcTokenBuilder
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Faculty_details, Users, Room, Message, RoomMember, ClassRooms, class_enrolled
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from bing_image_downloader import downloader
from LMS.settings import BASE_DIR




# Create your views here.
def login_page(request):
    return render(request,"login/login.html")

def login_into_home(request):
    user_name = request.POST.get('usr_name')
    password = request.POST.get('password')
    print(user_name,password)
    user = authenticate(username=user_name, password=password)
    print(user)
    if user is not None:
        login(request, user)
        user_detials = Users.objects.get(mail_id = user_name)
        role = user_detials.role
        usr_name = user_detials.user_name
        if role == 3 :
            return redirect('/home')
        elif role == 2:
            return redirect('/home')
        elif role == 1:
            return redirect('/home')
    else:
        return render(request,"login/login.html")

#--------------------------
def Personal_detials(request):
    usr_id = request.user.id
    usr_obj = User.objects.get(id=usr_id)
    faculty_details = Faculty_details.objects.get(mail=usr_obj.username)
    # request and get datas ..............
    role = Users.objects.get(mail_id = usr_obj.username)
    id_number = request.POST.get('idcard')
    name1 = request.POST.get('F_name')
    name2 = request.POST.get('surname')
    name = name1+' '+name2
    designation = request.POST.get('designation')
    department = request.POST.get('department')
    experience = request.POST.get('experience')
    qualififcation = request.POST.get('qualififcation')
    assessment_period = request.POST.get('AP')
    date_of_join = request.POST.get('date')
    bio = request.POST.get('about')
    d = date_of_join.split("-")
    date_formate = datetime.date(int(d[0]), int(d[1]), int(d[2]))
    my_uploaded_file = request.FILES['file_upload']
    print(date_of_join)
    usr_id = request.user.id
    usr_obj = User.objects.get(id=usr_id)
    edit = Faculty_details.objects.get(mail=usr_obj.username)
    print(edit.mail)
    edit.role=role
    edit.name=name
    edit.id_number=id_number
    edit.designation=designation
    edit.department=department
    edit.experience=experience
    edit.qualififcation=qualififcation
    edit.assessment_period=assessment_period
    edit.date_of_join=date_formate
    edit.image = my_uploaded_file
    edit.bio=bio
    edit.save()
    return render(request,"home/index.html",{'user_name':usr_obj.username,'detials':faculty_details})


#-------------------------
@login_required()
def home(request):
    usr_id = request.user.id
    usr_obj = User.objects.get(id=usr_id)
    name = Users.objects.get(mail_id=usr_obj.username)
    faculty_details = Faculty_details.objects.get(user_name=name.user_name)
    return render(request,"home/index.html",{'user_name':usr_obj.username,'detials':faculty_details})
    

def add_faculty(request):
    facultys = Faculty_details.objects.all()
    for i in facultys:
        print(i.name)
    return render(request,"admin/Admin_page_to_add_Facuilty.html",{'users':facultys})

def add_usr(request):
    usr_name = request.POST.get('user_name')
    password = request.POST.get('mail')
    role = request.POST.get('roles')
    mail = request.POST.get('password')

    facultys = Faculty_details.objects.all()
    for i in facultys:
        print(i.name)
    
    try:
        add_user = Users(user_name=usr_name,mail_id=mail,password=password,role=role)
        add_user.save()
        current_user = Users.objects.get(mail_id=mail)
        Fac_del = Faculty_details(user_name=usr_name,mail=mail,role=current_user, id_number=0, name=add_user.user_name)
        Fac_del.save()
        user = User.objects.create_user(mail, usr_name, password)
        user.save()
    except:
        print("unique are missed....")
    return render(request,"admin/Admin_page_to_add_Facuilty.html",{'users':facultys})

def add_facu(request):
    facultys = Faculty_details.objects.all()
    for i in facultys:
        print(i.name)
    return render(request,"dashboard/tables.html",{'users':facultys})


# Video chat ....

def lobby(request):
    return render(request, 'base/lobby.html')

def video_chat_room(request):
    return render(request, 'base/room.html')


def getToken(request):
    appId = "6c195af2970e48579689b47d0debf9ca"
    appCertificate = "acb5f43b05c74985aec64f691cf4311c"
    channelName = request.GET.get('channel')
    uid = random.randint(1, 230)
    expirationTimeInSeconds = 3600
    currentTimeStamp = int(time.time())
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)

    return JsonResponse({'token': token, 'uid': uid}, safe=False)


@csrf_exempt
def createMember(request):
    data = json.loads(request.body)
    member, created = RoomMember.objects.get_or_create(
        name=data['name'],
        uid=data['UID'],
        room_name=data['room_name']
    )

    return JsonResponse({'name':data['name']}, safe=False)


def getMember(request):
    uid = request.GET.get('UID')
    room_name = request.GET.get('room_name')

    member = RoomMember.objects.get(
        uid=uid,
        room_name=room_name,
    )
    name = member.name
    return JsonResponse({'name':member.name}, safe=False)

@csrf_exempt
def deleteMember(request):
    data = json.loads(request.body)
    member = RoomMember.objects.get(
        name=data['name'],
        uid=data['UID'],
        room_name=data['room_name']
    )
    member.delete()
    return JsonResponse('Member deleted', safe=False)

def gpt(queary):
    openai.api_key = "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"

    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=queary,
    temperature=0.5,
    max_tokens=60,
    top_p=1.0,
    frequency_penalty=0.5,
    presence_penalty=0.0,
    stop=["You:"]
    )
    return response.choices[0].get("text")


# chatbot ...........................................


messages = []
def chatbot(request):
    times = datetime.datetime.now()
    current_time = times.strftime("%H:%M %p")
    usr_input = request.GET.get('usr_input')
    print(usr_input)
    messages.append(usr_input)
    replay=""
    try:
        replay = gpt(usr_input)
        messages.append(replay)
    except:
        replay=None
    print(replay)
    if(replay == None):
        if usr_input != None :
            replay = gpt(usr_input)
        elif(usr_input == None) :
            replay = ""
        messages.append(replay)
    makefullcode = ""
    for i,x in enumerate(messages):
        if(i != 0 and i != 1):
            if(i%2 == 0):
                user = f"""<div id="messages" class="flex flex-col space-y-4 p-3 overflow-y-auto scrollbar-thumb-blue scrollbar-thumb-rounded scrollbar-track-blue-lighter scrollbar-w-2 scrolling-touch">
                                <div class="chat-message">
                                    <div class="flex items-end">
                                        <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
                                            <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">{x}</span></div>
                                        </div>
                                        <img src="https://images.unsplash.com/photo-1549078642-b2ba4bda0cdb?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=facearea&amp;facepad=3&amp;w=144&amp;h=144" alt="My profile" class="w-6 h-6 rounded-full order-1">
                                    </div>
                            </div>
                
                """
                makefullcode = makefullcode + user 
            else:
                system_ = f"""<div class="chat-message">
                                    <div class="flex items-end justify-end">
                                        <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-1 items-end">
                                            <div><span class="px-4 py-2 rounded-lg inline-block rounded-br-none bg-blue-600 text-white ">{x}</span></div>
                                        </div>
                                        <img src="https://images.unsplash.com/photo-1590031905470-a1a1feacbb0b?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=facearea&amp;facepad=3&amp;w=144&amp;h=144" alt="My profile" class="w-6 h-6 rounded-full order-2">
                                    </div>
                                </div>                
                """
                makefullcode = makefullcode + system_ 
    frontend = {"codes":makefullcode}

    return render(request,'chatbot/chatbot.html',frontend)
    


# ....... room chating


def chat_home(request):
    return render(request, 'chat_room/home.html')

def chat_room(request, room):
    username = request.GET.get('username') # henry
    room_details = Room.objects.get(name=room)
    return render(request, 'chat_room/room.html', {

        'username': username,
        'room': room,
        'room_details': room_details,
    })

def class_chat(request,room,username):
    if Room.objects.filter(name=room).exists():
        return redirect('/'+room+'/?username='+username)
    else:
        new_room = Room.objects.create(name=room)
        new_room.save()
        return redirect('/'+room+'/?username='+username)

def checkview(request):
    room = request.POST['room_name']
    username = request.POST['username']

    if Room.objects.filter(name=room).exists():
        return redirect('/'+room+'/?username='+username)
    else:
        new_room = Room.objects.create(name=room)
        new_room.save()
        return redirect('/'+room+'/?username='+username)

def send(request):
    message = request.POST['message']
    username = request.POST['username']
    room_id = request.POST['room_id']

    new_message = Message.objects.create(value=message, user=username, room=room_id)
    new_message.save()

def getMessages(request,  room):
    room_details = Room.objects.get(name=room)
    messages = Message.objects.filter(room=room_details.id)
    return JsonResponse({"messages": list(messages.values())})

# -------------------- Tools ------------------
def get_user_mail(request):
    usr_id = request.user.id
    usr_obj = User.objects.get(id=usr_id)
    faculty_details = Faculty_details.objects.get(mail=usr_obj.username)
    return faculty_details.mail
def get_user_name(request):
    usr_id = request.user.id
    usr_obj = User.objects.get(id=usr_id)
    faculty_details = Faculty_details.objects.get(mail=usr_obj.username)
    return faculty_details.user_name
def get_user_obj(request):
    usr_id = request.user.id
    usr_obj = User.objects.get(id=usr_id)
    faculty_details = Faculty_details.objects.get(mail=usr_obj.username)
    return faculty_details
def get_user_role(request):
    usr_id = request.user.id
    usr_obj = User.objects.get(id=usr_id)
    faculty_details = Faculty_details.objects.get(mail=usr_obj.username)
    if faculty_details.role.role == 1:
        return "Admin"
    elif faculty_details.role.role == 2:
        return "Hod"
    elif faculty_details.role.role == 3:
        return "staff"
    elif faculty_details.role.role == 4:
        return "Student"
def remove_space(string):
  out = ""
  for i in string:
    if i != " ":
      out = out +  i
  return out

#        ---------------- class room home --------------------------


def nave_home_classroom(request,pk,class_id):
    classes=[]
    img = {}
    sem = [ x for x in range(0,9)]

    if pk == "join":
            try:
                check = class_enrolled.objects.filter(mail_id=get_user_mail(request),subject_code = class_id)
            except:
                return render(request,"class_room/warning/already_enrolled.html",{"msg":"already_enrolled"})
            try:
                id_cl = ClassRooms.objects.get(subject_code = class_id)
            except:
                return render(request,"class_room/warning/already_enrolled.html",{"msg":"class rool is not avable"})
            try:
                person_obj = Users.objects.get(mail_id=get_user_mail(request))
            except:
                return render(request,"class_room/warning/already_enrolled.html",{"msg":"user not exteies"})
                
            no_usr = True
            try:
                for i in check:
                    if i.mail_id == get_user_mail(request):
                        no_usr = False
            except:
                no_usr = True
            if no_usr:
                class_en = class_enrolled(mail_id = get_user_mail(request),subject_code = class_id,class_id = id_cl.id )
                class_en.save()
            peoples=[]
            people = check = class_enrolled.objects.filter(subject_code = class_id)
            for i in people:
                person_obj = Users.objects.get(mail_id=i.mail_id)
                peoples.append(person_obj)
            detials = ClassRooms.objects.get(subject_code = class_id)
            return render(request, 'class_room/classroom.html',{'people':peoples,"detail":detials})
    else :
        return render(request, 'class_room/classroom.html')


def home_classroom(request):
    classes = []
    img = {}
    dep = []
    sem = [1,2,3,4,5,6,7,8]
    try :
        enroll_classes = class_enrolled.objects.filter(mail_id=get_user_mail(request))
        for i in enroll_classes:
            classrooms = ClassRooms.objects.get(id=i.class_id)
            classes.append(classrooms)
            if classrooms.department not in dep:
                dep.append(classrooms.department)
            try:
                item = os.listdir(classrooms.class_image)
            except:
                item=['nofiles.jpg','']
            if len(item)!=0:
                path = "..\\static\\" + classrooms.class_image.split('static\\')[1] + "\\" + item[0]
                print(path,item)
                img[classrooms.subject_code] = path

        return render(request, 'class_room/class_room_home.html',{'classes':classes,'img':img,'sem_':sem,'dep':dep,"user_name":get_user_name(request),"User_role":get_user_role(request),"usr_img":get_user_obj(request)})
        
    except:
        print("error at home_classroom function if you have any error in thin sfunction you can view this msg plz try to run without the try block")

    return render(request, 'class_room/class_room_home.html')

def add_class(request):
    return render(request, 'class_room/new_add.html')

def save_add_class(request):
    class_name = request.POST.get('class_name')
    subject_code = request.POST.get('subject_code')
    department = request.POST.get('department')
    semester = request.POST.get('semester')
    discription = request.POST.get('discription')
    
    out=os.path.join(os.path.join(BASE_DIR, 'static'),'classroom_pics')
    class_room = ClassRooms(class_image=os.path.join(os.path.join(os.path.join(BASE_DIR, 'static'),'classroom_pics'),"_".join(class_name.split(' '))+"_logos"),class_name=class_name,subject_code=subject_code,department=department,semester=semester,discription=discription,owner=Faculty_details(mail=get_user_mail(request)))
    class_room.save()
    class_id = ClassRooms.objects.get(subject_code=subject_code)
    enroll_class = class_enrolled(mail_id=get_user_mail(request),subject_code = subject_code,class_id=class_id.id)
    enroll_class.save()
    downloader.download(str("_".join(class_name.split(' ')))+"_logos", limit=2, output_dir=out, adult_filter_off=True, force_replace=False, timeout=60, verbose=True)

    return render(request, 'class_room/new_add.html')