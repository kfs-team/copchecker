from pymilvus import (
    MilvusClient,
    FieldSchema,
    CollectionSchema,
    DataType,
)

MILVUS_SERVER = 'http://192.168.0.110:19530'
MILVUS_USERNAME = ''
MILVUS_PASSWORD = ''


def create_db():
    client = MilvusClient(
        uri=MILVUS_SERVER,
        username=MILVUS_USERNAME,
        password=MILVUS_PASSWORD
    )
    
    client.create_






if __name__ == '__main__':
    create_db()
