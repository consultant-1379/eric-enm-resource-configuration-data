FROM node:16-alpine AS build

WORKDIR /web

COPY package.json package-lock.json ./

RUN npm i
