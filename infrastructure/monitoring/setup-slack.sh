#!/bin/bash

# Variables requises
# SLACK_WEBHOOK_URL
# AWS_REGION
# LAMBDA_ROLE_ARN
# SNS_TOPIC_ARN

# Création du package Lambda
cd slack-lambda
zip -r function.zip index.js
cd ..

# Création de la fonction Lambda
aws lambda create-function \
    --function-name nutrition-slack-notifications \
    --runtime nodejs18.x \
    --role ${LAMBDA_ROLE_ARN} \
    --handler index.handler \
    --zip-file fileb://slack-lambda/function.zip \
    --environment "Variables={SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}}" \
    --timeout 30

# Ajout de la permission SNS
aws lambda add-permission \
    --function-name nutrition-slack-notifications \
    --statement-id sns-invoke \
    --action lambda:InvokeFunction \
    --principal sns.amazonaws.com \
    --source-arn ${SNS_TOPIC_ARN}

# Abonnement de la Lambda au topic SNS
aws sns subscribe \
    --topic-arn ${SNS_TOPIC_ARN} \
    --protocol lambda \
    --notification-endpoint $(aws lambda get-function --function-name nutrition-slack-notifications --query 'Configuration.FunctionArn' --output text)

echo "Configuration Slack terminée"
