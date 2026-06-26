def unreadCount(request):
    if request.user.is_authenticated:
        return {'unreadCount': request.user.notifications.filter(is_read=False).count()}
    return {'unreadCount': 0}