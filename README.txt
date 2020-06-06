Matching Markets - Deferred Acceptance and Market Clearing HW2 assignment eCommerce Technion 2019



In the competitive part, we decided to "merge" each pair of students into one "pseudo-student".
Each "pseudo student" has unique ID ('sid_1.sid_2'), a combined projects preferences list and an average 
grade in CS and math.

Once the student merging is complete, we use the deferred acceptance algorithm and assign 
each "pseudo-student" a project in the following matter:
Data set 1 : using the average score in math or CS as a tiebreaker.
Data sets 2 - 4 : using the total utility as a tiebreaker (we chose the students with higher utility).

Finally, we iterate over all "pseudo-students" and assign the given project to the students in it.
