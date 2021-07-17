import torch
import numpy as np
from sklearn.metrics import confusion_matrix

import torch
torch.cuda.empty_cache()

def get_user_input(args):
    if torch.cuda.is_available():
        args.device = 'cuda:' + input('Input GPU ID: ')
    else:
        args.device = 'cpu'

    dataset_code = {'r': 'redd_lf', 'u': 'uk_dale', 't': 'teeavs'}
    args.dataset_code = dataset_code[input(
        'Input r for REDD, u for UK_DALE, t for TEEAVS: ')]

    if args.dataset_code == 'redd_lf':
        app_dict = {
            'r': ['refrigerator'],
            'w': ['washer_dryer'],
            'm': ['microwave'],
            'd': ['dishwaser'],
        }
        args.appliance_names = app_dict[input(
            'Input r, w, m or d for target appliance: ')]

    elif args.dataset_code == 'uk_dale':
        app_dict = {
            'k': ['kettle'],
            'f': ['fridge'],
            'w': ['washing_machine'],
            'm': ['microwave'],
            'd': ['dishwasher'],
        }
        args.appliance_names = app_dict[input(
            'Input k, f, w, m or d for target appliance: ')]

    elif args.dataset_code == 'teeavs':
        app_dict = {
            't': ['tv'],
            'd': ['dolap'],
            'l': ['lamba'],
            'c': ['camasir'],
        }
        args.appliance_names = app_dict[input(
            'Girdi olarak t, d, l ya da c hedef cihazlar icin giriniz: ')]

    args.num_epochs = int(input('Input training epochs: '))


def set_template(args):
    args.output_size = len(args.appliance_names)
    if args.dataset_code == 'redd_lf':
        args.window_stride = 120
        args.house_indicies = [1, 2, 3, 4, 5, 6]

        args.cutoff = {
            'aggregate': 6000,
            'refrigerator': 400,
            'washer_dryer': 3500,
            'microwave': 1800,
            'dishwaser': 1200
        }

        args.threshold = {
            'refrigerator': 50,
            'washer_dryer': 20,
            'microwave': 200,
            'dishwaser': 10
        }

        args.min_on = {
            'refrigerator': 10,
            'washer_dryer': 300,
            'microwave': 2,
            'dishwaser': 300
        }

        args.min_off = {
            'refrigerator': 2,
            'washer_dryer': 26,
            'microwave': 5,
            'dishwaser': 300
        }

        args.c0 = {
            'refrigerator': 1e-6,
            'washer_dryer': 0.001,
            'microwave': 1.,
            'dishwaser': 1.
        }

    elif args.dataset_code == 'uk_dale':
        args.window_stride = 240
        args.house_indicies = [1, 2, 3, 4, 5]

        args.cutoff = {
            'aggregate': 6000,
            'kettle': 3100,
            'fridge': 300,
            'washing_machine': 2500,
            'microwave': 3000,
            'dishwasher': 2500
        }

        args.threshold = {
            'kettle': 2000,
            'fridge': 50,
            'washing_machine': 20,
            'microwave': 200,
            'dishwasher': 10
        }

        args.min_on = {
            'kettle': 2,
            'fridge': 10,
            'washing_machine': 300,
            'microwave': 2,
            'dishwasher': 300
        }

        args.min_off = {
            'kettle': 0,
            'fridge': 2,
            'washing_machine': 26,
            'microwave': 5,
            'dishwasher': 300
        }

        args.c0 = {
            'kettle': 1.,
            'fridge': 1e-6,
            'washing_machine': 0.01,
            'microwave': 1.,
            'dishwasher': 1.
        }

    elif args.dataset_code == 'teeavs':
        args.window_stride = 240
        args.house_indicies = [1, 2]

        args.cutoff = {
            'aggregate': 6000,
            'tv': 50,
            'dolap': 400,
            'lamba': 100,
            'camasir': 300
        }

        args.threshold = {
            'tv': 10,
            'dolap': 20,
            'lamba': 10,
            'camasir': 20
        }

        args.min_on = {
            'tv': 2,
            'dolap': 100,
            'lamba': 2,
            'camasir': 200
        }

        args.min_off = {
            'tv': 2,
            'dolap': 10,
            'lamba': 2,
            'camasir': 20
        }

        args.c0 = {
            'tv': 0.001,
            'dolap': 1e-6,
            'lamba': 0.001,
            'camasir': 0.01
        }

    opt_flg = 'adam'

    if opt_flg == 'adam':

        args.optimizer = 'adam'
        args.lr = 1e-3
        args.enable_lr_schedule = False
        args.batch_size = 64

    if opt_flg == 'sgd':

        args.optimizer = 'sgd'
        args.lr = 0.001
        args.enable_lr_schedule = False
        args.batch_size = 128
        args.momentum = 0

    if opt_flg == 'adax':

        args.optimizer = 'adax'
        args.lr = 1e-3
        args.enable_lr_schedule = False
        args.batch_size = 128
        args.weight_decay = 5e-4

    if opt_flg == 'adaxw':

        args.optimizer = 'adaxw'
        args.lr = 0.005
        args.enable_lr_schedule = False
        args.batch_size = 128
        args.weight_decay = 5e-2

def acc_precision_recall_f1_score(pred, status):
    assert pred.shape == status.shape

    pred = pred.reshape(-1, pred.shape[-1])
    status = status.reshape(-1, status.shape[-1])
    accs, precisions, recalls, f1_scores = [], [], [], []

    for i in range(status.shape[-1]):
        tn, fp, fn, tp = confusion_matrix(status[:, i], pred[:, i], labels=[
                                          0, 1]).ravel()
        acc = (tn + tp) / (tn + fp + fn + tp)
        precision = tp / np.max((tp + fp, 1e-9))
        recall = tp / np.max((tp + fn, 1e-9))
        f1_score = 2 * (precision * recall) / \
            np.max((precision + recall, 1e-9))

        accs.append(acc)
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1_score)

    return np.array(accs), np.array(precisions), np.array(recalls), np.array(f1_scores)


def relative_absolute_error(pred, label):
    assert pred.shape == label.shape

    pred = pred.reshape(-1, pred.shape[-1])
    label = label.reshape(-1, label.shape[-1])
    temp = np.full(label.shape, 1e-9)
    relative, absolute, sum_err = [], [], []

    for i in range(label.shape[-1]):
        relative_error = np.mean(np.nan_to_num(np.abs(label[:, i] - pred[:, i]) / np.max(
            (label[:, i], pred[:, i], temp[:, i]), axis=0)))
        absolute_error = np.mean(np.abs(label[:, i] - pred[:, i]))

        relative.append(relative_error)
        absolute.append(absolute_error)

    return np.array(relative), np.array(absolute)
