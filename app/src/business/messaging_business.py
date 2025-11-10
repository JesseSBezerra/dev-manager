"""
Business layer para SQS e SNS
"""
from src.service.messaging_service import MessagingService

class MessagingBusiness:
    def __init__(self):
        self.service = MessagingService()
    
    # ==================== SQS ====================
    
    def list_queues(self, prefix=None):
        """Lista filas SQS"""
        return self.service.list_queues(prefix)
    
    def create_queue(self, queue_name, is_fifo=False, delay_seconds=0, 
                    message_retention_period=345600, visibility_timeout=30):
        """Cria fila SQS"""
        attributes = {
            'DelaySeconds': str(delay_seconds),
            'MessageRetentionPeriod': str(message_retention_period),
            'VisibilityTimeout': str(visibility_timeout)
        }
        
        return self.service.create_queue(queue_name, is_fifo, attributes)
    
    def delete_queue(self, queue_url):
        """Deleta fila SQS"""
        return self.service.delete_queue(queue_url)
    
    def send_message(self, queue_url, message_body, delay_seconds=0):
        """Envia mensagem para fila"""
        return self.service.send_message(queue_url, message_body, None, delay_seconds)
    
    def receive_messages(self, queue_url, max_messages=10):
        """Recebe mensagens da fila"""
        return self.service.receive_messages(queue_url, max_messages)
    
    def delete_message(self, queue_url, receipt_handle):
        """Deleta mensagem da fila"""
        return self.service.delete_message(queue_url, receipt_handle)
    
    def purge_queue(self, queue_url):
        """Limpa fila"""
        return self.service.purge_queue(queue_url)
    
    # ==================== SNS ====================
    
    def list_topics(self):
        """Lista tópicos SNS"""
        return self.service.list_topics()
    
    def create_topic(self, topic_name, is_fifo=False, display_name=None):
        """Cria tópico SNS"""
        attributes = {}
        if display_name:
            attributes['DisplayName'] = display_name
        
        return self.service.create_topic(topic_name, is_fifo, attributes if attributes else None)
    
    def delete_topic(self, topic_arn):
        """Deleta tópico SNS"""
        return self.service.delete_topic(topic_arn)
    
    def publish_message(self, topic_arn, message, subject=None):
        """Publica mensagem em tópico"""
        return self.service.publish_message(topic_arn, message, subject)
    
    def list_subscriptions(self, topic_arn=None):
        """Lista inscrições"""
        return self.service.list_subscriptions(topic_arn)
    
    def subscribe(self, topic_arn, protocol, endpoint):
        """Cria inscrição"""
        return self.service.subscribe(topic_arn, protocol, endpoint)
    
    def unsubscribe(self, subscription_arn):
        """Remove inscrição"""
        return self.service.unsubscribe(subscription_arn)
