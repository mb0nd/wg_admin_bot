#Separate build image
FROM python:3.11-alpine3.16 as compile-image
RUN apk add --update --no-cache gcc musl-dev g++
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
pip3 install --no-cache-dir -r requirements.txt

# Final image
FROM python:3.11-alpine3.16
RUN apk add -U --no-cache wireguard-tools iptables \
&& echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic
COPY bot /app/bot
COPY initwg.sh /app/initwg.sh
RUN chmod +x /app/initwg.sh
ENTRYPOINT [ "/app/initwg.sh" ]