# import pika
#
# credentials = pika.PlainCredentials('wezazbuz:wezazbuz', '28BUMuLXsp-3s_vT-nYhOEZf-8qoQXxG')
# parameters = pika.ConnectionParameters('eagle.rmq.cloudamqp.com',
#                                        1883,
#                                        '/',
#                                        credentials)
#
# connection = pika.BlockingConnection(parameters)
# channel = connection.channel()
#
#
# channel.queue_declare(queue='hello')
#
# channel.basic_publish(exchange='',
#                       routing_key='hello',
#                       body='Hello fdsffd!')
# print(" [x] Sent 'asdf World!'")


# consume.py

# publish.py
import pika, os

# Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
# url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672/%2f')
url = 'amqp://wezazbuz:28BUMuLXsp-3s_vT-nYhOEZf-8qoQXxG@eagle.rmq.cloudamqp.com/wezazbuz'
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel() # start a channel
channel.queue_declare(queue='hello2',durable=True) # Declare a queue
channel.basic_publish(exchange='',
                      routing_key='hello2',
                      body='{"job_id":44,"query":"cluj","url":"https://misstourist.com/cluj/"}')

print(" [x] Sent 'Hello World!'")
connection.close()

