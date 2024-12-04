const https = require('https');
const url = require('url');

// Configuration Slack webhook
const SLACK_WEBHOOK_URL = process.env.SLACK_WEBHOOK_URL;

exports.handler = async (event) => {
    const message = JSON.parse(event.Records[0].Sns.Message);
    
    // Formatage du message Slack
    const slackMessage = {
        attachments: [{
            color: message.NewStateValue === 'ALARM' ? '#FF0000' : '#36A64F',
            title: `${message.AlarmName} - ${message.NewStateValue}`,
            text: message.AlarmDescription,
            fields: [
                {
                    title: 'Metric',
                    value: message.Trigger.MetricName,
                    short: true
                },
                {
                    title: 'Threshold',
                    value: `${message.Trigger.Threshold} ${message.Trigger.ComparisonOperator}`,
                    short: true
                },
                {
                    title: 'Region',
                    value: event.Records[0].Sns.TopicArn.split(':')[3],
                    short: true
                }
            ],
            footer: 'AWS CloudWatch Alarm',
            ts: Math.floor(Date.now() / 1000)
        }]
    };
    
    // Envoi à Slack
    try {
        await postToSlack(slackMessage);
        return {
            statusCode: 200,
            body: 'Message envoyé à Slack avec succès'
        };
    } catch (error) {
        console.error('Erreur lors de l\'envoi à Slack:', error);
        throw error;
    }
};

function postToSlack(message) {
    return new Promise((resolve, reject) => {
        const webhookUrl = url.parse(SLACK_WEBHOOK_URL);
        const requestOptions = {
            hostname: webhookUrl.hostname,
            path: webhookUrl.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const req = https.request(requestOptions, (res) => {
            let response = '';
            res.on('data', (chunk) => response += chunk);
            res.on('end', () => resolve(response));
        });

        req.on('error', (error) => reject(error));
        req.write(JSON.stringify(message));
        req.end();
    });
}
