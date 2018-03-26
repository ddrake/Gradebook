# Gradebook
## Simple command-line application for quickly setting up a course to teach, recording student scores and viewing reports.

At this point the application has only been tested on Linux Mint 17 and 18. It requires Python 3.x.
The user interface is based on [Python Menu-3.1.0](https://pypi.python.org/pypi/Menu/).  Install that via "pip3 install --user Menu".  Of course, you will also want to have numpy installed for python3.  

All data for a course is stored in a single JSON file, which is written when you 'Save' or 'Quit'.  The top level 'Course' object has properties for the course name and the term.  The JSON file is named by a concatenation of these. A Course contains lists of Categories, Graded Items and Students and a dictionary of Scores.  

To open Gradebook for a specific saved course named "Math 251" in the term "Fall 2018" we execute it like this:

```$ ./gb1 Math_251_Fall_2018.json```  

Note: See the 'gb' script in the utils folder for an example of how to save keystrokes by starting the application with a specific course and automatically back up the data file to cloud storage using rclone.

### New Course Setup
You can create a new course simply by running the application without specifying a file.  You should see a menu like this:

Gradebook

1. Quit
2. Save
3. Enter Scores All Students
4. Enter Scores One Student
5. Reports
6. Manage Graded Items
7. Manage Categories
8. Manage Students
9. Manage Students (last, first)
10. Import Students
11. Export Students
12. Edit Course

```>>>``` 

#### Course

To set up your new course, first select 'Edit Course' to change the Course name and term from their default values.  You may also want to change the 'Letter +/- Pct.', which is used to determine letter grades.  For example if this is set to1.0, the default, a grade percent p such that 90.0 <= p < 91.0 will be assigned an A-, and 89.0 <= p < 90.0 will be assigned a B+.  The last option, 'Global Added Pct.', may be used near the end of the term to bump everyone's grades uniformly by some percent.  

#### Students

Next add your students, either by using 'Manage Students' to enter them manually (first name, last name, email) or by using 'Import Students' to import them from a tab-separated text file in the application directory named 'students.txt'.  A sample file, 'students.txt.sample', is provided in this repository.  Students are always 'active' when added, but can later be inactivated or deleted, whether or not they have scores.  Inactive students don't show up on reports or when entering new scores.  Later, as students add or drop the class, it's simple to export the list of students to a textfile for import into a spreadsheet.  The export process will automatically open the textfile in Libre Office, if it is installed.  It includes the current grade percent and letter grade for each student.

#### Categories

The next step is to Manage Categories. A category could be 'Quiz' or 'Midterm 1', for example, it counts collectively for a specific percent of the grade.  So if you said on the syllabus that 20% of the grade will based on quizzes and the midterm was worth 25%, you would set up these two categories accordingly.  If you want to automatically drop each student's lowest quiz grade, just enter 1 when prompted for 'drop lowest n' (this defaults to zero) when setting up the Quiz category.

#### Graded Items

Once a category has been set up, you can add graded items, such as Quiz 1.  Each graded item is associated with a category.  There is quite a bit of flexibility built in.  For example, you specify the points for each question.  If you want one of the questions to be a bonus, just subtract its point value from the total, which is specified separately.

Suppose half the class failed the midterm and you decide to allow a retake option so that students can earn 25% of the difference of the retake score and the original score.  This could be handled by setting the retake percentage of the graded item 'Midterm retake' to be 25.  You would just need to enter the differences between the scores.  If the retake percentage is 0 (the default) for all graded items in a category, they are combined simply by adding averaging their _percentages_.  For example, all homeworks count the equally toward the grade, even if one is out of 15 points and another is out of 20 points.

A graded item may also be "curved" by setting its "added points" or "added percent".  If either of these is nonzero, it will be applied to the graded item before any combination is applied.  It is easy to include bonus problems on a quiz or exam, since you specify separately the total points and the individual question points.  The sum of the individual question points may exceed the total points, but may not be less than the total.  These options don't appear when you add a new graded item, but are available when you edit an existing one.  

### Entering Scores
Entering scores is pretty simple and optimized for speed.  Normally you will want to enter scores for all students for a particular quiz.  The application will prompt you sequentially for each score for each student.  You can skip to the next student by entering 'n' or go back to the previous student using 'p'.  You can go back to the last problem using 'b' and quit data entry using 'q'.  You can also skip over a question by just hitting enter to leave the previous value unchanged.  This idea is used everywhere in the application.  It's also possible to select single student for score entry, which is handy if someone turns in an assignment late.  Score entry works the same in this case, except there is no need for 'n' (next student) or 'p' (previous student) so these keys are inactive. 

If you make an invalid entry, such as a typo, or entering a score for a question that is greater than the points for the question, an audible and visible warning will be given.  You will also receive an audible and printed warning when you reach the end of the list, or try to go back before the beginning.

#### Importing Scores

If part of the students' grade is determined by scores that are reccorded in another system, such as Webassign, it may be useful to import those scores.  For example, the total scores for a single Webassign assignment or the overall Webassign total can be imported into an existing graded item with a single question representing the total possible points.

The tab-separated scores file to be imported must be named online_scores.txt and located in the application folder, and must match the layout of the 'online_scores.txt.sample' file provided in this repository.  Often students may type their names differently when registering for the online course and use email addresses different from their university emails.  To get around this, you can create anoptional 'online_xref.txt' file with two columns.  The first column must contain the student's full name (last, first) as they have entered it in the online course.  The second column must contain the student's email address as set up in the gradebook application.  

See the documentation in the 'utils' folder for how to modify and use some useful scripts for exporting data from Webassign so it can be easily imported into Gradebook.

### Reporting

The reporting capabilities include the following:

* Graded Item Details: This has one row for each active student and a column for each question on the graded item along with total and percent columns.  The rows are sorted by total so it is easy to see which students are struggling.  An average row is provided at the bottom so you can see which problems were more difficult. 
* Class Details: This has a similar format to the graded items report, but instead of showing columns for individual questions, shows the total score as a column for each graded item.
* Class Summary: This groups the graded items into categories and displays the weight for each category.  Unlike the Graded Item Details and Class Details reports, this report is able to apply the special summarization features, such as dropping the lowest quiz or combining the midterm scores with the retake scores.
* Student Summary: This combines all scores for each student into a single text string like "Homework (10% of grade): 94%, Quizzes (25% of grade) 87%, Midterm 1 (20% of grade) 78%".  There is an option to email (via gmail) this grade summary to one or all students in the class.  All you need to do to make this work is rename the file 'gmail_credentials.txt.sample' to 'gmail_credentials.txt', edit it to include your personal gmail account information and signature, and move it to the application directory.
* Average score needed for grade:  This helps to answer the common, but elusive question asked by students: What do I need to score on future assignments to get my desired grade in the class?  The current logic needs some improvements, but gives a pretty good estimate.  For this to work correctly, you need to set the "Estimated Items" for each category.
* Student scores:  This report simply lists the scores for a student for each graded item.  It groups by category and sorts by the graded item name.  This report can be emailed to each student to let them know what grades you have recorded for them so that any errors can be corrected before the final grade is posted.

A histogram with letter grade bins pops up for each of the first three reports.

### Course Data Schema

A schema version number is now stored in the JSON course file.  If the gradebook application schema number is greater than that of the data file being loaded, a sequence of schema migrations will be automatically performed to bring the data file up to the current schema.  The file saved on exit will have the same schema number as that of the application being run.

### Contributing

I've designed this application primarily to suit my preferences as an instructor.  If there are other features that you would like included, please feel free to fork this repository and add them.  If you add a feature or bug fix that you think might be useful for others, you're welcome to submit a pull request.  As time permits, I'll probably do some testing on Windows and OSX.  If you encounter issues, you may post them here.
