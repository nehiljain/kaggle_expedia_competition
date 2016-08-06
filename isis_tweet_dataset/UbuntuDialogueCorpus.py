# Databricks notebook source exported at Sat, 6 Aug 2016 20:17:57 UTC
# MAGIC %sh /home/ubuntu/databricks/python/bin/pip install langid

# COMMAND ----------

# MAGIC %sh /home/ubuntu/databricks/python/bin/pip install nltk

# COMMAND ----------

import nltk
nltk.download('wordnet')
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk import pos_tag
import langid
import re
import string
sqlContext

# COMMAND ----------

def get_mentions(data_str):
  result = re.findall("(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)", data_str)
  return ', '.join(result)
def remove_mentions(data_str):
  return re.sub("(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)", "", data_str)
def remove_urls(data_str):
  return re.sub(r"http\S+", "", data_str)
  

# COMMAND ----------

def check_lang(data_str):
    predict_lang = langid.classify(data_str)
    if predict_lang[1] >= .9:
        language = predict_lang[0]
    else:
        language = 'NA'
    return language

# COMMAND ----------

def remove_stop_words(data_str):
    stops = set(stopwords.words("english"))
    list_pos = 0
    cleaned_str = ''
    text = word_tokenize(data_str)
    for word in text:
        if word not in stops:
            if list_pos == 0:
              cleaner_str = word
            else:
              cleaner_str += word
            list_pos += 1
    return cleaned_str

    

# COMMAND ----------

# MAGIC %python
# MAGIC data_path = "/FileStore/tables/5po7ek3t1470497347193/IsisFanboy.csv"
# MAGIC sqlContext.read.format("com.databricks.spark.csv")\
# MAGIC   .option("header", "true")\
# MAGIC   .option("inferSchema", "true")\
# MAGIC   .load(data_path)\
# MAGIC   .registerTempTable("isis_signal_twts")

# COMMAND ----------

isis_s = sqlContext.table("isis_signal_tweets")
isis_n = sqlContext.table("isis_noise_tweets")

# COMMAND ----------

isis_n.count()
isis_s.count()

# COMMAND ----------

remove_urls_udf = udf(remove_urls, StringType())
get_mentions_udf = udf(get_mentions, StringType())
remove_mentions_udf = udf(remove_mentions, StringType())
remove_stop_words_udf = udf(remove_stop_words, StringType())
check_lang_udf = udf(check_lang, StringType())

# COMMAND ----------

clean_tweets_df = isis_n.withColumn('tweets', remove_urls_udf(isis_n['tweets']))
clean_tweets_df = clean_tweets_df.withColumn('mentions', get_mentions_udf(clean_tweets_df['tweets']))
clean_tweets_df = clean_tweets_df.withColumn('tweets', remove_mentions_udf(clean_tweets_df['tweets']))


# COMMAND ----------

print clean_tweets_df.take(2)

# COMMAND ----------

lang_df = clean_tweets_df.withColumn("lang", check_lang_udf(clean_tweets_df["tweets"]))
en_df = lang_df.filter(lang_df["lang"] == "en")

# COMMAND ----------

display(lang_df)

# COMMAND ----------

isis_n.count()

# COMMAND ----------

isis_s.count()

# COMMAND ----------


