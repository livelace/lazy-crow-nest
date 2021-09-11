FROM            docker.io/python:3.9-buster

ENV             LCN_TEMP="/tmp/lcn"
ENV             LCN_URL="https://github.com/livelace/lazy-crow-nest"

# copy dataset.
RUN             mkdir -p "/data"

COPY            "data/spark/lazy-crow-nest/common.pickle" "/data/common.pickle"

# create user.
RUN             useradd -m -u 1000 -s "/bin/bash" "lcn"

USER            "lcn"

# install app.
COPY            "work" "$LCN_TEMP"

RUN             cd "$LCN_TEMP" && \
                pip install --user -r "requirements.txt" && \
                pip install --user . && \
                rm -rf "$LCN_TEMP"

WORKDIR         "/home/lcn"

CMD             ["/home/lcn/.local/bin/lazy-crow-nest"]