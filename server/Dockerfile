FROM golang:1.21-bullseye AS builder

RUN mkdir /app
WORKDIR /app
COPY . .
RUN go mod download

RUN GOOS=linux go build -o bin/redblue ./cmd/redblue

FROM ubuntu:focal

RUN mkdir /redblue
WORKDIR /redblue
RUN DEBIAN_FRONTEND=noninteractive apt update
COPY conf /redblue/conf
ENV CONF_DIR=/redblue/conf
COPY --from=builder /app/bin/redblue /redblue/redblue

CMD [ "/redblue/redblue" ]