# Saphetor_API

Clone the repository and activate the virtual environment by running "source env/bin/activate".

Then install the requirements by running "pip install -r requirements.txt".

Finally cd into the vcf_api folder and run "python manage.py test" to run the tests, and "python manage.py runserver" to start the development server.

The application will begin to run at 127.0.0.1:8000.

The endpoints are:

127.0.0.1:8000/get_data/
127.0.0.1:8000/get_data/?id=rs1234
127.0.0.1:8000/post_data/

The HTTP_AUTHORIZATION header is required for the post request with a value of "Token secret".

The vcf file must be named "file.vcf" and placed in the root folder (where requirements.txt is located) for the application to find it.
