# Gradebook
## Simple command-line application for quickly setting up a course to teach, recording student scores and viewing reports.

At this point the application has only been tested on Linux Mint 17 and 18. It requires Python 3.x.
The user interface is based on [Python Menu-3.1.0](https://pypi.python.org/pypi/Menu/).  Install that via "pip3 install --user Menu".  Of course, you will also want to have numpy installed for python3.  

All data for a course is stored in a single JSON file, which is written when you 'Save' or 'Quit'.  The top level 'Course' object has properties for the course name and the term.  The JSON file is named by a concatenation of these. A Course contains lists of Categories, Graded Items and Students and a dictionary of Scores.  

To open Gradebook for a specific saved course named "Math 251" in the term "Winter 2018" we execute it like this:

```$ ./gb1 Math_251_Winter_2018.json```  

Note: See the 'gb' script in the utils folder for an example of how to save keystrokes by starting the application with a specific course and automatically back up the data file to cloud storage using rclone.

### New Course Setup
You can create a new course simply by running the application without specifying a file.  You should see a menu like this:

Gradebook

1. Save and Exit
2. Save
3. Quit
4. Enter Scores All Students
5. Enter Scores One Student
6. Reports
7. Manage Graded Items
8. Manage Categories
9. Manage Students
10. Manage Students (last, first)
11. Import Students
12. Export Students
13. Edit Course

```>>>``` 

#### Course

To set up your new course, first select 'Edit Course' to change the Course name and term from their default values.  You may also want to change the 'Letter +/- Pct.', which is used to determine letter grades.  For example, if this is set to the default value of 1.0, a grade percent p such that 90.0 <= p < 91.0 will be assigned an A-, and 89.0 <= p < 90.0 will be assigned a B+.  You will probably want to leave the last option, 'Global Added Pct.', set to its default value of 0.0 initially.  It can be updated near the end of the term, if you want to bump everyone's grades uniformly by some percentage.  

#### Students

Next add your students, either by using 'Manage Students' to enter them manually (first name, last name, email) or by using 'Import Students' to import them from a tab-separated text file in the application directory named 'roster.txt'.  A sample file, 'roster.txt.sample', is provided in this repository.  Any existing students are deleted first, but the application will not allow you to import if there are any existing students with scores.

In case your school is using the Banner system, there are Python scripts in the utils/banner directoryr that will fetch your current roster from Banweb and create 'roster.txt' automatically for you.  Refer to the README.md file in that directory for more information.


Students are always 'active' when added, but can be later inactivated or deleted, whether or not they have scores.  Inactive students don't show up on reports or when entering new scores.  You can associate notes with students.  If you want to retain the notes for a student who dropped the class, it makes sense to inactivate them.

Later, as students add or drop the class, it's simple to export the list of students to a tab-separated text file 'students.txt' for import into a spreadsheet.  It includes notes, active status, the current grade percent and letter grade for each student.

#### Categories

The next step in getting your class set up is to Manage Categories. A category could be 'Quiz' or 'Midterm 1', for example, each category counts collectively for a specific percent of the grade.  So if you said on the syllabus that 20% of the grade will based on quizzes and the midterm was worth 25%, you would set up these two categories accordingly.  If you want to automatically drop each student's lowest quiz grade, just enter 1 when prompted for 'drop lowest n' (this defaults to zero) when setting up the Quiz category.

It's possible to weight students' exams based on their scores, for example, we could define a Category 'Exams' with three graded items: 'Midterm 1', 'Midterm 2', and 'Final'.  We can set the overall weight of the 'Exams' category to 60%, then at the category level, we can set the percentages to: (15, 20, 25).  In this case the 'Exam' component of a student's grade would be calculated by multiplying their lowest (percent) score by 15, their higher score by 20 and their best score by 25, adding these and dividing by 60.

The option 'Combine Points' for categories is discussed in the next section. 

The logic around Categories and Graded Items is fairly complicated at this point.  Some combinations of settings are not supported.  A 'config_warnings.log' will be created in the Gradebook directory after the file is saved if any issues are detected.

#### Graded Items

Once a category has been set up, you can add graded items, such as Quiz 1.  Each graded item is associated with a category.  There is quite a bit of flexibility built in.  For example, you specify the points for each question.  If you want one of the questions to be a bonus, just subtract its point value from the total, which is specified separately.

Suppose half the class failed the midterm and you decide to allow a retake option so that students can earn 25% of the difference of the retake score and the original score.  This could be handled by setting the retake percentage of the graded item 'Midterm retake' to be 25.  You would just need to enter the differences between the scores.  If the retake percentage is 0 (the default) for all graded items in a category, they are combined simply by adding averaging their _percentages_ or _scores_, depending on how the category is set up.  For example, if 'Combine Points' is 'N', all homeworks count the equally toward the grade, even if one is out of 15 points and another is out of 20 points.  In this case, it is possible to drop the lowest score.  If 'Combine Points' is 'Y' the sum of scores for the category is divided by the sum of possible scores to get the percentage for the catgory.  In this case, it is currently not possible to drop the lowest score.

A graded item may also be "curved" by setting its 'added points' or 'added percent'.  These are somewhat redundant since a given 'added points' value is equivalent to some 'added percent' value and vice versa.  If either of these is nonzero, it will be applied to the graded item before any combination is applied.  It is easy to include bonus problems on a quiz or exam, since you specify separately the total points and the individual question points.  The sum of the individual question points may exceed the total points, but may not be less than the total.  These options don't appear when you add a new graded item, but are available when you edit an existing one.  

### Entering Scores
Entering scores is pretty simple and optimized for speed.  Normally you will want to enter scores for all students for a particular graded item.  It will be helpful to have the papers sorted by student's first name.  The application will prompt you sequentially for each score for each student.  You can skip to the next student by entering 'n' or go back to the previous student using 'p'.  You can go back to the last problem using 'b' and quit data entry using 'q'.  You can also skip over a question by just pressing <Enter\> to leave the previous value unchanged.  This convention is used everywhere in the application.  

It's also possible to select a single student for score entry, which is handy if someone turns in an assignment late.  Score entry works the same in this case, except there is no need for 'n' (next student) or 'p' (previous student) so these keys are inactive. 

If you make an invalid entry, such as a typo, or entering a score for a question that is greater than the points for the question, an audible and visible warning will be given.  You will also receive an audible and printed warning when you reach the end of the list, or try to go back before the beginning.  Currently the audible warning is implemented using speech-dispatcher, which is pre-installed in Ubuntu-like Linux distros.  OSX uses 'Speech Synthesis Manager', I may add support for this in future versions.  Audible warnings can be turned on or off via Edit Course.

Once you've finished entering scores, you can go to Reports > Graded Item Reports, select the graded item, then select 'Details by Student'.  This will display a percent score for each student.  Then you can just flip back through the stack of items and mark each one with the percent.

#### Importing Scores

If part of the students' grade is determined by scores that are reccorded in another system, such as Webassign, it may be useful to import those scores.  For example, the total scores for a single Webassign assignment or the overall Webassign total can be imported into an existing graded item with a single question representing the total possible points.  Refer to the README.md file in the utils/webassign directory for more information.
The tab-separated scores file to be imported must be named online_scores.txt and located in the application folder, and must match the layout of the 'online_scores.txt.sample' file provided in this repository.  Often students may type their names differently when registering for the online course and use email addresses different from their university emails.  To get around this, you can create anoptional 'online_xref.txt' file with three columns.  The first two columns must be the student's first and last name as they have entered it in the online course (e.g. Webassign).  The last column must contain the student's email address as set up in the gradebook application.  

See the documentation in the 'utils' folder for how to modify and use some useful scripts for exporting data from Webassign so it can be easily imported into Gradebook.

### Reporting

The reporting capabilities include the following:

* Graded Item Details: This has one row for each active student and a column for each question on the graded item along with total and percent columns.  The rows are sorted by total so it is easy to see which students are struggling.  An average row is provided at the bottom so you can see which problems were more difficult. 
* Class Details: This has a similar format to the graded items report, but instead of showing columns for individual questions, shows the total score as a column for each graded item.
* Class Summary: This groups the graded items into categories and displays the weight for each category.  Unlike the Graded Item Details and Class Details reports, this report is able to apply the special summarization features, such as dropping the lowest quiz or combining the midterm scores with the retake scores.
* Student Summary: This combines all scores for each student into a single text string like "Homework (10% of grade): 94%, Quizzes (25% of grade) 87%, Midterm 1 (20% of grade) 78%".  There is an option to email (via gmail) this grade summary to one or all students in the class.  All you need to do to make this work is rename the file 'gmail_credentials.txt.sample' to 'gmail_credentials.txt', edit it to include your personal gmail account information and signature, and move it to the application directory.
* Average score needed for grade:  This helps to answer the question sometimes asked by students: What do I need to score on future assignments to get my desired grade in the class?  The current logic needs some improvements, but gives a pretty good estimate.  For best accuracy, you need to set the "Estimated Items" correctly for each category.
* Student scores:  This report simply lists the scores for a student for each graded item.  It groups by category and sorts by the graded item name.  This report can be emailed to each student to let them know what grades you have recorded for them so that any errors can be corrected before the final grade is posted.

A histogram with letter grade bins pops up for each of the first three reports.

### Course Data Schema

A schema version number is stored in the JSON course file.  If the schema number of the Gradebook application being used is greater than that of the data file being loaded, a sequence of schema migrations will be automatically performed to bring the data file up to the current schema.  The application will notify you of each update. The file saved on exit will have the same schema number as that of the application just run.

### Contributing

I've designed this application primarily to suit my preferences as an instructor.  If there are other features that you would like included, please feel free to fork this repository and add them.  If you add a feature or bug fix that you think might be useful for others, you're welcome to submit a pull request.  As time permits, I'll probably do some testing on Windows and OSX.  If you encounter issues, you may post them here.
