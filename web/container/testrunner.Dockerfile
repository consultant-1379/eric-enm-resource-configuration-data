FROM armdocker.rnd.ericsson.se/proj-eric-enm-resource-configuration-data/base:latest AS build
COPY run_front_end_tests.sh /run_front_end_tests.sh

RUN apk add --no-cache \
      chromium \
      nss \
      freetype \
      harfbuzz \
      ca-certificates \
      ttf-freefont \
      python3 \
      py3-pip \
      python3-dev \
      bash \
      libffi \
      libffi-dev \
      gcc \
      libc-dev; \
      npm i @playwright/test@1.33.0

ENTRYPOINT ["sh", "/run_front_end_tests.sh"]