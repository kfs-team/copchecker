FROM migrate/migrate:v4.15.1
COPY ./sql /migrations
RUN ["ls", "/migrations"]
ENTRYPOINT ["migrate", "-database", "postgres://postgres:postgres@postgres:5432/postgres?sslmode=disable", "-path", "/migrations", "up"]
