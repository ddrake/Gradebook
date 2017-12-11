# Gradebook
## Simple command-line application for quickly setting up a class, recording student scores and viewing reports.

At this point the application has only been tested on Linux Mint 17 and 18. It requires Python 3.
The user interface is based on [Python Menu-3.1.0](https://pypi.python.org/pypi/Menu/).  Install that via "pip3 install --user Menu".  Then make this script executable, via ```chmod +x gb1.py``` 
All data for a course is stored in a Pickle file containing a single 'Course' object which is named by a concatenation of the course name and the term.  To open gradebook for a specific saved course named "Math251" in the term "Fall2017" we execute it like this ```$ ./gb1 Math251_Fall2017.p```.  
You can create a new course by running the application without specifying a file.  You should see a menu like this:

Gradebook

1. Quit
2. Save
3. Enter Scores All Students
4. Enter Scores One Student
5. Import Students
6. Manage Students
7. Manage Categories
8. Manage Graded Items
9. Reports
10. Edit Course

>>> 

First change the Course name and term as you like.  Next add your students, either by entering them manually (first name, last name, email) or importing them from a tab-separated text file with no header and columns in that order.
The next step is to Manage Categories. A category could be 'Quiz' or 'Midterm', for example, it counts collectively for a specific percent of the grade.  So if you said on the syllabus that 20% of the grade will based on quizzes and the midterm was worth 25%, you would set up these two categories accordingly.
Once this is set up, you can add graded items, such as Quiz 1, each associated with a category.  There is quite a bit of flexibility built in.  For example, suppose half the class failed the midterm and you decide to allow a retake option so that students can earn 25% of the difference of the retake score and the original score.  This could be handled by setting the retake percentage of the graded item 'Midterm retake' to be 25.  You would just need to enter the differences between the scores.
Entering scores is pretty simple and optimized for speed.  Normally you will want to enter scores for all students for a particular quiz.  The application will prompt you sequentially for each score for each student.  You can skip to the next student by entering 'n' or go back to the previous student using 'p'.  You can go back to the last problem using 'b' and quit data entry using 'q'.  You can also skip over a question by just hitting enter to leave the previous value unchanged.  This idea is used everywhere in the application.

If make an invalid entry, such as entering a score for a question that is greater than the points for the question, an audible and visible warning will be given.

The reporting capabilities are not in place yet, but there will be one for overall grades for students, histograms for specific graded items and overall, etc...

