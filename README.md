# Saphetor_API  

**Instructions**  

Clone the repository.  

```
git clone https://github.com/nick-zervos/Saphetor_API.git
```
Navigate into the repository folder.  

```
cd Saphetor_API/
```

Activate the virtual environment.  

```
source env/bin/activate
```

Install the requirements.  
```
pip install -r requirements.txt
```

Finally navigate into the vcf_api folder
```
cd vcf_api/
```

and run
```
python manage.py migrate
```
then to run the tests
```
python manage.py test
``` 
and finally to activate the developlment server
```
python manage.py runserver
```


The application will begin to run at 127.0.0.1:8000, and can be accessed using an API testing tool like postman.

The endpoints are:
```
127.0.0.1:8000/get_data/  
```
```
127.0.0.1:8000/get_data/?id=rs1234  
```
```
127.0.0.1:8000/post_data/  
```
```
127.0.0.1:8000/put_data/?id=rs1234  
```
```
127.0.0.1:8000/delete_data/?id=rs1234  
```

The HTTP_AUTHORIZATION header is required for the POST, PUT and DELETE endpoints with a value of ```Token secret```. Also the "Content-type" header must be set to ```application/json```.

The vcf file must be named ```file.vcf``` and placed in the root folder of the project (where requirements.txt, env and vcf_api folders are located) for the application to locate it.
