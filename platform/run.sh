#!/bin/bash

service=$1  # Service as the first argument
cmd=$2      # Command as the second argument

# Project names
COMPOSE_PROJECT_NAME="platform"
export COMPOSE_PROJECT_NAME="$COMPOSE_PROJECT_NAME"

# Service names
ALL="all"
DYNAMODB="dynamodb"
REDIS="redis"
RESTART_SLEEP_SEC=2

usage() {
    echo "Usage:"
    echo "  run.sh <service> <command> [options]"
    echo "Available services:"
    echo "  $ALL"
    echo "  $DYNAMODB"
    echo "  $REDIS"
    echo "Available commands:"
    echo "  up           run container"
    echo "  down         stop and remove container"
    echo "  restart      restart container"
    echo "Available options:"
    echo "  --build      rebuild when up"
    echo "  --volumes    remove volumns when down"
}

get_docker_compose_file() {
    service=$1
    docker_compose_file="$service/$service-docker-compose.yml"
    echo "$docker_compose_file"
}

up() {
    service=$1
    shift
    docker_compose_file=$(get_docker_compose_file $service)

    # Run docker compose
    docker compose -f "$docker_compose_file" up -d "$@"
}

down() {
    service=$1
    shift
    docker_compose_file=$(get_docker_compose_file $service)

    # Stop docker compose
    docker compose -f "$docker_compose_file" down "$@"
}

# ALL
up_all() {
    up_dynamodb "$@"
    up_redis "$@"
}

down_all() {
    down_dynamodb "$@"
    down_redis "$@"
}

# DYNAMODB
up_dynamodb() {
    up "$DYNAMODB" "$@"
}

down_dynamodb() {
    down "$DYNAMODB" "$@"
}

#REDIS
up_redis() {
    up "$REDIS" "$@"
}

down_redis() {
    down "$REDIS" "$@"
}

if [[ "$1" == "-h" ]]; then
    usage
    exit 0
fi

if [[ -z "$cmd" ]]; then
    echo "Missing command"
    exit 1
fi

if [[ -z "$service" ]]; then
    echo "Missing service"
    exit 1
fi

shift 2

case $cmd in
up)
    case $service in
    "$ALL")
        up_all "$@"
        ;;
    "$DYNAMODB")
        up_dynamodb "$@"
        ;;
    "$REDIS")
        up_redis "$@"
        ;;
    *)
        echo "Unknown service"
        usage
        exit 1
        ;;
    esac
    ;;
down)
    case $service in
    "$ALL")
        down_all "$@"
        ;;
    "$DYNAMODB")
        down_dynamodb "$@"
        ;;
    "$REDIS")
        down_redis "$@"
        ;;
    *)
        echo "Unknown service"
        usage
        exit 1
        ;;
    esac
    ;;
restart)
    case $service in
    "$ALL")
        down_all "$@"
        sleep $RESTART_SLEEP_SEC
        up_all "$@"
        ;;
    "$DYNAMODB")
        down_dynamodb "$@"
        sleep $RESTART_SLEEP_SEC
        up_dynamodb "$@"
        ;;
    "$REDIS")
        down_redis "$@"
        sleep $RESTART_SLEEP_SEC
        up_redis "$@"
        ;;
    *)
        echo "Unknown service"
        usage
        exit 1
        ;;
    esac
    ;;
*)
    echo "Unknown command"
    usage
    exit 1
    ;;
esac
