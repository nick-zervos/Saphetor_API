# Saphetor_API  

**Instructions**  

Clone or download the repository and activate the virtual environment by running "source env/bin/activate".

Then install the requirements by running ```"pip install -r requirements.txt"```.


Finally cd into the vcf_api folder and run ```"python manage.py migrate"```, then ```"python manage.py test"``` to run the tests, and ```"python manage.py runserver"``` to start the development server.

The application will begin to run at 127.0.0.1:8000, and can be accessed using an API testing tool like postman.

The endpoints are:

127.0.0.1:8000/get_data/  
127.0.0.1:8000/get_data/?id=rs1234  
127.0.0.1:8000/post_data/  
127.0.0.1:8000/put_data/?id=rs1234  
127.0.0.1:8000/delete_data/?id=rs1234  

The HTTP_AUTHORIZATION header is required for the post request with a value of "Token secret". Also the "Content-type" header must be set to "application/json".

The vcf file must be named "file.vcf" and placed in the root folder of the project (where requirements.txt, env and vcf_api folders are located) for the application to locate it.
