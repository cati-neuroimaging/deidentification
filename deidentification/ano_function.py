#!/usr/bin/env python
# -*- coding: utf-8 -*-
import deidentification.anonymizer as anonymizer
from deidentification.config import tags_to_keep


def run_ano_function(subject, inputPath, outputPath):
    forced_values = {(0x0010, 0x0010): subject}
   
    print('Launch anonymization for ', subject)
    anonymizer.anonymize(
        dicom_in=inputPath,
        dicom_out=outputPath,
        tags_to_keep=tags_to_keep,
        forced_values=forced_values)
    print('Anonymization done for ', subject)
