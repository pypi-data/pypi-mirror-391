import torch, time
import torch.nn as nn
import numpy as np
import torch.utils.data as Data
from torch.nn.utils import parameters_to_vector
from junshan_kit import DataHub, ParametersHub, TrainingHub, Evaluate_Metrics

def chosen_loss_fn(model_name, Paras):
    # ---------------------------------------
    # There have an addition parameter
    if model_name == "LogRegressionBinaryL2":
        Paras["lambda"] = 1e-3
    # ---------------------------------------

    if model_name in ["LeastSquares"]:
        loss_fn = nn.MSELoss()

    else:
        if Paras["model_type"][model_name] == "binary":
            loss_fn = nn.BCEWithLogitsLoss()

        elif Paras["model_type"][model_name] == "multi":
            loss_fn = nn.CrossEntropyLoss()

        else:
            loss_fn = nn.MSELoss()
            print("\033[91m The loss function is error!\033[0m")
            assert False
            
    Paras["loss_fn"] = loss_fn

    return loss_fn, Paras


def load_data(model_name, data_name, Paras):
    # load data
    train_path = f"./exp_data/{data_name}/training_data"
    test_path = f"./exp_data/{data_name}/test_data"

    if data_name == "MNIST":
        train_dataset, test_dataset, transform = DataHub.MNIST(Paras, model_name)

    elif data_name == "CIFAR100":
        train_dataset, test_dataset, transform = DataHub.CIFAR100(Paras, model_name)

    elif data_name == "Adult_Income_Prediction":
        train_dataset, test_dataset, transform = DataHub.Adult_Income_Prediction(Paras)

    elif data_name == "Credit_Card_Fraud_Detection":
        train_dataset, test_dataset, transform = DataHub.Credit_Card_Fraud_Detection(Paras)
    

    # elif data_name == "CALTECH101_Resize_32":
    #     Paras["train_ratio"] = 0.7
    #     train_dataset, test_dataset, transform = datahub.caltech101_Resize_32(
    #         Paras["seed"], Paras["train_ratio"], split=True
    #     )

    # elif data_name in ["Vowel", "Letter", "Shuttle", "w8a"]:
    #     Paras["train_ratio"] = Paras["split_train_data"][data_name]
    #     train_dataset, test_dataset, transform = datahub.get_libsvm_data(
    #         train_path + ".txt", test_path + ".txt", data_name
    #     )

    # elif data_name in ["RCV1", "Duke", "Ijcnn"]:
    #     Paras["train_ratio"] = Paras["split_train_data"][data_name]
    #     train_dataset, test_dataset, transform = datahub.get_libsvm_bz2_data(
    #         train_path + ".bz2", test_path + ".bz2", data_name, Paras
    #     )

    else:
        transform = None
        print(f"The data_name is error!")
        assert False

    return train_dataset, test_dataset, transform


def get_dataloader(data_name, train_dataset, test_dataset, Paras):
    ParametersHub.set_seed(Paras["seed"])
    g = torch.Generator()
    g.manual_seed(Paras["seed"])
    
    train_loader = Data.DataLoader(
            dataset=train_dataset,
            shuffle=True,
            batch_size=Paras["batch_size"],
            generator=g,
            num_workers=4,
        )
    
    test_loader = Data.DataLoader(
            dataset=test_dataset,
            shuffle=False,
            batch_size=Paras["batch_size"],
            generator=g,
            num_workers=4,
        )
    
    return train_loader, test_loader

def chosen_optimizer(optimizer_name, model, hyperparams, Paras):
    if optimizer_name == "SGD":
        optimizer = torch.optim.SGD(model.parameters(), lr=hyperparams["alpha"])

    elif optimizer_name == "ADAM":
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=hyperparams["alpha"],
            betas=(hyperparams["beta1"], hyperparams["beta2"]),
            eps=hyperparams["epsilon"],
        )

    else:
        raise NotImplementedError(f"{optimizer_name} is not supported.")

    return optimizer

def load_model_dataloader(base_model_fun, initial_state_dict, data_name, train_dataset, test_dataset, Paras):
    ParametersHub.set_seed(Paras["seed"])
    model = base_model_fun()
    model.load_state_dict(initial_state_dict)
    model.to(Paras["device"])
    train_loader, test_loader = TrainingHub.get_dataloader(data_name, train_dataset, test_dataset, Paras)

    return model, train_loader, test_loader

def train(train_loader, optimizer_name, optimizer, model, loss_fn, Paras):
    metrics = ParametersHub.metrics()
    for epoch in range(Paras["epochs"]):
        for index, (X, Y) in enumerate(train_loader):
            X, Y = X.to(Paras["device"]), Y.to(Paras["device"])

            if optimizer_name in ["SGD", "ADAM"]:
                optimizer.zero_grad()
                loss = Evaluate_Metrics.compute_epoch_loss(X, Y, model, loss_fn, Paras)
                loss.backward()
                optimizer.step()

            elif optimizer_name in [
                "Bundle",
                "SBPM",
            ]:
                def closure():
                    optimizer.zero_grad()
                    loss = Evaluate_Metrics.compute_epoch_loss(X, Y, model, loss_fn, Paras)
                    loss.backward()
                    return loss

                loss = optimizer.step(closure)

            else:
                loss = 0
                raise NotImplementedError(f"{optimizer_name} is not supported.")
            
            if index == 0 and epoch == 0:
                metrics["iter_loss"].append(loss.item())
                metrics["epoch_loss"].append(loss.item())
                with torch.no_grad():
                    g_k = parameters_to_vector(
                        [
                            p.grad if p.grad is not None else torch.zeros_like(p)
                            for p in model.parameters()
                        ]
                    )
                    metrics["grad_norm"].append(torch.norm(g_k, p=2).detach().cpu().item())
        
            metrics["per_epoch_loss"].append(loss.item())
        metrics["epoch_loss"].append(np.mean(metrics["per_epoch_loss"]).item())

        
        
        
    