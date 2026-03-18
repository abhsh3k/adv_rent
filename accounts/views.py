from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from toolx.otp import set_otp, verify_otp, clear_otp
from toolx.notifications import send_otp_email, send_otp_sms
from django.contrib.admin.views.decorators import staff_member_required

User = get_user_model()

def register(request):
    if request.method == 'POST':
        username     = request.POST.get('username', '').strip()
        first_name   = request.POST.get('first_name', '').strip()
        last_name    = request.POST.get('last_name', '').strip()
        password1    = request.POST.get('password1', '')
        password2    = request.POST.get('password2', '')
        email        = request.POST.get('email', '').strip()
        country_code = request.POST.get('country_code', '').strip()
        phone_number = request.POST.get('phone', '').strip()
        phone        = f"{country_code}{phone_number}" if phone_number else ''
        role         = request.POST.get('role', 'renter')

        # ── Validations ──────────────────────────────────────────────
        if not username:
            messages.error(request, 'Username is required.')
            return render(request, 'register.html', {'form': request.POST})

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html', {'form': request.POST})

        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'register.html', {'form': request.POST})

        if not email and not phone:
            messages.error(request, 'Please provide either an email or phone number.')
            return render(request, 'register.html', {'form': request.POST})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'register.html', {'form': request.POST})

        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'register.html', {'form': request.POST})

        if phone and User.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already registered.')
            return render(request, 'register.html', {'form': request.POST})

        # ── Create inactive user ──────────────────────────────────────
        user = User.objects.create_user(
            username   = username,
            password   = password1,
            first_name = first_name,
            last_name  = last_name,
            email      = email,
            phone      = phone or None,   # store None instead of empty string
            role       = role,
            is_active  = False,           # inactive until OTP verified
        )

        # ── Send OTP ──────────────────────────────────────────────────
        if email:
            otp = set_otp(user, 'email')
            send_otp_email(user, otp)
            request.session['otp_user_id'] = user.pk
            request.session['otp_method']  = 'email'
            messages.info(request, f'A verification code was sent to {email}.')
        else:
            otp = set_otp(user, 'phone')
            send_otp_sms(user, otp)
            request.session['otp_user_id'] = user.pk
            request.session['otp_method']  = 'phone'
            messages.info(request, f'A verification code was sent to {phone}.')

        return redirect('verify_otp')

    # GET request
    return render(request, 'register.html', {'form': {}})


def verify_otp_view(request):
    user_id = request.session.get('otp_user_id')
    method  = request.session.get('otp_method')

    if not user_id:
        return redirect('register')

    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        code = request.POST.get('otp_code', '').strip()

        if verify_otp(user, code):
            clear_otp(user)
            user.is_active = True
            if method == 'email':
                user.email_verified = True
            else:
                user.phone_verified = True
            user.save()

            # clean session
            del request.session['otp_user_id']
            del request.session['otp_method']

            login(request, user)
            messages.success(request, f'Welcome to ToolX, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid or expired code. Try again.')

    return render(request, 'verify_otp.html', {
        'method': method,
        'contact': user.email if method == 'email' else user.phone,
    })


def resend_otp(request):
    user_id = request.session.get('otp_user_id')
    method  = request.session.get('otp_method')

    if not user_id:
        return redirect('register')

    user = get_object_or_404(User, pk=user_id)
    otp  = set_otp(user, method)

    if method == 'email':
        send_otp_email(user, otp)
        messages.info(request, 'New code sent to your email.')
    else:
        send_otp_sms(user, otp)
        messages.info(request, 'New code sent to your phone.')

    return redirect('verify_otp')


def forgot_password(request):
    if request.method == 'POST':
        contact = request.POST.get('contact', '').strip()

        # find user by email or phone
        user = None
        method = None
        if '@' in contact:
            user = User.objects.filter(email=contact).first()
            method = 'email'
        else:
            user = User.objects.filter(phone=contact).first()
            method = 'phone'

        if not user:
            messages.error(request, 'No account found with that email or phone.')
            return render(request, 'forgot_password.html', {})

        otp = set_otp(user, method)
        if method == 'email':
            send_otp_email(user, otp)
        else:
            send_otp_sms(user, otp)

        request.session['reset_user_id'] = user.pk
        request.session['reset_method']  = method
        messages.info(request, f'Reset code sent to your {method}.')
        return redirect('reset_password')

    return render(request, 'forgot_password.html', {})


def reset_password(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('forgot_password')

    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        code      = request.POST.get('otp_code', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not verify_otp(user, code):
            messages.error(request, 'Invalid or expired code.')
            return render(request, 'reset_password.html', {})

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'reset_password.html', {})

        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'reset_password.html', {})

        clear_otp(user)
        user.set_password(password1)
        user.save()

        del request.session['reset_user_id']
        del request.session['reset_method']

        messages.success(request, 'Password reset! Please log in.')
        return redirect('login')

    return render(request, 'reset_password.html', {})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            if not user.is_active:
                messages.error(request, 'Please verify your account first.')
                return redirect('login')
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html', {'form': {}})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    if request.method == 'POST':
        u = request.user
        u.first_name        = request.POST.get('first_name', '')
        u.last_name         = request.POST.get('last_name', '')
        u.bio               = request.POST.get('bio', '')
        u.telegram_username = request.POST.get('telegram_username', '')
        u.telegram_chat_id  = request.POST.get('telegram_chat_id', '')
        if request.FILES.get('avatar'):
            u.avatar = request.FILES['avatar']
        # never update email/phone from profile form directly
        # they are changed via change_contact view with OTP
        u.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile')

    telegram_link_url = request.session.pop('telegram_link_url', None)
    return render(request, 'profile.html', {
        'telegram_link_url': telegram_link_url
    })


