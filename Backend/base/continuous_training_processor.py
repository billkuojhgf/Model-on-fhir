from base.object_store import bulk_server

if __name__ == "__main__":
    from object_store import bulk_server
    print("starting...")
    bulk_server.provision()
    ndj = bulk_server.iter_ndjson_dict()
    pass