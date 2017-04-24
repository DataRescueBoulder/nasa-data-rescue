#!/usr/bin/env python
"""auto_cluster scientific fixed-width blocks of EBCDIC data"""

import sys
import collections
import numpy as np
import matplotlib.pyplot as plt

def chunkstring(string, length):
    "A generator which return the string, split up into fixed-width substrings of given length"
    return (string[0+i:length+i] for i in range(0, len(string), length))


def dswrite(data, recordLen, colspecs):
    """Write out the records in a text format that can be read by pandas.read_fwf()
    FIXME: somehow check whether the last record is valid
    """
    with open("/tmp/file.txt", "w") as f:
        for l in chunkstring(data, recordLen):
            print(l, file=f)


def dpcols(record):
    "list of columns with decimal points in this byte array"

    chd = [record[col] == b'.' for col in range(record.shape[0])]
    cwd = tuple(i for i,v in enumerate(chd)  if v)
    return cwd


def dpacols(record):
    "list of columns with decimal points or non-number-characters in this byte array"

    chd = [record[col] not in b'-0123456789 ' for col in range(record.shape[0])]
    cwd = tuple(i for i,v in enumerate(chd)  if v)
    return cwd


def chunkstring(string, length):
    "A generator which return the string, split up into fixed-width substrings of given length"
    return (string[0+i:length+i] for i in range(0, len(string), length))


def findRecordLen(segment, maxLen=1000):
    "Find record length in given string, via autocorrelation"

    # Turn string into array of byte with zero mean
    arr = np.array([float(ord(c)) for c in segment])
    arrNorm = arr - np.mean(arr)

    (lags, c, line, b) = plt.acorr(arrNorm, maxlags=maxLen)
    
    return c[maxLen+1:].argmax() + 1

# ETL

def signatures(fn):
    with open(fn, 'rt', encoding='cp500') as f:
        data_ascii = f.read()

    filelen = len(data_ascii)

    # FIXME: determine blocksize
    segmentLen = 10000

    blocksize = findRecordLen(data_ascii[:segmentLen])

    print("File: %s" % fn)
    print("File length: %d" % filelen)
    print("Block size: %d" % blocksize)
    print("Blocks: %f" % (filelen / blocksize, ))

    left_over = filelen % blocksize
    if left_over != 0:
        print("WARNING: %d bytes left over" % left_over)

        if left_over == blocksize / 2:   # FIXME: deal better with mistakes from thes odd paired data structures
            blocksize = left_over
            print("New block size: %d" % blocksize)

    # Convert contents of file to a 2-d array of characters, one row per block
    try:
        data_c = np.array(data_ascii, 'c')
    except UnicodeEncodeError as e:
        print(e)
        return
    data_c.shape = (-1, blocksize)

    # If we take the positions of decimal places as a signature, there are only 6 unique signatures in dr2129: here is a count for each unique tuple of columns.  E.g. 54 records have a "." in columns 7 and 14.
    # 
    # If we use a more specific signature: all columns that have an unusual character or decimal point, we get 9 unique signatures.  Here we look for any character other than a digit, a minus sign and a space.

    alldpacols = [dpacols(record) for record in data_c]
    dpacol = collections.Counter(alldpacols)

    print("%d unique marker character position signatures. Counts and columns for each:" % len(dpacol))
    sigs = sorted(list(dpacol.items()), key=lambda t: t[1], reverse=True)
    for t, v in sigs[:10]:
        print((v, str(t)))
    assert(sum(dpacol.values())) == len(data_c)

    """
    alldpcols = [dpcols(record) for record in data_c]
    dct = collections.Counter(alldpcols)
    print("%d unique decimal-point character position signatures. Counts and columns for each:" % len(dct))
    print([(v, str(t)) for t, v in list(dct.items())[:10]])
    """

if __name__ == "__main__":
    for fn in sys.argv[1:]:
        signatures(fn)
