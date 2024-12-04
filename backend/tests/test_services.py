import pytest
from datetime import datetime, timedelta
from backend.services.notifications.email_sender import EmailSender
from backend.services.notifications.push_sender import PushSender
from backend.services.notifications.sms_sender import SMSSender
from backend.services.cache.cache_manager import CacheManager
from backend.services.monitoring.performance_monitor import PerformanceMonitor
from backend.services.monitoring.system_monitor import SystemMonitor
from backend.services.monitoring.api_monitor import APIMonitor
import json

class TestEmailSender:
    @pytest.fixture
    def email_sender(self):
        return EmailSender()

    def test_send_email(self, email_sender, mocker):
        """Test l'envoi d'email"""
        mock_smtp = mocker.patch('smtplib.SMTP')
        
        result = email_sender.send(
            to_email='test@example.com',
            subject='Test Email',
            body='Test content'
        )
        
        assert result
        mock_smtp.return_value.__enter__.return_value.send_message.assert_called_once()

    def test_send_batch_emails(self, email_sender, mocker):
        """Test l'envoi d'emails en lot"""
        mock_smtp = mocker.patch('smtplib.SMTP')
        
        emails = [
            {
                'to': 'user1@example.com',
                'subject': 'Test 1',
                'body': 'Content 1'
            },
            {
                'to': 'user2@example.com',
                'subject': 'Test 2',
                'body': 'Content 2'
            }
        ]
        
        results = email_sender.send_batch(emails)
        assert len(results) == 2
        assert all(r['success'] for r in results)

class TestPushSender:
    @pytest.fixture
    def push_sender(self):
        return PushSender()

    def test_send_push(self, push_sender, mocker):
        """Test l'envoi de notification push"""
        mock_messaging = mocker.patch('firebase_admin.messaging')
        
        result = push_sender.send(
            user_id='123',
            title='Test Push',
            message='Test content'
        )
        
        assert result
        mock_messaging.send_multicast.assert_called_once()

    def test_register_device(self, push_sender, db_session):
        """Test l'enregistrement d'un appareil"""
        result = push_sender.register_device(
            user_id='123',
            token='test_token',
            device_info={'platform': 'android'}
        )
        
        assert result

class TestSMSSender:
    @pytest.fixture
    def sms_sender(self):
        return SMSSender()

    def test_send_sms(self, sms_sender, mocker):
        """Test l'envoi de SMS"""
        mock_client = mocker.patch('twilio.rest.Client')
        
        result = sms_sender.send(
            phone_number='+33612345678',
            message='Test SMS'
        )
        
        assert result
        mock_client.return_value.messages.create.assert_called_once()

    def test_validate_phone_number(self, sms_sender):
        """Test la validation des numéros de téléphone"""
        assert sms_sender._validate_phone_number('+33612345678')
        assert not sms_sender._validate_phone_number('invalid')

class TestCacheManager:
    @pytest.fixture
    def cache_manager(self):
        return CacheManager()

    def test_set_get_cache(self, cache_manager):
        """Test le stockage et la récupération du cache"""
        cache_manager.set('test_key', {'data': 'test'})
        value = cache_manager.get('test_key')
        
        assert value == {'data': 'test'}

    def test_cache_expiration(self, cache_manager):
        """Test l'expiration du cache"""
        cache_manager.set('test_key', 'test', ttl=1)
        import time
        time.sleep(2)
        
        value = cache_manager.get('test_key')
        assert value is None

class TestPerformanceMonitor:
    @pytest.fixture
    def perf_monitor(self):
        return PerformanceMonitor()

    def test_function_profiling(self, perf_monitor):
        """Test le profilage de fonction"""
        @perf_monitor.profile_function
        def test_func():
            return sum(range(1000))
            
        result = test_func()
        assert result == 499500

    def test_memory_tracking(self, perf_monitor):
        """Test le suivi de la mémoire"""
        memory_usage = perf_monitor.get_memory_usage()
        
        assert 'current' in memory_usage
        assert 'peak' in memory_usage
        assert 'system' in memory_usage

class TestSystemMonitor:
    @pytest.fixture
    def sys_monitor(self):
        return SystemMonitor()

    def test_collect_metrics(self, sys_monitor):
        """Test la collecte des métriques système"""
        metrics = sys_monitor.collect_metrics()
        
        assert 'cpu' in metrics
        assert 'memory' in metrics
        assert 'disk' in metrics
        assert 'network' in metrics

    def test_system_health(self, sys_monitor):
        """Test l'état de santé du système"""
        health = sys_monitor.get_system_health()
        
        assert 'status' in health
        assert health['status'] in ['healthy', 'warning', 'critical']

class TestAPIMonitor:
    @pytest.fixture
    def api_monitor(self):
        return APIMonitor()

    def test_endpoint_monitoring(self, api_monitor):
        """Test le monitoring d'endpoint"""
        @api_monitor.monitor_endpoint('test_endpoint')
        def test_endpoint():
            return 'success'
            
        result = test_endpoint()
        assert result == 'success'

        stats = api_monitor.get_endpoint_stats('test_endpoint')
        assert stats['requests'] == 1
        assert stats['errors'] == 0

    def test_error_tracking(self, api_monitor):
        """Test le suivi des erreurs"""
        @api_monitor.monitor_endpoint('error_endpoint')
        def error_endpoint():
            raise ValueError('Test error')
            
        with pytest.raises(ValueError):
            error_endpoint()

        errors = api_monitor.get_recent_errors(minutes=1)
        assert len(errors) == 1
        assert errors[0]['endpoint'] == 'error_endpoint'
