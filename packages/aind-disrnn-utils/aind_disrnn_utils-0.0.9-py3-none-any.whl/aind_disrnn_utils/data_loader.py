"""
Tools for loading AIND dynamic foraging data into the disRNN format
"""

import numpy as np
from disentangled_rnns.library import rnn_utils


def create_disrnn_dataset(
    df_trials, ignore_policy="include", batch_size=None, features=None
) -> rnn_utils.DatasetRNN:
    """
    Creates a disrnn dataset object

    args:
    df_trials, a trial dataframe, created by aind_dynamic_foraging_data_utils
        must have 'ses_idx' as an column which indicates how to divide
        trials by session
    ignore_policy (str), must be "include" or "exclude", and determines
        how to use trials where the mouse did not response
    batch_size (int) input argument to disrnn dataset
    features (dict), keys must be columns in df_trials to be used as prediction
        features. values are the semantic labels for that feature. If None,
        use previous choice and previous reward
    """

    # Input checking
    if "ses_idx" not in df_trials:
        raise ValueError("df_trials must contain index of sessions ses_idx")
    if ignore_policy not in ["include", "exclude"]:
        raise ValueError('ignore_policy must be either "include" or "exclude"')

    # Copy so we can modify
    df_trials = df_trials.copy()

    # Determine the number of classes in the output prediction
    if ignore_policy == "include":
        n_classes = 3
    else:
        n_classes = 2
        # Remove trials without a response
        df_trials = df_trials[df_trials["animal_response"] != 2]

    # Format inputs
    # Make 0/1 coded reward vector
    df_trials["rewarded"] = df_trials["earned_reward"].astype(int)

    # Break down feature dictionary
    if features is None:
        features = {
            "animal_response": "prev choice",
            "rewarded": "prev reward",
        }
    feature_cols = list(features.keys())
    feature_labels = [features[x] for x in feature_cols]

    # Ensure all feature columns are in df_trials
    for feature in feature_cols:
        if feature not in df_trials.columns:
            raise ValueError(
                "input feature '{}' not in df_trials".format(feature)
            )

    # Determine size of input matrix
    # Input matrix has size [# trials, # sessions, # features]
    max_session_length = df_trials.groupby("ses_idx")["trial"].count().max()

    num_sessions = len(df_trials["ses_idx"].unique())
    num_input_features = len(feature_cols)
    # Pad trials to be ignored with -1
    xs = np.full((max_session_length, num_sessions, num_input_features), -1)

    # Load each session into xs
    for dex, ses_idx in enumerate(df_trials["ses_idx"].unique()):
        temp = df_trials.query("ses_idx == @ses_idx")
        this_xs = temp[feature_cols].to_numpy()[:-1, :]
        xs[1 : len(temp), dex, :] = this_xs  # noqa E203

    # Determine size of output matrix
    # Output matrix has size [# trials, # sessions, # features]
    num_output_features = 1
    # pad trials to be ignored with -1
    ys = np.full((max_session_length, num_sessions, num_output_features), -1)

    # Load each session into ys
    for dex, ses_idx in enumerate(df_trials["ses_idx"].unique()):
        temp = df_trials.query("ses_idx == @ses_idx")
        this_ys = temp[["animal_response"]].to_numpy()
        ys[0 : len(temp), dex, :] = this_ys  # noqa E203

    # Pack into a DatasetRNN object
    dataset = rnn_utils.DatasetRNN(
        ys=ys,
        xs=xs,
        y_type="categorical",
        n_classes=n_classes,
        x_names=feature_labels,
        y_names=["choice"],
        batch_size=batch_size,
        batch_mode="random",
    )
    return dataset
