import datetime
import os
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from myapp.models import *
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
import json

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
            if b.type == 'advocate':
                try:
                    advocate = Advocates.objects.get(LOGIN=b)
                    advocate_status = AdvocateStatus.objects.filter(advocate=advocate).first()
                    if advocate_status and advocate_status.status == 'Blocked':
                        error_message = "Your account is blocked. Please contact the administrator."
                    else:
                        request.session['lid'] = b.id
                        request.session['advocate_id'] = advocate.id
                        return redirect('/advocate_home')
                except Advocates.DoesNotExist:
                    error_message = "No advocate account found for this login."
            else:
                request.session['lid'] = b.id
                if b.type == 'admin':
                    return redirect('/adminhome')
                elif b.type == 'user':
                    return redirect('/user_home')
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
    # Fetch all cases from the database
    cases = NewCase.objects.all()

    # Calculate the number of active, pending, and closed cases
    active_cases = cases.filter(case_status='Open').count()
    pending_cases = cases.filter(case_status='Pending').count()
    closed_cases = cases.filter(case_status='Closed').count()

    case_data = {
        'active_cases': active_cases,
        'pending_cases': pending_cases,
        'closed_cases': closed_cases,
    }

    context = {
        'case_data': case_data,
    }

    return render(request, 'admin/admin_home.html', context)

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
        # Try to retrieve the AdvocateStatus instance for each advocate
        advocate_status = AdvocateStatus.objects.filter(advocate=advocate).first()

        # If advocate_status is found, use its status; otherwise, default to 'Active'
        # This also checks if the status field itself is None, to ensure we get a valid value
        status = advocate_status.status if advocate_status and advocate_status.status else 'Active'

        # Append the advocate's data to the list
        advocate_data.append({
            'id': advocate.id,
            'name': advocate.name,
            'specialization': advocate.category,
            'place': advocate.place,
            'phone': advocate.phone,
            'email': advocate.email,
            'status': status,
            'image': advocate.image,
        })

    # Pass the advocate data to the template for rendering
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
    print(f"POST Data: {request.POST}")

    # Check if the advocate is authorized to manage this case
    if case.ADVOCATE.id != advocate_id:
        return JsonResponse({'status': 'error', 'message': 'You are not authorized to manage this case.'})

    if request.method == 'POST':
        try:
            # Handle evidence removal
            if 'remove_evidence' in request.POST:
                evidence_id = request.POST.get('remove_evidence')
                print(f"Attempting to remove evidence ID: {evidence_id}")

                try:
                    # Get the evidence object
                    evidence = Evidence.objects.get(id=evidence_id, case=case)

                    # Store evidence details for confirmation
                    evidence_details = {
                        'id': evidence.id,
                        'filename': evidence.file.name if evidence.file else 'No file'
                    }

                    # Delete the physical file if it exists
                    if evidence.file:
                        try:
                            # Get the full file path
                            file_path = evidence.file.path
                            if os.path.exists(file_path):
                                os.remove(file_path)
                        except Exception as e:
                            print(f"Error deleting physical file: {str(e)}")

                    # Delete the evidence record from database
                    evidence.delete()

                    return JsonResponse({
                        'status': 'success',
                        'message': 'Evidence removed successfully',
                        'removed_evidence': evidence_details
                    })

                except Evidence.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Evidence with ID {evidence_id} not found'
                    })
                except Exception as e:
                    print(f"Error removing evidence: {str(e)}")
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Error removing evidence: {str(e)}'
                    })

            # Handle evidence upload
            elif 'evidenceFile' in request.FILES:
                if 'evidenceDescription' not in request.POST:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Evidence description is required'
                    })

                for evidence_file in request.FILES.getlist('evidenceFile'):
                    fs = FileSystemStorage()
                    filename = fs.save(evidence_file.name, evidence_file)
                    evidence = Evidence(
                        case=case,
                        description=request.POST['evidenceDescription'],
                        file=filename
                    )
                    evidence.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Evidence uploaded successfully'
                })

            # Handle case update
            else:
                # Validate required fields
                required_fields = {
                    'editCaseStatus': 'Case Status',
                    'editCaseDescription': 'Case Description',
                    'editWitnessInformation': 'Witness Information',
                    'editNextHearingDate': 'Next Hearing Date'
                }

                missing_fields = [
                    field_name for field, field_name in required_fields.items()
                    if field not in request.POST or not request.POST[field].strip()
                ]

                if missing_fields:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Missing required fields: {", ".join(missing_fields)}'
                    })

                # Update case
                try:
                    case.case_status = request.POST['editCaseStatus']
                    case.case_description = request.POST['editCaseDescription']
                    case.witness_information = request.POST['editWitnessInformation']
                    case.next_hearing_date = request.POST['editNextHearingDate']
                    case.save()
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Case updated successfully'
                    })
                except Exception as e:
                    print(f"Error updating case: {str(e)}")
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Error updating case: {str(e)}'
                    })

        except Exception as e:
            print(f"Error processing request: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error processing request: {str(e)}'
            })

    # For GET requests, render the template with case details
    return render(request, 'advocate/manage_case.html', {'case': case})

