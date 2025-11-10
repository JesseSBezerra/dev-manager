"""
Controller para SQS e SNS
"""
from flask import Blueprint, render_template, request, jsonify
from src.business.messaging_business import MessagingBusiness

messaging_bp = Blueprint('messaging', __name__, url_prefix='/messaging')
business = MessagingBusiness()

@messaging_bp.route('/')
def index():
    """Página principal"""
    return render_template('messaging/index.html')

# ==================== SQS ====================

@messaging_bp.route('/sqs/queues', methods=['GET'])
def list_queues():
    """Lista filas SQS"""
    try:
        prefix = request.args.get('prefix')
        result = business.list_queues(prefix)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@messaging_bp.route('/sqs/queues', methods=['POST'])
def create_queue():
    """Cria fila SQS"""
    try:
        data = request.get_json()
        result = business.create_queue(
            queue_name=data.get('queue_name'),
            is_fifo=data.get('is_fifo', False),
            delay_seconds=data.get('delay_seconds', 0),
            message_retention_period=data.get('message_retention_period', 345600),
            visibility_timeout=data.get('visibility_timeout', 30)
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@messaging_bp.route('/sqs/queues', methods=['DELETE'])
def delete_queue():
    """Deleta fila SQS"""
    try:
        data = request.get_json()
        result = business.delete_queue(data.get('queue_url'))
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@messaging_bp.route('/sqs/messages/send', methods=['POST'])
def send_message():
    """Envia mensagem para fila"""
    try:
        data = request.get_json()
        result = business.send_message(
            queue_url=data.get('queue_url'),
            message_body=data.get('message_body'),
            delay_seconds=data.get('delay_seconds', 0)
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@messaging_bp.route('/sqs/messages/receive', methods=['POST'])
def receive_messages():
    """Recebe mensagens da fila"""
    try:
        data = request.get_json()
        result = business.receive_messages(
            queue_url=data.get('queue_url'),
            max_messages=data.get('max_messages', 10)
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@messaging_bp.route('/sqs/messages', methods=['DELETE'])
def delete_message():
    """Deleta mensagem da fila"""
    try:
        data = request.get_json()
        result = business.delete_message(
            queue_url=data.get('queue_url'),
            receipt_handle=data.get('receipt_handle')
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@messaging_bp.route('/sqs/queues/purge', methods=['POST'])
def purge_queue():
    """Limpa fila"""
    try:
        data = request.get_json()
        result = business.purge_queue(data.get('queue_url'))
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

# ==================== SNS ====================

@messaging_bp.route('/sns/topics', methods=['GET'])
def list_topics():
    """Lista tópicos SNS"""
    try:
        result = business.list_topics()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@messaging_bp.route('/sns/topics', methods=['POST'])
def create_topic():
    """Cria tópico SNS"""
    try:
        data = request.get_json()
        result = business.create_topic(
            topic_name=data.get('topic_name'),
            is_fifo=data.get('is_fifo', False),
            display_name=data.get('display_name')
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@messaging_bp.route('/sns/topics', methods=['DELETE'])
def delete_topic():
    """Deleta tópico SNS"""
    try:
        data = request.get_json()
        result = business.delete_topic(data.get('topic_arn'))
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@messaging_bp.route('/sns/publish', methods=['POST'])
def publish_message():
    """Publica mensagem em tópico"""
    try:
        data = request.get_json()
        result = business.publish_message(
            topic_arn=data.get('topic_arn'),
            message=data.get('message'),
            subject=data.get('subject')
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@messaging_bp.route('/sns/subscriptions', methods=['GET'])
def list_subscriptions():
    """Lista inscrições"""
    try:
        topic_arn = request.args.get('topic_arn')
        result = business.list_subscriptions(topic_arn)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@messaging_bp.route('/sns/subscriptions', methods=['POST'])
def subscribe():
    """Cria inscrição"""
    try:
        data = request.get_json()
        result = business.subscribe(
            topic_arn=data.get('topic_arn'),
            protocol=data.get('protocol'),
            endpoint=data.get('endpoint')
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500

@messaging_bp.route('/sns/subscriptions', methods=['DELETE'])
def unsubscribe():
    """Remove inscrição"""
    try:
        data = request.get_json()
        result = business.unsubscribe(data.get('subscription_arn'))
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500
