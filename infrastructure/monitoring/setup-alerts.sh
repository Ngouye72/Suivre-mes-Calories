#!/bin/bash

# Variables requises
# SNS_TOPIC_NAME
# AWS_REGION
# ALB_NAME
# DB_INSTANCE_ID
# CACHE_CLUSTER_ID

# Création du topic SNS
SNS_TOPIC_ARN=$(aws sns create-topic --name ${SNS_TOPIC_NAME} --output text)

# Ajout des abonnements email
aws sns subscribe \
    --topic-arn ${SNS_TOPIC_ARN} \
    --protocol email \
    --notification-endpoint alerts@votredomaine.com

# Création des alarmes
for alarm in $(cat cloudwatch-alarms.json | jq -c '.Alarms[]'); do
    aws cloudwatch put-metric-alarm \
        --alarm-name "$(echo $alarm | jq -r '.AlarmName')" \
        --alarm-description "$(echo $alarm | jq -r '.AlarmDescription')" \
        --metric-name "$(echo $alarm | jq -r '.MetricName')" \
        --namespace "$(echo $alarm | jq -r '.Namespace')" \
        --statistic "$(echo $alarm | jq -r '.Statistic')" \
        --dimensions "$(echo $alarm | jq -r '.Dimensions')" \
        --period "$(echo $alarm | jq -r '.Period')" \
        --evaluation-periods "$(echo $alarm | jq -r '.EvaluationPeriods')" \
        --threshold "$(echo $alarm | jq -r '.Threshold')" \
        --comparison-operator "$(echo $alarm | jq -r '.ComparisonOperator')" \
        --alarm-actions "${SNS_TOPIC_ARN}"
done

# Vérification des alarmes créées
aws cloudwatch describe-alarms \
    --alarm-names $(cat cloudwatch-alarms.json | jq -r '.Alarms[].AlarmName')
