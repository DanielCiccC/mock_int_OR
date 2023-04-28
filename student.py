from company import *
import itertools

MAX_PREFERENCE = 4
PREF_SENSITIVITY = 0.8 #no touching!


class Student:

    id_obj = itertools.count()

    all_students = set()

    def __init__(self, name, preferences, early_bird_scalar):

        #the index is related to the preference of the company
        self.preferences = [Company.find_company(comp) for comp in preferences]
        # print(f"{name} has preferences {self.preferences}")

        self.id = next(Student.id_obj)

        self.name = name.strip()

        self.scalar = early_bird_scalar

        self.early_bird_amount = 0 #applied at runtime

        cls = self.__class__
        cls.all_students.add(self)
    
    
    #Determine the preference of the company (value we wish to maximise on)
    #the company is an object type, not the name (i.e. str) of the company
    def calculate_preference(self, company):
        if company in self.preferences:
            # print(f'{self.name} has preference {MAX_PREFERENCE - self.preferences.index(company)} for company {company}')
            return MAX_PREFERENCE - self.preferences.index(company)
        else:
            return 1
    
    def get_name(self):
        return self.name

    def get_id(self):
        return self.id
    
    def find_company(student_name):
        for student in Student.all_students:
            # print(company)
            if student.get_name() == student_name:
                return student
            
        raise Exception(f"Could not find student name {student_name}. Please check to make sure" +
            " the student name is written exactly the same as in the preference sheet")

    def name_from_id(id):
        for student in Student.all_students:
            if id == student.get_id():
                return student.get_name()
    
    def from_id(id):
        for student in Student.all_students:
            if id == student.get_id():
                return student
    
    '''
    The early bird reward is proportional to the index of the student in the input sheet.
    since students are added into the solver incrementally (from top to bottom) we can safely 
    identify the most oldest student enrolments by the id assigned on input.
    '''
    def eb_reward(self, company):
        # print(f'the reward is {self.scalar * (1.0 - (float(self.get_id()) / float(len(Student.all_students))))} for id {self.id}')
        #take a staggered approach, the 'reward' is greatest for the first preference, and less so for the rest of the preferences
        reward = self.scalar * (1.0 - (float(self.get_id()) / float(len(Student.all_students))))
        pref_inv = self.preferences.index(company) if company in self.preferences else MAX_PREFERENCE
        return reward * (PREF_SENSITIVITY ** pref_inv)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
    
    def len():
        return len(Student.all_students)

    
