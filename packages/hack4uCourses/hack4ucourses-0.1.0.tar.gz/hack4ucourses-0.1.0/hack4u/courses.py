class Course:
    def __init__(self, name, duration, link):
        self.name = name
        self.duration = duration
        self.link = link

    def __repr__(self):
        return f"El curso: {self.name}, tiene una duración de {self.duration} horas. Link = {self.link}"


courses = [ 
    Course("Introducción a Linux", 15, "https://hack4u.io/cursos/introduccion-a-linux/"),
    Course("Personalización de Entorno Linux", 3, "https://hack4u.io/cursos/personalizacion-de-entorno-en-linux/"),
    Course("Introducción al Hacking", 53, "https://hack4u.io/cursos/introduccion-al-hacking/"),
    Course("Python Ofensivo", 35, "https://hack4u.io/cursos/python-ofensivo/"),
    Course("Hacking Web", 51, "https://hack4u.io/cursos/hacking-web/")
]

def list_courses():
    for course in courses:
        print(course)

def search_by_name(name):
    for course in courses:
        if course.name == name:
            return course
        
    return None