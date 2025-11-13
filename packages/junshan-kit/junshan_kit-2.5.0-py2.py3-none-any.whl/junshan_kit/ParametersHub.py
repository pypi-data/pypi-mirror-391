import numpy as np
import sys, os, torch, random
import argparse
import junshan_kit.ModelsHub as ModelsHub


class check_args:
    def __init__(self):
        pass

    def get_args(self):
        parser = argparse.ArgumentParser(description="Combined config argument example")

        allowed_models = ["LS", "LRL2","ResNet18"]
        allowed_optimizers = ["ADAM", "SGD", "Bundle"]

        allowed_datasets = ["MNIST", 
                            "CIFAR100",
                            "AIP", 
                            "CCFD",
                            ]
        
        optimizers_mapping = {
            "ADAM": "ADAM",
            "SGD": "SGD",
            "Bundle": "Bundle"
        }

        model_mapping = {
            "LS": "LeastSquares",
            "LRL2": "LogRegressionBinaryL2",
            "ResNet18": "ResNet18"
        }
        
        data_name_mapping = {
            "MNIST": "MNIST",
            "CIFAR100": "CIFAR100",
            "AIP": "Adult_Income_Prediction",
            "CCFD": "Credit_Card_Fraud_Detection"
        }

        

        # Single combined argument that can appear multiple times
        parser.add_argument(
            "--train",
            type=str,
            nargs="+",                   # Allow multiple configs
            required=True,
            help = f"Format: model-dataset-optimizer (e.g., ResNet18-CIFAR10-Adam). model: {model_mapping}, \n datasets: {allowed_datasets}, optimizers: {allowed_optimizers},"
        )

        parser.add_argument(
        "--e",
        type=int,
        required=True,
        help="Number of training epochs. Example: --e 50"
        )

        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Random seed for experiment reproducibility. Default: 42"
        )

        parser.add_argument(
            "--bs",
            type=int,
            required=True,
            help="Batch size for training. Example: --bs 128"
        )

        parser.add_argument(
            "--cuda",
            type=int,
            default=0,
            required=True,
            help="The number of cuda. Example: --cuda 1 (default=0) "
        )

        parser.add_argument(
            "--s",
            type=float, 
            default=1.0, 
            # required=True,
            help="Proportion of dataset to use for training split. Example: --s 0.8 (default=1.0)"
        )

        parser.add_argument(
        "--subset",
        type=float,
        nargs=2,
        # required=True,
        help = "Two subset ratios (train, test), e.g., --subset 0.7 0.3 or --subset 500 500"
        )

        args = parser.parse_args()
        args.model_name_mapping = model_mapping
        args.data_name_mapping = data_name_mapping
        args.optimizers_name_mapping = optimizers_mapping


        if args.subset is not None:
            self.check_subset_info(args, parser)


        self.check_args(args, parser, allowed_models, allowed_optimizers, allowed_datasets)

        return args
    
    def check_subset_info(self, args, parser):
        total = sum(args.subset)
        if args.subset[0]>1:
            # CHECK
            for i in args.subset:
                if i < 1:
                    parser.error(f"Invalid --subset {args.subset}: The number of subdata must > 1")    
        else:
            if abs(total - 1.0) != 0.0:  
                parser.error(f"Invalid --subset {args.subset}: the values must sum to 1.0 (current sum = {total:.6f}))")


    def check_args(self, args, parser, allowed_models, allowed_optimizers, allowed_datasets):
        # Parse and validate each train_group
        for cfg in args.train:
            try:
                model, dataset, optimizer = cfg.split("-")
            
                if model not in allowed_models:
                    parser.error(f"Invalid model '{model}'. Choose from {allowed_models}")
                if optimizer not in allowed_optimizers:
                    parser.error(f"Invalid optimizer '{optimizer}'. Choose from {allowed_optimizers}")
                if dataset not in allowed_datasets:
                    parser.error(f"Invalid dataset '{dataset}'. Choose from {allowed_datasets}")

            except ValueError:
                parser.error(f"Invalid format '{cfg}'. Use model-dataset-optimizer")

        for cfg in args.train:
            model_name, dataset_name, optimizer_name = cfg.split("-")
            try:
                f = getattr(ModelsHub, f"Build_{args.model_name_mapping[model_name]}_{args.data_name_mapping[dataset_name]}")

            except:
                print(getattr(ModelsHub, f"Build_{args.model_name_mapping[model_name]}_{args.data_name_mapping[dataset_name]}"))
                assert False

def get_train_group(args):
    training_group = []
    for cfg in args.train:
        model, dataset, optimizer = cfg.split("-")
        training_group.append((args.model_name_mapping[model], args.data_name_mapping[dataset], args.optimizers_name_mapping[optimizer]))

    return training_group


def set_paras(args, OtherParas):
    Paras = {
        # Name of the folder where results will be saved.
        "results_folder_name": OtherParas["results_folder_name"],

        # Print loss every N epochs.
        "epoch_log_interval": 1,

        # Timestamp string for result saving.
        "time_str": ["time_str"],

        # Random seed
        "seed": args.seed,

        # Device used for training.
        "cuda": f"cuda:{args.cuda}",

        # batch-size 
        "batch_size": args.bs,

        # epochs
        "epochs": args.e,

        # split_train_data
        "split_train_data": args.s,

        # select_subset
        "select_subset": args.subset
    }

    Paras = model_list(Paras)
    Paras = model_type(Paras)
    Paras = data_list(Paras)
    Paras = optimizer_dict(Paras, OtherParas)
    Paras = device(Paras)
        
    return Paras


