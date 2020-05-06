from content_scrape.service.content_scraper_service import ContentScraperService
from content_scrape.service.google_search_scraper_service import GoogleSearchScraperService
import pandas as pd
import sklearn as sk
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import text
import re


class AnalyzerService:
    url = ''
    target_query = ''

    def __init__(self, content_url, target_query) -> None:
        super().__init__()
        self.url = content_url
        self.target_query = target_query
        self.scraping_service = ContentScraperService()
        self.google_scrape_service = GoogleSearchScraperService()
        print("Getting request page content.")
        self.request_page_content = self.scraping_service.get_page_content(self.url)
        if self.request_page_content is not None:
            self.request_page_content = self.request_page_content.text_content
            self.request_page_content = self.pre_process(self.request_page_content)
            print("Getting google search results.")
            self.google_content = self.google_scrape_service.get_search_result_with_content(self.target_query)
            self.clean_google_content = []
            for content in self.google_content:
                preprocessed = self.pre_process(content.text_content)
                self.clean_google_content.append(preprocessed)
            print("Finished getting content. Beginning analysis.")
            self.tfidf_vectorizer = TfidfVectorizer(stop_words=text.ENGLISH_STOP_WORDS, min_df=0.1, max_df=0.7)
            self.google_vectors = self.tfidf_vectorizer.fit_transform(self.clean_google_content)
            self.feature_names_google = self.tfidf_vectorizer.get_feature_names()

            self.unable = False
        else:
            self.unable = True
            print("Cannot do analysis")


    def compare_len(self):
        sum = 0
        for content in self.google_content:
            content = content.text_content
            sum += len(content.split(" "))

        target_length = sum / len(self.google_content)
        request_length = len(self.request_page_content.split(" "))

        return request_length, target_length


    def pre_process(self, text_string):
        # lowercase
        text_string = text_string.lower()

        # remove tags
        text_string = re.sub("<!--?.*?-->", "", text_string)

        # remove special characters and digits
        text_string = re.sub("(\\d|\\W)+", " ", text_string)

        return text_string


    def get_tfidf_google(self):
        if self.unable:
            return None

        dense = self.google_vectors.todense()
        # get mean tfidf

        denselist = dense.tolist()

        df = pd.DataFrame(denselist, columns=self.feature_names_google)
        print(df.head())
        print("Mean: \n")
        mean_res = df.mask(df.eq(0)).mean()
        mean_res = mean_res.sort_values(ascending=False)
        print(mean_res)
        print(type(mean_res))

        df = mean_res.to_frame()
        df = df.head(50)
        # df = df.nlargest(50,[1])
        df.to_csv("result.csv")

        tfidf_score = df.values.tolist()
        tfidf_terms = df.index.values.tolist()

        return tfidf_score, tfidf_terms


    def get_request_tf_idf_result(self):
        googletf, googleterms = self.get_tfidf_google()
        tfidf = self.tfidf_vectorizer.transform([self.request_page_content])
        dense = tfidf.todense().tolist()

        df = pd.DataFrame(dense, columns=self.feature_names_google)

        print("Mean: \n")
        mean_res = df.mask(df.eq(0)).mean()
        print(mean_res)
        print(type(mean_res))

        df = mean_res.to_frame()
        df = df.loc[googleterms, :]
        print(df.head(50))
        # df = df.nlargest(50,[1])
        df.to_csv("result-request.csv")

        tfidf_score = df.values.tolist()
        tfidf_terms = df.index.values.tolist()

        return tfidf_score, tfidf_terms, googletf, googleterms
