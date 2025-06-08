FROM golang:bullseye

WORKDIR /app

RUN apt -y --no-install-recommends update && \
    apt -y --no-install-recommends upgrade && \
    apt install -y --no-install-recommends upx-ucl gcc-mingw-w64 && \
    rm -rf /var/cache/apk/* && \
    go install mvdan.cc/garble@latest

ENV PATH="${PATH}:$(go env GOPATH)/bin"

COPY go.mod go.sum ./

RUN go mod download -x

COPY . .

RUN make server

RUN chmod +x /app/docker-entrypoint.sh /app/wait-for-it.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
