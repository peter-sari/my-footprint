# MY FOOTPRINT
###final project for CS50 2021
###by Viktor Nemeth and Peter Sari

#### Video Demo:
<URL HERE>

####App location:
[my-footprint.herokuapp.com](https://my-footprint.herokuapp.com/)

##DESCRIPTION
My Footprint is a website to demonstrate the idea of the impact of our behaviour on the world we live in. Following a registration visitors complete a questionnaire about their consumption. Based on our proprietary scoring we give a colour coded feedback on the impact. When no user is logged in we show the average result of all answers. The website’s main page also promotes some relevant charities.

##REASONS OF CHOSING THIS TASK
We worked in a pair to simulate a co-working situation. Using Heroku and GitHub we created a collaborative environment to simulate a real-world like project environment. We decided to build a web application to practice skills needed for:
- designing website logic using Python to create dynamic pages, including calculations from data in runtime
- using SQL to store data, including password hashed securely
- user sessions securely managed at server side
- using json to include file use and ensure the opportunity to amend with external content through an API
- using HTML, CSS and Bootstrap to create the front-end

##TASK SHARING
Most of the visual design and front-end was done by Peter. The SQL backend was done by Viktor and the python/flask coding was shared around half-half.

##DECISIONS TAKEN
The initial decision to use Heroku and Git were based on the idea of collaboration and “shareability”. Furthermore, since Heroku is a good starting place for apps and the base package is free that seemed like the right choice. Since Heroku’s filesystem is ephemeral SQLite wasn’t a viable option. 
In terms of collecting as little personal data as possible we have agreed not to take people’s email addresses. Usernames must be unique and contain no space. We didn’t put a restriction on the passwords because this is a demo. In real life of course that would be different. We collect the birth year and country of the user largely for “analytical purposes”. It would actually be interesting to see how different age/location groups respond. Again in real life there’d need to be a way to exclude bots/spam registrations. 
On the database side the star-schema was picked mostly as a “good coding habit” thing. With a demo/project app the data sizes are unlikely to reach the level where spending time on foreign keys and relationships is really justified but in the big scheme of things narrow tables are better suited for OLTP apps. Also, we’ve had discussions on the storage and retrieval model for the quiz answers data (i.e., more things stored or more things computed upon retrieval) and figured we’d strike a middle ground. If this were a large “real” project the cost of each component would drive the decision.
On the python/flask side the main decisions were around trying to write code efficiently (for beginners anyway) and avoid copy-pasting as much as possible. That said we haven’t created classes to a number of things where such would have been justified for larger projects. 
Visually the CSS primarily focuses on “traditional screen” use. While we could have done designs for mobile or print, we felt that for the intro to CS course that’s an overkill. 
The scoring “system” is proprietary, which is more to say we haven’t gone into lengths to define what precisely the actual points mean, and they don’t have a unit of measure. The idea is that each activity has a specific effect on every category (but not all the same), which then gets further weighted by the frequency the user picks.

##FILE LIST DESCRIPTION(S)
- static/styles.css: styling for the front-end.
- static/promoted.json: a json file for describing some relevant charities.
- templates/apology.html: error template file.
- templates/change_pwd.html: what it says on the tin.
- templates/index.html: this file generates the main output. If the user is logged in and they’ve done the quiz it will show their scores else suggest completing the quiz. If the user isn’t logged in it shows the average scores across the board.
- templates/layout.html: layout template.
- templates/login.html: what it says on the tin.
- templates/quiz.html: this is where the users can complete the quiz.
- templates/register.html: what it says on the tin – see description on discussion re: registration above.
- app.py: the main flask/python file. It drives all the processes.