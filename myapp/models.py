from django.db import models

class Login(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    type = models.CharField(max_length=100)

class User(models.Model):
    LOGIN = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)
    post = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    image = models.CharField(max_length=400)
    type = models.CharField(max_length=300)

class Advocates(models.Model):
    LOGIN = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)
    post = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    image = models.CharField(max_length=400)
    category = models.CharField(max_length=300)
    type = models.CharField(max_length=300)

class Notifications(models.Model):
    ADVOCATE = models.ForeignKey(Advocates, on_delete=models.CASCADE)
    USER = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.CharField(max_length=500)
    date = models.DateField()

class Schedule(models.Model):
    ADVOCATE = models.ForeignKey(Advocates, on_delete=models.CASCADE)
    notification = models.CharField(max_length=500)
    from_time = models.CharField(max_length=100)
    to_time = models.CharField(max_length=100)
    date = models.DateField()

class Booking(models.Model):
    ADVOCATE = models.ForeignKey(Advocates, on_delete=models.CASCADE, default=1)
    USER = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Pending')
    date = models.DateTimeField()

class Case(models.Model):
    USER = models.ForeignKey(User, on_delete=models.CASCADE)
    case = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    details = models.CharField(max_length=500)
    report = models.CharField(max_length=500)
    date = models.DateField()

class Chat(models.Model):
    FROM_ID = models.ForeignKey(Login, on_delete=models.CASCADE, related_name='from_id')
    TO_ID = models.ForeignKey(Login, on_delete=models.CASCADE, related_name='to_id')
    case = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    details = models.CharField(max_length=500)
    report = models.CharField(max_length=500)
    date = models.DateField()

class Report(models.Model):
    USER = models.ForeignKey(User, on_delete=models.CASCADE)
    case = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    report = models.CharField(max_length=500)
    date = models.DateField()

class NewCase(models.Model):
    USER = models.ForeignKey(User, on_delete=models.CASCADE)
    ADVOCATE = models.ForeignKey(Advocates, on_delete=models.CASCADE, default=1)
    case_number = models.CharField(max_length=100, unique=True, default='C001')
    client_name = models.CharField(max_length=100, default='Unknown')
    case_type = models.CharField(max_length=100, default='Civil')
    filing_date = models.DateField(default='2023-10-01')
    court_name = models.CharField(max_length=100, default='Unknown Court')
    judge_assigned = models.CharField(max_length=100, blank=True, null=True)
    opposing_counsel = models.CharField(max_length=100, blank=True, null=True)
    case_status = models.CharField(max_length=50, choices=[('Open', 'Open'), ('Pending', 'Pending'), ('Closed', 'Closed')], default='Open')
    case_description = models.TextField(default='No description provided')
    evidence_list = models.TextField(blank=True, null=True)
    witness_information = models.TextField(blank=True, null=True)
    next_hearing_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.case_number

class Evidence(models.Model):
    case = models.ForeignKey(NewCase, on_delete=models.CASCADE, related_name='evidences')
    description = models.TextField()
    file = models.FileField(upload_to='evidence/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidence for Case {self.case.case_number}"

class CaseNotification(models.Model):
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE)
    sender_advocate = models.ForeignKey(Advocates, related_name='sent_notifications_advocate', on_delete=models.CASCADE,
                                        null=True, blank=True)
    recipient = models.ForeignKey(User, related_name='received_notifications', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification from {self.sender.username} to {self.recipient.username}"

class ComplaintFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=[('complaint', 'Complaint'), ('feedback', 'Feedback')])
    message = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='Pending', choices=[('Pending', 'Pending'), ('Replied', 'Replied')])

    def __str__(self):
        return f"{self.type} by {self.user.username}"

class AdvocateStatus(models.Model):
    advocate = models.OneToOneField(Advocates, on_delete=models.CASCADE, primary_key=True)
    status = models.CharField(max_length=10, default='Active')

    def __str__(self):
        return f"{self.advocate.name} - {self.status}"