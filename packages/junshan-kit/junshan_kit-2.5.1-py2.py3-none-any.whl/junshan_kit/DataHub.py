import torchvision, torch
import torchvision.transforms as transforms
import pandas as pd

from junshan_kit import DataSets, DataProcessor











def Adult_Income_Prediction(Paras):

    df = DataSets.adult_income_prediction() 
    transform = {
        "train_size": 0.7,
        "normalization": True
    }
    label_col='income'

    train_dataset, test_dataset, transform = DataProcessor.Pandas_TO_Torch(df, label_col).to_torch(transform, Paras)

    return train_dataset, test_dataset, transform


def Credit_Card_Fraud_Detection(Paras):
    df = DataSets.credit_card_fraud_detection()
    transform = {
        "train_size": 0.7,
        "normalization": True
    }
    label_col='Class'

    train_dataset, test_dataset, transform = DataProcessor.Pandas_TO_Torch(df, label_col).to_torch(transform, Paras)

    return train_dataset, test_dataset, transform



def MNIST(Paras, model_name):
    """
    Load the MNIST dataset and return both the training and test sets,
    along with the transformation applied (ToTensor).
    """
    transform = torchvision.transforms.ToTensor()

    train_dataset = torchvision.datasets.MNIST(
        root='./exp_data/MNIST',
        train=True,
        download=True,
        transform=transform
    )

    test_dataset = torchvision.datasets.MNIST(
        root='./exp_data/MNIST',
        train=False,
        download=True,
        transform=transform
    )

    if Paras["model_type"][model_name] == "binary":

        train_mask = (train_dataset.targets == 0) | (train_dataset.targets == 1)
        test_mask = (test_dataset.targets == 0) | (test_dataset.targets == 1)

        train_indices = torch.nonzero(train_mask, as_tuple=True)[0]
        test_indices = torch.nonzero(test_mask, as_tuple=True)[0]

        train_dataset = torch.utils.data.Subset(train_dataset, train_indices.tolist())
        test_dataset = torch.utils.data.Subset(test_dataset, test_indices.tolist())

    return train_dataset, test_dataset, transform


def CIFAR100(Paras, model_name):
    """
    Load the CIFAR-100 dataset with standard normalization and return both
    the training and test sets, along with the transformation applied.
    """
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5071, 0.4867, 0.4408],   
                            std=[0.2675, 0.2565, 0.2761])     
    ])

    train_dataset = torchvision.datasets.CIFAR100(
        root='./exp_data/CIFAR100',
        train=True,
        download=True,
        transform=transform
    )

    test_dataset = torchvision.datasets.CIFAR100(
        root='./exp_data/CIFAR100',
        train=False,
        download=True,
        transform=transform
    )
    if Paras["model_type"][model_name] == "binary":
        train_mask = (torch.tensor(train_dataset.targets) == 0) | (torch.tensor(train_dataset.targets) == 1)
        test_mask = (torch.tensor(test_dataset.targets) == 0) | (torch.tensor(test_dataset.targets) == 1)

        train_indices = torch.nonzero(train_mask, as_tuple=True)[0]
        test_indices = torch.nonzero(test_mask, as_tuple=True)[0]

        train_dataset = torch.utils.data.Subset(train_dataset, train_indices.tolist())
        test_dataset = torch.utils.data.Subset(test_dataset, test_indices.tolist())

    return train_dataset, test_dataset, transform