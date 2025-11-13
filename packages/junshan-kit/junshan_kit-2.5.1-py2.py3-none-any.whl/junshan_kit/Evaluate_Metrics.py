import torch
from torch.nn.utils import parameters_to_vector
import torch.nn.functional as F

def compute_epoch_loss(X, y, model, loss_fn, Paras):
    pred = model(X)
    _, c = pred.shape

    if c == 1:
        # Logistic Regression with L2 (binary)
        if isinstance(loss_fn, torch.nn.BCEWithLogitsLoss):
            pred = pred.view(-1).float()
            loss = loss_fn(pred, y.float())
            if Paras["model_name"] == "LogRegressionBinaryL2":
                x = parameters_to_vector(model.parameters())
                lam = Paras["lambda"]
                loss = loss + 0.5 * lam * torch.norm(x, p=2) ** 2

        else:
            assert False

    else:
        # Least Square (mutil)
        if isinstance(loss_fn, torch.nn.MSELoss):
            # loss
            y_onehot = F.one_hot(y.long(), num_classes=c).float()
            pred_prob = torch.softmax(pred, dim=1)
            loss = 0.5 * loss_fn(pred_prob, y_onehot) * float(c)

        elif isinstance(loss_fn, torch.nn.CrossEntropyLoss):
            # loss
            loss = loss_fn(pred, y.long())

        else:
            print(
                f"\033[34m **** isinstance(loss_fn, torch.nn.MSELoss)? {loss_fn} **** \033[0m"
            )
            assert False

    return loss