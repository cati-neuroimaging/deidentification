# deidentification
Tool to remove metadata allowing to identify a subject from DICOM images used in neuroimaging research

**Anonymization script**

Le script d'anonymisation est composé de 6 fichiers.

aggregator.py :  lecture des dicom
ano_function.py : fonction principale pour lancer le script pour les ARCs
anon_example.py : fonction principale pour lancer le script
anonymizer.py : parcours des dicom et anonymisation 
archive.py : gere les archives et compressions de dossiers/fichiers pour donner n’importe quel format en entrée
tag_lists.py : procédure d’anonymisation construite à partir de l’annexe E de la partie 15 du standard dicom


**prérequis :**
*Python*
*Pydicom*



**Norme d’anonymisation :**

http://dicom.nema.org/medical/dicom/current/output/html/part15.html#chapter_E

 - X means the attribute must be removed
 - U means the attribute must be replaced with a cleaned but internally consistent UUID
 - D means replace with a non-zero length dummy value
 - Z means replace with a zero or non-zero length dummy value
 - C means the attribute can be kept if it is cleaned

annex_e = {
    (0x0008, 0x0050): ['N', 'Y', 'Z', '', '', '', '', '', '', '', '', ''],  # Accession Number
    (0x0018, 0x4000): ['Y', 'N', 'X', '', '', '', '', '', '', 'C', '', ''],  # Acquisition Comments
    (0x0040, 0x0555): ['N', 'Y', 'X', '', '', '', '', '', '', '', 'C', ''],  # Acquisition Context Sequence
    (0x0008, 0x0022): ['N', 'Y', 'X/Z', '', '', '', '', 'K', 'C', '', '', ''],  # Acquisition Date
    (0x0008, 0x002A): ['N', 'Y', 'X/D', '', '', '', '', 'K', 'C', '', '', ''],  # Acquisition DateTime
    (0x0018, 0x1400): ['N', 'Y', 'X/D', '', '', '', '', '', '', 'C', '', ''],  # Acquisition Device Processing Description
    (0x0018, 0x9424): ['N', 'Y', 'X', '', '', '', '', '', '', 'C', '', ''],  # Acquisition Protocol Description
    (0x0008, 0x0032): ['N', 'Y', 'X/Z', '', '', '', '', 'K', 'C', '', '', ''],  # Acquisition Time
    (0x0040, 0x4035): ['N', 'N', 'X', '', '', '', '', '', '', '', '', ''],  # Actual Human Performers Sequence
    (0x0010, 0x21B0): ['N', 'Y', 'X', '', '', '', '', '', '', 'C', '', ''],  # Additional Patient's History
    (0x0038, 0x0010): ['N', 'Y', 'X', '', '', '', '', '', '', '', '', ''],  # Admission ID
    (0x0038, 0x0020): ['N', 'N', 'X', '', '', '', '', 'K', 'C', '', '', ''],  # Admitting Date
    (0x0008, 0x1084): ['N', 'Y', 'X', '', '', '', '', '', '', 'C', '', ''],  # Admitting Diagnoses Code Sequence
    (0x0008, 0x1080): ['N', 'Y', 'X', '', '', '', '', '', '', 'C', '', ''],  # Admitting Diagnoses Description
    (0x0038, 0x0021): ['N', 'N', 'X', '', '', '', '', 'K', 'C', '', '', ''],  # Admitting Time

[....]

}




**Fichier de config**
Tag à garder pour le CATI :

``tags_to_keep = [``
``    (0x0008, 0x0020), (0x0008, 0x0031), (0x0008, 0x0032), (0x0008, 0x0033),``
``    (0x0008, 0x103E), (0x0010, 0x0010), (0x0019, 0x100A), (0x0019, 0x100C),``
``    (0x0019, 0x101E), (0x0019, 0x105A), (0x0019, 0x107E), (0x0019, 0x109F),``
``    (0x0021, 0x105A), (0x0025, 0x1007), (0x0027, 0x1060), (0x0043, 0x102C),``
``    (0x0043, 0x102F), (0x0043, 0x1039), (0x0051, 0x100A), (0x0051, 0x100B),``
``    (0x0051, 0x100C), (0x0051, 0x100E), (0x0051, 0x100F), (0x0051, 0x1011),``
``    (0x0051, 0x1016), (0x2001, 0x1003), (0x2001, 0x100B), (0x2001, 0x1013),``
``    (0x2001, 0x1014), (0x2001, 0x1018), (0x2001, 0x101B), (0x2001, 0x1081),``
``    (0x2005, 0x101D), (0x2005, 0x1074), (0x2005, 0x1075), (0x2005, 0x1076),``
``    (0x2005, 0x10A1), (0x2005, 0x10A9)``
]``


Prévoir le cas de la version XA11
Que faire du CSA header ?

**Méthode Normale :**


Lancer la fonction anon_example.py

Exemple:

Sans choisir d’identifiant sujet (il sera mis à “Unknown” par défaut”
``python anon_example.py -in myInputFolder -out myOutputFolder``



Pour forcer l’identifiant sujet
``python anon_example.py -in myInputFolder -out myOutputFolder -ID 0001XXXX``




**Méthode ARC**
*Pour lancer le scirpt en singlesubject:*

lancer un python / ipython / spyder,...
Ouvrir en parallèle le fichier ano_function.py

Remplir les champs:
tag to keep
forced_values

lancer la fonction ‘run_ano_function’ avec comme parametres l’identifiant sujet, le chemin dicom d’entrée et le chemin dicom de sortie. Le dicom en entrée peut etre zippé ou non. Si le chemin du dicom en sortie est le même que je le chemin du dicom en entrée, celui-ci sera écrasé.

*Pour lancer le scirpt en multisubjects:*

lancer un python / ipython / spyder,...
Ouvrir en parallèle le fichier ano_function.py

Remplir les champs:
tag to keep
forced_values

lancer la fonction run_ano_function_MultiSubjects avec comme parametres une liste. Cette liste condiendra des sous listes de 3 éléments:  l’identifiant sujet, le chemin dicom d’entrée et le chemin dicom de sortie. Le dicom en entrée peut etre zippé ou non. Si le chemin du dicom en sortie est le même que je le chemin du dicom en entrée, celui-ci sera écrasé.

Si besoin il est possible de créer la liste a donner en entrée à l’aide de la fonction fileToList.
fileToList prend en entrée un fichier texte avec sur chaque ligne l’identifiant sujet, le chemin dicom d’entrée et le chemin dicom de sortie, séparés par un ‘;’.
fileToList retourne la liste



