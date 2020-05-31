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
channel = connection.channel() # start a channel
channel.queue_declare(queue='hello2',durable=True) # Declare a queue
def callback(ch, method, properties, body):
  print(" [x] Received " + str(body))

channel.basic_consume('hello2',
                      callback,
                      auto_ack=True)

print(' [*] Waiting for messages:')
channel.start_consuming()
connection.close()