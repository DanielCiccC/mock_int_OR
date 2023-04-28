import os
import csv

class name_tag:

    '''
    classdocs
    '''

    def __init__(self, name, subheading=None, logo=None):
        '''
        Constructor
        '''
        self.name = name
        self.subheading = subheading
        self.logo = logo

    def get_name(self):
        return self.name

    def get_subheading(self):
        return self.subheading

    def get_logo(self):
        return self.logo


def loader():
    local_address = os.getcwd()
    with open(local_address + '\\nametags.csv', newline='', encoding="utf8") as csvfile:

        tags = []
        reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
        next(reader, None)  # skip the headers

        for row in reader:
            tags.append(name_tag(row[0], row[1], (row[2] if row[2] != "" else "white")))
            
    return tags

def buildtags(student_list):
    # tags = loader()
    latextags = ""
    for student in student_list:
        latextags += "\\confpin{" + "images/watermark2}{" + (student[1] if student[1] != '' else '--' ) + "}{" 
        latextags += (student[2] if student[2] != '' else '--') + "}{" 
        latextags += (student[3] if student[3] != '' else '--') + "}{" 
        latextags += (student[4] if student[4] != '' else '--') + "}{" 
        latextags += student[0] + "}\n"
    
    return latextags


def latex_writer(student_list):
    local_address = os.getcwd()
    with open(local_address + '/nametag_build/main.tex', newline='', encoding="utf8") as latexdoc:

        oldcontents = latexdoc.read()
        lindex = oldcontents.find("\\begin{document}")
        newcontents = oldcontents[0:lindex] + "\\begin{document}\n" + buildtags(student_list) + "\\end{document}"
        # with open(local_address + '/text.txt', 'w', encoding="utf8") as text:
        #     text.write(newcontents)

    with open(local_address + '/nametag_build/main.tex', 'w', newline='', encoding="utf8") as latexdoc:
        latexdoc.write(newcontents)

    print('END NAMETAG BUILD')

