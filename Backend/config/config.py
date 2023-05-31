_config = {
    "DEFAULT": {
        "ServerAliveInterval": 45,
    },
    "table_path": {
        "FEATURE_TABLE": "./config/features.csv",
    },
    "fhir_server": {
        "FHIR_SERVER_URL": "http://ming-desktop.ddns.net:8192/fhir",
        "FHIR_SERVER_URL_LOCAL": "http://localhost:8090/fhir",
    },
    "bulk_server": {
        "BULK_SERVER_URL": "http://ming-desktop.ddns.net:8193/fhir",
        "BULK_SERVER_URL_LOCAL": "http://localhost:8888/fhir"
    },
    "base_urls": {
        "SMART_URL": "http://localhost:5000/launch",
        "CDS_HOOKS_URL": "http://localhost:5001",
        "FRONTEND_URL": "http://localhost:8080"
    },
    "patient_id": "test-03121002",
}

configObject = _config
