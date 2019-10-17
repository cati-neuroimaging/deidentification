#!/usr/bin/env python
# -*- coding: utf-8 -*-
import anonymizer as anonymizer


def run_ano_function(subject, inputPath, outputPath):
    tags_to_keep = [
    (0x0008, 0x0020), (0x0008, 0x0031), (0x0008, 0x0032), (0x0008, 0x0033),
    (0x0008, 0x103E), (0x0010, 0x0010), (0x0019, 0x100A), (0x0019, 0x100C),
    (0x0019, 0x101E), (0x0019, 0x105A), (0x0019, 0x107E), (0x0019, 0x109F),
    (0x0021, 0x105A), (0x0025, 0x1007), (0x0027, 0x1060), (0x0043, 0x102C),
    (0x0043, 0x102F), (0x0043, 0x1039), (0x0051, 0x100A), (0x0051, 0x100B),
    (0x0051, 0x100C), (0x0051, 0x100E), (0x0051, 0x100F), (0x0051, 0x1011),
    (0x0051, 0x1016), (0x2001, 0x1003), (0x2001, 0x100B), (0x2001, 0x1013),
    (0x2001, 0x1014), (0x2001, 0x1018), (0x2001, 0x101B), (0x2001, 0x1081),
    (0x2005, 0x101D), (0x2005, 0x1074), (0x2005, 0x1075), (0x2005, 0x1076),
    (0x2005, 0x10A1), (0x2005, 0x10A9)
]

    forced_values = {(0x0010, 0x0010): subject}
   
    print 'Launch anonymization for ', subject
    anonymizer.anonymize(
        dicom_in=inputPath,
        dicom_out=outputPath,
        tags_to_keep=tags_to_keep,
        forced_values=forced_values)
    print 'Anonymization done for ', subject



def run_ano_function_MultiSubjects(myListe):

    for el in myListe:
        subject = el[0]
        inputPath = el[1]
        outputPath = el[2]
        try:
            run_ano_function(subject, inputPath, outputPath)
        except:
            print 'Error during anonymization for ', subject



def fileToList(filePath):

    myListe = []
    liste = [ i.strip() for i in  open( filePath ) ]
    for el in liste:
        subject = el.split(';')[0]
        inputPath = el.split(';')[1]
        outputPath = el.split(';')[2]
        mySubList = [subject, inputPath, outputPath]
        myListe.append(mySubList)

    return myListe
