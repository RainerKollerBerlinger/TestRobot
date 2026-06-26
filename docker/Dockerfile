FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        vim \
        git \
        curl \
        wget \
        apt-transport-https \
        software-properties-common \
        nodejs \
        npm \
        ca-certificates && \
    wget -q https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y powershell && \
    rm -rf /var/lib/apt/lists/*


COPY requirements.txt /tmp/

RUN pip3 install --break-system-packages \
    -r /tmp/requirements.txt

RUN rfbrowser init

WORKDIR /workspace

CMD ["/bin/bash"]