#!/usr/bin/env python
"""auto_parse scientific fixed-width blocks of data"""

import sys
import os
import codecs
import re
import json
import logging
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
    
    return int(c[maxLen+1:].argmax()) + 1

# ETL

def signatures(fn):
    with open(fn, 'rb') as f:
        data = f.read()

    filelen = len(data)

    stat = os.stat(fn)
    desc = collections.OrderedDict([('len', stat.st_size), ('name',fn)])

    # print("File: %s" % fn)
    # print("File length: %d" % filelen)

    segmentLen = 10000

    # print("Most common bytes: %s" % ' '.join("%02s" % hex(b[0])[2:4] for b in collections.Counter(data[:segmentLen]).most_common(10)))

    common = [t[0] for t in collections.Counter(data[:segmentLen]).most_common(10)]
    # print("Most common bytes: %s" % ' '.join("%02x" % chr for chr in common))
    desc.update(topbytes=["%02x" % chr for chr in common])

    # space character
    if 0x40 in common:
        isobytes = data.decode('cp037') # or cp500 - international?
    else:
        isobytes = data.decode('iso8859-1')

    # Find bytes with upper bit set: non-ascii

    # finds = [(m.span()[0], codecs.encode(m.group(), "hex").decode('ascii') )
    finds = [(m.span()[0], codecs.encode(m.group().encode('iso8859-1'), "hex").decode('ascii') )
             for m in re.finditer('[\x80-\xff]', isobytes[:10000])]

    # print("%d offset [j.span()[0] - i.span()[1] for i, j in zip(t[:-1], t[1:])]

    upperbitchars = "none"
    if finds:
        upperbitchars = ("offset %d, intervals %s" %
                     (finds[0][0],
                      [j[0] - i[0] for i, j in zip(finds[:-1], finds[1:])]))

    #print("upperbitchars of %s at %s" % (set((find[1] for find in finds)), upperbitchars))
    desc.update(upperbitchars=list(set((find[1] for find in finds))))

    blocksize = findRecordLen(isobytes[:segmentLen], min(1000, filelen-1))

    # print("Block size: %d" % blocksize)
    # print("Blocks: %f" % (filelen / blocksize, ))

    left_over = filelen % blocksize
    if left_over != 0:
        #print("WARNING: %d bytes left over" % left_over)

        if left_over == blocksize / 2:   # FIXME: deal better with mistakes from thes odd paired data structures
            # print("New block size: %d" % blocksize)
            desc.update(firstblocksize=blocksize)
            blocksize = left_over
            left_over = filelen % blocksize

    desc.update(blocksize=blocksize)
    desc.update(blocks=filelen / blocksize)
    desc.update(left_over=left_over)

    # Convert contents of file to a 2-d array of characters, one row per block
    try:
        data_c = np.array(isobytes, 'c')
    except UnicodeEncodeError as e:
        logging.error("badchar in %s: %s" % (fn, e))
        desc.update(badchar=True)
        return desc

    if left_over:
        logging.error("left_over: %d at blocksize %s for %s" % (left_over, blocksize, fn))
        return desc
                    
    data_c.shape = (-1, blocksize)

    # If we take the positions of decimal places as a signature, there are only 6 unique signatures in dr2129: here is a count for each unique tuple of columns.  E.g. 54 records have a "." in columns 7 and 14.
    # 
    # If we use a more specific signature: all columns that have an unusual character or decimal point, we get 9 unique signatures.  Here we look for any character other than a digit, a minus sign and a space.

    alldpacols = [dpacols(record) for record in data_c]
    dpacol = collections.Counter(alldpacols)

    #print("%d unique marker character position signatures. Counts and columns for each:" % len(dpacol))
    desc.update(num_markers=len(dpacol))

    sigs = sorted(list(dpacol.items()), key=lambda t: t[1], reverse=True)
    desc.update(sigs=sigs[:3])

    for t, v in sigs[:10]:
        #print((v, str(t)))
        pass

    assert(sum(dpacol.values())) == len(data_c)

    return desc

    """
    alldpcols = [dpcols(record) for record in data_c]
    dct = collections.Counter(alldpcols)
    print("%d unique decimal-point character position signatures. Counts and columns for each:" % len(dct))
    print([(v, str(t)) for t, v in list(dct.items())[:10]])
    """

if __name__ == "__main__":
    print("[")
    for fn in sys.argv[1:]:
        if os.path.splitext(fn)[1] in ['.pdf', '.html', '.tar', '.xml', '.txt']:
            continue

        desc = signatures(fn)
        print(json.dumps(desc) + ",")

    print("[]\n]")
