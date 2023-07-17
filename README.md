# Cinema-project (Pet project)
This is a web application for a cinema site.

The project implements user, cinema hall, cinema session, purchase models.

**Functionality:**

1) **Superuser** can:
   - create a cinema hall and cinema sessions;
   - can change a hall or session if no tickets have been purchased for this hall or for this cinema session.
     
2) **User** (logged in) can:
   - view the list of cinema sessions for today and in a separate page for tomorrow, the number of empty seats in the cinema hall;
   - buy tickets for the cinema session;
   - view the list of purchases he made, and the total amount spent for the entire time; 
3) If the user is not logged in, then he sees only a list of cinema sessions, can sort it, but cannot buy anything;
4) Cinema sessions can be sorted by price (ascending or descending) or start time;
5) Cinema sessions in the same hall cannot overlap.  

**REST API**

According to the REST has been added the ability to receive information about all cinema sessions for today, which begin at a certain period of time and/or go in a specific hall.

**Getting started guide**

To run the application, follow these steps:
1)  clone this repository;
2)  install the required dependencies (using pip install -r requirements.txt);
3)  create a .env file with the required environment variables;
4)  run python manage.py migrate to create the database tables;
5)  create a superuser account using python manage.py createsuperuser;
6)  run python manage.py runserver to start the development server;
7)  navigate to http://localhost:8000 in your web browser.

**Technologies Used**

Django

Django REST framework

SQLite

HTML

