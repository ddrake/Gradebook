
The script 'wa' is used to scrape Webassign to download a report with all scores for all students
for the course into a text file called 'raw_scores.txt'.  This is necessary because Webassign 
doesn't provide an API for this purpose.  This script requires the wa_credentials.txt file 
to be present in the gradebook folder.  It then extracts the specified assignment to a file 
called 'online_scores.txt' which can be imported into gradebook.

The script wa_scores_from_raw can be used to extract a different assignment from a previously downloaded
'raw_scores.txt' file, overwriting the current 'online_scores.txt' file.  

