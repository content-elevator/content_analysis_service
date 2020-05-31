from django.db import models
import requests
# Create your models here.
from django.db.models.signals import post_save


class AnalysisJob(models.Model):
    class StatusChoice(models.TextChoices):
        CONFIRMED = "CONFIRMED"
        IN_QUEUE = "IN_QUEUE"
        RECEIVED = "RECEIVED"
        GOOGLE_SCRAPING_STARTED = "GOOGLE_SCRAPING_STARTED"
        URL_SCRAPING_STARTED = "URL_SCRAPING_STARTED"
        ANALYSIS_STARTED = "ANALYSIS_STARTED"
        SAVING = "SAVING"
        COMPLETED = "COMPLETED"

    user_id = models.IntegerField(default=None, blank=True, null=True)
    job_status = models.CharField(
        choices=StatusChoice.choices,
        default=StatusChoice.CONFIRMED,
        max_length=250
    )
    url = models.CharField(max_length=250)
    query = models.CharField(max_length=250)

    jwt_token = models.CharField(max_length=500, default=None, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)

class AnalysisResult(models.Model):
    word_count_user = models.IntegerField()
    word_count_google = models.IntegerField()
    tfidf_general_score = models.FloatField()
    analysis_instance = models.ForeignKey(AnalysisJob, on_delete=models.CASCADE, related_name='result')


class TfIdfResult(models.Model):
    analysis_instance = models.ForeignKey(AnalysisResult, on_delete=models.CASCADE, related_name='tfidf_results')
    word = models.CharField(max_length=150)
    user_score = models.FloatField()
    google_score = models.FloatField()


class ScrapingResult(models.Model):
    analysis_instance = models.ForeignKey(AnalysisJob, on_delete=models.CASCADE, related_name="scraping_results")
    is_user_article = models.BooleanField()
    is_last_google_article = models.BooleanField()
    title = models.CharField(max_length=150)
    content = models.TextField()


def new_job_post_save(sender, instance, created, **kwargs):
    if created:
        import pika, os

        current_job = instance

        # Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
        # url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672/%2f')
        url = 'amqp://zdblkbpl:LdADoprUeh9MViM85YcwsuIKYRhU6DJs@eagle.rmq.cloudamqp.com/zdblkbpl'
        params = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)

        channel = connection.channel()  # start a channel
        channel.queue_declare(queue='hello2', durable=True)  # Declare a queue

        id = instance.id
        query = instance.query
        url = instance.url
        channel.basic_publish(exchange='',
                              routing_key='hello2',
                              body='{"job_id":' + str(id) + ',"query":"' + str(query) + '","url":"' + str(url) + '"}')

        print(" [x] Sent " + '{"job_id":' + str(id) + ',"query":"' + str(query) + '","url":"' + str(url) + '"}')
        connection.close()

        current_job.job_status = AnalysisJob.StatusChoice.IN_QUEUE
        current_job.save()
        print("STATUS CHANGED TO: " + current_job.job_status)
        pass


def scraping_result_post_save(sender, instance, created, **kwargs):
    if created:

        if instance.is_user_article:
            # generate word counts
            user_word_count = len(instance.content.split(" "))
            # save it

            # update status to google scraping started
            pass
        elif instance.is_last_google_article:
            # get all articles for job
            current_job = instance.analysis_instance

            scraping_results = list(current_job.scraping_results.all())

            # change status
            current_job.job_status = AnalysisJob.StatusChoice.ANALYSIS_STARTED
            current_job.save()
            # generate and save word counts
            google_word_count, user_word_count = get_word_counts(scraping_results)

            result = AnalysisResult()
            result.analysis_instance = current_job
            result.word_count_google = google_word_count
            result.word_count_user = user_word_count
            result.tfidf_general_score = 0

            result.save()
            current_job.save()

            # generate and save tfidf + update status
            tfidf_score, tfidf_terms, googletf, googleterms = generate_tf_idf(scraping_results)

            general_score_diff = 0
            for (term, google_score, tfidf_score) in zip(tfidf_terms, googletf, tfidf_score):
                tfidf_res_entry = TfIdfResult()
                tfidf_res_entry.analysis_instance = result
                tfidf_res_entry.word = term
                tfidf_res_entry.google_score = google_score
                tfidf_res_entry.user_score = tfidf_score
                tfidf_res_entry.save()

                general_score_diff += abs(google_score - tfidf_score)

            general_score_diff = general_score_diff / len(tfidf_terms)
            result.tfidf_general_score = general_score_diff
            result.save()

            current_job.job_status = AnalysisJob.StatusChoice.SAVING
            current_job.save()
            print("STATUS CHANGED TO: " + current_job.job_status)

            ## save stuff

            current_job.job_status = AnalysisJob.StatusChoice.COMPLETED
            current_job.save()
            print("STATUS CHANGED TO: " + current_job.job_status)

            save_job_history(current_job)


            pass

        pass


