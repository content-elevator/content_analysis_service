from django.http import HttpResponse
import jwt

from analyser.models import AnalysisJob


class JwtMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        ALLOWED_URLS = ['/docs/', '/docs/schema.js']

        if request.path not in ALLOWED_URLS:
            if 'Authorization' in request.headers:
                jwt_token = request.headers['Authorization'].split()[1]
                try:
                    self.authorize(jwt_token)
                except:
                    return HttpResponse('Unauthorized', status=401)

            else:
                return HttpResponse('Unauthorized', status=401)

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    @staticmethod
    def authorize(jwt_token):
        return jwt.decode(jwt_token,
                          'vdsNJHUptbte5p55rYvsoKF+UiaZB/Se7ZwFDtox8ZR1kgh41hcl7rnbhubM6OR4',
                          algorithms=['HS512'],
                          audience='user_management, analysis_history, analysis')


class NewJobMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        ALLOWED_URLS = ['/jobs/']



        response = self.get_response(request)
        if request.path in ALLOWED_URLS and request.method == 'POST':
            jwt_token = request.headers['Authorization'].split()[1]
            payload = jwt.decode(jwt_token,
                       'vdsNJHUptbte5p55rYvsoKF+UiaZB/Se7ZwFDtox8ZR1kgh41hcl7rnbhubM6OR4',
                       algorithms=['HS512'],
                       verify=False)
            if response.status_code == 201:
                id = response.data['id']
                job = AnalysisJob.objects.get(pk = int(id))
                job.user_id = int(payload['sub'])
                job.jwt_token = jwt_token
                job.save()
        # Code to be executed for each request/response after
        # the view is called.

        return response

