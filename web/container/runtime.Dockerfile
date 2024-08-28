FROM armdocker.rnd.ericsson.se/proj-eric-enm-resource-configuration-data/base:latest AS build

COPY ./ ./

RUN npm run build


FROM armdocker.rnd.ericsson.se/proj-eric-enm-resource-configuration-data/nginx:1.21.1-alpine

WORKDIR /srv/rcd-fe

COPY --from=build /web/dist ./
COPY container/nginx.conf /etc/nginx/nginx.conf

EXPOSE 443
