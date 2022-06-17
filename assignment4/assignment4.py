#!usr/bin/env python3

"""
Assignment 4

Reads in a FastQ file from stdin
and verifies if it is a valid FastQ file
It also calculates the average line length ,
the minimum line length and the max line length
This is written to stdout along with the file name

Usage: python3 assignment4.py fastabestand1.fastq
"""

__author__ = "Yaprak Yigit"
__version__ = "1.0"

import sys
import argparse

def get_line_lengths(fastq_file):
    """
    Opens a FastQ file and returns
    the length of every line

    fastq_file (str): FastQ file name

    Return
    line_length (list): Contains all the line lengths
    """
    with open(fastq_file) as file_obj:
        line = file_obj.readline()
        line_lengths = []
        while line:
            line_lengths.append(len(line.strip()))
            line = file_obj.readline()
    return line_lengths


def verify_fasta(lengths):
    """
    Receives line lengths and decides the validity
    of the file by comparing the sequence lines with
    the quality lines

    lengths (list): Contains all the line lengths
    Return
    bool: Whether or not the FastQ file is valid
    """
    bool_list = []
    count = 0
    for length in lengths:
        count+=1
        # Sequence line
        if count == 2:
            temp_seq = length
        # Quality line
        if count == 4:
            bool_list.append(temp_seq == length)
            count = 0
    if bool(all(bool_list)) and len(lengths)%4 == 0:
        return True
    # Default return, assuming it is not a FastQ file
    return False


def format_output(file_name, lengths, validity):
    """
    Receives line lengths and calculates the average line length ,
    the minimum line length and the max line length
    This is written to stdout along with the file name and validity

    fastq_file (str): FastQ file name
    validity (bool): Whether or not the FastQ file is valid
    lengths (list): Contains all the line lengths

    Return
    stdout (String): Output string in CSV format,
    can be received by a bash script
    """
    txt = "Filename, Validity, Max, Min, Avg \n{}, {}, {}, {}, {}"\
        .format(file_name, validity, max(lengths), min(lengths), sum(lengths)/len(lengths))
    return sys.stdout.write(txt)


def main(args):
    """
    Main function, uses argparse to receive stdin
    writes a string in CSV format to stdout
    """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('FastQFile', type=str, help='File with F')
    args = parser.parse_args()

    line_lengths = get_line_lengths(args.FastQFile)
    file_validity = verify_fasta(line_lengths)
    format_output(args.FastQFile, line_lengths, file_validity)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
    