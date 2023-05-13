#!/bin/bash
# NOTE 1: Run outside of Docker container, on production server
# NOTE 2: First run build.sh on development server
# NOTE 3: If docker-compose file was changed since the last build, you should prune the containers and images before running this script.
# Finishes up the deployment process, which was started by build.sh:
# 1. Runs git fetch and git pull to get the latest changes.
# 2. Runs setup.sh
# 3. Restarts docker containers
# 
# Arguments (all optional):
# -n: Nginx proxy location (e.g. "/root/NginxSSLReverseProxy")
# -h: Show this help message
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "${HERE}/prettify.sh"

# Read arguments
SETUP_ARGS=()
for arg in "$@"; do
    case $arg in
    -n | --nginx-location)
        NGINX_LOCATION="${2}"
        shift
        shift
        ;;
    -h | --help)
        echo "Usage: $0 [-v VERSION] [-n NGINX_LOCATION]"
        echo "  -n --nginx-location: Nginx proxy location (e.g. \"/root/NginxSSLReverseProxy\")"
        echo "  -h --help: Show this help message"
        exit 0
        ;;
    *)
        SETUP_ARGS+=("${arg}")
        shift
        ;;
    esac
done

# Pull the latest changes from the repository.
info "Pulling latest changes from repository..."
git fetch
git pull
if [ $? -ne 0 ]; then
    error "Could not pull latest changes from repository. You likely have uncommitted changes."
    exit 1
fi

# Check if nginx-proxy and nginx-proxy-le are running
if [ ! "$(docker ps -q -f name=nginx-proxy)" ] || [ ! "$(docker ps -q -f name=nginx-proxy-le)" ]; then
    error "Proxy containers are not running!"
    if [ -z "$NGINX_LOCATION" ]; then
        while true; do
            prompt "Enter path to proxy container directory (defaults to /root/NginxSSLReverseProxy):"
            read -r NGINX_LOCATION
            if [ -z "$NGINX_LOCATION" ]; then
                NGINX_LOCATION="/root/NginxSSLReverseProxy"
            fi

            if [ -d "${NGINX_LOCATION}" ]; then
                break
            else
                error "Not found at that location."
                prompt "Do you want to try again? Say no to clone and set up proxy containers (yes/no):"
                read -r TRY_AGAIN
                if [[ "$TRY_AGAIN" =~ ^(no|n)$ ]]; then
                    info "Proceeding with cloning..."
                    break
                fi
            fi
        done
    fi

    # Check if the NginxSSLReverseProxy directory exists
    if [ ! -d "${NGINX_LOCATION}" ]; then
        info "NginxSSLReverseProxy not installed. Cloning and setting up..."
        git clone --depth 1 --branch main https://github.com/MattHalloran/NginxSSLReverseProxy.git "${NGINX_LOCATION}"
        chmod +x "${NGINX_LOCATION}/scripts/*"
        "${NGINX_LOCATION}/scripts/fullSetup.sh"
    fi

    # Check if ${NGINX_LOCATION}/docker-compose.yml or ${NGINX_LOCATION}/docker-compose.yaml exists
    if [ -f "${NGINX_LOCATION}/docker-compose.yml" ] || [ -f "${NGINX_LOCATION}/docker-compose.yaml" ]; then
        info "Starting proxy containers..."
        cd "${NGINX_LOCATION}" && docker-compose up -d
    else
        error "Could not find docker-compose.yml file in ${NGINX_LOCATION}"
        exit 1
    fi
fi

# Running setup.sh
info "Running setup.sh..."
"${HERE}/setup.sh" "${SETUP_ARGS[@]}" -p
if [ $? -ne 0 ]; then
    error "setup.sh failed"
    exit 1
fi

# Transfer and load Docker images
BUILD_ZIP="/var/tmp/embeddings"
if [ -f "${BUILD_ZIP}/production-docker-images.tar.gz" ]; then
    info "Loading Docker images from ${BUILD_ZIP}/production-docker-images.tar.gz"
    docker load -i "${BUILD_ZIP}/production-docker-images.tar.gz"
    if [ $? -ne 0 ]; then
        error "Failed to load Docker images from ${BUILD_ZIP}/production-docker-images.tar.gz"
        exit 1
    fi
else
    error "Could not find Docker images archive at ${BUILD_ZIP}/production-docker-images.tar.gz"
    exit 1
fi

# Stop docker containers
info "Stopping docker containers..."
docker-compose --env-file ${BUILD_ZIP}/.env down

# Restart docker containers.
info "Restarting docker containers..."
docker-compose --env-file ${BUILD_ZIP}/.env -f ${HERE}/../docker-compose.yml up -d

success "Done! You may need to wait a few minutes for the Docker containers to finish starting up."
info "Now that you've deployed, here are some next steps:"
info "- Manually check that it is working correctly"
