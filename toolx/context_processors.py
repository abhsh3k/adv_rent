def unread_messages(request):
    if request.user.is_authenticated:
        from rentals.models import Message
        count = Message.objects.filter(
            rental__renter=request.user,
            is_read=False
        ).exclude(sender=request.user).count() + \
        Message.objects.filter(
            rental__tool__owner=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        return {'unread_count': count}
    return {'unread_count': 0}