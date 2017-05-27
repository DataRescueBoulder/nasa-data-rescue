nasa-data-rescue
==============================

[Data Rescue Boulder](https://www.facebook.com/dataRescueBoulder/)
helping NASA rescue old fixed-width EBCDIC and ASCII data files
from magnetic tape archives.

See [Files to Rescue](notebooks/files_to_rescue.ipynb) to see an overview
of the 94 priority 6 assignments we're working with, and the sizes of the
tens of thousands of files associated with them,
automatically generated from `data/NASA_Project_Assignments.csv`.

See results/SPMS-00050/ats-1_k0_es_19661209_v01.cdf for
an early draft of a hopefully-ISTP-compliant CDF file.

Project Organization
--------------------

    .
    ├── README.md
    ├── LICENSE
    ├── data       Assignments, list of files per assignment
    ├── explore    Experimentation with data rescue techniques
    ├── notebooks
    └── src
