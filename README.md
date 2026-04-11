Group Names: Devin Alvarez, Isai Quirino

First Preliminary Delivery (3/6/26)
Project Description:
Homework/assignment tracker where students can share deadlines, post tips, questions and form study groups. 
Like a personal tracker with a social aspect. 
The main goal is to connect students across any field of study with other students in the same field. 
Some features in mind include sharing events, internship experiences, and professor ratings.
Students will be able to post in their respective communities and have comments. 
The intention is to make a Reddit-like social app but for college students. 

Agile Planning:
[Agile Plan (3-6-26).docx](https://github.com/user-attachments/files/25808983/Agile.Plan.3-6-26.docx)

---

Steps To Run Website From A New Codespace:

1-Create and activate the virtual environment
(python3 -m venv virt , source virt/bin/activate)

2-Go into project directory
(cd socialApp/)

3-Install Dependencies
(pip install -r requirements.txt)

4-Run Migrations
(python3 manage.py migrate)

5-Create a superuser -optional-
-used to access admin panel/user database-
(python3 manage.py createsuperuser)

6-Run Server 
(python3 manage.py runserver)


Note: The project starts with an empty user database (.gitignore)