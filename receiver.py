# #!/usr/bin/env python
# import pika
#
# connection = pika.BlockingConnection(
#     pika.ConnectionParameters(host='localhost'))
# channel = connection.channel()
#
# channel.queue_declare(queue='hello')
#
#
# def callback(ch, method, properties, body):
#     print(" [x] Received %r" % body)
#
#
# channel.basic_consume(
#     queue='hello', on_message_callback=callback, auto_ack=True)
#
# print(' [*] Waiting for messages. To exit press CTRL+C')
# channel.start_consuming()

import pika, os

# Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
# url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672/%2f')
url = 'amqp://zdblkbpl:LdADoprUeh9MViM85YcwsuIKYRhU6DJs@eagle.rmq.cloudamqp.com/zdblkbpl'
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()  # start a channel
channel.queue_declare(queue='hello2', durable=True)  # Declare a queue


def callback(ch, method, properties, body):
    print(" [x] Received " + str(body))


# channel.basic_consume('hello2', callback, auto_ack=True)

# print(' [*] Waiting for messages:')
# channel.start_consuming()
connection.close()

import requests

URL = "https://analysis-history.gigalixirapp.com/history/v1/save"

data = '{"analysis_result": {' \
       + '"average_length": 1721,' \
       + '"length": 1222,' \
       + '"query": "budapest",' \
       + '"url": "https://misstourist.com/budapest/",' \
       + ' "score": 13}}'


# data = {
#         "analysis_result": {
#             "average_length": 1721,
#             "length": 1222,
#             "query": "budapest",
#             "url": "https://misstourist.com/budapest/",
#             "score": 13
#         }
#     }
headers = {
    "content-type": "application/json",
    "Authorization": "Bearer " + "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ1c2VyX21hbmFnZW1lbnQsIGFuYWx5c2lzX2hpc3RvcnksIGFuYWx5c2lzIiwiZXhwIjoxNTkzNDQ3NzQwLCJpYXQiOjE1OTEwMjg1NDAsImlzcyI6InVzZXJfbWFuYWdlbWVudCIsImp0aSI6ImM2MTM3NWFhLWM0MzMtNGQ0Mi1hNTJhLTA2N2RhNTdlZmE2NCIsIm5iZiI6MTU5MTAyODUzOSwic3ViIjoiNiIsInR5cCI6ImFjY2VzcyJ9.wRmt9H34SUwlAbDyvN0p8CjF31bOpnVoMVaRVDbI-OU_ueZPqajhqP7uoN6vsCmbImJHqsj-SQ5qfgep_I-wDQ"
}
print("data:")
print(data)
print("headers:")
print(headers)
print("Saving job")

resp = requests.post(url=URL, data=data, headers=headers)
max_tries = 5
curent_tries = 0
if resp.status_code != 201:
    print("Something went wrong while saving")
    print(resp.status_code)

    while resp.status_code != 201 and curent_tries < max_tries:
        resp = requests.post(url=URL, data=data, headers=headers)
        curent_tries += 1

if resp.status_code == 201:
    print("Save successful")
    # AnalysisJob.objects.filter(id=job_instance.id).delete()
