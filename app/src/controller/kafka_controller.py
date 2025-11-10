"""
Controller para Kafka
"""
from flask import Blueprint, render_template, request, jsonify
from src.business.kafka_business import KafkaBusiness

kafka_bp = Blueprint('kafka', __name__, url_prefix='/kafka')
business = KafkaBusiness()

@kafka_bp.route('/')
def index():
    """Página principal"""
    return render_template('kafka/index.html')

# ==================== OWNERS ====================

@kafka_bp.route('/owners', methods=['GET'])
def get_owners():
    result = business.get_owners()
    return jsonify(result), 200 if result['success'] else 400

@kafka_bp.route('/owners', methods=['POST'])
def create_owner():
    data = request.get_json()
    result = business.create_owner(data.get('name'), data.get('description'))
    return jsonify(result), 201 if result['success'] else 400

@kafka_bp.route('/owners/<int:owner_id>', methods=['DELETE'])
def delete_owner(owner_id):
    result = business.delete_owner(owner_id)
    return jsonify(result), 200 if result['success'] else 400

# ==================== AUTHENTICATIONS ====================

@kafka_bp.route('/authentications', methods=['GET'])
def get_authentications():
    result = business.get_authentications()
    return jsonify(result), 200 if result['success'] else 400

@kafka_bp.route('/authentications', methods=['POST'])
def create_authentication():
    data = request.get_json()
    result = business.create_authentication(
        owner_id=data.get('owner_id'),
        name=data.get('name'),
        auth_type=data.get('auth_type'),
        sasl_mechanism=data.get('sasl_mechanism'),
        username=data.get('username'),
        password=data.get('password'),
        ssl_ca_cert=data.get('ssl_ca_cert'),
        ssl_client_cert=data.get('ssl_client_cert'),
        ssl_client_key=data.get('ssl_client_key')
    )
    return jsonify(result), 201 if result['success'] else 400

@kafka_bp.route('/authentications/<int:auth_id>', methods=['DELETE'])
def delete_authentication(auth_id):
    result = business.delete_authentication(auth_id)
    return jsonify(result), 200 if result['success'] else 400

# ==================== SCHEMAS ====================

@kafka_bp.route('/schemas', methods=['GET'])
def get_schemas():
    result = business.get_schemas()
    return jsonify(result), 200 if result['success'] else 400

@kafka_bp.route('/schemas', methods=['POST'])
def create_schema():
    data = request.get_json()
    result = business.create_schema(
        owner_id=data.get('owner_id'),
        name=data.get('name'),
        schema_type=data.get('schema_type'),
        schema_content=data.get('schema_content'),
        description=data.get('description')
    )
    return jsonify(result), 201 if result['success'] else 400

@kafka_bp.route('/schemas/<int:schema_id>', methods=['DELETE'])
def delete_schema(schema_id):
    result = business.delete_schema(schema_id)
    return jsonify(result), 200 if result['success'] else 400

# ==================== CLUSTERS ====================

@kafka_bp.route('/clusters', methods=['GET'])
def get_clusters():
    result = business.get_clusters()
    return jsonify(result), 200 if result['success'] else 400

@kafka_bp.route('/clusters', methods=['POST'])
def create_cluster():
    data = request.get_json()
    result = business.create_cluster(
        owner_id=data.get('owner_id'),
        name=data.get('name'),
        bootstrap_servers=data.get('bootstrap_servers'),
        auth_id=data.get('auth_id'),
        description=data.get('description')
    )
    return jsonify(result), 201 if result['success'] else 400

@kafka_bp.route('/clusters/<int:cluster_id>', methods=['DELETE'])
def delete_cluster(cluster_id):
    result = business.delete_cluster(cluster_id)
    return jsonify(result), 200 if result['success'] else 400

# ==================== TOPICS ====================

@kafka_bp.route('/topics/<int:cluster_id>', methods=['GET'])
def get_topics(cluster_id):
    result = business.get_topics(cluster_id)
    return jsonify(result), 200 if result['success'] else 400

@kafka_bp.route('/topics', methods=['POST'])
def create_topic():
    data = request.get_json()
    result = business.create_topic(
        cluster_id=data.get('cluster_id'),
        topic_name=data.get('topic_name'),
        schema_id=data.get('schema_id'),
        partitions=data.get('partitions', 1),
        replication_factor=data.get('replication_factor', 1),
        description=data.get('description')
    )
    return jsonify(result), 201 if result['success'] else 400

@kafka_bp.route('/topics/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    result = business.delete_topic(topic_id)
    return jsonify(result), 200 if result['success'] else 400

# ==================== PUBLISH ====================

@kafka_bp.route('/publish/<int:topic_id>', methods=['POST'])
def publish_message(topic_id):
    data = request.get_json()
    result = business.publish_message(
        topic_id=topic_id,
        payload=data.get('payload'),
        key=data.get('key'),
        headers=data.get('headers')
    )
    return jsonify(result), 200 if result['success'] else 400
