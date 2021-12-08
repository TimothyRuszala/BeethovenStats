# BeethovenStats

This repository holds a suite of python programs that I wrote in order to statistically analyze harmonies in the Beethoven String Quartets, using music data from the Annotated Beethoven Corpus (https://github.com/DCMLab/ABC).

## Contents

### report.pdf

report.pdf contains the paper I wrote summarizing the results of my analyses, also containing a detailed explanation of the data structures I used for the project. It was written as my Spring Junior Paper in the Music department, advised by Prof. Dmitri Tymoczko.

### Music/Beethoven Quartets

This directory contains .mxl files and .txt files corresponding to each of the Beethoven String Quartets. .mxl files are a standard digital representation of sheet music, whilte the .txt files are written in rntxt notation. Rntxt ("Roman Numeral Text) was developed by Dmitri Tymoczko as a standardized way of representing roman numeral analyses so that they could be easily processed by computers.

The programs here preprocess .mxl files representing the scores of the quartets to prepare them for further analysis. 

### getProgs.py

getProgs.py contains the getProgs() function, which is used to collect all local harmonic progressions from a given .mxl file. It takes two arguments: the name of a Beethoven String quartet file (e.g. 'op18_no1_mov1'), and a boolean which if true, loads previously found chord progression data, otherwise the program finds the chord progressions for the file again.

### bigScore.py

bigscore.py contains the BigScore object, which preprocesses an .mxl music file to prepare it for further analysis.

### voicing.py

voicing.py contains the Voicing and VL objects. These objects are used to represent harmonies and voice-leadings, respectively.

### bigVoicing.py

bigVoicing.py contains the BigVoicing object. The BigVoicing object is like a regular voicing, but collects all chord tones within the space of a single harmony into one giant chord. Useful for looking at implied voice leadings.

### bigVL.py

BigVL is to BigVoicing as VL is to Voicing. That is, BigVL groups two BigVL objects. This class is not fully developed, but can be adapted for more advanced analysis of implicit voice-leadings in Beethoven.

### progs.py

progs.py contains the progs object, which stores a collection of chord progressions, split into major and minor keys.

### getStats.py
getStats.py is a rather messy program which I used to collect the actual statistical data enabled by the other programs. Currently, its commenting does not allow for easy use, but I include it here as an example of how the above programs might be used for statistical analysis.








