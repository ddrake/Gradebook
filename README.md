# Gradebook
## Simple command-line application for quickly setting up a course to teach, recording student scores and viewing reports.

At this point the application has only been tested on Linux Mint 17 and 18. It requires Python 3.x.
The user interface is based on [Python Menu-3.1.0](https://pypi.python.org/pypi/Menu/).  Install that via "pip3 install --user Menu".  Of course, you will also want to have numpy installed for python3.

Now make sure the gb1.py script is executable, via ```chmod +x gb1.py``` 

All data for a course is stored in a single JSON file.  The top level 'Course' object is named by a concatenation of the course name and the term.  It contains collections of Categories, Graded Items, Students and Scores.  

To open Gradebook for a specific saved course named "Math 251" in the term "Fall 2017" we execute it like this ```$ ./gb1 Math_251_Fall_2018.json```.  You can create a new course by running the application without specifying a file.  You should see a menu like this:

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

```>>>``` 

First select 'Edit Course' to change the Course name and term as you like.  Next add your students, either by using 'Manage Students' to enter them manually (first name, last name, email) or by using 'Import Students' to import them from a tab-separated text file with no header and columns in that order named 'students.txt'.  A sample 'students.txt' is provided in this repository.

The next step is to Manage Categories. A category could be 'Quiz' or 'Midterm 1', for example, it counts collectively for a specific percent of the grade.  So if you said on the syllabus that 20% of the grade will based on quizzes and the midterm was worth 25%, you would set up these two categories accordingly.  If you want to automatically drop each student's lowest quiz grade, just enter 1 when prompted for 'drop lowest n' (this defaults to zero) when setting up the Quiz category.

Once this is set up, you can add graded items, such as Quiz 1, each associated with a category.  There is quite a bit of flexibility built in.  For example, suppose half the class failed the midterm and you decide to allow a retake option so that students can earn 25% of the difference of the retake score and the original score.  This could be handled by setting the retake percentage of the graded item 'Midterm retake' to be 25.  You would just need to enter the differences between the scores.  If the retake percentage is 0 (the default) for all graded items in a category, they are combined simply by averaging.  

A graded item may also be "curved" by setting its "added points" or "added percent".  If either of these is nonzero, it will be applied to the graded item before any combination is applied.  It is easy to include bonus problems on a quiz or exam, since you specify separately the total points and the individual question points.  The sum of the individual question points may exceed the total points, but may not be less than it.  

Entering scores is pretty simple and optimized for speed.  Normally you will want to enter scores for all students for a particular quiz.  The application will prompt you sequentially for each score for each student.  You can skip to the next student by entering 'n' or go back to the previous student using 'p'.  You can go back to the last problem using 'b' and quit data entry using 'q'.  You can also skip over a question by just hitting enter to leave the previous value unchanged.  This idea is used everywhere in the application.

If you make an invalid entry, such as a typo, or entering a score for a question that is greater than the points for the question, an audible and visible warning will be given.  You will also receive an audible and printed warning if you try to go past the end of the list, or go back before the beginning.

The reporting capabilities (in progress) will include the following:

* Graded Item Details: This has one row for each active student and a column for each question on the graded item along with total and percent columns.  The rows are sorted by total so it is easy to see which students are struggling.  An average row is provided at the bottom so you can see which problems were more difficult. 
* Class Details: This has a similar format to the graded items report, but instead of showing columns for individual questions, shows the total score as a column for each graded item.
* Class Summary: This groups the graded items into categories and displays the weight for each category.
* Student Summary: This combines all scores for each student into a single text string like "Homework (10% of grade): 94%, Quizzes (25% of grade) 87%, Midterm 1 (20% of grade) 78%".  There will soon be an option to email (via gmail) this grade summary to one or all students in the class.

A histogram with letter grade bins pops up for each of the first three reports.

