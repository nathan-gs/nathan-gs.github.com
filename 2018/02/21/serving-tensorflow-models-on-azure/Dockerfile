FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential \
        curl \
        libfreetype6-dev \
        libpng12-dev \
        libzmq3-dev \
        pkg-config \
        python \
        python-dev \
        rsync \
        software-properties-common \
        unzip \
        nodejs \ 
        npm \
        git-core \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN curl -O https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

RUN git clone https://github.com/sugyan/tensorflow-mnist /sugyan-tensorflow-mnist
RUN cd /sugyan-tensorflow-mnist;  pip --no-cache-dir install -r requirements.txt

RUN cd /sugyan-tensorflow-mnist; npm install

RUN cd /sugyan-tensorflow-mnist; cp src/js/main.js static/js/main.js


EXPOSE 80
ENV PATH="/sugyan-tensorflow-mnist:$PATH"

WORKDIR /sugyan-tensorflow-mnist
CMD ["gunicorn", "main:app", "--log-file=-", "-b", "0.0.0.0:80"]