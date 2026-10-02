from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone


@shared_task
def send_welcome_email_task(user_id):
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return f"\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c {user_id} \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d"
    if not user.email:
        return f"\u0423 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f {user_id} \u043d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d email"
    send_mail(
        "\u0414\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c!",
        f"\u0417\u0434\u0440\u0430\u0432\u0441\u0442\u0432\u0443\u0439\u0442\u0435, {user.get_username()}! \u0421\u043f\u0430\u0441\u0438\u0431\u043e \u0437\u0430 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044e.",
        None,
        [user.email],
        fail_silently=False,
    )
    return f"\u041f\u0440\u0438\u0432\u0435\u0442\u0441\u0442\u0432\u0435\u043d\u043d\u043e\u0435 \u043f\u0438\u0441\u044c\u043c\u043e \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043e \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044e {user_id}"


@shared_task
def clean_inactive_users_task(days=30):
    User = get_user_model()
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _details = User.objects.filter(
        is_active=False, date_joined__lt=cutoff
    ).delete()
    return f"\u0423\u0434\u0430\u043b\u0435\u043d\u043e \u043d\u0435\u0430\u043a\u0442\u0438\u0432\u043d\u044b\u0445 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439: {deleted}"


@shared_task
def send_daily_admin_report_task():
    User = get_user_model()
    counts = {role: 0 for role in ("ADMIN", "MODERATOR", "USER")}
    if any(field.name == "role" for field in User._meta.get_fields()):
        for role in counts:
            counts[role] = User.objects.filter(role=role).count()
    else:
        counts["ADMIN"] = User.objects.filter(is_superuser=True).count()
        for user in User.objects.prefetch_related("groups"):
            for group in user.groups.all():
                role = group.name.upper()
                if role in counts and role != "ADMIN":
                    counts[role] += 1
        counts["USER"] = User.objects.count() - counts["ADMIN"] - counts["MODERATOR"]
    report = "\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439: " + ", ".join(
        f"{role}={count}" for role, count in counts.items()
    )
    print(report)
    return report
