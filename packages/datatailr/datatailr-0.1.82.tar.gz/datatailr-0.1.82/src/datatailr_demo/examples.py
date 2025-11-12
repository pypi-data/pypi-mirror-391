# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************
from datatailr import set_allow_unsafe_scheduling

set_allow_unsafe_scheduling(True)


def simple_workflow():
    from datatailr import workflow
    from data_pipelines.data_processing import func_no_args

    @workflow(name="simple_data_pipeline_<>USERNAME<>")
    def simple_data_pipeline():
        func_no_args()

    return simple_data_pipeline()


def simple_app():
    from datatailr import App
    from dashboards.app import main

    app = App(
        name="simple_dashboard_app_<>USERNAME<>",
        entrypoint=main,
        python_requirements="streamlit",
    )
    return app


def simple_service():
    from datatailr import Service
    from services.flask_service import main

    service = Service(
        name="simple_dashboard_service_<>USERNAME<>",
        entrypoint=main,
        python_requirements="flask",
    )
    return service
