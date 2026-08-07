FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html /usr/share/nginx/html/index.html

RUN chown -R nginx:nginx /usr/share/nginx/html

USER nginx

# a non-root user cannot bind a port below 1024, which is why the app listens on 8080
EXPOSE 8080

# any wget failure becomes exit 1, the code docker reads as unhealthy
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
