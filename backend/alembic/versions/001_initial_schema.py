"""Initial schema migration for SentinelAI

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-27 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('username', sa.String(100), unique=True, index=True, nullable=False),
        sa.Column('display_name', sa.String(150), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), default='analyst', nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 2. network_events
    op.create_table(
        'network_events',
        sa.Column('id', sa.String(50), primary_key=True, index=True),
        sa.Column('timestamp', sa.BigInteger(), index=True, nullable=False),
        sa.Column('source_ip', sa.String(50), index=True, nullable=False),
        sa.Column('dest_ip', sa.String(50), index=True, nullable=False),
        sa.Column('src_port', sa.Integer(), nullable=True),
        sa.Column('dst_port', sa.Integer(), nullable=True),
        sa.Column('protocol', sa.String(20), default='TCP', nullable=False),
        sa.Column('category', sa.String(100), default='Anomalous traffic', nullable=False),
        sa.Column('source', sa.String(100), default='Rule engine', nullable=False),
        sa.Column('severity', sa.String(20), default='low', nullable=False),
        sa.Column('risk_score', sa.Integer(), default=0, nullable=False),
        sa.Column('status', sa.String(30), default='new', nullable=False),
        sa.Column('duplicates', sa.Integer(), default=0, nullable=False),
        sa.Column('event_source', sa.String(50), default='json_file', nullable=False),
        sa.Column('flow_features', sa.JSON(), nullable=True),
        sa.Column('collector_metadata', sa.JSON(), nullable=True),
        sa.Column('ingestion_status', sa.String(30), default='processed', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_events_source_dest', 'network_events', ['source_ip', 'dest_ip'])
    op.create_index('idx_events_sev_time', 'network_events', ['severity', 'timestamp'])

    # 3. alerts
    op.create_table(
        'alerts',
        sa.Column('id', sa.String(50), primary_key=True, index=True),
        sa.Column('related_event_id', sa.String(50), sa.ForeignKey('network_events.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('timestamp', sa.BigInteger(), index=True, nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), default='medium', nullable=False),
        sa.Column('risk_score', sa.Integer(), default=50, nullable=False),
        sa.Column('detection_sources', sa.JSON(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(30), default='new', nullable=False),
        sa.Column('notes', sa.String(2000), nullable=True),
        sa.Column('model_versions', sa.JSON(), nullable=True),
        sa.Column('rule_ids', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_alert_status_sev', 'alerts', ['status', 'severity'])

    # 4. detection_rules
    op.create_table(
        'detection_rules',
        sa.Column('id', sa.String(50), primary_key=True, index=True),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), default='medium', nullable=False),
        sa.Column('enabled', sa.Boolean(), default=True, nullable=False),
        sa.Column('threshold', sa.Integer(), default=10, nullable=False),
        sa.Column('window_sec', sa.Integer(), default=60, nullable=False),
        sa.Column('last_triggered', sa.BigInteger(), default=0, nullable=False),
        sa.Column('matches', sa.Integer(), default=0, nullable=False),
        sa.Column('rule_type', sa.String(50), default='threshold', nullable=False),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 5. firewall_requests
    op.create_table(
        'firewall_requests',
        sa.Column('id', sa.String(50), primary_key=True, index=True),
        sa.Column('source_ip', sa.String(50), index=True, nullable=False),
        sa.Column('reason', sa.String(255), nullable=False),
        sa.Column('alert_id', sa.String(50), index=True, nullable=True),
        sa.Column('requested_by', sa.String(100), default='analyst', nullable=False),
        sa.Column('requested_at', sa.BigInteger(), nullable=False),
        sa.Column('duration_min', sa.Integer(), default=60, nullable=False),
        sa.Column('status', sa.String(30), default='pending', nullable=False),
        sa.Column('direction', sa.String(20), default='Inbound', nullable=False),
        sa.Column('reviewed_by', sa.String(100), nullable=True),
        sa.Column('reviewed_at', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_fw_req_status_ip', 'firewall_requests', ['status', 'source_ip'])

    # 6. firewall_actions
    op.create_table(
        'firewall_actions',
        sa.Column('id', sa.String(50), primary_key=True, index=True),
        sa.Column('managed_rule_name', sa.String(150), unique=True, index=True, nullable=False),
        sa.Column('request_id', sa.String(50), sa.ForeignKey('firewall_requests.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('target_ip', sa.String(50), index=True, nullable=False),
        sa.Column('direction', sa.String(20), default='Inbound', nullable=False),
        sa.Column('action_type', sa.String(30), default='block', nullable=False),
        sa.Column('status', sa.String(30), default='created', nullable=False),
        sa.Column('duration_min', sa.Integer(), default=60, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verification_status', sa.String(50), default='simulated', nullable=False),
        sa.Column('rollback_status', sa.String(50), nullable=True),
        sa.Column('failure_details', sa.String(500), nullable=True),
    )
    op.create_index('idx_fw_action_status_exp', 'firewall_actions', ['status', 'expires_at'])

    # 7. model_registry
    op.create_table(
        'model_registry',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('version', sa.String(50), unique=True, index=True, nullable=False),
        sa.Column('artifact_location', sa.String(255), nullable=False),
        sa.Column('training_dataset', sa.String(150), default='CIC-IDS2017', nullable=False),
        sa.Column('feature_schema_version', sa.String(50), default='v1.0', nullable=False),
        sa.Column('features_count', sa.Integer(), default=78, nullable=False),
        sa.Column('classes', sa.JSON(), nullable=False),
        sa.Column('evaluation_metrics', sa.JSON(), nullable=True),
        sa.Column('confusion_matrix', sa.JSON(), nullable=True),
        sa.Column('per_class_metrics', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(50), default='Loaded', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 8. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(50), primary_key=True, index=True),
        sa.Column('timestamp', sa.BigInteger(), index=True, nullable=False),
        sa.Column('actor', sa.String(100), index=True, nullable=False),
        sa.Column('action', sa.String(100), index=True, nullable=False),
        sa.Column('target', sa.String(100), nullable=False),
        sa.Column('result', sa.String(30), default='Success', nullable=False),
        sa.Column('reason', sa.String(255), default='—', nullable=False),
        sa.Column('related', sa.String(100), default='—', nullable=False),
        sa.Column('correlation_id', sa.String(100), nullable=True),
        sa.Column('extra_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_audit_actor_time', 'audit_logs', ['actor', 'timestamp'])

    # 9. system_settings
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(100), unique=True, index=True, nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('category', sa.String(50), default='general', nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_by', sa.String(100), default='system', nullable=False),
    )

    # 10. feedbacks
    op.create_table(
        'feedbacks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('category', sa.String(50), default='general', nullable=False),
        sa.Column('message', sa.String(2000), nullable=False),
        sa.Column('status', sa.String(30), default='received', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('feedbacks')
    op.drop_table('system_settings')
    op.drop_table('audit_logs')
    op.drop_table('model_registry')
    op.drop_table('firewall_actions')
    op.drop_table('firewall_requests')
    op.drop_table('detection_rules')
    op.drop_table('alerts')
    op.drop_table('network_events')
    op.drop_table('users')