@csrf_exempt
def send_notification(request, case_id):
    if request.method == 'POST':
        case = get_object_or_404(NewCase, id=case_id)
        advocate_id = request.session.get('advocate_id')

        if case.ADVOCATE.id != advocate_id:
            return JsonResponse({
                'status': 'error',
                'message': 'You are not authorized to send notifications for this case.'
            })

        recipient_id = case.USER.id  # Correctly reference the USER attribute
        message = request.POST.get('message')

        if not message:
            return JsonResponse({
                'status': 'error',
                'message': 'Message cannot be empty.'
            })

        notification = CaseNotification.objects.create(
            sender_id=advocate_id,
            recipient_id=recipient_id,
            message=message
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Notification sent successfully.'
        })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    })

def get_notifications(request):
    if not request.session.get('lid'):
        return JsonResponse({
            'status': 'error',
            'message': 'User not logged in.'
        })

    try:
        # Get the logged-in user from Login model
        login_id = request.session.get('lid')
        user = User.objects.get(LOGIN_id=login_id)

        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)

        # Get notifications for this user
        notifications = CaseNotification.objects.filter(
            recipient=user
        ).order_by('-timestamp')

        # Handle pagination
        paginator = Paginator(notifications, page_size)
        page_obj = paginator.get_page(page)

        notifications_list = []
        for notification in page_obj.object_list:
            sender_id = notification.sender.id
            sender_name = notification.sender.name

            try:
                advocate = Advocates.objects.get(LOGIN_id=sender_id)
                sender_name = advocate.name  # Use advocate's name if sender is an advocate
            except Advocates.DoesNotExist:
                pass  # If advocate not found, use sender's name

            notifications_list.append({
                'sender_name': sender_name,
                'message': notification.message,
                'timestamp': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'is_read': notification.is_read
            })

        # Mark notifications as read
        unread_notifications = notifications.filter(is_read=False)
        unread_notifications.update(is_read=True)

        return JsonResponse({
            'status': 'success',
            'notifications': notifications_list,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page': page_obj.number,
            'total_pages': paginator.num_pages
        })

    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error fetching notifications: {str(e)}'
        })

def client_notification(request):
    if not request.session.get('lid'):
        return redirect('/login')

    try:
        # Get the logged-in user from Login model
        login_id = request.session.get('lid')
        user = User.objects.get(LOGIN_id=login_id)

        # Get notifications for this user
        notifications = CaseNotification.objects.filter(
            recipient=user
        ).order_by('-timestamp')

        context = {
            'notifications': notifications,
        }

        return render(request, 'user/client_notification.html', context)

    except User.DoesNotExist:
        return redirect('/login')
    except Exception as e:
        context = {
            'error': f'Error fetching notifications: {str(e)}'
        }
        return render(request, 'user/client_notification.html', context)

def client_cases(request):
    # Get the logged-in user's ID from the session
    user_id = request.session.get('lid')

    # Fetch the user object
    user = get_object_or_404(User, LOGIN__id=user_id)

    # Fetch all cases associated with this user, including related advocate and evidence
    cases = NewCase.objects.filter(USER=user).select_related('ADVOCATE').prefetch_related('evidences')

    # Filter cases into active and closed categories
    active_cases = cases.filter(case_status__in=['Open', 'Pending'])
    closed_cases = cases.filter(case_status='Closed')

    context = {
        'active_cases': active_cases,
        'closed_cases': closed_cases,
    }

    return render(request, 'user/client_case.html', context)

