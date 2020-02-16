FROM python:alpine3.8
RUN apk add make
COPY . /topper
WORKDIR /topper
RUN ls
RUN make install

ENTRYPOINT ["topper"]