def set_seed(seed=42):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def device(Paras) -> dict:
    device = torch.device(f"{Paras['cuda']}" if torch.cuda.is_available() else "cpu")
    Paras["device"] = device
    use_color = sys.stdout.isatty()
    Paras["use_color"] = use_color

    return Paras

def model_list(Paras) -> dict:
    model_list = [
        "ResNet18",
        "ResNet34",
        "LeastSquares",
        "LogRegressionBinary",
        "LogRegressionBinaryL2",
    ]
    Paras["model_list"] = model_list
    return Paras

def model_type(Paras) -> dict:
    model_type = {
        "ResNet18": "multi",
        "ResNet34": "multi",
        "LeastSquares": "multi",
        "LogRegressionBinary": "binary",
        "LogRegressionBinaryL2": "binary",
    }

    Paras["model_type"] = model_type
    return Paras

def data_list(Paras) -> dict:
    """
    Attach a predefined list of dataset names to the parameter dictionary.

    The predefined datasets include:
    - Duke:
        - classes: 2
        - data: 42 (38 + 4)
        - features: 7,129
    - Ijcnn:
        - classes: 2
        - data: (35,000 + 91,701)
        - features: 22
    - w8a:
        - classes: 2
        - data: (49,749 + 14,951)
        - features: 300
    - RCV1
    - Shuttle
    - Letter
    - Vowel
    - MNIST
    - CIFAR100
    - CALTECH101_Resize_32
    - Adult Income Prediction
        - 
    - Credit_Card_Fraud_Detection
    """

    data_list = [
        "Duke",
        "Ijcnn",
        "w8a",
        "RCV1",
        "Shuttle",
        "Letter",
        "Vowel",
        "MNIST",
        "CIFAR100",
        "CALTECH101_Resize_32",
        "Adult_Income_Prediction",
        "Credit_Card_Fraud_Detection"
    ]
    Paras["data_list"] = data_list
    return Paras


def optimizer_dict(Paras, OtherParas)->dict:
    optimizer_dict = {
    # ----------------- ADAM --------------------
    "ADAM": {
        "params": {
            # "alpha": [2 * 1e-3],
            "alpha": (
                [0.5 * 1e-3, 1e-3, 2 * 1e-3]
                if OtherParas["SeleParasOn"]
                else [0.0005]
            ),
            "epsilon": [1e-8],
            "beta1": [0.9],
            "beta2": [0.999],
        },
    },
    # ------------- ALR-SMAG --------------------
    "ALR-SMAG": {
        "params": {
            "c": ([0.1, 0.5, 1, 5, 10] if OtherParas["SeleParasOn"] else [0.1]),
            "eta_max": (
                [2**i for i in range(-8, 9)]
                if OtherParas["SeleParasOn"]
                else [0.125]
            ),
            "beta": [0.9],
        },
    },
    # ------------ Bundle -----------------------
    "Bundle": {
        "params": {
            "delta": (
                [2**i for i in range(-8, 9)]
                if OtherParas["SeleParasOn"]
                else [0.25]
            ),
            "cutting_number": [10],
        },
    },
    # ------------------- SGD -------------------
    "SGD": {
        "params": {
            "alpha": (
                [2**i for i in range(-8, 9)] if OtherParas["SeleParasOn"] else [0.1]
            )
        }
    },
    # ------------------- SPSmax ----------------
    "SPSmax": {
        "params": {
            "c": ([0.1, 0.5, 1, 5, 10] if OtherParas["SeleParasOn"] else [0.1]),
            "gamma": (
                [2**i for i in range(-8, 9)]
                if OtherParas["SeleParasOn"]
                else [0.125]),
        },
    },
    # -------------- SPBM-PF --------------------
    "SPBM-PF": {
        "params": {
            "M": [1e-5],
            "delta": (
                [2**i for i in range(9, 20)]
                if OtherParas["SeleParasOn"]
                else [1]
            ),
            "cutting_number": [10],
        },
    },
    # -------------- SPBM-TR --------------------
    "SPBM-TR": {
        "params": {
            "M": [1e-5],
            "delta": (
                [2**i for i in range(9, 20)]
                if OtherParas["SeleParasOn"]
                else [256]
            ),
            "cutting_number": [10],
        },
    },
    
    # ----------- SPBM-TR-NoneLower -------------
    "SPBM-TR-NoneLower": {
        "params": {
            "M": [1e-5],
            "delta": (
                [2**i for i in range(0, 9)]
                if OtherParas["SeleParasOn"]
                else [256]
            ),
            "cutting_number": [10],
        },
    },
    # ----------- SPBM-TR-NoneSpecial -----------
    "SPBM-TR-NoneSpecial": {
        "params": {
            "M": [1e-5],
            "delta": (
                [2**i for i in range(-8, 9)]
                if OtherParas["SeleParasOn"]
                else [1]
            ),
            "cutting_number": [10],
        },
    },
    # ------------- SPBM-PF-NoneLower -----------
    "SPBM-PF-NoneLower": {
        "params": {
            "M": [1e-5],
            "delta": (
                [2**i for i in range(0, 9)]
                if OtherParas["SeleParasOn"]
                else [0]
            ),
            "cutting_number": [10],
        },
    },
    }

    Paras["optimizer_dict"] = optimizer_dict
    return Paras