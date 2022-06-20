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
    14: (GO annotations (e.g. GO:0005515) - optional column;
    only displayed if –goterms option is switched on)
    15: (Pathways annotations (e.g. REACT_71) - optional column;
    only displayed if –pathways option is switched on)
"""

__author__ = "Yaprak Yigit"
__version__ = "1.0"

from pyspark.sql import SparkSession
from pyspark.sql.functions import countDistinct, col, split, explode
from pyspark.sql.types import *
import sys, argparse, csv

spark = SparkSession.builder.getOrCreate()
#c = SparkContext('local[16]')

# "/data/dataprocessing/interproscan/all_bacilli.tsv"
answer_list = [[i, None, None] for i in range(1, 11)]

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


def get_distinct_prot():
    """
    Question one and two
    """
    n_uniq_prot_acc = df.select(countDistinct("protein_accession"))
    answer_list[0][1] = n_uniq_prot_acc.collect()[0][0]
    answer_list[0][2] = n_uniq_prot_acc.explain()
    answer_list[1][1] = round(df.count() / answer_list[0][1], 2)
    answer_list[1][2] = "Same as question one"


def find_most_common_go():
    """
    Question three
    """
    raw_go_counts = df.groupby('go_annotations').count()
    go_counts = raw_go_counts.sort(col("count").desc()).\
        where(raw_go_counts.go_annotations != "-").na.drop()
    answer_list[2][1] = go_counts.collect()[0][0]
    answer_list[2][2] = go_counts.explain()

def calc_average_size():
    """
    Question 4
    Returns the dataframe with an additional column
    """
    modified_df = df.withColumn('Result', (df['stop'] - df['start']))
    average_length = modified_df.select('Result').agg({"Result": "avg"})
    answer_list[3][1] = round(average_length.collect()[0][0], 2)
    answer_list[3][2] = average_length.explain()
    return modified_df

def get_most_com():
    """
    Question 5
    """
    raw_prot_counts = df.groupby('protein_accession').count()
    prot_counts = raw_prot_counts.sort(col("count").desc()).na.drop()
    answer_list[4][1] = [prot_counts.collect()[row][0] for row in range(10)]
    answer_list[4][2] = prot_counts.explain()


def get_homology():
    "Question 6"
    e_value_filtered_counts = df.where(df.score<=0.01).groupby('protein_accession').count()
    filtered_prot_counts = e_value_filtered_counts.sort(col("count").desc()).na.drop()
    answer_list[5][1] = [filtered_prot_counts.collect()[row][0] for row in range(10)]
    answer_list[5][2] = filtered_prot_counts.explain()


def get_annotation():
    """
    Question 7 and 8
    """
    all_words = df.select("interpro_annotations_description").where(df.interpro_annotations_description != "-").na.drop()
    count_all_words = all_words.withColumn('interpro_annotations_description',explode(split('interpro_annotations_description', ' ')))
    most_common = count_all_words.groupby("interpro_annotations_description").count().sort(col("count").desc()).na.drop()
    least_common = count_all_words.groupby("interpro_annotations_description").count().sort(col("count").asc()).na.drop()
    answer_list[6][1] = [most_common.collect()[row][0] for row in range(10)]
    answer_list[6][2] = most_common.explain()
    answer_list[7][1] = [least_common.collect()[row][0] for row in range(10)]
    answer_list[7][2] = least_common.explain()


def get_largest_most_com(updated_df):
    """
    Question 9 and 10
    """
    filtered_df = df.select("interpro_annotations_description").filter(df.protein_accession.isin(answer_list[5][1])==True).where(df.interpro_annotations_description != "-").na.drop()
    words_in_top_ten = filtered_df.withColumn('interpro_annotations_description',explode(split('interpro_annotations_description', ' ')))
    most_common_top_ten = words_in_top_ten.groupby("interpro_annotations_description").count().sort(col("count").desc()).na.drop()
    answer_list[8][1] = [most_common_top_ten.collect()[row][0] for row in range(10)]
    answer_list[8][2] = most_common_top_ten.explain()
    # 10
    answer_list[9][1] = round(updated_df.stat.corr("score", "Result"), 3)
    answer_list[9][2] = "The explain function doesn't work for the function corr"

# Write to a csv file

def write_to_csv(data):
    with open("out.csv", 'w', newline='') as csvfile:
        # Use csv writer
        spamwriter = csv.writer(csvfile, delimiter='\t')
        spamwriter.writerow(["Question", "Answer", "Schedule"])
        for question_list in data:
            spamwriter.writerow(question_list)
            #spamwriter.writerow([key, "{:.2f}".format(phred_dict[key])])


def main():
    """
    The arguments in the main function are processed with argparse
    The user has to specify a tsv file
    """
    parser = argparse.ArgumentParser(description='Process some arguments')
    parser.add_argument('TSV', nargs="+", type=str,
                        help='A tsv file from InterPro')
    args = parser.parse_args()
    # Polluting
    global df
    df = spark.read.csv(args.TSV, sep="\t", header=False, schema=schema)
    get_distinct_prot()
    find_most_common_go()
    updated_df = calc_average_size()
    get_most_com()
    get_homology()
    get_annotation()
    get_largest_most_com(updated_df)
    write_to_csv(answer_list)


if __name__ == '__main__':
    sys.exit(main())