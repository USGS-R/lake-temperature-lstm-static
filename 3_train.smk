
configfile: "3_train/train_config.yaml"

# Train model
rule train_model:
    input:
        train_data_file = "2_process/out/{data_source}/train.npz"
    output:
        weights_file = "3_train/out/{data_source}/lstm.pt"
    params:
        config = config
    script:
        "3_train/src/train.py"
