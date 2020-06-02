from django.http import HttpResponse
import jwt
from datetime import datetime, timedelta
from django.utils.timezone import now
from analyser.models import AnalysisJob


class JwtMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if not request.path.startswith('/admin/'):
            ALLOWED_URLS = ['/docs/', '/docs/schema.js','/admin']

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
            count = AnalysisJob.objects.all().count()
            if count > 150:
                print("Total number of jobs: " + str(count))
                print("Cleaning up old jobs...")
                how_many_days = 3
                old_jobs = AnalysisJob.objects.filter(start_date__lt=(now() - timedelta(days=how_many_days)))
                print("Old jobs: " + str(old_jobs.count()))
                old_jobs.delete()
                if AnalysisJob.objects.all().count() == count:
                    print("Old jobs not cleaned.")
                else:
                    print("Old jobs cleaned.")
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

                import pika, os

                

                # Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
                # url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672/%2f')
                url = 'amqp://zdblkbpl:LdADoprUeh9MViM85YcwsuIKYRhU6DJs@eagle.rmq.cloudamqp.com/zdblkbpl'
                params = pika.URLParameters(url)
                connection = pika.BlockingConnection(params)

                channel = connection.channel()  # start a channel
                channel.queue_declare(queue='hello2', durable=True)  # Declare a queue

                id = job.id
                query = job.query
                url = job.url
                channel.basic_publish(exchange='',
                                      routing_key='hello2',
                                      body='{"jwt_token":"' + str(job.jwt_token) + '","job_id":' + str(
                                          id) + ',"query":"' + str(query) + '","url":"' + str(url) + '"}')

                print(" [x] Sent " + '{"jwt_token":"' + str(job.jwt_token) + '","job_id":' + str(
                    id) + ',"query":"' + str(query) + '","url":"' + str(url) + '"}')
                connection.close()

                job.job_status = AnalysisJob.StatusChoice.IN_QUEUE
                job.save()
                print("STATUS CHANGED TO: " + job.job_status)



        # Code to be executed for each request/response after
        # the view is called.

        return response

