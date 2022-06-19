#!usr/bin/env python3

"""
Assignment 2

Reads in an InterPROscan output file and finds the amount of protein annotations
(distinct InterPRO numbers)in the dataset, the average amount of annotations from a protein,
the most common GO term, the average size of an InterPRO feature and...

TSV interpro columns:
    1: Protein accession (e.g. P51587)
    2: Sequence MD5 digest (e.g. 14086411a2cdf1c4cba63020e1622579)
    3: Sequence length (e.g. 3418)
    4: Analysis (e.g. Pfam / PRINTS / Gene3D)
    5: Signature accession (e.g. PF09103 / G3DSA:2.40.50.140)
    6: Signature description (e.g. BRCA2 repeat profile)
    7: Start location
    8: Stop location
    9: Score - is the e-value (or score) of the match reported by member database method (e.g. 3.1E-52)
    10: Status - is the status of the match (T: true)
    11: Date - is the date of the run
    12: InterPro annotations - accession (e.g. IPR002093)
    13: InterPro annotations - description (e.g. BRCA2 repeat)
    14: (GO annotations (e.g. GO:0005515) - optional column; only displayed if –goterms option is switched on)
    15: (Pathways annotations (e.g. REACT_71) - optional column; only displayed if –pathways option is switched on)
"""

__author__ = "Yaprak Yigit"
__version__ = "1.0"

from pyspark.sql import SparkSession
from pyspark.sql.functions import countDistinct, col, split
from pyspark.sql.types import *

spark = SparkSession.builder.getOrCreate()
#c = SparkContext('local[16]')

# "/data/dataprocessing/interproscan/all_bacilli.tsv"
input_file = "all_bacilli.tsv" # Testing on local machine

# Column names since the file has no header
schema = StructType([
    StructField("protein_accession", StringType(), True),
    StructField("sequence_MD5_digest", StringType(), True),
    StructField("sequence_length", IntegerType(), True),
    StructField("analysis", StringType(), True),
    StructField("signature_accession", StringType(), True),
    StructField("signature_description", StringType(), True),
    StructField("start", IntegerType(), True),
    StructField("stop", IntegerType(), True),
    StructField("score", FloatType(), True),
    # Boolean but cannot be BoolType()
    StructField("status", StringType(), True),
    # Not the correct format for DataType()
    StructField("date", StringType(), True),
    StructField("interpro_annotations_accession", StringType(), True),
    StructField("interpro_annotations_description", StringType(), True),
    StructField("go_annotations", StringType(), True),
    StructField("pathway_annotations", StringType(), True)]
)

# Create a spark data frame
df = spark.read.csv(input_file, sep="\t", header=False, schema=schema)

# Question one and two
n_uniq_prot_acc = df.select(countDistinct("protein_accession"))
question_one = n_uniq_prot_acc.collect()[0][0]
question_two = round(df.count() / question_one, 2)

# Question three
raw_go_counts = df.groupby('go_annotations').count()
go_counts = raw_go_counts.sort(col("count").desc()).\
    where(raw_go_counts.go_annotations != "-").na.drop()
question_three = go_counts.collect()[0][0]

# Question four
df = df.withColumn('Result', (df['stop'] - df['start']))
average_length = df.select('Result').agg({"Result": "avg"})
question_four = round(average_length.collect()[0][0], 2)

# Question five
raw_prot_counts = df.groupby('protein_accession').count()
prot_counts = raw_prot_counts.sort(col("count").desc()).na.drop()
question_five = [prot_counts.collect()[row][0] for row in range(10)]

# Question six
# E-value is maximum strength of association
# It should be < 0.01 for homology
e_value_filtered_counts = df.where(df.score<=0.01).groupby('protein_accession').count()
filtered_prot_counts = e_value_filtered_counts.sort(col("count").desc()).na.drop()
question_six = [filtered_prot_counts.collect()[row][0] for row in range(10)]

# Question seven
all_words = df.select("interpro_annotations_description").where(df.interpro_annotations_description != "-").na.drop()
#split_col = split(all_words['interpro_annotations_description'], ' ')
#split_col.select('interpro_annotations_description').show()
