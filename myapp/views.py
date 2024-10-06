import datetime
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from myapp.models import *
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return render(request, 'index.html')

def login(request):
    error_message = None
    if 'submit' in request.POST:
        username = request.POST['username']
        password = request.POST['password']

        a = Login.objects.filter(username=username, password=password)
        if a.exists():
            b = Login.objects.get(username=username, password=password)
            request.session['lid'] = b.id
            if b.type == 'admin':
                return redirect('/adminhome')
            elif b.type == 'user':
                return redirect('/user_home')
            elif b.type == 'advocate':
                advocate = Advocates.objects.get(LOGIN=b)
                request.session['advocate_id'] = advocate.id
                return redirect('/advocate_home')
            else:
                error_message = "Invalid user type"
        else:
            error_message = "Invalid email or password"

    return render(request, 'login.html', {'error_message': error_message})

def reg(request):
    if request.method == 'POST':
        # Initialize an empty dictionary to store field-specific errors
        field_errors = {}

        # Extract form data
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        gender = request.POST.get('gender', '')
        phone = request.POST.get('phone', '')
        place = request.POST.get('place', '')
        pin = request.POST.get('pin', '')
        type = request.POST.get('type', '')
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm', '')

        # Validate required fields
        required_fields = ['name', 'email', 'gender', 'phone', 'place', 'pin', 'type', 'password', 'confirm']
        for field in required_fields:
            if not request.POST.get(field):
                field_errors[field] = f"{field.capitalize()} is required"

        # Check if the email is already registered
        if Login.objects.filter(username=email).exists():
            field_errors['email'] = "This email is already registered"

        # Check if passwords match
        if password != confirm:
            field_errors['confirm'] = "Passwords do not match"

        # Check if image is provided
        if 'image' not in request.FILES:
            field_errors['image'] = "Image is required"

        # If there are any errors, return to the registration form with error messages
        if field_errors:
            return render(request, 'login.html', {
                'field_errors': field_errors,
                'form_data': request.POST  # Send back the form data to pre-fill the fields
            })

        # If all validations pass, proceed with registration
        image = request.FILES['image']
        fs = FileSystemStorage()
        date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.jpg'
        fs.save(date, image)
        path = fs.url(date)

        # Save the user credentials in the Login table
        a = Login(username=email, password=password, type=type)
        a.save()

        if type == "advocate":
            # Save data in the Advocates table
            category = request.POST.get('category', '')
            if not category:
                field_errors['category'] = "Category is required for advocates"
                return render(request, 'login.html', {
                    'field_errors': field_errors,
                    'form_data': request.POST
                })

            adv = Advocates(
                LOGIN=a, name=name, place=place, gender=gender, post=pin,
                email=email, phone=phone, category=category, type=type, image=path
            )
            adv.save()
        else:
            # Save data in the User table for other types (e.g., "client")
            o = User(
                LOGIN=a, name=name, place=place, gender=gender, post=pin,
                email=email, phone=phone, type=type, image=path
            )
            o.save()

        return redirect('/login')

    # If it's a GET request, just render the registration form
    return render(request, 'login.html')

def adminhome(request):
    return render(request, 'admin/admin_home.html')

def advocate_home(request):
    return render(request, 'advocate/advocate_home.html')

def user_home(request):
    return render(request, 'user/user_home.html')

def admclient(request):
    # Fetch all users (clients) from the database
    clients = User.objects.filter(LOGIN__type='user')

    # Create a list to store client data
    client_data = []

    for client in clients:
        client_data.append({
            'name': client.name,
            'email': client.email,
            'phone': client.phone,
            'place': client.place,
            'image': client.image,
            'type': client.type,
            'status': 'Active' if client.LOGIN.type == 'user' else 'Inactive'
        })

    context = {
        'clients': client_data
    }

    return render(request, 'admin/client.html', context)

def adCase(request):
    cases = NewCase.objects.all()
    users = User.objects.all()
    advocates = Advocates.objects.all()
    return render(request, 'admin/adcase.html', {'cases': cases, 'users': users, 'advocates': advocates})

