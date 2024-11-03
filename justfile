default:
    just --list

dev-backend:
    cd backend && just dev

dev-frontend:
    cd frontend && just dev