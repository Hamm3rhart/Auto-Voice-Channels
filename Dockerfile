FROM python:3

ENV DISABLE_LOOP=false
ENV HEARTBEAT_TIMEOUT=60
ENV RDY_MESSAGE=false
ENV AWS=false

RUN apt-get update -y &&\
    apt-get upgrade -y &&\
    apt-get -y install curl unzip &&\
    curl https://codeload.github.com/hamm3rhart/Auto-Voice-Channels/zip/master -o avc.zip &&\
    unzip avc.zip &&\
    mv Auto-Voice-Channels-master AutoVoiceChannels &&\
    apt-get -y remove curl unzip &&\
    rm avc.zip 
    

WORKDIR /AutoVoiceChannels

RUN apt-get -y install build-essential &&\
    pip install -r /AutoVoiceChannels/requirements.txt &&\
    apt-get -y remove build-essential
    
# Clear unused files
RUN apt clean && \
    rm -rf \
	/tmp/* \
	/var/lib/apt/lists/* \
	/var/tmp/*

CMD [ "bash", "startAVC.sh" ]
