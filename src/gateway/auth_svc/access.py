import os , requests # this requests is different from requests we import in flask
# this requests is going to be the module that we use to make HTTP calls to our auth service

def login(request):
    auth = request.authorization
    if not auth: # if the user is not authenticated
        return None,("missing credentials",401) # None for our token
    
    basicAuth = (auth.username, auth.password)
    # auth_url = "XXXXXXXXXXXXXXXXXXXXXXXXXX" # this is the url of our auth service
    res = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
        auth=basicAuth
    ) # we're making a post request to our auth service with the data from the request
    
    if res.status_code == 200: # if the request is successful
        return res.text,None # token and none for the error
    else:
        return None,(res.text,res.status_code)
    