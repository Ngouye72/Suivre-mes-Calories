import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

def init_sentry(app, config):
    """Initialize Sentry configuration for the Flask application."""
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        environment=config.ENVIRONMENT,
        traces_sample_rate=0.2,
        profiles_sample_rate=0.2,
        integrations=[
            FlaskIntegration(
                transaction_style='url',
                request_bodies='medium',
            ),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
        ],
        before_send=before_send,
        before_breadcrumb=before_breadcrumb,
    )

def before_send(event, hint):
    """Process and filter events before sending to Sentry."""
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        
        # Filter out specific errors
        if isinstance(exc_value, (KeyError, ValueError)):
            event['fingerprint'] = ['{{ default }}', str(exc_type)]
        
        # Add custom context
        event.setdefault('extra', {}).update({
            'error_type': exc_type.__name__,
            'error_module': getattr(exc_type, '__module__', None),
        })
        
        # Sanitize sensitive data
        if 'request' in event and 'data' in event['request']:
            sanitize_request_data(event['request']['data'])
    
    return event

def before_breadcrumb(crumb, hint):
    """Process breadcrumbs before adding them to the event."""
    # Filter out noisy breadcrumbs
    if crumb.get('category') == 'httplib':
        return None
    
    # Sanitize SQL queries
    if crumb.get('category') == 'query':
        crumb['data'] = sanitize_sql_query(crumb['data'])
    
    return crumb

def sanitize_request_data(data):
    """Remove sensitive information from request data."""
    sensitive_fields = {'password', 'token', 'api_key', 'credit_card'}
    
    if isinstance(data, dict):
        for key in list(data.keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                data[key] = '[FILTERED]'
            elif isinstance(data[key], (dict, list)):
                sanitize_request_data(data[key])
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                sanitize_request_data(item)

def sanitize_sql_query(query_data):
    """Sanitize SQL queries to remove sensitive data."""
    if isinstance(query_data, dict) and 'sql' in query_data:
        # Basic SQL query sanitization
        query_data['sql'] = query_data['sql'].replace('\n', ' ').strip()
        
        # Remove specific values from INSERT/UPDATE statements
        if 'INSERT INTO' in query_data['sql'] or 'UPDATE' in query_data['sql']:
            query_data['sql'] = '[FILTERED SQL]'
    
    return query_data