@login_required
def link_telegram(request):
    if request.method == 'POST':
        import uuid
        token = uuid.uuid4().hex
        request.user.telegram_link_token = token
        request.user.save()
        bot_username = 'to_ol_x_bot'  # ← replace with your bot username
        telegram_link_url = f'https://t.me/{bot_username}?start={token}'
        request.session['telegram_link_url'] = telegram_link_url
        messages.success(request, 'Telegram link generated!')
    return redirect('profile')


@login_required
def unlink_telegram(request):
    if request.method == 'POST':
        request.user.telegram_chat_id = ''
        request.user.save()
        messages.success(request, 'Telegram unlinked.')
    return redirect('profile')


@login_required
def verify_id(request):
    if request.method == 'POST':
        if request.FILES.get('id_document'):
            request.user.id_document   = request.FILES['id_document']
            request.user.terms_accepted = True
            request.user.save()
            messages.success(request, 'ID submitted! We will verify it shortly.')
        return redirect('profile')
    return render(request, 'verify_id.html', {})


@login_required
def change_contact(request):
    if request.method == 'POST':
        contact_type = request.POST.get('contact_type')  
        new_contact  = request.POST.get('new_contact', '').strip()
        password     = request.POST.get('password', '')
        if contact_type == 'phone':
            code = request.POST.get('country_code').strip()
            new_contact = f"{code}{new_contact}"

        # verify current password
        if not request.user.check_password(password):
            messages.error(request, 'Incorrect password.')
            return redirect('profile')

        if not new_contact:
            messages.error(request, 'Please enter a valid email or phone number.')
            return redirect('profile')

        # check not already taken
        if contact_type == 'email':
            if User.objects.filter(email=new_contact).exclude(pk=request.user.pk).exists():
                messages.error(request, 'That email is already in use.')
                return redirect('profile')
        else:
            if User.objects.filter(phone=new_contact).exclude(pk=request.user.pk).exists():
                messages.error(request, 'That phone number is already in use.')
                return redirect('profile')

        # send OTP
        otp = set_otp(request.user, contact_type)
        if contact_type == 'email':
            # temporarily store new email in session
            request.session['pending_email'] = new_contact
            # send OTP to new email
            from toolx.notifications import send_email
            send_email(
                new_contact,
                'Verify your new ToolX email',
                f'Hi {request.user.first_name or request.user.username},\n\n'
                f'Your verification code is:\n\n'
                f'    {otp}\n\n'
                f'This code expires in 10 minutes.\n\n'
                f'— ToolX'
            )
            messages.info(request, f'Verification code sent to {new_contact}')
        else:
            request.session['pending_phone'] = new_contact
            from toolx.notifications import send_sms
            send_sms(
                new_contact,
                f'Your ToolX verification code: {otp}. Valid 10 minutes.'
            )
            messages.info(request, f'Verification code sent to {new_contact}')

        request.session['otp_user_id']      = request.user.pk
        request.session['otp_method']       = contact_type
        request.session['otp_purpose']      = 'change_contact'
        return redirect('verify_contact_otp')

    return redirect('profile')


@login_required
def verify_contact_otp(request):
    """Step 2 — verify OTP and update contact."""
    user_id = request.session.get('otp_user_id')
    method  = request.session.get('otp_method')
    purpose = request.session.get('otp_purpose')

    if not user_id or purpose != 'change_contact':
        return redirect('profile')

    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        code = request.POST.get('otp_code', '').strip()

        if verify_otp(user, code):
            clear_otp(user)

            if method == 'email':
                new_email = request.session.pop('pending_email', None)
                if new_email:
                    user.email          = new_email
                    user.email_verified = True
                    user.save()
                    messages.success(request, 'Email updated and verified!')

            elif method == 'phone':
                new_phone = request.session.pop('pending_phone', None)
                if new_phone:
                    user.phone          = new_phone
                    user.phone_verified = True
                    user.save()
                    messages.success(request, 'Phone number updated and verified!')

            # clean session
            request.session.pop('otp_user_id', None)
            request.session.pop('otp_method', None)
            request.session.pop('otp_purpose', None)
            return redirect('profile')

        else:
            messages.error(request, 'Invalid or expired code. Try again.')

    contact = request.session.get('pending_email') or request.session.get('pending_phone', '')
    return render(request, 'verify_contact_otp.html', {
        'method': method,
        'contact': contact,
    })

@staff_member_required
def verification_queue(request):
    # This must match the name in your urls.py exactly
    unverified_users = User.objects.filter(is_verified=False, is_superuser=False)
    return render(request, 'admin/verification_queue.html', {
        'unverified_users': unverified_users
    })

@staff_member_required
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_verified = True
    user.save()
    messages.success(request, f"User {user.username} has been verified.")
    return redirect('verification_queue')

