# Gradebook
## Simple command-line application for quickly setting up a course to teach, recording student scores and viewing reports.

At this point the application has only been tested on Linux Mint 17 and 18. It requires Python 3.x.
The user interface is based on [Python Menu-3.1.0](https://pypi.python.org/pypi/Menu/).  Install that via "pip3 install --user Menu".  Of course, you will also want to have numpy installed for python3.

All data for a course is stored in a single JSON file, which is written when you 'Save' or 'Quit'.  The top level 'Course' object has properties for the course name and the term.  The JSON file is named by a concatenation of these. A Course contains lists of Categories, Graded Items and Students and a dictionary of Scores.  

To open Gradebook for a specific saved course named "Math 251" in the term "Fall 2017" we execute it like this:

```$ ./gb1 Math_251_Fall_2018.json```  

### New Course Setup
You can create a new course by running the application without specifying a file.  You should see a menu like this:

Gradebook

1. Quit
2. Save
3. Enter Scores All Students
4. Enter Scores One Student
5. Reports
6. Manage Graded Items
7. Manage Categories
8. Manage Students
9. Import Students
10. Edit Course

```>>>``` 

#### Course

To set up a new course, first select 'Edit Course' to change the Course name and term as you like.  

#### Students

Next add your students, either by using 'Manage Students' to enter them manually (first name, last name, email) or by using 'Import Students' to import them from a tab-separated text file with no header and columns in that order named 'students.txt'.  A sample file, 'students.txt.sample', is provided in this repository.  Students are always 'active' when added, but can later be inactivated or deleted.

#### Categories

The next step is to Manage Categories. A category could be 'Quiz' or 'Midterm 1', for example, it counts collectively for a specific percent of the grade.  So if you said on the syllabus that 20% of the grade will based on quizzes and the midterm was worth 25%, you would set up these two categories accordingly.  If you want to automatically drop each student's lowest quiz grade, just enter 1 when prompted for 'drop lowest n' (this defaults to zero) when setting up the Quiz category.

#### Graded Items

Once a category has been set up, you can add graded items, such as Quiz 1.  Each graded item is associated with a category.  There is quite a bit of flexibility built in.  For example, you specify the points for each question.  If you want one of the questions to be a bonus, just subtract its point value from the total, which is specified separately.

Suppose half the class failed the midterm and you decide to allow a retake option so that students can earn 25% of the difference of the retake score and the original score.  This could be handled by setting the retake percentage of the graded item 'Midterm retake' to be 25.  You would just need to enter the differences between the scores.  If the retake percentage is 0 (the default) for all graded items in a category, they are combined simply by averaging.  

A graded item may also be "curved" by setting its "added points" or "added percent".  If either of these is nonzero, it will be applied to the graded item before any combination is applied.  It is easy to include bonus problems on a quiz or exam, since you specify separately the total points and the individual question points.  The sum of the individual question points may exceed the total points, but may not be less than the total.  These options don't appear when you add a new graded item, but are available when you edit an existing one.  

### Entering Scores
Entering scores is pretty simple and optimized for speed.  Normally you will want to enter scores for all students for a particular quiz.  The application will prompt you sequentially for each score for each student.  You can skip to the next student by entering 'n' or go back to the previous student using 'p'.  You can go back to the last problem using 'b' and quit data entry using 'q'.  You can also skip over a question by just hitting enter to leave the previous value unchanged.  This idea is used everywhere in the application.

If you make an invalid entry, such as a typo, or entering a score for a question that is greater than the points for the question, an audible and visible warning will be given.  You will also receive an audible and printed warning if you try to go past the end of the list, or go back before the beginning.

#### Importing Scores

If part of the students' grade is determined by scores that are reccorded in another system, such as Webassign, it may be useful to import those scores.  For example, the total scores for a single Webassign assignment or the overall webassign total can be imported into an existing graded item with a single question representing the total possible points.

The tab-separated scores file to be imported must be named scores.txt and located in the application folder, and must match the layout of the 'scores.txt.sample' file provided in this repository.

### Reporting

The reporting capabilities include the following:

* Graded Item Details: This has one row for each active student and a column for each question on the graded item along with total and percent columns.  The rows are sorted by total so it is easy to see which students are struggling.  An average row is provided at the bottom so you can see which problems were more difficult. 
* Class Details: This has a similar format to the graded items report, but instead of showing columns for individual questions, shows the total score as a column for each graded item.
* Class Summary: This groups the graded items into categories and displays the weight for each category.  Unlike the Graded Item Details and Class Details reports, this report is able to apply the special summarization features, such as dropping the lowest quiz or combining the midterm scores with the retake scores.
* Student Summary: This combines all scores for each student into a single text string like "Homework (10% of grade): 94%, Quizzes (25% of grade) 87%, Midterm 1 (20% of grade) 78%".  There is an option to email (via gmail) this grade summary to one or all students in the class.  All you need to do to make this work is rename the file 'gmail_credentials.txt.sample' to 'gmail_credentials.txt' and edit it to include your personal gmail account information and signature.

A histogram with letter grade bins pops up for each of the first three reports.

### Course Data Schema

A schema version number is now stored in the JSON course file.  If the gradebook application schema number is greater than that of the data file being loaded, a sequence of schema migrations will be automatically performed to bring the data file up to the current schema.  The file saved on exit will have the same schema number as that of the application being run.
