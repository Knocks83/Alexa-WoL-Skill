FROM python:buster

WORKDIR /app

# Install required packages
RUN apt install git
RUN apt install binutils

# Clone the repo to /app
RUN git clone https://github.com/Knocks83/Alexa-WoL-Skill.git /app

# Install dependencies
RUN pip3 install -r /app/requirements.txt
RUN pip3 install pyopenssl

COPY config.env /app/config.env

CMD ["python3", "run.py"]
