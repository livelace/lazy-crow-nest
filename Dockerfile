FROM            docker.io/python:3.9-buster

ENV             LCN_TEMP="/tmp/lcn"
ENV             PIP_CONFIG_FILE="pip.conf"

# copy dataset.
RUN             mkdir -p "/data"

# year.
COPY            "data/spark/lazy-crow-nest/job-hh-common-rss-year.pickle" "/data/common-year.pickle"
COPY            "data/spark/lazy-crow-nest/job-hh-it-rss-year.pickle" "/data/it-year.pickle"

# six months.
COPY            "data/spark/lazy-crow-nest/job-hh-common-rss-six-months.pickle" "/data/common-six-months.pickle"
COPY            "data/spark/lazy-crow-nest/job-hh-it-rss-six-months.pickle" "/data/it-six-months.pickle"

# three months.
COPY            "data/spark/lazy-crow-nest/job-hh-common-rss-three-months.pickle" "/data/common-three-months.pickle"
COPY            "data/spark/lazy-crow-nest/job-hh-it-rss-three-months.pickle" "/data/it-three-months.pickle"

# create user.
RUN             useradd -m -u 1000 -s "/bin/bash" "lcn"

USER            "lcn"

# install app.
COPY            "work" "$LCN_TEMP"

RUN             cd "$LCN_TEMP" && \
                pip install --no-cache-dir --user -r "requirements.txt" && \
                pip install --no-cache-dir --user . && \
                rm -rf "$LCN_TEMP"

WORKDIR         "/home/lcn"

CMD             ["/home/lcn/.local/bin/lazy-crow-nest"]
