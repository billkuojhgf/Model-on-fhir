import threading
from datetime import datetime
import pandas as pd
from flask import Blueprint, jsonify
from requests import HTTPError
from base_module import encode_model_data_set
from base_module import train_model
from base_module import get_machine_learning_model
from base_module import choose_model
from base.lib import transform_to_correct_type
from base.continuous_training_processor import \
    combine_training_and_predicting_feature_table, \
    separate_patients, \
    allocate_feature_resources, \
    extract_value_and_datetime, \
    resources_filter, \
    transform_data, \
    merge_transformed_data, \
    drop_unuseful_rows, \
    split_data, \
    imputation_stategy, \
    model_evaluation, \
    drop_trained_data
from base.object_store import \
    training_sets_table, \
    bulk_server, \
    feature_table, \
    training_feature_table, \
    model_feature_table, \
    training_model_feature_table, \
    training_status_table

ct_app = Blueprint('con_train', __name__)
lock = threading.Lock()


@ct_app.route("/<api>", methods=['GET'])
def continuous_training_process(api):

    thread = threading.Thread(target=training_process, kwargs={'model_name': api})
    thread.start()

    return jsonify({"message": "Training process is running in the background."})


def training_process(model_name):
    # Lock the thread
    lock.acquire(timeout=1200)

    # Get the training set from the training_sets_table
    training_sets = training_sets_table.get_training_set(model_name)
    # Add exception for error 404
    try:
        bulk_server.content = "http://ming-desktop.ddns.net:8193/fhir/$export-poll-status?_jobId=945d3bd7-2fd1-41b0-bf2a-3d39a197686d"
        bulk_server.provision()
    except HTTPError:
        print("Connection error. Trying to generate a new bulk request")
        bulk_server.content = None
        bulk_server.provision()
        print(bulk_server.content)

    ndj = bulk_server.iter_ndjson_dict()
    """
    Differences between code_dict and predict_and_training_feature_tables is:
    code_dict combines the training and predicting feature tables with Resource type. It takes the resource type as the
    key. While predict_and_training_feature_tables combines the training and predicting feature tables with feature.
    It takes the feature as the key, and is more useful in the later process.
    """
    code_dict = combine_training_and_predicting_feature_table(model_name)
    data_with_separated_patient = separate_patients(ndj)
    data_with_separated_patient = allocate_feature_resources(
        data_with_separated_patient, code_dict)

    # Extract the value and datetime from the resources.
    predict_and_training_feature_tables = \
        feature_table.get_model_feature_dict(
            model_name) | training_feature_table.get_model_feature_dict(model_name)
    value_and_datetime_of_patients = extract_value_and_datetime(
        data_with_separated_patient, predict_and_training_feature_tables)

    # Drop the resources that are not needed.
    x_value_and_datetime_of_patients_after_filter, y_value_and_datetime_of_patients_after_filter = resources_filter(
        value_and_datetime_of_patients,
        predict_and_training_feature_tables,
        training_sets.data_filter
    )

    # translate the value from the value_and_datetime_of_patients_after_filter
    transformed_x_data_of_patients = transform_data(model_feature_table,
                                                    x_value_and_datetime_of_patients_after_filter,
                                                    model_name)
    transformed_y_data_of_patients = transform_data(training_model_feature_table,
                                                    y_value_and_datetime_of_patients_after_filter,
                                                    model_name, y_data=True)

    transformed_training_data = merge_transformed_data(transformed_x_data_of_patients,
                                                       transformed_y_data_of_patients)

    # Drop the rows that have been trained before. By checking the time of the y data.
    transformed_training_data, max_training_data_time = drop_trained_data(transformed_training_data,
                                                                          training_status_table.get_last_training_data_filter_operation(model_name))

    # Time for some dataframe works
    column = model_feature_table.get_model_feature_column(model_name) \
        + training_model_feature_table.get_model_feature_column(model_name)
    df = pd.DataFrame.from_dict(transformed_training_data, orient="index")

    numbers_of_patients = len(df.index)
    if numbers_of_patients == 0:
        print("Since last training, there is no new data to train.")
        lock.release()
        return
    df.columns = column

    # First is to drop the rows that matches the condition we've set in the training_sets_table.
    df = drop_unuseful_rows(df, training_sets.null_value_strategy["drop"])

    # Then split the data into X,Y training set and X,Y testing set.
    x_training_df, x_testing_df, y_train_df, y_test_df \
        = split_data(df,
                     training_sets.training_config,
                     training_model_feature_table.get_model_feature_column(model_name))
    x_train_imp, x_test_imp = imputation_stategy(x_training_df, training_sets.null_value_strategy.copy()), \
        imputation_stategy(
            x_testing_df, training_sets.null_value_strategy.copy())

    # Encode the data
    x_train_encoded, x_test_encoded, y_train_encoded, y_test_encoded = encode_model_data_set(
        x_train_imp, x_test_imp, y_train_df, y_test_df, model_name)

    # Train the model
    train_model(x_train_encoded, y_train_encoded, model_name)

    # Evaluate the model
    register_model = get_machine_learning_model("register", model_name)
    new_model = get_machine_learning_model("new", model_name)
    evaluate = model_evaluation(
        register_model, new_model, x_test_encoded, y_test_encoded)

    # Save the model
    validate_method = training_sets.training_config["validate_method"]
    evaluate_result = evaluate[validate_method]
    threshold = evaluate['best_threshold']

    print("The evaluation result is: ", evaluate)

    if evaluate_result['register_model'] > evaluate_result['new_model']:
        chosed_model = "register"
    else:
        chosed_model = "new"
    choose_model(model_name, chosed_model)

    if chosed_model == "new":
        last_training_time = max_training_data_time
    else:
        last_training_time = transform_to_correct_type(training_status_table.get_last_training_data_filter_operation(
            model_name).threshold, "date")

    return_dict = {
        "model": model_name,
        "last_training_time": datetime.now(),
        "last_training_data_time": last_training_time,
        "numbers_of_patients": numbers_of_patients,
        "old_model_evaluate": evaluate_result['register_model'],
        "new_model_evaluate": evaluate_result['new_model'],
        "register_model": chosed_model,
        "threshold": threshold[f'{chosed_model}_model']
    }

    training_status_table.write_new_data_into_csv(return_dict)

    # Release the lock
    lock.release()

    print("Training process finished. The return dict is: ", return_dict)


if __name__ == "__main__":
    print("starting...")
    print(training_process("SPC"))
    print("ending...")
    pass