def user_profile(request):
    # Check if the user is logged in
    if 'lid' not in request.session:
        print("Session variable 'lid' not found")
        return redirect('login')  # Redirect to login if the user is not logged in

    try:
        # Fetch the user details from the User model using the session variable 'lid'
        user_id = request.session['lid']
        print(f"Fetching user with ID: {user_id}")
        user = User.objects.get(LOGIN__id=user_id)
        print(f"User fetched: {user}")
    except User.DoesNotExist:
        print("User does not exist")
        return redirect('login')  # Redirect to login if the user does not exist

    if request.method == 'POST':
        # Only update fields that are submitted and not empty
        if request.POST.get('name'):
            user.name = request.POST.get('name')
        if request.POST.get('place'):
            user.place = request.POST.get('place')
        if request.POST.get('gender'):
            user.gender = request.POST.get('gender')
        if request.POST.get('post'):
            user.post = request.POST.get('post')
        if request.POST.get('phone'):
            user.phone = request.POST.get('phone')

        # Handle image URL update (if an image is uploaded)
        if request.FILES.get('image'):
            user.image = request.FILES.get('image')  # Handle file uploads correctly

        user.save()
        print("User profile updated")
        return redirect('user_profile')  # Redirect to the profile page after saving

    print("Rendering user profile page")
    return render(request, 'user/user_profile.html', {'user': user})

def user_com(request):
    if not request.session.get('lid'):
        return redirect('/login')

    if request.method == 'POST':
        type = request.POST.get('type')
        message = request.POST.get('message')
        user = User.objects.get(LOGIN__id=request.session.get('lid'))
        complaint = ComplaintFeedback.objects.create(user=user, type=type, message=message)
        return JsonResponse({'status': 'success', 'complaint_id': complaint.id})

    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    complaints = ComplaintFeedback.objects.filter(user__LOGIN__id=request.session.get('lid')).order_by('-timestamp')
    paginator = Paginator(complaints, page_size)
    page_obj = paginator.get_page(page)

    return render(request, 'user/user_com.html', {'page_obj': page_obj})

def admfeed(request):
    if not request.session.get('lid'):
        return redirect('/login')

    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        reply_message = request.POST.get('reply_message')
        complaint = get_object_or_404(ComplaintFeedback, id=complaint_id)
        complaint.admin_reply = reply_message
        complaint.status = 'Replied'
        complaint.save()
        return JsonResponse({'status': 'success'})

    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    complaints = ComplaintFeedback.objects.all().order_by('-timestamp')
    paginator = Paginator(complaints, page_size)
    page_obj = paginator.get_page(page)

    return render(request, 'admin/admfeed.html', {'page_obj': page_obj})

def get_complaint_details(request, complaint_id):
    complaint = get_object_or_404(ComplaintFeedback, id=complaint_id)
    return JsonResponse({
        'type': complaint.type,
        'user_name': complaint.user.name,
        'message': complaint.message,
        'admin_reply': complaint.admin_reply,
        'status': complaint.status,
    })

@csrf_exempt
def admin_reply(request):
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        reply_message = request.POST.get('reply_message')
        complaint = get_object_or_404(ComplaintFeedback, id=complaint_id)
        complaint.admin_reply = reply_message
        complaint.status = 'Replied'
        complaint.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


@csrf_exempt
@require_http_methods(["POST"])
def block_unblock_advocate(request, advocate_id):
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        new_status = data.get('status')

        # Get the advocate
        advocate = get_object_or_404(Advocates, id=advocate_id)

        # Get or create advocate status
        advocate_status, created = AdvocateStatus.objects.get_or_create(
            advocate=advocate,
            defaults={'status': new_status}
        )

        # Update status if different
        if not created and advocate_status.status != new_status:
            advocate_status.status = new_status
            advocate_status.save()

        return JsonResponse({
            'status': 'success',
            'new_status': new_status,
            'advocate_id': advocate_id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)