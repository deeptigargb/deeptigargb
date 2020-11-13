# TODO: Merge requirements.txt and requirements-dbt.txt
# TODO: Merge Dockerfile and Dockerfile.dbt
# TODO: Accomodate these changes in KubernetedPodOperator and Makefile

FROM quay.io/deeptigargb/deeptigargb:latest

USER root

WORKDIR /home/jenkins/my_deploy

RUN mkdir ~/.ssh && sh -c "echo -e 'Host github.com \n\tHostName github.com\n\tUser git\n' > ~/.ssh/config"

# Downloading and install gcloud package
RUN curl https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-292.0.0-linux-x86_64.tar.gz > /tmp/google-cloud-sdk-292.0.0-linux-x86_64.tar.gz
RUN mkdir -p /usr/local/gcloud \
    && tar -C /usr/local/gcloud -xf /tmp/google-cloud-sdk-292.0.0-linux-x86_64.tar.gz \
    && /usr/local/gcloud/google-cloud-sdk/install.sh \
    && rm /tmp/google-cloud-sdk-292.0.0-linux-x86_64.tar.gz

# Adding the gcloud package path to local
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

COPY requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

COPY deeptigargb/ deeptigargb/
COPY manifest.yml deeptigargb/manifest.yml
COPY sync_composer.py deeptigargb/sync_composer.py

# As COPY auto-assigns ownership to `root`, we change it
# so that `jenkins` can access the files as needed.
RUN chown -R jenkins:jenkins /home/jenkins/my_deploy
