# @shared_task
def send_otp_email(user_email, otp_code):
    print(user_email, otp_code)
    # user = get_user_model().objects.filter(id=user_id).first()
    # current_site = get_current_site(request)
    mail_subject = _('کد ورود یکبار مصرف')
    # context = {
    #     'user': user,
    # }

    # msg = render_to_string('core/otp_email.html', context)
    msg = f"کد ورود شما: {otp_code}"
    email = EmailMessage(mail_subject, msg, to=[user_email])
    print('before send email')
    email.send()
    print('after send email')
    # return HttpResponse(_('برو ایمیل چک کن'))


@shared_task
def send_sms(phone, otp_code):
    print(otp_code)
    # phone_number = '983000685995'
    # phone_number2 = '985000248725'
    group_id = random.randint(0, 99999999)
    ws = restfulapi(settings.SMS_USER, settings.SMS_PASSWORD)
    msg = f'با سلام کد احراز هویت شما \n {otp_code}'
    res = ws.SendMessage(PhoneNumber=settings.SMS_PHONE, Message=msg, Mobiles=[phone],
                         UserGroupID=str(group_id), SendDateInTimeStamp=time.time())
    print(res)