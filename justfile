default:
    just --list

dev-backend:
    cd platform && just dynamodb-up
    cd backend && just dev

dev-frontend:
    cd frontend && just dev