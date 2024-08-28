FROM alpine:3.16.0

RUN apk add --update python3 py3-pip python3-dev curl openssl bash libffi libffi-dev gcc libc-dev
COPY gen/ ./gen
ARG GERRIT_USERNAME
ARG GERRIT_PASSWORD_ENCRYPTED
ENV GERRIT_USERNAME=$GERRIT_USERNAME
ENV GERRIT_PASSWORD=$GERRIT_PASSWORD_ENCRYPTED
ENV EIC_HELM_VERSION=3.13.2
RUN curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x ./kubectl \
    && cp /bin/sh /usr/bin \
    && mv ./kubectl /usr/local/bin/kubectl \
    && curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 \
    && chmod +x get_helm.sh && ./get_helm.sh --version v3.9.0 \
    && curl -O https://arm1s11-eiffel052.eiffel.gic.ericsson.se:8443/nexus/service/local/repositories/eo-3pp-tools/content/com/helm/helmfile/0.149.0/helmfile-0.149.0.gz \
    && tar xfz helmfile-0.149.0.gz \
    && chmod a+rwx ./helmfile \
    && mv ./helmfile /usr/local/bin \
    && python3 -m pip install --upgrade pip \
    && pip3 install -r /gen/requirements.txt \
    && mkdir -p /eic_helm \
    && curl -sSL https://get.helm.sh/helm-v${EIC_HELM_VERSION}-linux-amd64.tar.gz | tar xz -C /eic_helm --strip-components=1

EXPOSE 5000

ENTRYPOINT ["bash", "/gen/container/run_generator.sh"]
