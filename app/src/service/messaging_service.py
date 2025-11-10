"""
Service para gerenciar SQS e SNS
"""
import boto3
import os
import json
from botocore.exceptions import ClientError

class MessagingService:
    def __init__(self):
        """
        Inicializa conexão com SQS e SNS
        """
        self.aws_region = os.getenv('AWS_REGION', 'sa-east-1')
        self.sqs_client = boto3.client('sqs', region_name=self.aws_region)
        self.sns_client = boto3.client('sns', region_name=self.aws_region)
    
    # ==================== SQS ====================
    
    def list_queues(self, prefix=None):
        """
        Lista filas SQS
        """
        try:
            params = {}
            if prefix:
                params['QueueNamePrefix'] = prefix
            
            response = self.sqs_client.list_queues(**params)
            queue_urls = response.get('QueueUrls', [])
            
            queues = []
            for url in queue_urls:
                # Pega atributos da fila
                attrs = self.sqs_client.get_queue_attributes(
                    QueueUrl=url,
                    AttributeNames=['All']
                )
                
                attributes = attrs.get('Attributes', {})
                queue_name = url.split('/')[-1]
                
                queues.append({
                    'name': queue_name,
                    'url': url,
                    'messages_available': int(attributes.get('ApproximateNumberOfMessages', 0)),
                    'messages_in_flight': int(attributes.get('ApproximateNumberOfMessagesNotVisible', 0)),
                    'messages_delayed': int(attributes.get('ApproximateNumberOfMessagesDelayed', 0)),
                    'created_timestamp': attributes.get('CreatedTimestamp'),
                    'delay_seconds': attributes.get('DelaySeconds'),
                    'max_message_size': attributes.get('MaximumMessageSize'),
                    'retention_period': attributes.get('MessageRetentionPeriod'),
                    'visibility_timeout': attributes.get('VisibilityTimeout'),
                    'is_fifo': queue_name.endswith('.fifo')
                })
            
            return {
                'success': True,
                'queues': queues,
                'count': len(queues)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    def create_queue(self, queue_name, is_fifo=False, attributes=None):
        """
        Cria uma fila SQS
        """
        try:
            if is_fifo and not queue_name.endswith('.fifo'):
                queue_name += '.fifo'
            
            params = {'QueueName': queue_name}
            
            if attributes:
                params['Attributes'] = attributes
            
            if is_fifo:
                if 'Attributes' not in params:
                    params['Attributes'] = {}
                params['Attributes']['FifoQueue'] = 'true'
            
            response = self.sqs_client.create_queue(**params)
            
            return {
                'success': True,
                'message': f'Fila {queue_name} criada com sucesso',
                'queue_url': response['QueueUrl']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    def delete_queue(self, queue_url):
        """
        Deleta uma fila SQS
        """
        try:
            self.sqs_client.delete_queue(QueueUrl=queue_url)
            
            return {
                'success': True,
                'message': 'Fila deletada com sucesso'
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    def send_message(self, queue_url, message_body, attributes=None, delay_seconds=0):
        """
        Envia mensagem para fila SQS
        """
        try:
            params = {
                'QueueUrl': queue_url,
                'MessageBody': message_body,
                'DelaySeconds': delay_seconds
            }
            
            if attributes:
                params['MessageAttributes'] = attributes
            
            response = self.sqs_client.send_message(**params)
            
            return {
                'success': True,
                'message': 'Mensagem enviada com sucesso',
                'message_id': response['MessageId']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    def receive_messages(self, queue_url, max_messages=10, wait_time=0):
        """
        Recebe mensagens da fila SQS
        """
        try:
            response = self.sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
                AttributeNames=['All'],
                MessageAttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            
            return {
                'success': True,
                'messages': messages,
                'count': len(messages)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    def delete_message(self, queue_url, receipt_handle):
        """
        Deleta mensagem da fila SQS
        """
        try:
            self.sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            
            return {
                'success': True,
                'message': 'Mensagem deletada com sucesso'
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    def purge_queue(self, queue_url):
        """
        Limpa todas as mensagens da fila
        """
        try:
            self.sqs_client.purge_queue(QueueUrl=queue_url)
            
            return {
                'success': True,
                'message': 'Fila limpa com sucesso'
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    # ==================== SNS ====================
    
    def list_topics(self):
        """
        Lista tópicos SNS
        """
        try:
            response = self.sns_client.list_topics()
            topic_arns = [t['TopicArn'] for t in response.get('Topics', [])]
            
            topics = []
            for arn in topic_arns:
                # Pega atributos do tópico
                attrs = self.sns_client.get_topic_attributes(TopicArn=arn)
                attributes = attrs.get('Attributes', {})
                
                topic_name = arn.split(':')[-1]
                
                topics.append({
                    'name': topic_name,
                    'arn': arn,
                    'subscriptions_confirmed': int(attributes.get('SubscriptionsConfirmed', 0)),
                    'subscriptions_pending': int(attributes.get('SubscriptionsPending', 0)),
                    'subscriptions_deleted': int(attributes.get('SubscriptionsDeleted', 0)),
                    'display_name': attributes.get('DisplayName', ''),
                    'owner': attributes.get('Owner', ''),
                    'is_fifo': topic_name.endswith('.fifo')
                })
            
            return {
                'success': True,
                'topics': topics,
                'count': len(topics)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    def create_topic(self, topic_name, is_fifo=False, attributes=None):
        """
        Cria um tópico SNS
        """
        try:
            if is_fifo and not topic_name.endswith('.fifo'):
                topic_name += '.fifo'
            
            params = {'Name': topic_name}
            
            if attributes:
                params['Attributes'] = attributes
            
            if is_fifo:
                if 'Attributes' not in params:
                    params['Attributes'] = {}
                params['Attributes']['FifoTopic'] = 'true'
            
            response = self.sns_client.create_topic(**params)
            
            return {
                'success': True,
                'message': f'Tópico {topic_name} criado com sucesso',
                'topic_arn': response['TopicArn']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    def delete_topic(self, topic_arn):
        """
        Deleta um tópico SNS
        """
        try:
            self.sns_client.delete_topic(TopicArn=topic_arn)
            
            return {
                'success': True,
                'message': 'Tópico deletado com sucesso'
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    def publish_message(self, topic_arn, message, subject=None, attributes=None):
        """
        Publica mensagem em tópico SNS
        """
        try:
            params = {
                'TopicArn': topic_arn,
                'Message': message
            }
            
            if subject:
                params['Subject'] = subject
            
            if attributes:
                params['MessageAttributes'] = attributes
            
            response = self.sns_client.publish(**params)
            
            return {
                'success': True,
                'message': 'Mensagem publicada com sucesso',
                'message_id': response['MessageId']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    def list_subscriptions(self, topic_arn=None):
        """
        Lista inscrições SNS
        """
        try:
            if topic_arn:
                response = self.sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
            else:
                response = self.sns_client.list_subscriptions()
            
            subscriptions = response.get('Subscriptions', [])
            
            return {
                'success': True,
                'subscriptions': subscriptions,
                'count': len(subscriptions)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    def subscribe(self, topic_arn, protocol, endpoint):
        """
        Cria inscrição em tópico SNS
        """
        try:
            response = self.sns_client.subscribe(
                TopicArn=topic_arn,
                Protocol=protocol,
                Endpoint=endpoint
            )
            
            return {
                'success': True,
                'message': 'Inscrição criada com sucesso',
                'subscription_arn': response.get('SubscriptionArn')
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    def unsubscribe(self, subscription_arn):
        """
        Remove inscrição de tópico SNS
        """
        try:
            self.sns_client.unsubscribe(SubscriptionArn=subscription_arn)
            
            return {
                'success': True,
                'message': 'Inscrição removida com sucesso'
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro AWS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
