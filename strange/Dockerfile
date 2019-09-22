FROM ubuntu:18.04 as build

RUN apt -y update && apt -y upgrade && apt -y install build-essential

WORKDIR /build

COPY ./strange.c ./Makefile ./

ARG ADMIN_KEY="misconfigured"
RUN make ADMIN_KEY=${ADMIN_KEY} -

FROM ubuntu:18.04

RUN apt -y update && apt -y upgrade && apt -y install socat

RUN useradd -ms /bin/sh strange

WORKDIR /opt
COPY --from=build /build/strange ./

ARG flag=flag{dummy_misconfigured}
RUN echo ${flag} > flag.txt
COPY ./docker-entrypoint.sh ./README ./

RUN chown -R root:strange /opt && \
      chmod 750 /opt && \
      chmod 554 /opt/strange && \
      chown root:strange /opt/flag.txt && \
      chmod 440 /opt/flag.txt && \
      chown root:strange /opt/docker-entrypoint.sh && \
      chmod 550 /opt/docker-entrypoint.sh && \
      chown root:strange README && \
      chmod 444 /opt/README

EXPOSE 7331
ENTRYPOINT [ "/opt/docker-entrypoint.sh" ]
