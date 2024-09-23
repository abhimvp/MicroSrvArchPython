import os,requests

def token(request):
    if not "Authorization" in request.headers:# check if the client has sent the authorization header in request.headers:
        return None, ("missing credentials",401)
    
    token = request.headers['Authorization'] # get the token from the header

    if not token: # check if the token is empty
        return None, ("missing credentials", 401)
    
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token}
    )

    if response.status_code == 200: # check if the token is valid
        return response.text,None
    else:
        return None, (response.text, response.status_code)