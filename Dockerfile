FROM python:3.8
WORKDIR /authorizer
COPY ["./test*", "./operations*", "./app.py", "/authorizer/" ] 
CMD [ "python", "./app.py" ]