FROM scratch

ADD boot.tar /

COPY boot/* /

CMD ["bash"]

