My project takes on a few different options, though one of the challenging parts is redirecting to login by default. Typically I'll modify my track to go to /login or click on login to start. From there pages can be searched, isbn's can be clicked on to lead to reviews and Goodread reviews, and /api can be added to pull my review information directly.

User passwords are hashed. 

Error.html is used a few times to populate error messages. 
Layout.html is using bootstrap to spice up the site, though more CSS is needed long-term.
Index.html is the default search page.
Login.html is functional and stores hashed passwords in a database called users.
Registration is allowed and policed.
Partial search terms work, but only incomplete terms and not miscapitalized ones at this time.
Temp.html was a temporary holding cell to test my API route.
Thanks.html pops up after a user gives a review, which is stored in a reviews table and accessible on an individual book page.