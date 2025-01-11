# Infrastructure (managed by Terraform)

## Steps to push image to ECR from local machine

### 1. Build backend image

Login to ECR

```bash
aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 484907490685.dkr.ecr.eu-north-1.amazonaws.com
```

Build image

```bash
docker buildx build --platform linux/amd64 -t weavens-backend:${IMAGE_TAG} .
docker tag weavens-backend:${IMAGE_TAG} 484907490685.dkr.ecr.eu-north-1.amazonaws.com/weavens-backend:${IMAGE_TAG}
```

### 2. Push image to ECR

```bash
docker push 484907490685.dkr.ecr.eu-north-1.amazonaws.com/weavens-backend:${IMAGE_TAG}
```

### 3. Update backend image tag in SSM parameter

Change directory to `infra/global/ssm_parameters` and run `terraform apply` with variable of new image tag.
Make sure to check the plan and commit the changes to the repository.

### 4. Update backend image tag in ECS task definition

Change directory to `infra/environments/production/backend` and run `terraform apply`
Make sure to check the plan and commit the changes to the repository. Verify that the change only includes the image tag change.

Go to AWS ECS console and verify that the task definition is updated with the new image tag.