@csrf_exempt
def add_case(request):
    if request.method == 'POST':
        case_number = request.POST['caseNumber']
        client_name = request.POST['clientName']
        case_type = request.POST['caseType']
        filing_date = request.POST['filingDate']
        court_name = request.POST['courtName']
        judge_assigned = request.POST['judgeAssigned']
        opposing_counsel = request.POST['opposingCounsel']
        case_status = request.POST['caseStatus']
        case_description = request.POST['caseDescription']
        evidence_list = request.POST['evidenceList']
        witness_information = request.POST['witnessInformation']
        next_hearing_date = request.POST['nextHearingDate']
        user_id = request.POST['user']
        advocate_id = request.POST['advocate']

        user = User.objects.get(id=user_id)
        advocate = Advocates.objects.get(id=advocate_id)

        case = NewCase(
            USER=user,
            ADVOCATE=advocate,
            case_number=case_number,
            client_name=client_name,
            case_type=case_type,
            filing_date=filing_date,
            court_name=court_name,
            judge_assigned=judge_assigned,
            opposing_counsel=opposing_counsel,
            case_status=case_status,
            case_description=case_description,
            evidence_list=evidence_list,
            witness_information=witness_information,
            next_hearing_date=next_hearing_date
        )
        case.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def view_case(request, case_id):
    case = get_object_or_404(NewCase, id=case_id)
    case_details = {
        'caseNumber': case.case_number,
        'clientName': case.client_name,
        'caseType': case.case_type,
        'filingDate': case.filing_date,
        'courtName': case.court_name,
        'judgeAssigned': case.judge_assigned,
        'opposingCounsel': case.opposing_counsel,
        'caseStatus': case.case_status,
        'caseDescription': case.case_description,
        'evidenceList': case.evidence_list,
        'witnessInformation': case.witness_information,
        'nextHearingDate': case.next_hearing_date,
        'user': case.USER.id,
        'advocate': case.ADVOCATE.id
    }
    return JsonResponse(case_details)

@csrf_exempt
def edit_case(request, case_id):
    case = get_object_or_404(NewCase, id=case_id)
    if request.method == 'POST':
        case.case_number = request.POST['editCaseNumber']
        case.client_name = request.POST['editClientName']
        case.case_type = request.POST['editCaseType']
        case.filing_date = request.POST['editFilingDate']
        case.court_name = request.POST['editCourtName']
        case.judge_assigned = request.POST['editJudgeAssigned']
        case.opposing_counsel = request.POST['editOpposingCounsel']
        case.case_status = request.POST['editCaseStatus']
        case.case_description = request.POST['editCaseDescription']
        case.evidence_list = request.POST['editEvidenceList']
        case.witness_information = request.POST['editWitnessInformation']
        case.next_hearing_date = request.POST['editNextHearingDate']
        case.USER = User.objects.get(id=request.POST['editUser'])
        case.ADVOCATE = Advocates.objects.get(id=request.POST['editAdvocate'])
        case.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def delete_case(request, case_id):
    case = get_object_or_404(NewCase, id=case_id)
    case.delete()
    return JsonResponse({'status': 'success'})

def adAdv(request):
    # Fetch all advocates from the database
    advocates = Advocates.objects.all()

    # Create a list to store advocate data
    advocate_data = []

    for advocate in advocates:
        advocate_data.append({
            'id': advocate.id,
            'name': advocate.name,
            'specialization': advocate.category,
            'place': advocate.place,
            'phone': advocate.phone,
            'email': advocate.email,
            'status': 'Active' if advocate.LOGIN.type == 'advocate' else 'Inactive',
            'image': advocate.image,
        })

    context = {
        'advocates': advocate_data
    }

    return render(request, 'admin/adadv.html', context)

def bookAd(request):
    advocates = Advocates.objects.all()

    # Create a list to store advocate data
    advocate_data = []

    for advocate in advocates:
        advocate_data.append({
            'id': advocate.id,
            'name': advocate.name,
            'specialization': advocate.category,
            'image': advocate.image,
        })

    context = {
        'advocates': advocate_data
    }

    return render(request, 'user/bookad.html', context)

