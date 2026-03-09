from society.models import Society
from core.context.society_context import set_current_society


class SocietyContextMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        society_id = request.headers.get("X-Society-ID")

        if society_id:
            try:
                society = Society.objects.get(id=society_id)
                set_current_society(society)
            except Society.DoesNotExist:
                pass

        response = self.get_response(request)
        return response
        