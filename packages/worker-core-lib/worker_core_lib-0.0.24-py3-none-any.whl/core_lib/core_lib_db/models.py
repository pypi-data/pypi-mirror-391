import uuid
from sqlalchemy import Column, String, ForeignKey, JSON, Text, Integer, BigInteger, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from dataclasses import dataclass
from typing import Dict

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    storage_connections = relationship("StorageConnection", back_populates="user")

class StorageProviderConfig(Base):
    __tablename__ = "storage_provider_configs"
    id = Column(UUID(as_uuid=True), primary_key=True)
    encryptedCredentials = Column('encryptedCredentials', JSON, nullable=False, default={})
    scanRootPath = Column('scanRootPath', String)

class StorageConnection(Base):
    __tablename__ = "storage_connections"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column('providerType', String)
    user_id = Column('userId', UUID(as_uuid=True), ForeignKey("users.id"))
    storage_provider_config_id = Column('storageProviderConfigId', UUID(as_uuid=True), ForeignKey("storage_provider_configs.id"))
    # host and port are now stored in encryptedCredentials JSON
    encrypted_credentials = Column('encryptedCredentials', Text)
    
    user = relationship("User", back_populates="storage_connections")
    config = relationship("StorageProviderConfig")

class Model(Base):
    __tablename__ = 'models'
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String)
    thumbnail_url = Column('thumbnailUrl', String)
    description = Column(Text, nullable=True)
    file_size = Column('fileSize', BigInteger, nullable=True)
    file_types = Column('fileTypes', String, nullable=True)  # simple-array stored as comma-separated
    file_path = Column('filePath', String, nullable=True)
    original_file_path = Column('originalFilePath', String, nullable=True)

    storage_items = relationship("StorageItem", back_populates="platform_model")

class StorageItem(Base):
    __tablename__ = 'storage_items'
    id = Column(UUID(as_uuid=True), primary_key=True)
    provider_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    connection_id = Column(UUID(as_uuid=True), ForeignKey('storage_connections.id'))
    platform_model_id = Column(UUID(as_uuid=True), ForeignKey('models.id'), nullable=True)
    size = Column(BigInteger)
    last_modified = Column('last_modified', DateTime)
    
    platform_model = relationship("Model", back_populates="storage_items")
    metamodel_storage_items = relationship("MetamodelStorageItem", back_populates="storage_item")


class Metamodel(Base):
    __tablename__ = 'metamodels'
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    library_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String, nullable=False)
    confidence_score = Column('confidence_score', String, nullable=True)
    
    metamodel_storage_items = relationship("MetamodelStorageItem", back_populates="metamodel")


class MetamodelStorageItem(Base):
    __tablename__ = 'metamodel_storage_items'
    metamodel_id = Column(UUID(as_uuid=True), ForeignKey('metamodels.id'), primary_key=True)
    storage_item_id = Column(UUID(as_uuid=True), ForeignKey('storage_items.id'), primary_key=True)
    
    metamodel = relationship("Metamodel", back_populates="metamodel_storage_items")
    storage_item = relationship("StorageItem", back_populates="metamodel_storage_items")


# Dataclasses for job data remain useful
@dataclass
class FilePath:
    value: str


@dataclass
class DownloadJobData:
    modelId: str
    storageConnectionId: str
    filePath: Dict
    originalJobName: str