FROM nginx:trixie-perl
RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-venv libaugeas-dev gcc
RUN apt-get remove certbot
RUN python3 -m venv /opt/certbot/
RUN /opt/certbot/bin/pip install --upgrade pip
RUN /opt/certbot/bin/pip install certbot certbot-nginx
RUN ln -s /opt/certbot/bin/certbot /usr/bin/certbot
# renewal cron job
RUN echo "0 0,12 * * * root /opt/certbot/bin/python -c 'import random; import time; time.sleep(random.random() * 3600)' && sudo certbot renew -q" | tee -a /etc/crontab > /dev/null
