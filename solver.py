import csv 
import pulp 
import re 
import pandas as pd
from openpyxl import load_workbook
from importer import *
from nametagbuilder import *
from timeit import default_timer as timer

#Modify these elements
START = timer()
INPUT_SHEET = 'input_1.xlsx'
OUTPUT_FILE = "output/mockintoutput.xlsx"
ROUNDS = 4
TIMESLOTS = range(ROUNDS) #sessions
TOLERANCE = None
TIME_LIMIT = None

#Additional elements
ENROLMENT_REQUIREMENT = 0.00 #MUST BE FLOAT. If you don't want to use this, leave as 0.00
EARLY_BIRD_SCALAR = 3.00 #MUST BE FLOAT. If you don't want to use this, leave as 0.00
NAMETAG_BUILD = True  #because who want to hand write name tags?


# Import all our data parameters
#######################################################################################
import_companies(INPUT_SHEET, ROUNDS)
import_students(INPUT_SHEET, EARLY_BIRD_SCALAR)

# Make model
INTSCHEDULE = pulp.LpProblem("interviewSchedule", pulp.LpMaximize) #maximise flight time


#VARIABLES
#######################################################################################
RepInterviewStudentAtTime = pulp.LpVariable.dicts(
    'RepInterviewStudentAtTime', ((c.get_id(), r.get_id(), k.get_id(), t) for c in Company.all_companies 
        for r in c.get_reps() for k in Student.all_students for t in TIMESLOTS), cat=pulp.LpBinary
) #A student attends an interview with a company representative at time T


#OBJECTIVE FUNCTION
#######################################################################################
INTSCHEDULE += pulp.lpSum(RepInterviewStudentAtTime[c.get_id(), r.get_id(), k.get_id(), t] * (k.calculate_preference(c) + k.eb_reward(c)) for c in Company.all_companies 
        for r in c.get_reps() for k in Student.all_students for t in TIMESLOTS)


#CONSTRAINTS
#######################################################################################

# A student can only participate in one lesson (MAX) per each timeslot
for k in Student.all_students:
    for t in TIMESLOTS:
        INTSCHEDULE += pulp.lpSum(RepInterviewStudentAtTime[c.get_id(), r.get_id(), k.get_id(), t] for
            c in Company.all_companies for r in c.get_reps()) <= 1

#A company representative can only take one lesson at a time
for c in Company.all_companies:
    for r in c.get_reps():
        for t in TIMESLOTS:
            INTSCHEDULE += pulp.lpSum(RepInterviewStudentAtTime[c.get_id(), r.get_id(), k.get_id(), t] for
            k in Student.all_students ) <= 1

# This is a rule enforced by Lois. A Student is supposed to attend two timeslot sessions in 
# periods {0, 2} or {1, 3} (i.e. a students should not be enrolled in sessions {0,1} for example).
# Build constraints to enforce this rule.
for k in Student.all_students:
    INTSCHEDULE += pulp.lpSum(RepInterviewStudentAtTime[c.get_id(), r.get_id(), k.get_id(), 0] for
            c in Company.all_companies for r in c.get_reps()) + pulp.lpSum(
                RepInterviewStudentAtTime[c.get_id(), r.get_id(), k.get_id(), 1] for
            c in Company.all_companies for r in c.get_reps()) >= 1

    INTSCHEDULE += pulp.lpSum(RepInterviewStudentAtTime[c.get_id(), r.get_id(), k.get_id(), 2] for
            c in Company.all_companies for r in c.get_reps()) + pulp.lpSum(
                RepInterviewStudentAtTime[c.get_id(), r.get_id(), k.get_id(), 3] for
            c in Company.all_companies for r in c.get_reps()) >= 1
    
    INTSCHEDULE += pulp.lpSum(RepInterviewStudentAtTime[c.get_id(), r.get_id(), k.get_id(), 2] for
            c in Company.all_companies for r in c.get_reps()) + pulp.lpSum(
                RepInterviewStudentAtTime[c.get_id(), r.get_id(), k.get_id(), 1] for
            c in Company.all_companies for r in c.get_reps()) >= 1

# A student can only take maximum one lesson per company
for k in Student.all_students:
    for c in Company.all_companies:
        INTSCHEDULE += pulp.lpSum(RepInterviewStudentAtTime[c.get_id(), r.get_id(), k.get_id(), t] for r in c.get_reps() for t in TIMESLOTS) <= 1

#ASIDE: the following is further implementation that is not required by the scheduler by may be implemented if the 
# organiser sees fit.

#A company should enrolled in at least x% of their interviews
for c in Company.all_companies:
    INTSCHEDULE += (pulp.lpSum(RepInterviewStudentAtTime[c.get_id(), r.get_id(), k.get_id(), t] for r in c.get_reps() 
            for t in TIMESLOTS for k in Student.all_students) / c.total_interviews()) >= ENROLMENT_REQUIREMENT


