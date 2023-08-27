import boto3
import time

#add boto3 client for RDS. No resource options for RDS

rds = boto3.client('rds')

#set up variables for RDS creation
username = ''
password = ''
db_subnet_group = ''
db_cluster_id = ''

#create the Aurora SERVERLESS DB cluster. Using a try / expect block to check if DB already exists before creation. we could use the practice XD
try:
    response = rds.describe_db_clusters(DBClusterIdentifier=db_cluster_id)
    print (f"The DB cluster {db_cluster_id} already exists. Skipping creation.")
except rds.exceptions.DBClusterNotFoundFault:
    response = rds.create_db_cluster(
        Engine='aurora-mysql',
        EngineVersion='5.7.mysql_aurora.2.08.3',
        DBClusterIdentifier=db_cluster_id,
        MasterUsername=username,
        MasterUserPassword=password,
        DatabaseName='',
        DBSubnetGroupName=db_subnet_group,
        EngineMode='serverless',
        EnableHttpEndpoint=True,
        ScalingConfiguration={
            'MinCapacity': 1, #Minimum ACU's
            'MaxCapacity': 8, #Maximum ACU's
            'AutoPause': True, #Feature that allows the cluster to pause after Idle past configured time.
            'SecondsUntilAutoPause': 300 #pause cluster after 5 mins of inactivity.
        }
    ) 
    print (f"The DB Serverless cluster {db_cluster_id} has been created.")  
    
    #Wait for DB CLuster to become available. Takes a bit of time. Loop went thru 5 times. so 200 sec(3mins) next time.
    while True:
        response = rds.describe_db_clusters(DBClusterIdentifier=db_cluster_id)
        status = response['DBClusters'][0]['Status']
        print(f"The Status of the DB Cluster is '{status}'")
        if status == 'available':
            break
        print("Waiting for the DB cluster to become available...")
        time.sleep(45)
        
#Modify our DB Cluster by updating the scaling config for the cluster
response = rds.modify_db_cluster(
        DBClusterIdentifier=db_cluster_id,
        ScalingConfiguration={
            'MinCapacity': 1, #Minimum ACU's
            'MaxCapacity': 16, #Maximum ACU's
            'SecondsUntilAutoPause': 600 #pause cluster after 5 mins of inactivity.
        }
    ) 
print (f"Updated the scaling configuration for the DB Serverless cluster '{db_cluster_id}'. ") 

#Delete the DB cluster
esponse = rds.delete_db_cluster(
        DBClusterIdentifier=db_cluster_id,
        SkipFinalSnapshot = True
    ) 
print (f"the DB cluster '{db_cluster_id}' has been deleted. ") 
