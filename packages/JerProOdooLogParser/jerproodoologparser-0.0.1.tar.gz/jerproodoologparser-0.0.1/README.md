# A library for parsing Odoo logs and collecting test information

Example of use:

    # -*- coding: utf-8 -*-
    import odoo_log_parser
    with open("odoo_log_file.log, "r") as logfilo:
        logparser = odoo_log_parser.OdooTestDigest(logfilo)
        digest = logparser.get_full_test_digest()
        # Accessing test data:
        tests_succeeded = digest["db_name"]['tests_succeeded']
        tests_failing = digest["db_name"]['tests_failing']
        tests_errors = digest["db_name"]['tests_errors']
        setup_errors = digest["db_name"]['setup_errors']
        # Accessing details:
        tests_failing[0]['test_path']
        tests_failing[0]['test_log']