post_save.connect(new_job_post_save, sender=AnalysisJob)
post_save.connect(scraping_result_post_save, sender=ScrapingResult)



def save_job_history(job_instance):
    # api-endpoint
    URL = "https://analysis-history.gigalixirapp.com/v1/save"

    data = {
        "analysis_result": {
            "user_id": job_instance.user_id,
            "average_length": job_instance.result.google_word_count,
            "length": job_instance.result.user_word_count,
            "query": job_instance.query,
            "url": job_instance.url,
            "score": job_instance.result.tfidf_general_score
        }
    }

    headers = {
        "content-type":"application/json",
        "Authorization": "Bearer "+job_instance.jwt_token
    }

    resp = requests.post(url=URL,data=data,headers=headers)
    max_tries = 5
    curent_tries =0
    if resp.status_code != 201:
        while resp.status_code!=201 and curent_tries<max_tries:
            resp = requests.post(url=URL, data=data, headers=headers)
            curent_tries+=1

    #if resp.status_code == 201:
        #AnalysisJob.objects.filter(id=job_instance.id).delete()

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import text
import pandas as pd


def get_word_counts(scraping_results):
    user_word_count = 0
    google_word_count = 0
    for scraping_result in scraping_results:
        if scraping_result.is_user_article:
            user_word_count += len(scraping_result.content.split(" "))
        else:
            google_word_count += len(scraping_result.content.split(" "))
    google_word_count = google_word_count / (len(scraping_results) - 1)
    return google_word_count, user_word_count


def pre_process(text_string):
    # lowercase
    text_string = text_string.lower()

    # remove tags
    text_string = re.sub("<!--?.*?-->", "", text_string)

    # remove special characters and digits
    text_string = re.sub("(\\d|\\W)+", " ", text_string)

    return text_string


def generate_tf_idf(scraping_results):
    tfidf_vectorizer = TfidfVectorizer(stop_words=text.ENGLISH_STOP_WORDS, min_df=0.1, max_df=0.7)
    clean_google_content = []
    user_result = None
    for content in scraping_results:
        if not content.is_user_article:
            preprocessed = pre_process(content.content)
            clean_google_content.append(preprocessed)
        else:
            user_result = content
    google_vectors = tfidf_vectorizer.fit_transform(clean_google_content)
    feature_names_google = tfidf_vectorizer.get_feature_names()

    dense = google_vectors.todense()
    denselist = dense.tolist()

    df = pd.DataFrame(denselist, columns=feature_names_google)

    mean_res = df.mask(df.eq(0)).mean()
    mean_res = mean_res.sort_values(ascending=False)

    df = mean_res.to_frame()
    df = df.head(50)
    # df = df.nlargest(50,[1])
    df.to_csv("result.csv")

    google_tfidf_score = df.values.tolist()
    google_tfidf_terms = df.index.values.tolist()

    tfidf = tfidf_vectorizer.transform([user_result.content])
    dense = tfidf.todense().tolist()

    df = pd.DataFrame(dense, columns=feature_names_google)

    mean_res = df.mask(df.eq(0)).mean()

    df = mean_res.to_frame()
    df = df.loc[google_tfidf_terms, :]
    # df = df.nlargest(50,[1])
    df.to_csv("result-request.csv")

    tfidf_score = df.values.tolist()
    tfidf_terms = df.index.values.tolist()

    tfidf_score = map(lambda x: x[0] if x[0] == 'nan' else 0, tfidf_score)
    google_tfidf_score = map(lambda x: x[0], google_tfidf_score)
    # for score in tfidf_score:

    return tfidf_score, tfidf_terms, google_tfidf_score, google_tfidf_terms