def submit_booking(request):
    if request.method == 'POST':
        advocate_id = request.POST.get('advocate_id')
        booking_date = request.POST.get('booking_date')
        booking_time = request.POST.get('booking_time')

        # Combine date and time into a datetime object
        booking_datetime = timezone.datetime.strptime(f"{booking_date} {booking_time}", "%Y-%m-%d %H:%M")

        # Get the advocate and user
        advocate = Advocates.objects.get(id=advocate_id)
        user = User.objects.get(LOGIN__id=request.session.get('lid'))

        # Create a new booking
        booking = Booking(
            ADVOCATE=advocate,
            USER=user,
            status='Pending',
            date=booking_datetime
        )
        booking.save()

        return redirect('/user_home')

    return redirect('/bookAd')

def booking_status(request):
    # Assuming the user ID is stored in the session as 'lid'
    user_id = request.session.get('lid')
    user = get_object_or_404(User, LOGIN__id=user_id)
    bookings = Booking.objects.filter(USER=user)

    context = {
        'bookings': bookings
    }

    return render(request, 'user/booking_status.html', context)

def advocate_schedule(request):
    advocate_id = request.session.get('lid')
    advocate = get_object_or_404(Advocates, LOGIN__id=advocate_id)
    bookings = Booking.objects.filter(ADVOCATE=advocate, status='Pending')

    context = {
        'advocate': advocate,
        'bookings': bookings
    }

    return render(request, 'advocate/advocate_schedule.html', context)

@csrf_exempt
def update_booking_status(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        status = request.POST.get('status')

        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = status
        booking.save()

        if status == 'Accepted':
            # Add the booking to the advocate's calendar
            event = {
                'title': f"Appointment with {booking.USER.name}",
                'start': booking.date.isoformat(),
                'end': (booking.date + datetime.timedelta(hours=1)).isoformat(),
                'className': 'fc-event-meeting'
            }
            return JsonResponse({'status': 'success', 'event': event})

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})


def advocate_cases(request, advocate_id):
    advocate = get_object_or_404(Advocates, id=advocate_id)
    cases = NewCase.objects.filter(ADVOCATE=advocate)
    return render(request, 'advocate/manage_case.html', {'cases': cases, 'advocate': advocate})


@csrf_exempt
def manage_case(request, case_id):
    case = get_object_or_404(NewCase, id=case_id)

    # Get the advocate ID from the session
    advocate_id = request.session.get('advocate_id')

    # Debugging statements
    print(f"Advocate ID from session: {advocate_id}")
    print(f"Advocate ID from case: {case.ADVOCATE.id}")

    # Check if the advocate is authorized to manage this case
    if case.ADVOCATE.id != advocate_id:
        return JsonResponse({'status': 'error', 'message': 'You are not authorized to manage this case.'})

    if request.method == 'POST':
        # Debugging statements to print POST data
        print(f"POST Data: {request.POST}")

        case.case_status = request.POST['editCaseStatus']
        case.case_description = request.POST['editCaseDescription']
        case.witness_information = request.POST['editWitnessInformation']
        case.next_hearing_date = request.POST['editNextHearingDate']
        case.save()

        if 'evidenceFile' in request.FILES:
            for evidence_file in request.FILES.getlist('evidenceFile'):
                fs = FileSystemStorage()
                filename = fs.save(evidence_file.name, evidence_file)
                evidence = Evidence(
                    case=case,
                    description=request.POST['evidenceDescription'],
                    file=filename
                )
                evidence.save()

        # Handle removal of evidence files
        if 'remove_evidence' in request.POST:
            for evidence_id in request.POST.getlist('remove_evidence'):
                evidence = Evidence.objects.get(id=evidence_id)
                evidence.file.delete()
                evidence.delete()

        return JsonResponse({'status': 'success'})

    return render(request, 'advocate/manage_case.html', {'case': case})