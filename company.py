import itertools

class Company:

    all_companies = set()

    id_obj = itertools.count()


    # representatives needs to be a list.  index corresponds to the id.
    def __init__(self, name, representatives, rounds):

        self.representatives = set([Representative(rep) for rep in representatives])

        #the name of the company
        self.name = name.strip()

        #the number of rounds in the interview. Will facilitate further 
        # implementation to availability down the track
        self.rounds = rounds

        self.id = next(Company.id_obj)
        # print(representatives)
        cls = self.__class__

        for company in cls.all_companies:
            if self.name == company.get_name():
                raise Exception("two companies of the same name cannot exist")
   
        cls.all_companies.add(self)
    
    def total_interviews(self):
        return len(self.representatives) * self.rounds

    def name_from_id(id):
        for company in Company.all_companies:
            if id == company.get_id():
                return company.get_name()

    def __lt__(self, other):
        return self.name < other.get_name()

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name
    
    def find_company(company_name):
        for company in Company.all_companies:
            # print(company)
            if company.get_name() == company_name:
                return company
            
        raise Exception(f"Could not find company name {company_name}. Please check to make sure" +
            " the company name is written exactly the same as in the company sheet")
    
    def from_id(id):
        for company in Company.all_companies:
            if company.get_id() == id:
                return company
        raise Exception(f"Could not find company relating to id {id}. Please check to make sure" +
                        "that this is a relevant id")
    
    def len():
        return len(Company.all_companies)
    
    def get_reps(self):
        return self.representatives

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

class Representative:

    id_obj = itertools.count()

    all_reps = set()

    def __init__(self, name):
        self.name = name.strip()

        self.id = next(Representative.id_obj)

        self.__class__.all_reps.add(self)
    
    def len():
        return len(Representative.all_reps)
    
    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name
    
    def name_from_id(id):
        for rep in Representative.all_reps:
            if id == rep.get_id():
                return rep.get_name()
            
    def from_id(id):
        for rep in Representative.all_reps:
            if rep.get_id() == id:
                return rep
        raise Exception(f"Could not find representative relating to id {id}. Please check to make sure" +
                        "that this is a relevant id")

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
