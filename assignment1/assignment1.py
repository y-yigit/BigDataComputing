#!usr/bin/env python3

"""
Assignment 1

Reads in one or more FastQ files and calculates PHRED scores
The user specifies the amount of CPUs used to divide the workload
The scores are written to a csv file, named by the user

Usage: python3 assignment1.py -n <aantal_cpus> [OPTIONEEL: -o <output csv file>]
       fastabestand1.fastq [fastabestand2.fastq ... fastabestandN.fastq]

This script is an improvement of my assignment 1 from last year
It can be used as module in assignment 2
"""

__author__ = "Yaprak Yigit"
__version__ = "2.0"


import sys
import os
import argparse
import multiprocessing as mp
import csv

class FastQC:
    """
    This class contains methods that can process a FastQ file
    It is able to divide the file into parts, read the data,
    convert the quality scores into PHRED scores and write
    these scores to a csv file
    """

    def __init__(self, fastq_file, n_proc):
        """
        Initiation of FastQ object

        Parameters:
            n_proc (int): Number of processes
            fastq_file (String): A FastQ file
        """
        self.fastq_file = fastq_file
        self.n_proc = n_proc


    def __split_file__(self):
        """
        Splits any file in bytes based on the amount of processes.

        Return:
            Positions (list): A list containing tuples of end and start positions.
        """
        # Total byte size of the FastQFile
        try:
            n_bytes = os.path.getsize(self.fastq_file)
        except FileNotFoundError as error:
            print(error, "No file found, shutting down")
            exit()
        # Amount of bytes per process as equal as possible
        byte_chunks = ([n_bytes // self.n_proc + (1 if x < n_bytes % self.n_proc else 0)
        for x in range (self.n_proc)])
        positions = []
        start = 0
        end = byte_chunks[0]
        for chunk in byte_chunks:
            positions.append((start, end))
            start += chunk
            end += chunk
        return positions


    def __read_file__(self, file_parts):
        """
        Opens a FastQ file and calculates the PHRED score
        of the line containing the quality values.

        Parameters:
            file_parts(list): A list containing tuples of start and end positions.

        Return:
            phred_dict (dict): A dictionary with as key the sequence position
                               And lists with multiple phred scores as values
        """
        phred_dict = {}

        print("Calculating PHRED scores from {} in byte range {}"
              .format(self.fastq_file, file_parts))
        with open(self.fastq_file) as file_obj:
            file_obj.seek(file_parts[0])
            line = file_obj.readline()
            while line.startswith("+") == False and \
                    line.startswith("-") == False and file_obj.tell() < file_parts[1]:
                line = file_obj.readline()
            count = 3
            while line and file_obj.tell() < file_parts[1]:
                count += 1
                line = file_obj.readline()
                if count % 4 == 0:
                    # Im starting from 1 so that the base positions
                    # in the output csv fle start from 1 and not 0
                    for position, quality in enumerate(line.strip(), start=1):
                        if position in phred_dict:
                            phred_dict[position].append(ord(quality) - 33)
                        else:
                            phred_dict[position] = [ord(quality) - 33]
        print("Finished calculating the PHRED scores from bytes {}"
              .format(file_parts))
        return phred_dict


    def __calculate_averages__(self, results, queue_dictionary):
        """
        Loops through all the dictionaries generated by multiprocessing
        queue or process and combines them

        Parameters:
            results (List): List of dictionaries
            queue_dictionary (Boolean): Should be false unless it is run via process
        """
        combined_dict = {}
        for result_dictionary in results:
            if queue_dictionary == True:
                # This allows me to import in assignment 2
                result_dictionary = result_dictionary['result']
            for key, value in result_dictionary.items():
                if key in combined_dict:
                    combined_dict[key] += result_dictionary[key]
                else:
                    combined_dict[key] = result_dictionary[key]
        return {key: round(sum(values) / len(values), 2)
                for key, values in result_dictionary.items()}


    def __csv_writer__(self, phred_dict, outfile=None):
        """
        Writes the multiprocessing dictionary from the class
        to a CSV file

        Parameters
            phred_dict (dict): A dictionary with as key the sequence position
                               And lists with multiple
            optional_name (String): Optional argument used in naming the csv file
        """
        # If the filename contains a path, python will try to write to that location
        head, tail = os.path.split(self.fastq_file)
        if outfile == None:
            outfile = tail + "outfile.csv"
        else:
            outfile = tail + outfile
        with open(outfile, 'w', newline='') as csvfile:
            # Use csv writer
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(["Base position", "Phred Score"])
            for key in phred_dict.keys():
                spamwriter.writerow([key, "{:.2f}".format(phred_dict[key])])
        print("File {} created, stopping workers soon".format(outfile))


def arg_parser():
    """
    The arguments in the main function are processed with argparse
    The user has to provide the numberOFCPUs and at least one FastQ file
    """
    parser = argparse.ArgumentParser(description='Process some arguments')
    parser.add_argument('-n', '--numberOfCPUs', type=int, required=True,
                        help='Number of CPUs used to divide the workload')
    parser.add_argument('-o', '--outputFile', type=str, required=False,
                        help='File name for the csv file')
    # This is actually a list
    parser.add_argument('FastQFiles', nargs="+", type=str,
                        help='Can be one or more FastQ files')
    args = parser.parse_args()
    main(args)


def main(args):
    """
    Calls the FastQC class and processes one or more FastQ files
    The output is written to a csv file
    """
    for file in args.FastQFiles:
        fastqc_object = FastQC(file, args.numberOfCPUs)
        byte_chunks = fastqc_object.__split_file__()
        with mp.Pool() as mp_pool:
            results = mp_pool.map(fastqc_object.__read_file__, byte_chunks)
        phred_dict = fastqc_object.__calculate_averages__(results, False)
        fastqc_object.__csv_writer__(phred_dict, args.outputFile)


if __name__ == '__main__':
    sys.exit(arg_parser())
