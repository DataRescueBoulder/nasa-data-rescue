nasa-data-rescue
==============================

[Data Rescue Boulder](https://www.facebook.com/dataRescueBoulder/)
helping NASA rescue old fixed-width EBCDIC, ASCII and binary data files,
mostly related to space physics, previously recovered from magnetic tape archives.

## Project:   NASA Moon Mission Records Rescue

## Overview:  
This project will digitally package, translate (if needed) and make publicly available data sets from the original NASA rocket and moon missions that is not, and has not, been available to the research or education community before.  Project files will likely not be in ASCII format, but in legacy, proprietary bit formats and date back to the 1950’s.  Converting these files to a readable format is critical to their usability.  The final output will be on the Space Physics web data page managed by Goddard Space Flight Center, as well as the Data Rescue Boulder portal.  The NASA Moon Mission Records Rescue Team will create an operational plan, identify software tools needed to support the plan, execute a proof of concept, and finally, execute the operational plan to convert these important records.

## Source of Project:  
NASA, Dr. Robert Candey; UCAR, Ruth Duerr

## Raw data
The raw data files, documentation for the files, and original associated metadata are at
http://spdf.sci.gsfc.nasa.gov/pub/data/

## This repository

See [Files to Rescue](notebooks/files_to_rescue.ipynb) to see an overview
of the 94 priority 6 assignments we're working with, and the sizes of the
tens of thousands of files associated with them,
automatically generated from `data/NASA_Project_Assignments.csv`.

See results/SPMS-00050/ats-1_k0_es_19661209_v01.cdf for
an early draft of a hopefully-ISTP-compliant CDF file.

## Project Organization

    .
    ├── README.md
    ├── LICENSE
    ├── data       Assignments, list of files per assignment
    ├── explore    Experimentation with data rescue techniques
    ├── notebooks
    └── src
