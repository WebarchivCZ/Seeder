

def get_dashboard_data(user, context):
    context['user_sources'] = user.source_set.filter()
    return context