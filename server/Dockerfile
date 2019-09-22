FROM ubuntu:18.04

RUN apt -y update && apt -y upgrade && apt -y install curl && apt -y remove cmdtest
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - && apt -y update && apt -y install nodejs

WORKDIR /opt/powerplant

COPY ./package.json ./
RUN npm install

COPY . .

CMD ["npm", "run", "serve"]