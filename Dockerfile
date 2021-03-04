FROM            docker.io/python:3.9.2-buster

ENV             LCN_TEMP="/tmp/lcn"
ENV             LCN_URL="https://github.com/livelace/lazy-crow-nest"

# copy data.
RUN             mkdir -p "/data"

COPY            "/mnt/spark/lazy-crow-nest/common.pickle" "/data/common.pickle"
COPY            "/mnt/spark/lazy-crow-nest/keywords.pickle" "/data/keywords.pickle"
COPY            "/mnt/spark/lazy-crow-nest/tags.pickle" "/data/tags.pickle"

# create user.
RUN             useradd -m -u 1000 -s "/bin/bash" "lcn"

USER            "lcn"

# lcn.
RUN             git clone --depth 1 --branch "$VERSION" "$LCN_URL" "$LCN_TEMP" && \
                cd "$LCN_TEMP" && \
                pip install --user -r "requirements.txt" && \
                pip install --user . && \
                rm -rf "$LCN_TEMP"

WORKDIR         "/home/lcn"

CMD             ["/home/lcn/.local/bin/lazy-crow-nest"]