provider "aws" {
    region = "eu-west-2"
}
data "aws_vpc" "c9-vpc" {
    id = "vpc-04423dbb18410aece"
}

data "aws_ecs_cluster" "c9-cluster" {
    cluster_name = "c9-ecs-cluster"
}

data "aws_iam_role" "execution-role" {
    name = "ecsTaskExecutionRole"
}

data "aws_sesv2_email_identity" "anu-email" {
  email_identity = "trainee.anurag.kaur@sigmalabs.co.uk"
}
data "aws_sesv2_email_identity_mail_from_attributes" "anu-email-from" {
  email_identity = data.aws_sesv2_email_identity.anu-email.email_identity
}

#ECRs

#iam role: Lambda for text
resource "aws_iam_role" "iam_for_lambda_text" {
  name               = "iam_for_lambda_text"
  assume_role_policy = jsonencode({
        Version: "2012-10-17",
        Statement: [
            {
                Effect: "Allow",
                Principal: {
                    Service: "lambda.amazonaws.com"
                },
                Action: "sts:AssumeRole",
            }, 
        ],
  })
}

#Text Lambda:
resource "aws_lambda_function" "c9-tech-news-text-lambda-tf" {
    function_name = "c9-tech-news-text-lambda-tf"
    role = aws_iam_role.iam_for_lambda_anu_tf.arn
    image_uri = "DOCKER IMAGE REPO"
    package_type = "Image"
    environment {
        variables = {
        AWS_BUCKET=var.AWS_BUCKET
        DATABASE=var.DATABASE
        HOST=var.HOST
        PASSWORD=var.PASSWORD
        PORT=var.PORT
        USERNAME=var.USERNAME
        }
    }
}
#Iam: Lambda for email
resource "aws_iam_role" "iam_for_lambda_email" {
  name               = "iam_for_lambda_email"
  assume_role_policy = jsonencode({
        Version: "2012-10-17",
        Statement: [
            {
                Effect: "Allow",
                Principal: {
                    Service: "lambda.amazonaws.com"
                },
                Action: "sts:AssumeRole",
            }, 
        ],
  })
}
#Lambda for email
resource "aws_lambda_function" "c9-anu-lambda-tf" {
    function_name = "c9-tech-news-email-lambda-tf"
    role = aws_iam_role.iam_for_lambda_anu_tf.arn
    image_uri = "DOCKER_IMAGE_REPO"
    package_type = "Image"
    environment {
        variables = {
        AWS_BUCKET=var.AWS_BUCKET
        DATABASE=var.DATABASE
        HOST=var.HOST
        PASSWORD=var.PASSWORD
        PORT=var.PORT
        USERNAME=var.USERNAME
        }
    }
}
# Scheduler for Lambda 

#Scheduler for text: has a trigger

#Task Definition
resource "aws_ecs_task_definition" "task-def" {
    family = "c9-anu-dashboard-td-tf"
    requires_compatibilities = ["FARGATE"]
    network_mode             = "awsvpc"
    container_definitions = file("./task-def.json")
    memory    = 2048
    cpu = 1024
    execution_role_arn = data.aws_iam_role.execution-role.arn
}
# ECS service to run dashboard
resource "aws_ecs_service" "dashboard-service" {
    name = var.SERVICE_NAME
    cluster = data.aws_ecs_cluster.c9-cluster.id
    task_definition = "arn:aws:ecs:eu-west-2:129033205317:task-definition/c9-anu-truck-dashboard:2" 
    desired_count = 1
    launch_type = "FARGATE"
    network_configuration {
      subnets = ["subnet-0d0b16e76e68cf51b", "subnet-081c7c419697dec52", "subnet-02a00c7be52b00368"]
      security_groups = ["sg-0ce150705484be1ce"]
      assign_public_ip = true
    }
}