#OPTIMISE
INTSCHEDULE.solve(pulp.PULP_CBC_CMD(timeLimit=TIME_LIMIT, gapRel=TOLERANCE))

print("Objective value ", pulp.value(INTSCHEDULE.objective))

#capture all variables
inspect = [[v.name, v.varValue] for v in INTSCHEDULE.variables()]


'''
This function builds the timetable based on the LP formulation output
'''
def build_timetable(key_value):
    companies_sorted = list(Company.all_companies)
    sortedByName = sorted(companies_sorted, key=lambda x: x.name)

    schedule = [[c.get_name(), r.get_name(), '', '', '', ''] for c in sortedByName for r in list(c.get_reps())]
    preference_schedule = [[c.get_name(), r.get_name(), '', '', '', ''] for c in sortedByName for r in list(c.get_reps())]
    student_list = [[k.get_name(), '', '', '', ''] for k in Student.all_students]
    
    for key, value in key_value:

        # continue if an interview did not transpire
        if value == 0:
            continue

        # dimensions: c, r, k, t
        indexes = key.split("(")[1].split(")")[0].split(',_')
        
        company =  Company.from_id(int(indexes[0]))
        rep = Representative.from_id(int(indexes[1]))
        student = Student.from_id(int(indexes[2]))
        t = int(indexes[3])
        
        schedule, preference_schedule = update_schedule(schedule, 
                preference_schedule, company, rep, student, t)
        
        
        if NAMETAG_BUILD:
            student_list = update_name_list(student_list, company, rep, student, t)

    df = pd.DataFrame(numpy.array(schedule),
                   columns=['', '', 'ROUND 1', 'ROUND 2', 'ROUND 3', 'ROUND 4'])
    df_pref_schedule = pd.DataFrame(numpy.array(preference_schedule),
                   columns=['', '', 'ROUND 1', 'ROUND 2', 'ROUND 3', 'ROUND 4'])
    
    df2 = pd.DataFrame(build_summary(pulp.LpStatus[INTSCHEDULE.status], 
            TOLERANCE, (END-START), TIME_LIMIT, Student.len(), 
            Representative.len(), Company.len(), len(TIMESLOTS), 
            INPUT_SHEET, OUTPUT_FILE, pulp.value(INTSCHEDULE.objective), 
            len(inspect), ENROLMENT_REQUIREMENT, EARLY_BIRD_SCALAR))
    
    book = load_workbook(OUTPUT_FILE)
    writer = pd.ExcelWriter(OUTPUT_FILE, engine = 'openpyxl')

    #If we are also going to build the nametags
    if NAMETAG_BUILD:
        # build_nametags(student_list)
        print('STARTING NAMETAG BUILD')
        latex_writer(student_list)


    writer.book = book
    df2.to_excel(writer, "OVERVIEW", index=False)
    df.to_excel(writer, "Timetable", index=False)
    df_pref_schedule.to_excel(writer, "Preference schedule", index=False)
    
    writer.close()

'''
updates the schedule array
'''
def update_schedule(schedule, preference_sched, company, rep, student, t):
    #we will be testing our logic on 'schedule' but the preference schedule mirrors the same 
    #dimensionality
    for idx in range(len(schedule)):
        if schedule[idx][0] == company.get_name() and schedule[idx][1] == rep.get_name():
            if schedule[idx][t + 2] != '':
                raise Exception('two people have been scheduled for the same time. You are replacing' +
                f" {schedule[idx][t+2]} with {student}")
            schedule[idx][t + 2] = student.get_name()
            preference_sched[idx][t + 2] = round(float(student.calculate_preference(company) + student.eb_reward(company)), 3)
            
    return schedule, preference_sched

'''
Updates the name list that is later piped into the main.tex file
'''
def update_name_list(schedule, company, rep, student, t):
    for row in schedule:
        if row[0] == student.get_name():
            if row[t + 1] != '':
                raise Exception('two companies have been scheduled for the same time. You are replacing' +
                f" {row[t+1]} with {student}")
            row[t + 1] = f'{company.get_name()}: {rep.get_name()}'
    return schedule

'''
Builds a summary worksheet of the LP formulation
'''
def build_summary(status, tolerance, timer, timelimit, students, reps, 
        companies, time, input, output, result, variables, enrol_require, 
        eb_scalar):
    return {'Particulars' : ['Status', 'Tolerance', 'Minimum Company enrolment',
             'Early-bird quantity', 'Performance (sec)', 'Time limit', 
            'Input sheet', 'Output sheet', 'Result', '---', 'Students', 
            'Representatives', 'Companies', 'Timeslots', 'Variables'],
            'Value': [status, (tolerance if tolerance is not None else 'n.a.'), 
            (f'{enrol_require * 100}%' if enrol_require != 0 else 'n.a.'), 
            (eb_scalar if eb_scalar != 0 else 'n.a.'),
            timer, (timelimit if timelimit is not None else 'n.a.'), 
            input, output, result, '---', students, reps, companies, 
            time, variables]}

END = timer()
build_timetable(inspect)