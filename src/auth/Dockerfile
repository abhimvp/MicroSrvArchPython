# when we are building a docker image , we're building on top of base image which is below line
FROM python:3.12-slim-bullseye
# think image as file system snapshot - which contains neccesary dependencies to run our python applications
# also remember each instruction creates a image layer on top of each other - here on top of base image instruction we will gave RUn instruction
# in purpose of cache only builds the changed files & improves build time instead of running each instruction again 


# we move onto install OS dependencies & all these flags(--) & (\) is to avoid installing unneccesary additional packages as well as
# avoiding taking up additional space with caching & stuff like that , we want our container to be as light as possible
RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    pkg-config \
    build-essential default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip 


# creating a directory to work in & this dir is where our application source is going t live
WORKDIR /app
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

# our app listens on port 5000
EXPOSE 5000

CMD ["python3","server.py"] 
# same as python3 server.py