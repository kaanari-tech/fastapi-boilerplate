ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP_ADDRESS" << ENDSSH
    cd /app
    export $(cat .env | xargs)
    docker login -u $CI_REGISTRY_USER -p $CI_JOB_TOKEN $CI_REGISTRY
    docker pull $API_IMAGE
    docker-compose -f docker-compose.yml up --build -d
ENDSSH