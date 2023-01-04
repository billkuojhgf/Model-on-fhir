_config = {
    "DEFAULT": {
        "ServerAliveInterval": 45,
    },
    "table_path": {
        "FEATURE_TABLE": "./config/features.csv",
    },
    "fhir_server": {
        "FHIR_SERVER_URL_": "http://localhost:8090/fhir",
        "FHIR_SERVER_URL": "http://ming-desktop.ddns.net:8192/fhir",
    },
    "bulk_server": {
        "BULK_SERVER_URL": "http://ming-desktop.ddns.net:8193/fhir"
    },
    "frontend": {
        "FRONTEND_URL": "http://localhost:8080"
    }
}

configObject = _config
