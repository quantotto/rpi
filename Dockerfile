FROM scratch

ADD root.tar /

RUN apt-get -yy update && apt-get -yy upgrade

COPY packages_list.txt /tmp/packages_list.txt

RUN xargs -a /tmp/packages_list.txt apt-get -yy install

RUN mkdir -p /opt/quantotto

ENV QUANTOTTO_HOME=/opt/quantotto
ENV VIRTUAL_ENV=${QUANTOTTO_HOME}/.venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

RUN pip install -U pip
COPY requirements.txt /tmp/requirements.txt
COPY qto_requirements.txt /tmp/qto_requirements.txt

RUN pip install git+https://github.com/wearefair/protobuf-to-dict#egg=protobuf-to-dict
RUN pip install -r /tmp/requirements.txt
RUN pip install -r /tmp/qto_requirements.txt

COPY simple.py ${VIRTUAL_ENV}/lib/python3.7/site-packages/zeep/xsd/types/simple.py

COPY run_capture.py ${QUANTOTTO_HOME}/
COPY run_discovery.py ${QUANTOTTO_HOME}/

CMD ["bash"]

