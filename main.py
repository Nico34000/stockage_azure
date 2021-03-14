import sys
import argparse
import configparser
import logging
import os.path
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient
from azure.storage.blob import generate_account_sas, ResourceTypes, AccountSasPermissions
from datetime import datetime, timedelta



def listb(args, containerclient):
    """ 
    This function print on console all name of 
    blobs in the container.

    args : is the argument 'list'.

    container : is the container when you want see
    list of blobs.
    """
    logging.debug("Start function listb, we want to have all list of blobs")
    blob_list=containerclient.list_blobs()
    #configure the variable for return all blobs in container
    logging.info(f"list of blobs in container")

    for blob in blob_list:
        print(blob.name)
    logging.info(f"list of blobs in container")



def upload(cible, blobclient):
    """
    This function upload  file on the container
    the file on the container is a blob.

    cible : is the path of the file want to upload.

    blobclient : is the config for connect to azure.

    """
    with open(cible, "rb") as f:
        logging.warning("Upload blob in the container")
        blobclient.upload_blob(f)
        logging.info(f"Upload {f}done")


def download(filename, dl_folder, blobclient):
    """
    This function download blob on container.

    filename : is the name of the blob in the container.

    blobclient : is the config for connect to azure.


    """

    with open(os.path.join(dl_folder,filename), "wb") as my_blob:
        logging.debug("we join path of the local folder for write blob")
        #iniatilize the variable blob_data for connect to blob client end
        #download it
        blob_data=blobclient.download_blob()
        # We write blob on the file 
        logging.warning("Write blob, be care of your path  !!!")
        blob_data.readinto(my_blob)
        logging.info(f"Write done{my_blob}")


def create_container(name,blobclient):
    """
    This function create a new container on
    the storage account.

    name: name of the new container.

    blobclient : is the config for connect to azure.
    """
    container_client = blobclient.create_container(name)
    return container_client


def sas_account_token():
    """
    This function create a token with account and key
    the token sas, is a provisory key for share.
    
    """

    sas_token = generate_account_sas(
    account_name=(f"{config['storage']['account']}"),
    account_key=(f"{config['storage']['key']}"),
    resource_types=ResourceTypes(container=True,object=True),
    permission=AccountSasPermissions(read=True,list=True),
    expiry=datetime.utcnow() + timedelta(hours=1))
    return sas_token

def main(args,config):
    """
    This function connect to azure if the application run
    with argument. with argument "upload" we uploading a file
    in the container, with argument "download we download a blob 
    in the container with argument "list" we have a list of
    all blobs is in the container and with argument "sas" we have 
    a token in the console for sharing this token.
    """
    # blobclient=BlobServiceClient(
    #     f"https://{config['storage']['account']}.blob.core.windows.net",
    #     config["storage"]["key"],
    #     logging_enable=True)
    blobclient = BlobServiceClient(account_url=f"https://{config['storage']['account']}.blob.core.windows.net",
    credential=f'{sas_account_token()}')
    logging.debug(f"account : {blobclient}")
    containerclient=blobclient.get_container_client(config["storage"]["container"])
    logging.debug(f"container : {containerclient}")
    if args.action=="list":
        logging.debug(f"account : {blobclient}")
        logging.debug("start of argument list we return function listb")
        return listb(args, containerclient)
        logging.info(f"{listb(args,containerclient)}")
        logging.debug(f"account : {blobclient}")

    else:
        if args.action=="upload":
            blobclient=containerclient.get_blob_client(os.path.basename(args.cible))
            logging.debug(f"Udapte file on container client : {blobclient} ")
            return upload(args.cible, blobclient)
            logging.info(f"The file {upload(args.cible,blobclient)}has been add on container")
        elif args.action=="download":
            blobclient=containerclient.get_blob_client(os.path.basename(args.remote))
            logging.debug(f"Download  file from container client : {blobclient} ")
            logging.warning("Risk to delete file be care of your path")
            return download(args.remote, config["general"]["restoredir"], blobclient)
        elif args.action=="create_container":
            create_container(args.name, blobclient)
        elif args.action=="sas":
            print(sas_account_token())


    

if __name__=="__main__":
    parser=argparse.ArgumentParser("Logiciel d'archivage de documents")
    parser.add_argument("-cfg",default="config.ini",help="chemin du fichier de configuration")
    parser.add_argument("-lvl",default = "info", help="niveau de log")
    subparsers=parser.add_subparsers(dest="action",help="type d'operation")
    subparsers.required=True
    
    parser_s=subparsers.add_parser("upload")
    parser_s.add_argument("cible",help="fichier à envoyer")

    parser_c=subparsers.add_parser("create_container")
    parser_c.add_argument("name", help="name of your new container")

    parser_sas=subparsers.add_parser("sas")

    parser_r=subparsers.add_parser("download")
    parser_r.add_argument("remote",help="nom du fichier à télécharger")
    parser_r=subparsers.add_parser("list")

    args=parser.parse_args()

    loglevels={"debug":logging.DEBUG, "info":logging.INFO, "warning":logging.WARNING, "error":logging.ERROR, "critical":logging.CRITICAL}
    print(loglevels[args.lvl.lower()])
    print(f" lvl of logging = {[args.lvl.lower()]}")
    logging.basicConfig(level=loglevels[args.lvl.lower()])

    config=configparser.ConfigParser()
    config.read(args.cfg)

    sys.exit(main(args,config))