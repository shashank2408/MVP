FROM apache/kafka:3.9.1

COPY start-kafka.sh /tmp/start-kafka.sh

USER root
RUN chmod +x /tmp/start-kafka.sh

CMD ["/tmp/start-kafka.sh"]
