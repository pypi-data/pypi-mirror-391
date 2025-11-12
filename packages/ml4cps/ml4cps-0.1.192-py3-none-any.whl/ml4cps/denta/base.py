"""
    The module implements the novel DENTA algorithm for the learning of hybrid automata from data.

    Author:
    Nemanja Hranisavljevic, hranisan@hsu-hh.de, nemanja@ai4cps.com
"""

import pprint
import time
import pandas as pd
from plotly import graph_objects as go
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import f1_score, roc_auc_score
from datetime import timedelta
from ml4cps import automata, tools, vis
from ml4cps.automata import learn as automata_learn
from plotly.subplots import make_subplots
import mlflow
import torch
import torch.nn as nn
import torch.nn.functional as F


loss_bce_pp = nn.BCELoss(reduction='none')
loss_mse_pp = nn.MSELoss(reduction='none')
loss_bce = nn.BCELoss()
loss_mse = nn.MSELoss()


class DentaEbm(nn.Module):
    """
        DentaEbm: Deep Energy-Based Model for Learning Latent Representations.

        This class implements an energy-based neural network designed to learn
        latent encodings of input data and reconstruct input signals via
        an encoder-decoder architecture. It supports anomaly detection,
        latent discretization, sparsity constraints, and integrates with MLflow for logging.

        The model follows a structure similar to deep belief networks or restricted Boltzmann machines,
        with extensions for denoising, score matching, and anomaly detection tasks.

        Attributes:
            _discretization_layers (nn.Sequential): Encoder neural network mapping input → latent space.
            _decoder (nn.Sequential): Decoder neural network mapping latent space → reconstructed input.
            log_sigma_x (nn.Parameter or torch.Tensor): Log of standard deviation parameter(s) for input normalization.
            threshold (float or None): Threshold used for anomaly detection.
            learning_curve (list): Stores training metrics per epoch.
            valid_curve (list): Stores validation metrics per epoch.
            num_epoch (int): Total number of epochs trained.
            log_mlflow (bool): Whether to log parameters and metrics to MLflow.

        Args:
            num_y (int): Number of input variables (visible units).
            num_h (int): Number of hidden latent units.
            num_d (int, optional): Number of derivative input features (default=0).
            num_b (int, optional): Number of bias input features (default=0).
            first_hidden_size (int, optional): Number of units in the first hidden layer (default: auto-calculated).
            sigma (float, optional): Standard deviation for input normalization (default=1.0).
            sigma_learnable (bool, optional): If True, allows sigma to be learned as a parameter (default=False).
            sparsity_weight (float, optional): Weight for sparsity regularization (default=0.01).
            transience (bool, optional): Whether to include transience constraint (default=True).
            transience_weight (float, optional): Weight for transience regularization (default=0).
            num_sigm_layers (int, optional): Number of hidden layers in encoder/decoder (default=1).
            split_on_quantile (float, optional): Quantile threshold for splitting signals (default=1).
            window_size (int, optional): Window size for temporal input processing (default=1).
            window_step (int, optional): Step size for sliding window (default=1).
            sparsity_target (float, optional): Target activation sparsity level (default=0.1).
            use_derivatives (int or list, optional): If non-zero, includes derivatives as input features.
            device (str, optional): Device identifier ('cpu' or 'cuda') for model tensors (default='cpu').
            log_mlflow (bool, optional): Whether to enable MLflow logging (default=False).
            *args: Additional positional arguments passed to `nn.Module`.
            **kwargs: Additional keyword arguments passed to `nn.Module`.

        Example:
            model = DentaEbm(num_y=4, num_h=8, num_sigm_layers=2, sigma_learnable=True)
        """
    def __init__(self, num_y, num_h, num_d=0, num_b=0, first_hidden_size=None, sigma=1., sigma_learnable=False,
                 sparsity_weight=0.01, transience=True, transience_weight=0, num_sigm_layers=1, split_on_quantile=1,
                 window_size=1, window_step=1, sparsity_target=0.1, use_derivatives=0, device='cpu', log_mlflow=False,
                 n_factors=10, replicate_h=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.split_on_quantile = split_on_quantile
        self.sparsity_weight = sparsity_weight
        self.sparsity_target = sparsity_target
        self.transience = transience
        self.transience_weight = transience_weight
        self.use_derivatives = np.asarray(use_derivatives).reshape(-1).tolist()
        self.window_size = window_size
        self.window_step = window_step
        self.device = device
        self._mean = None
        self._std = None
        self.num_b = num_b
        self.num_d = num_d
        self.num_y = num_y
        self.replicate_h = replicate_h

        if use_derivatives:
            input_size = num_y * len(self.use_derivatives)
        else:
            input_size = num_y

        if sigma_learnable:
            self.is_sigma_learnable = True
            self.log_sigma_x = nn.Parameter(np.log(sigma) * torch.ones(1, input_size, requires_grad=True)).to(device)
        else:
            self.is_sigma_learnable = False
            self.log_sigma_x = np.log(sigma) * torch.ones(1, input_size, requires_grad=False).to(device)

        if self.window_size > 1:
            input_size = input_size * self.window_size

        self._discretization_layers = nn.Sequential().to(device)
        self._decoder_biases = nn.ParameterList().to(device)
        # self._decoder = nn.Sequential().to(device)

        self.timed_model = None # FactorizedThreeWayLayer(num_h, num_h, round(num_h * 1.1), n_factors).to(device)

        enc_layers = []
        if first_hidden_size is None:
            if num_sigm_layers == 1:
                first_hidden_size = num_h
            else:
                first_hidden_size = int(input_size * 1.5)

        layer_sizes = ([input_size] +
                       np.round(np.linspace(first_hidden_size, num_h, num_sigm_layers)).astype(int).tolist())
        for i in range(num_sigm_layers):
            enc_layers.append(nn.Linear(layer_sizes[i], layer_sizes[i+1], device=device))
            self._discretization_layers.add_module(f'linear_v2h{i}', enc_layers[i])
            self._discretization_layers.add_module(f'sigmoid_v2h{i}', nn.Sigmoid())
            self._decoder_biases.append(nn.Parameter(torch.zeros(layer_sizes[i], device=device)))

        # dec_layers = []
        # layer_sizes.reverse()
        # for i in range(num_sigm_layers):
        #     dec_lin = nn.Linear(layer_sizes[i], layer_sizes[i+1], device=device)
        #     dec_lin.weight = nn.Parameter(enc_layers[-i-1].weight.transpose(0, 1))
        #     dec_layers.append(dec_lin)
        #     self._decoder.add_module(f'linear_h2v{i}', dec_lin)
        #     if i != num_sigm_layers - 1:
        #         self._decoder.add_module(f'sigmoid_h2v{i}', nn.Sigmoid())


        self.threshold = None
        self.learning_curve = []
        self.valid_curve = []
        self.num_epoch = 0

        if log_mlflow:
            mlflow.log_param("model", "denta")
            mlflow.log_param("num_signals", num_y)
            mlflow.log_param("input_size", input_size)
            mlflow.log_param("num_sigm_layers", num_sigm_layers)
            mlflow.log_param("num_hidden_units", num_h)
            mlflow.log_param("sparsity_target", self.sparsity_target)
            mlflow.log_param("sparsity_weight", self.sparsity_weight)
            mlflow.log_param("sigma", sigma)
            mlflow.log_param("use_derivatives", self.use_derivatives)
            mlflow.log_param("window_size", self.window_size)
            mlflow.log_param("first_hidden_size", first_hidden_size)
            mlflow.log_param('transience_weight', transience_weight)
            mlflow.log_param('replicate_h', replicate_h)

    def encode(self, x, context, rounding=False, x_level=0, h_level=None):
        """
        Encode input data into latent representations.

        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, features).
            rounding (bool): If True, rounds the latent output (default=False).
            x_level (int): Unused (placeholder for multi-level encoding).
            h_level (int or None): If None, uses default hidden layer depth.

        Returns:
            torch.Tensor: Latent representation tensor.
        """
        if h_level is None:
            h_level = self.num_hidden_layers()
        if type(x) is list:
            return [self.encode(xx, rounding=rounding) for xx in x]
        else:
            if x_level == 0:
                sigma_x = torch.exp(self.log_sigma_x)
                x = torch.div(x, sigma_x)
                x = torch.flatten(x, start_dim=-2)

            h = self._discretization_layers[x_level * 2:h_level * 2](x)

            if h_level > self.num_hidden_layers():
                context = self._discretization_layers[:h_level * 2](context)
                context = torch.div(context, sigma_x)
                context = torch.flatten(context, start_dim=-2)
                h = self.timed_model.forward(h, context)
            if rounding:
                h = torch.round(h)
            return h, context

    def decode(self, h, z, x_level=0, h_level=None):
        if h_level is None:
            h_level = self.num_hidden_layers()
        if h_level > self.num_hidden_layers():
            self.timed_model.decode(h, z)

        y = h
        for l in range(h_level, x_level, -1):
            W = self._discretization_layers[(l-1)*2].weight
            if l == 1 and self.replicate_h:
                y = F.linear(y, self.replicate_h * W.t(), self._decoder_biases[l-1])
            else:
                y = F.linear(y, W.t(), self._decoder_biases[l - 1])
            if l != 1:
                y = F.sigmoid(y)

        # y = self._decoder[2 * (self.num_hidden_layers() - h_level):2 * (self.num_hidden_layers() - x_level)](h)
        if x_level == 0:
            sigma_x = torch.exp(self.log_sigma_x)
            y = torch.mul(y.reshape(y.shape[0], -1, self.num_y), sigma_x)
        return y

    def prepare_data(self, x):
        windowed = tools.window(x, 2, 1)
        context = windowed[:, :, 0:windowed.shape[-2]//2, :].detach()
        data = windowed[:, :, windowed.shape[-2]//2:, :]
        return data, context
        # x = tools.extend_derivative(x, self.use_derivatives)
        # if update_mean_std:
        #     x, self._mean, self._std = tools.standardize(x)
        # else:
        #     x = tools.standardize(x, self._mean, self._std)
        # x = tools.window(x, self.window_size, self.window_step)

    def predict_discrete_mode(self, data, context):
        if type(data) is list:
            return [self.predict_discrete_mode(d) for d in data]
        else:
            # if prepare_data:
            #     data = self.prepare_data(data)
            h, z = self.encode(data, context, rounding=True)
            h = self.binary_vector_to_mode(h)
            return np.concatenate([np.full((self.window_size-1,), np.nan), h], axis=0)

    def binary_vector_to_mode(self, h):
        if type(h) is list:
            return [self.binary_vector_to_mode(x) for x in h]
        else:
            df = pd.DataFrame(h.cpu().detach().numpy())
            df = df.astype(int).astype(str)
            return df.agg(''.join, axis=1).to_numpy()

    def forward(self, x):
        x = self.prepare_data(x)
        return self.decode(*self.encode(x))

    # def energy(self, x, h):
    #     vis = torch.sum(torch.div(torch.square(x - self.bx), (2 * torch.square(torch.exp(self.log_sigma_x)))), dim=1)
    #     hid = torch.matmul(h, self._discretization_layers[-2].bias)
    #     xWh = torch.sum(torch.matmul(x, self._discretization_layers[-2].weight.T) * h, dim=1)
    #     return vis - hid - xWh

    def free_energy(self, x, context, level=1):
        if level == 1:
            bx = self._decoder_biases[0]
            bx = bx.reshape(-1, self.num_y)
            vis = torch.sum(torch.div(torch.square(x - bx), (2 * torch.square(torch.exp(self.log_sigma_x)))), dim=[1,2])
            x = torch.div(x, torch.exp(self.log_sigma_x))
            wx_b, _ = self.encode(x, context, h_level=level)
            fec = F.softplus(wx_b).sum(dim=1)
            return vis - fec
        else:
            bx = self._decoder_biases[level-1]
            wx_b, _ = self.encode(x, context, x_level=level-1, h_level=level)
            vis = -torch.sum(x * bx, dim=1)
            fec = F.softplus(wx_b).sum(dim=1)
            return vis - fec


    def score(self, x, sigma=None):
        x = x.requires_grad_()
        logp = -self.free_energy_components(x).sum()
        grad = torch.autograd.grad(logp, x, create_graph=True)[0] # Create graph True to allow later backprop
        return grad

    def encode_ordinal(self, x, columns, order=None):
        return tools.encode_ordinal(x, columns, order)

    def encode_nominal(self, x, columns=None):
        return tools.encode_nominal(x, columns)

    def dsm_loss(self, x, v, sigma=0.1):
        """DSM loss from
        A Connection Between Score Matching
            and Denoising Autoencoders
        The loss is computed as
        x_ = x + v   # noisy samples
        s = -dE(x_)/dx_
        loss = 1/2*||s + (x-x_)/sigma^2||^2
        Args:
            x (torch.Tensor): input samples
            v (torch.Tensor): sampled noises
            sigma (float, optional): noise scale. Defaults to 0.1.

        Returns:
            DSM loss
        """
        x = x.requires_grad_()
        v = v * sigma
        x_ = x + v
        s = self.score(x_)
        loss = torch.norm(s + v / (sigma ** 2), dim=-1) ** 2
        loss = loss.mean() / 2.
        return loss

    # def num_y(self):
    #     l = self._discretization_layers[0]
    #     return l.in_features

    def num_h(self):
        l = self._discretization_layers[-2]
        return l.out_features

    def num_hidden_layers(self):
        L = len(self._discretization_layers) // 2
        if self.timed_model is not None:
            L += 1
        return L

    # def sample_h(self, x):
    #     p_h_given_v = self.encode(x)
    #     return p_h_given_v, torch.bernoulli(p_h_given_v)
    def sample_h(self, h):
        return torch.bernoulli(h)

    # def sample_x(self, h):
    #     p_v_given_h = self.decode(h)
    #     return p_v_given_h, torch.normal(p_v_given_h, std=torch.exp(self.log_sigma_x))
    def sample_x(self, x, level):
        if level==0:
            return torch.normal(x, std=torch.exp(self.log_sigma_x))
        else:
            return torch.bernoulli(x)

    def generate(self, num_examples, num_steps=10):
        x = torch.randn([num_examples, self.num_y()])
        for k in range(num_steps):
            ph, h = self.sample_h(x)
            px, x = self.sample_x(h)
        return x

    def contrastive_divergence(self, v0, vk, context, level=1):
        # return self.free_energy(v0) - self.free_energy(vk)
        # sparsity_penalty = self.sparsity_weight * torch.sum((self.sparsity_target - hk) ** 2)
        return self.free_energy(v0, context, level=level) - self.free_energy(vk, context, level=level)

    def recon(self, v, context, round=False, x_level=0, h_level=None):
        # y (batch_size, 2 consecutive, 2 for past and future, window_size, num_y)
        # if self.input_layer == 'dsebm':
        #     v = v.requires_grad_()
        #     logp = -self.free_energy_components(v).sum()
        #     return torch.autograd.grad(logp, v, create_graph=True)[0]
        if h_level is None:
            h_level = self.num_hidden_layers()
        h, z = self.encode(v, context, x_level=x_level, h_level=h_level)
        if round:
            h = torch.round(h)
        r = self.decode(h, z, x_level, h_level)
        return r, h

    def pretrain_layers(self, train_data, valid_data, **kwargs):
        for layer in range(1, self.num_hidden_layers() + 1): # +1 for three way RBM on top
            print('Training layer {}'.format(layer))
            self.train_rbm(train_data, valid_data, level=layer, **kwargs)

    def train_rbm(self, train_data, valid_data, level=1, learning_rule='cd', min_epoch=0, max_epoch=10, weight_decay=0.,
                  batch_size=128, num_k=1, verbose=True, early_stopping=False, early_stopping_patience=3,
                  momentum=0.9, use_probability_last_x_update=True, lr=0.001, log_mlflow=False):
        """
        Trainin a layer of the network like an RBM. In case of the first layer it is a Gaussian binary RBM, in case of
        other layers it is a binary RBM.

        :param train_data:
        :param valid_data:
        :param level:
        :param learning_rule:
        :param min_epoch:
        :param max_epoch:
        :param weight_decay:
        :param batch_size:
        :param momentum:
        :param num_k:
        :param verbose:
        :param early_stopping:
        :param early_stopping_patience:
        :param use_probability_last_x_update:
        :param lr:
        :param log_mlflow:
        :return:
        """
        if log_mlflow:
            mlflow.log_param("min_epoch" + f"/{level}", min_epoch)
            mlflow.log_param("max_epoch" + f"/{level}", max_epoch)
            mlflow.log_param("batch_size" + f"/{level}", batch_size)
            mlflow.log_param("momentum" + f"/{level}", momentum)
            mlflow.log_param("weight_decay" + f"/{level}", weight_decay)
            mlflow.log_param("early_stopping_patience" + f"/{level}", early_stopping_patience)
            mlflow.log_param("early_stopping" + f"/{level}", early_stopping)

        # if valid_data is not None:
        #     self.valid_curve.append(self._get_progress_rbm(valid_data, level=level))
        #
        # self.learning_curve.append(self._get_progress_rbm(train_data, level=level))
        self.learning_curve = []
        self.valid_curve = []

        # Because persistence is encouraged, we want to get data windows in pairs of two consecutive windows,
        # then we can compare them and use difference in the loss.
        train_data.pairs = True
        valid_data.pairs = True

        # In principle shuffle is always True, and the
        data_loader = DataLoader(dataset=train_data, batch_size=batch_size, shuffle=True)

        # Typical for RBMs.
        opt = torch.optim.SGD(self.parameters(), lr=lr, weight_decay=weight_decay, momentum=momentum)

        # Tracking duration of the learning.
        t_start = time.time()

        # Epoch counted starting from 1.
        for epoch in range(1, max_epoch + 1):
            # Data loader returns two consecutive windows, while each window is divided in context and visible units.
            for i, (past_context, past_x, context, x0) in enumerate(data_loader):
                # If we are learning any other RBM then the level 1 (lowest one) we need to propagate data thrugh the
                # layers below to get the input for this RBM training.
                x0level0 = None
                x0 = x0.to(self.device)
                past_x = past_x.to(self.device)
                if level > 1:
                    with torch.no_grad():
                        x0level0 = x0
                        x0, _ = self.encode(x0, context, h_level=level-1)
                        past_x, _ = self.encode(past_x, past_context, h_level=level-1)
                xk = x0
                # Contrastive divergence
                if learning_rule == 'cd':
                    # Sampling is done without tracking the gradients
                    with torch.no_grad():
                        eh0, _ = self.encode(x0, None, x_level=level-1, h_level=level)
                        h0 = self.sample_h(eh0)
                        hk = h0
                        # K Gibbs samples
                        for k in range(num_k):
                            exk = self.decode(hk, None, x_level=level-1, h_level=level)
                            xk = self.sample_x(exk, level=level-1)
                            ehk, _ = self.encode(xk, context, x_level=level-1, h_level=level)
                            hk = self.sample_h(ehk)

                    # Determines if we use the probabilties instead of sampled values in the update of CD
                    if use_probability_last_x_update:
                        cd = torch.mean(self.contrastive_divergence(x0, exk, context, level=level))
                    else:
                        cd = torch.mean(self.contrastive_divergence(x0, xk, context, level=level))
                    opt.zero_grad()
                    cd.backward()
                    opt.step()
                elif learning_rule == 'sm':
                    r = self.recon(xk)
                    loss = (r - x0).pow(2).sum()
                    opt.zero_grad()
                    loss.backward()
                    opt.step()
                elif learning_rule == 'dsm':
                    x0noise = torch.normal(torch.zeros_like(x0))
                    loss = self.dsm_loss(x0, x0noise)
                    opt.zero_grad()
                    loss.backward()
                    opt.step()

            with torch.no_grad():
                progress = self._get_progress_rbm(x0, context, x0level0, context, x_level=level-1, h_level=level)
                if verbose:
                    print(f'\n############### Epoch {epoch} ###############')
                    print('Train: ')
                    pprint.pp(progress)
                self.learning_curve.append(progress)
            if valid_data is not None:
                with torch.no_grad():
                    past_source, past_dest, source, dest = valid_data.get_random_sample()
                    dest = dest.to(self.device)
                    source = source.to(self.device)
                    dest_level_0 = None
                    source_level_0 = None
                    if level > 1:
                        dest_level_0 = dest
                        source_level_0 = source
                        dest, source = self.encode(dest, source, x_level=0, h_level=level-1)
                        dest = dest.to(self.device)
                        source = source.to(self.device)

                    progress = self._get_progress_rbm(dest, source, dest_level_0, source_level_0,
                                                      x_level=level-1, h_level=level)
                    self.valid_curve.append(progress)
                if verbose:
                    print('Valid: ')
                    pprint.pp(progress)

                if early_stopping and epoch > min_epoch and epoch > early_stopping_patience:
                    valid_metrics = np.array([v['MSE'] for v in self.valid_curve[-early_stopping_patience - 1:]])
                    if np.all(valid_metrics[1:] > valid_metrics[0]):
                        print('Early stop after valid metrics: ', valid_metrics)
                        break

            if self.is_sigma_learnable:
                print(torch.exp(self.log_sigma_x))

        self.eval()
        self.num_epoch = epoch

        if log_mlflow:
            with torch.no_grad():
                mlflow.log_metrics(self.valid_curve[-1])
                mlflow.log_metric("num_epoch", self.num_epoch)
                run_id = mlflow.active_run().info.run_id
                mlflow.log_figure(self.plot_learning_curve(), f'figures/learning_curve_denta_rbm_{level}_{run_id}.html')

                past_source, past_dest, source, dest = valid_data.get_random_sample()
                mlflow.log_figure(self.plot_activation_probabilities(dest, source),
                                  f'figures/activations_hist_denta_rbm_{level}_{run_id}.html')
                mlflow.log_figure(self.plot_frequency_of_latent_combinations(dest, source),
                                  f'figures/latent_frequencies_denta_rbm_{level}_{run_id}.html')



        print('Training finished after ', timedelta(seconds=time.time() - t_start))

    def mse(self, x, r, per_point=False):
        if per_point:
            return loss_mse_pp(x, r)
        else:
            return loss_mse(x, r)

    def bce(self, x, r, per_point=False):
        if per_point:
            return loss_bce_pp(x, r)
        else:
            return loss_bce(x, r)

    def transience_bce(self, past_h, h, per_point=False):
        if per_point:
            return loss_bce_pp(past_h, h)
        else:
            return loss_bce(past_h, h)


    def _get_progress_learn(self, past_source, past_dest, source, dest):
        with torch.no_grad():
            past_source = past_source[:,:,:self.num_y].to(self.device)
            past_dest = past_dest[:,:,:self.num_y].to(self.device)

            source = source[:, :, :self.num_y].to(self.device)
            dest = dest[:, :, :self.num_y].to(self.device)

            past_r, past_h = self.recon(past_source, past_dest)
            r, h = self.recon(source, dest)

        progress = dict(MSE=self.mse(dest, r).item(),
                        Transience=self.transience_bce(past_h, h).item(),
                        Sparsity=self.sparsity(h).item())
        if False:
            valid_energy = torch.mean(self.free_energy(valid_data)).item()
            progress['Energy'] = valid_energy
        return progress

    def _get_progress_rbm(self, d, context, d_vis, context_vis, x_level, h_level):
        r, h = self.recon(d, context, x_level=h_level-1, h_level=h_level)
        e = self.free_energy(d, context, level=h_level)
        if x_level == 0:
            progress = dict(MSE=self.mse(d, r).item(),
                            Sparsity=self.sparsity(h).item(),
                            Energy=torch.mean(e).item())
        else:
            r_vis, _ = self.recon(d_vis, context_vis, x_level=0, h_level=h_level)
            progress = dict(BCE=self.bce(d, r).item(),
                            MSEvis=self.mse(d_vis, r_vis).item(),
                            Sparsity=self.sparsity(h).item(),
                            Energy=torch.mean(e).item())
        return progress

    def _is_set_mean_std(self):
        return self._std is not None and self._mean is not None

    def finetune(self, train_data, valid_data, max_epoch=10, min_epoch=0, estimate_switches_every=5, lr=0.01,
                            weight_decay=0., batch_size=128, shuffle=True, verbose=True, early_stopping=False,
                            early_stopping_patience=3, round_latent_during_learning=False, log_mlflow=False):
        if log_mlflow:
            mlflow.log_param("min_epoch_ft", min_epoch)
            mlflow.log_param("max_epoch_ft", max_epoch)
            mlflow.log_param("batch_size_ft", batch_size)
            mlflow.log_param("shuffle_ft", shuffle)
            mlflow.log_param("weight_decay_ft", weight_decay)
            mlflow.log_param("early_stopping_patience_ft", early_stopping_patience)
            mlflow.log_param("early_stopping_ft", early_stopping)
            mlflow.log_param('round_latent_during_learning_ft', round_latent_during_learning)
            mlflow.log_param('estimate_switches_every_ft', estimate_switches_every)

        train_data.pairs = True
        valid_data.pairs = True
        if valid_data is not None:
            past_source, past_dest, source, dest = valid_data.get_random_sample()
            self.valid_curve.append(self._get_progress_learn(past_source, past_dest, source, dest))

        past_source, past_dest, source, dest = train_data.get_random_sample()
        self.learning_curve.append(self._get_progress_learn(past_source, past_dest, source, dest))

        data_loader = DataLoader(dataset=train_data, batch_size=batch_size, shuffle=shuffle, num_workers=1,
                                 pin_memory=True)

        opt = torch.optim.Adam(self.parameters(), lr=lr, weight_decay=weight_decay)
        # opt = torch.optim.RMSprop(self.parameters(), weight_decay=weight_decay, lr=lr)
        t_start = time.time()
        epoch = 0
        for epoch in range(1, max_epoch + 1):
            if epoch!=0 and estimate_switches_every and epoch % estimate_switches_every == 0:
                pass
            # train_data = self.prepare_data(train_data)
            # valid_data = self.prepare_data(valid_data)
            start_time = time.time()
            for i, (past_source, past_dest, source, dest) in enumerate(data_loader):
                if i % 100 == 0:
                    elapsed = time.time() - start_time
                    print(f"Processed {i} batches in {elapsed:.2f} seconds")
                # xk, context_k = self.prepare_data(d[:, :, :self.num_y])
                context_k = dest.to(self.device)
                xk = source.to(self.device)

                x0 = xk.clone()
                if False: # self.variant in ['dsebm', 'dae']:
                    xk = torch.normal(mean=xk, std=torch.exp(self.log_sigma_x))

                r, h = self.recon(xk, context_k, round=round_latent_during_learning)
                with torch.no_grad():
                    h_past, _ = self.encode(past_dest.to(self.device), past_source.to(self.device))
                loss = self.mse(x0, r) + self.transience_weight * self.transience_bce(h_past, h) + self.sparsity_weight * self.sparsity_loss(h)
                opt.zero_grad()
                loss.backward()
                opt.step()

            with torch.no_grad():
                past_source, past_dest, source, dest = train_data.get_random_sample()
                progress = self._get_progress_learn(past_source, past_dest, source, dest)
                if verbose:
                    print(f'\n############### Epoch {epoch} ###############')
                    print('Train: ')
                    pprint.pp(progress)
                self.learning_curve.append(progress)
            if valid_data is not None:
                with torch.no_grad():
                    past_source, past_dest, source, dest = valid_data.get_random_sample()
                    progress = self._get_progress_learn(past_source, past_dest, source, dest)
                    self.valid_curve.append(progress)
                if verbose:
                    print('Valid: ')
                    pprint.pp(progress)

                if early_stopping and epoch > min_epoch and epoch > early_stopping_patience:
                    valid_metrics = np.array([v['MSE'] for v in self.valid_curve[-early_stopping_patience-1:]])
                    if np.all(valid_metrics[1:] > valid_metrics[0]):
                        print('Early stop after valid metrics: ', valid_metrics)
                        break

            if self.is_sigma_learnable:
                print(torch.exp(self.log_sigma_x))
        self.eval()
        self.num_epoch = epoch

        if log_mlflow:
            with torch.no_grad():
                mlflow.log_metrics(self.valid_curve[-1])
                mlflow.log_metric("num_epoch", self.num_epoch)
                run_id = mlflow.active_run().info.run_id
                mlflow.log_figure(self.plot_learning_curve(), f'figures/learning_curve_denta_{run_id}.html')

                past_source, past_dest, source, dest = valid_data.get_random_sample()
                mlflow.log_figure(self.plot_activation_probabilities(dest, source),
                                  f'figures/activations_hist_denta_{run_id}.html')
                mlflow.log_figure(self.plot_frequency_of_latent_combinations(dest, source),
                                  f'figures/latent_frequencies_denta_{run_id}.html')

        if verbose:
            print('Training finished after ', timedelta(seconds=time.time() - t_start))

    # def sparsity_loss(self, h):
    #     sparsity_penalty = self.sparsity_weight * torch.sum((self.sparsity_target - h) ** 2)
    #     return sparsity_penalty
    def sparsity(self, activations, per_point=False):
        if per_point:
            return torch.mean(activations, dim=1)
        else:
            return torch.mean(activations)

    def sparsity_loss(self, activations):
        # Mean activation per neuron
        mean_activations = self.sparsity(activations, per_point=True)

        # KL divergence between the target sparsity level and the means
        kl_div = self.sparsity_target * torch.log(self.sparsity_target / mean_activations) + \
                 (1 - self.sparsity_target) * torch.log((1 - self.sparsity_target) / (1 - mean_activations))
        kl_div = torch.mean(kl_div)  # Sum over all neurons

        return kl_div

    def recon_error(self, data, input=None, per_point=False, round=False):
        if input is None:
            input = data
        recon, _ = self.recon(input, round=round)
        if per_point:
            dim = (1, 2)
        else:
            dim = None
        squared_error = torch.mean(torch.square(data - recon), dim=dim)
        return squared_error

    def anomaly_score(self, s):
        # d = d[:]
        # t, s, = d['time'], d
        # if self.input_layer in ['gbrbm']:
        #     score_in_time = self.free_energy(s)
        # else:
        #     score_in_time = self.recon_error(s)
        # score = score_in_time.cpu().detach().numpy()

        s = self.prepare_data(s)
        score_in_time = self.recon_error(s, per_point=True).cpu().detach().numpy()
        return score_in_time

    def calculate_ad_threshold(self, d, quantile=0.95):
        scores = self.anomaly_score(d)
        self.threshold = np.sort(scores)[int((len(scores) - 1) * quantile)]
        # if self.log_mlflow:
        #     mlflow.log_metric('threshold', self.threshold)

    def plot_activation_probabilities(self, d, source):
        # if prepare_data:
        #     d = self.prepare_data(d)
        d = d.to(self.device)
        source = source.to(self.device)
        h, z = self.encode(d, source)#
        h = h.cpu().detach().numpy()
        fig = go.Figure(data=[go.Histogram(x=h.reshape(-1), name="Probability", histnorm="percent", nbinsx=20)],
                        layout_title="Histogram of activation probabilities")
        return fig

    def plot_error_histogram(self, d, v=None):
        s = self.anomaly_score(d)
        fig = go.Figure(data=[go.Histogram(x=s, name="Anomaly score", histnorm="density")], layout_title="Histogram of scores")
        if v is not None:
            s = self.anomaly_score(v)
            fig.add_trace(go.Histogram(x=s, name="Anomaly score - validation set", histnorm="density"))
        if self.threshold is not None:
            fig.add_vline(x=self.threshold, line_width=2, line_dash="dash", line_color="red")
        return fig

    def anomaly_detection(self, s):
        s = self.prepare_data(s)
        score_in_time = self.recon_error(s, per_point=True).cpu().detach().numpy()
        return (score_in_time > self.threshold).astype(float), score_in_time

    def plot_learning_curve(self):
        return vis.plot_timeseries([pd.DataFrame(self.learning_curve), pd.DataFrame(self.valid_curve)],
                                   title='Learning curve', names=['Train', 'Valid'], xaxis_title='Epoch')

    # Transforms the p(v) into mixture of Gaussians and returns the weight, mean and sigma for each Gaussian component as
    # well the corresponding hidden states.This function is for use with very small models.Otherwize it will last forever
    def gmm_model(self):
        def gbrbm_h2v(type, h, W, bv, sigma):
            x = np.matmul(np.atleast_2d(h), W)
            if type == 'gbrbm':
                x *= sigma
            return x + bv
        sigma = np.exp(self.log_sigma_x.detach().numpy())
        bv = self.bx.detach().numpy()
        bh = self._discretization_layers[-2].bias.detach().numpy()
        W = self._discretization_layers[-2].weight.detach().numpy()

        num_components = 2 ** self.num_h()

        if sigma.size == 1:
            sigma = np.repeat(sigma, self.num_y(), axis=1)
            sigma = sigma[None]

        gmm_sigmas = np.repeat(sigma, num_components, axis=0)

        # Initialize
        weights = np.zeros((num_components, 1))
        means = np.zeros((num_components, self.num_y()))
        hid_states = np.zeros((num_components, self.num_h()))

        phi0 = np.prod(np.sqrt(2 * np.pi) * sigma)

        weights[0] = phi0
        means[0, :] = bv
        for i in range(1, num_components):
            hs = list(bin(i)[2:])
            hid_states[i, -len(hs):] = hs
            hs = hid_states[i, :]
            # Calc means
            mean = gbrbm_h2v(self.variant, hs, W, bv, sigma)
            means[i, :] = mean

            # Calc phi
            phi = (np.sum(mean ** 2 / (2 * sigma ** 2)) - np.sum(bv ** 2 / (2 * sigma ** 2)))
            phi = np.sum(phi) + np.sum(bh * hs)
            phi = phi0 * np.exp(phi)

            weights[i] = phi

        # Normalize weights
        Z = sum(weights)
        weights = weights / Z
        return weights, means, gmm_sigmas, hid_states, Z

    def plot_frequency_of_latent_combinations(self, d, context):
        d = d.to(self.device)
        context = context.to(self.device)
        h = self.predict_discrete_mode(d, context)
        if type(h) is list:
            h = np.concatenate(h, axis=0)
        fig = go.Figure(data=[go.Histogram(x=h, name="Frequency", histnorm="percent")],
                        layout_title="Frequency of latent combinations")
        return fig

    def plot_discretization(self, time, target, prediction, data=None, data_time=None):
        target = np.asarray(target)
        target = target[:, 0]
        if data is not None:
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.01)
            for i in range(data.shape[1]):
                fig.add_trace(go.Scatter(x=data_time, y=data[:, i], name=f'Signal{i + 1}'), row=1, col=1)

            if torch.is_tensor(data):
                data = data.to(self.device)
            else:
                data = torch.tensor(data, device=self.device)

            fig.add_trace(go.Scatter(x=np.asarray(time), y=target.astype(str), name='Mode Target',
                                     mode='lines+markers'), row=2, col=1)
            fig.add_trace(go.Scatter(x=np.asarray(time), y=np.asarray(prediction).astype(str), name='Mode Prediction',
                                     mode='lines+markers'), row=2, col=1)

            error = self.recon_error(self.prepare_data(data), per_point=True)
            error_rounding = self.recon_error(self.prepare_data(data), per_point=True, round=True)
            fig.add_trace(go.Scatter(x=np.asarray(time), y=error.cpu().detach().numpy(), name='Reconstruction error',
                                     mode='lines+markers'), row=3, col=1)
            fig.add_trace(go.Scatter(x=np.asarray(time), y=error_rounding.cpu().detach().numpy(),
                                     name='Reconstruction error from rounded',
                                     mode='lines+markers'), row=3, col=1)
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=np.asarray(time), y=target.astype(str), name='Mode Target',
                                     mode='lines+markers'))
            fig.add_trace(go.Scatter(x=np.asarray(time), y=np.asarray(prediction).astype(str), name='Mode Prediction',
                                     mode='lines+markers'))
        fig.update_layout(height=1200)
        return fig

    def plot_input_space(self, data=None, samples=None, show_gaussian_components=False, data_limit=10000,
                         xmin=None, xmax=None, ymin=None, ymax=None, figure_width=600, figure_height=600,
                         show_axis_titles=True, show_energy_contours=False, showlegend=True,
                         show_recon_error_contours=False, ncontours=None,
                         plot_code_positions=True, show_recon_error_heatmap=False, plot_bias_vector=False,
                         show_reconstructions=False, **kwargs):
        fig = go.Figure()
        if show_recon_error_heatmap:
            if xmin is None and xmax is None and ymin is None and ymax is None:
                if data is None:
                    xmin, xmax = -5, 5
                    ymin, ymax = -5, 5
                else:
                    xmin = ymin = data.min().min()
                    xmax = ymax = data.max().max()

            x = np.linspace(xmin, xmax, 100)
            y = np.linspace(ymin, ymax, 100)
            xv, yv = np.meshgrid(x, y)
            d = np.hstack([xv.reshape(-1, 1), yv.reshape(-1, 1)])
            with torch.no_grad():
                fe = self.recon_error(torch.Tensor(d)).numpy()

            trace = go.Heatmap(x=x, y=y, z=np.reshape(fe, xv.shape),
                               name="Reconstruction Error", showlegend=True, showscale=False)
            fig.add_trace(trace)

        if show_recon_error_contours and data.shape[0] == 2:
            if xmin is None and xmax is None and ymin is None and ymax is None:
                if data is None:
                    xmin, xmax = -5, 5
                    ymin, ymax = -5, 5
                else:
                    xmin = ymin = data.min().min()
                    xmax = ymax = data.max().max()

            x = np.linspace(xmin, xmax, 100)
            y = np.linspace(ymin, ymax, 100)
            xv, yv = np.meshgrid(x, y)
            d = np.hstack([xv.reshape(-1, 1), yv.reshape(-1, 1)])
            with torch.no_grad():
                fe = self.recon_error(torch.Tensor(d)).numpy()
                fe = np.reshape(fe, xv.shape)

                trace = go.Contour(x=x, y=y, z=fe, contours=dict(coloring='lines'), name="Reconstruction Error",
                                   showlegend=True, showscale=False, ncontours=ncontours)
                fig.add_trace(trace)

        if show_energy_contours:
            if xmin is None and xmax is None and ymin is None and ymax is None:
                if data is None:
                    xmin, xmax = -5, 5
                    ymin, ymax = -5, 5
                else:
                    xmin = ymin = data.min().min()
                    xmax = ymax = data.max().max()

            x = np.linspace(xmin, xmax, 100)
            y = np.linspace(ymin, ymax, 100)
            xv, yv = np.meshgrid(x, y)
            d = np.hstack([xv.reshape(-1, 1), yv.reshape(-1, 1)])
            fe = self.free_energy(torch.Tensor(d)).detach().numpy()

            trace = go.Contour(x=x, y=y, z=np.reshape(fe, xv.shape),
                               contours=dict(coloring='lines'), name="Free energy", ncontours=ncontours, showlegend=True, showscale=False)
            fig.add_trace(trace)

        if data is not None:
            if data_limit is not None and data.shape[0] > data_limit:
                data = data.sample(data_limit)
            fig.add_trace(vis.plot2d(data[data.columns[0]], data[data.columns[1]], name='Data',
                                     marker=dict(size=3, opacity=0.2, color='MediumPurple')))
            if show_reconstructions:
                recon, _ = self.recon(torch.Tensor(data.values)).detach().numpy()
                fig.add_trace(vis.plot2d(recon[:,0], recon[:, 1], name='Reconstruction',
                                         marker=dict(size=3, opacity=0.2, color='limegreen')))
        if samples is not None:
            fig.add_trace(vis.plot2d(samples[:, 0], samples[:, 1], name='Samples',
                                     marker=dict(size=3, opacity=0.2, color='darkgreen')))

        if show_axis_titles:
            fig.update_layout(
                xaxis_title="$x_1$",
                yaxis_title="$x_2$",
            )
        if plot_code_positions:
            num_h = self.num_h()
            num_v = self.num_y()
            num_components = 2 ** num_h
            # Initialize
            means = np.zeros((num_components, num_v))
            hid_states = np.zeros((num_components, num_h))
            for i in range(0, num_components):
                hs = list(bin(i)[2:])
                hid_states[i, -len(hs):] = hs
                hs = hid_states[[i], :]
                # Calc means
                mean = self.decode(torch.Tensor(hs))
                means[i, :] = mean.detach().numpy()

            hm_mapping = dict()
            for h, m in zip(list(hid_states), list(means)):
                hm_mapping[str(h)] = m
            for i in range(means.shape[0]):
                mean = means[i, :]
                hid = hid_states[i, :]
                for i, hi in enumerate(hid):
                    if hi == 1:
                        hid_prev = hid.copy()
                        hid_prev[i] = 0
                        mean_start = hm_mapping[str(hid_prev)]
                        fig.add_annotation(xref="x", yref="y", axref="x", ayref="y",
                                           ax=mean_start[0], ay=mean_start[1], x=mean[0], y=mean[1],
                                           showarrow=True, arrowhead=2, arrowsize=1.5)

            fig.add_trace(go.Scatter(x=means[:, 0], y=means[:, 1], text=hid_states, mode='text+markers',
                                     name='Codes', textfont_size=12,
                                     textposition="top left", marker_color='orange', marker_size=4))
        if plot_bias_vector:
            bx = self.bx.detach().numpy()
            fig.add_annotation(xref="x", yref="y", axref="x", ayref="y",
                               x=bx[0][0], y=bx[0][1], ax=0, ay=0,
                               showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=1,
                               arrowcolor="#636363")
        if show_gaussian_components:
            weights, means, gmm_sigmas, hid_states, Z = self.gmm_model()
            hm_mapping = dict()
            for h, m in zip(list(hid_states), list(means)):
                hm_mapping[str(h)] = m
            for i in range(weights.shape[0]):
                weight = weights[i, 0]
                mean = means[i, :]
                sigma = gmm_sigmas[i, :]
                hid = hid_states[i, :]
                fig.add_shape(type="circle",
                              xref="x", yref="y",
                              x0=mean[0] - 2 * sigma[0], y0=mean[1] - 2 * sigma[1],
                              x1=mean[0] + 2 * sigma[0], y1=mean[1] + 2 * sigma[1],
                              # opacity=weight/max(max(weights)),
                              fillcolor='rgba(23, 156, 125, {:.2f})'.format(0.7 * weight / max(max(weights))),
                              line_color='rgba(23, 156, 125)',
                              line_width=1,
                              layer='below')
                for i, hi in enumerate(hid):
                    if hi == 1:
                        hid_prev = hid.copy()
                        hid_prev[i] = 0
                        mean_start = hm_mapping[str(hid_prev)]
                        fig.add_annotation(xref="x", yref="y", axref="x", ayref="y",
                                           ax=mean_start[0], ay=mean_start[1], x=mean[0], y=mean[1],
                                           showarrow=True, arrowhead=2, arrowsize=1.5)

            weights = list(weights[i, :] for i in range(weights.shape[0]))
            hid_states = [' '.join(list(hid_states[i, :].astype(int).astype(str))) for i in range(hid_states.shape[0])]
            # fig.add_trace(go.Scatter(x=means[:, 0], y=means[:, 1], text=hid_states, mode='text+markers',
            #                          hovertext=weights,
            #                          name='GMM',
            #                          textposition="top left", marker_color='orange'))
        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
            title_standoff=0,
            range=[ymin, ymax]
        )
        fig.update_xaxes(
            title_standoff=0,
            range=[xmin, xmax]
        )
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20),
                          width=figure_width,
                          height=figure_height,
                          showlegend=showlegend,
                          legend=dict(yanchor="bottom", y=1, xanchor="left", x=0.01, orientation="h",
                                      font=dict(size=8)))
        fig.update_layout(**kwargs)
        return fig

    def find_optimal_threshold_for_f1(self, data, search_every=1, plot=False):
        scores_unsorted = self.anomaly_score(data[:])
        sort_ind = np.argsort(scores_unsorted)
        sort_ind = sort_ind[0::search_every]
        thresholds = scores_unsorted[sort_ind]
        labels_unsorted = data[:]['label'].cpu().detach().numpy()

        f1_scores = [f1_score(labels_unsorted != 0, scores_unsorted > th) for th in thresholds]
        opt_ind = np.argmax(f1_scores)
        opt_th = thresholds[opt_ind]
        max_f1 = f1_scores[opt_ind]
        if plot:
            fig = vis.plot2d(np.arange(0, scores_unsorted.shape[0]), scores_unsorted, return_figure=True)
            fig.add_trace(vis.plot2d(np.arange(0, labels_unsorted.shape[0]), labels_unsorted))
            fig.show()
            vis.plot2d(thresholds, f1_scores, return_figure=True).show()
        return opt_th, max_f1

    def get_auroc(self, data):
        scores = self.anomaly_score(data[:])
        labels = data[:]['label'].cpu().detach().numpy()
        labels = labels != 0
        return roc_auc_score(labels, scores)


class DENTA(automata.Automaton):
    """
    DENTA: DEep Network Timed Automata.

    This class represents an automaton model built from a latent representation
    learned by a neural energy-based model (EBM). It integrates deep learning (via `DentaEbm`)
    with automata theory (via `automata.Automaton`).

    Attributes:
        ebm (DentaEbm): The underlying energy-based model for learning latent representations.
        _mean (float or None): Placeholder for mean normalization (not initialized).
        _std (float or None): Placeholder for standard deviation normalization (not initialized).
        log_mlflow (bool): Whether to log metrics and figures to MLflow.
    """

    def __init__(self, log_mlflow=False, *args, **kwargs):
        """
        Initialize the DENTA automaton.

        Args:
            log_mlflow (bool): If True, enables logging metrics and figures to MLflow.
            *args: Additional positional arguments passed to DentaEbm constructor.
            **kwargs: Additional keyword arguments passed to DentaEbm constructor.
        """
        automata.Automaton.__init__(self)
        self.ebm = DentaEbm(*args, **kwargs, log_mlflow=log_mlflow)
        self._mean = None
        self._std = None
        self.log_mlflow = log_mlflow

    def predict(self, context, model_input: pd.DataFrame) -> pd.DataFrame:
        return self.ebm.predict_discrete_mode(model_input, prepare_data=True)

    def pretrain_layers(self, train_data, valid_data, *args, **kwargs):
        self.ebm.pretrain_layers(train_data, valid_data, log_mlflow=self.log_mlflow, **kwargs)

    def finetune_denta_network(self, train_dataset, valid_dataset, **kwargs):
        """
        Train the underlying energy-based model (EBM) using provided data.

        Args:
            *args: Positional arguments passed to `self.ebm.learn`.
            **kwargs: Keyword arguments passed to `self.ebm.learn`.
        """
        self.ebm.finetune(train_dataset, valid_dataset, log_mlflow=self.log_mlflow, **kwargs)

    def recon(self, dest, source):
        # v = v[:, :self.ebm.num_y]
        # v = self.ebm.prepare_data(v)
        dest = dest.to(self.ebm.device)
        source = source.to(self.ebm.device)
        r, h = self.ebm.recon(dest, source, round=True)
        return r, h

    def learn_latent_automaton(self, train_dataset, valid_dataset, verbose=True):
        """
        Learn the latent automaton by discretizing latent states and extracting transitions.

        This function:
        1. Encodes training data into latent representations using the EBM.
        2. Discretizes the latent representations by rounding.
        3. Learns an automaton structure from the discretized latent vectors.

        Args:
            train_dataset: The training dataset object with `windowed_sequences()` method.
            valid_dataset: Validation dataset (not used in current implementation).
            verbose (bool): If True, prints progress messages during discretization.

        Side Effects:
            - Updates `self._G` with the learned automaton graph.
            - If `log_mlflow` is True, logs:
                - Metric "num_modes" (number of discrete modes/states)
                - Visualization figure (Plotly HTML) of the automaton
        """
        sig_names = [f'h{i + 1}' for i in range(self.ebm.num_h())]
        h = []
        all_sequences = train_dataset.windowed_sequences()

        for seq_ind, (s, d) in enumerate(all_sequences):
            if verbose:
                print(f"Discretizing sequence {seq_ind+1}/{len(all_sequences)} of length {d.shape[0]}")

            # Prepare input data for encoding
            # d = self.ebm.prepare_data(d[:, :, :self.ebm.num_y])

            # Encode the data and discretize latent states
            hh, zz = self.ebm.encode(d.to(self.ebm.device), s.to(self.ebm.device), rounding=True)
            hh = hh.cpu().detach().numpy()

            # Convert latent states to DataFrame with symbolic column names
            hh = pd.DataFrame(hh, columns=sig_names) # index=np.arange(hh.shape[0])
            # hh.reset_index(inplace=True)
            h.append(hh)

        # Learn automaton from discretized latent signal vectors
        a = automata_learn.simple_learn_from_signal_vectors(h, drop_no_changes=True, verbose=verbose)
        self._G = a._G

        if self.log_mlflow:
            # Log the number of discovered modes (states)
            mlflow.log_metric("num_modes", self.num_modes)

            # Log an interactive visualization of the automaton as an HTML figure
            mlflow.log_figure(
                vis.plot_cps_plotly(self, show_num_occur=True),
                f'figures/denta_automaton_{mlflow.active_run().info.run_id}.html'
            )


class FactorizedThreeWayLayer(nn.Module):
    def __init__(self, input_dim, context_dim, output_dim, n_factors):
        super(FactorizedThreeWayLayer, self).__init__()
        self.input_dim = input_dim
        self.context_dim = context_dim
        self.output_dim = output_dim
        self.n_factors = n_factors

        # Factor matrices
        self.U = nn.Parameter(torch.randn(input_dim, n_factors) * 0.1)
        self.V = nn.Parameter(torch.randn(context_dim, n_factors) * 0.1)
        self.S = nn.Parameter(torch.randn(output_dim, n_factors) * 0.1)

        # Output bias
        self.output_bias = nn.Parameter(torch.zeros(output_dim))
        self.input_bias = nn.Parameter(torch.zeros(input_dim))

    def forward(self, x, context):
        """
        x: (batch_size, input_dim)
        context: (batch_size, context_dim)
        returns: (batch_size, output_dim)
        """
        # Project input and context to factors
        input_factors = torch.matmul(x, self.U)        # (batch_size, n_factors)
        context_factors = torch.matmul(context, self.V) # (batch_size, n_factors)

        # Element-wise multiplication of factor representations
        joint_factors = input_factors * context_factors  # (batch_size, n_factors)

        # Project joint factors to output space
        output = torch.matmul(joint_factors, self.S.t())  # (batch_size, output_dim)

        output = output + self.output_bias
        output = torch.sigmoid(output)

        return output

    def decode(self, h, context):
        """
        Reconstruct input x_hat given hidden h and context.
        """
        hidden_factors = torch.matmul(h, self.S)  # (batch_size, n_factors)
        context_factors = torch.matmul(context, self.V)  # (batch_size, n_factors)

        # Element-wise multiplicative interaction
        joint_factors = hidden_factors * context_factors  # (batch_size, n_factors)

        # Project back to input space
        x_logits = torch.matmul(joint_factors, self.U.t()) + self.input_bias  # (batch_size, input_dim)

        x_recon = torch.sigmoid(x_logits)  # Reconstruction in [0, 1]
        return x_recon

class SparseSmoothRBM:
    def __init__(self, num_y, num_b, sigma, num_h, num_w):
        return None



if __name__ == '__main__':
    from ml4cps import examples
    data = examples.conveyor_system_sfowl()

    # # Use model URI: path, run-relative path, or registered model name
    # model_uri = "file:///D:/Repos/kiss_reconfig/mlruns/0/85781f03639d472f8f870f6cf370e7b8/artifacts/model"
    #
    # loaded_model = mlflow.pyfunc.load_model(model_uri)
    # mdl = loaded_model._model_impl.python_model
    #
    # data = torch.load('data/data.pt')
    # dataset = WindowedSequenceDataset([data])
    # dataset.normalize(variables=range(mdl.ebm.num_y))
    # d = dataset.sequences[0:100000, :, :mdl.ebm.num_y]
    # r, h = mdl.recon(d.to(mdl.ebm.device))
    # r = r[:,0,0,:].to("cpu").detach().numpy()
    # d = d[:,0,:].detach().numpy()
    # print("Plotting")
    # vis.plot_timeseries([d, r]).show("browser")




    # vis.plot_timeseries()
    # # Preprocess the data
    # num_sequences = 1  # Number of sequences
    # sequence_length = 60  # Length of each sequence
    # num_features = 3  # Number of features per time step
    #
    # # Generate synthetic data
    # data = torch.randn(sequence_length, num_features, device='cuda')
    # valid = torch.randn(sequence_length, num_features, device='cuda')
    # timestamp = torch.arange(sequence_length)
    # valid_states = torch.randint(0, 10, (sequence_length, 1))
    #
    # # Hyperparameters
    # sparsity_target = 1 / 3
    # sparsity_weight = 0
    # sigma = 0.3
    # max_epoch = 2
    # window_size = 5
    # window_step = 1
    #
    # # Parameters
    # latent_dim = 7
    # num_hidden_layers = 3
    #
    # # Train model
    # model = DENTA(data.shape[1], latent_dim, sigma=sigma, sigma_learnable=False, sparsity_weight=sparsity_weight,
    #               num_hidden_layers=num_hidden_layers, window_size=window_size, window_step=window_step,
    #               sparsity_target=sparsity_target, use_derivatives=0, device='cuda')
    # model.pretrain_dbn([data], [valid])
    # # model.learn_denta_network([data], [valid], max_epoch=max_epoch, verbose=False)
    # model.learn_latent_automaton([data], [valid])
    # model.view_plotly().show()
    # model.plot_learning_curve().show('browser')
    #
    # valid_mode_prediction = model.predict_discrete_mode([valid])
    # # model.plot_frequency_of_latent_combinations([data]).show()
    # model.plot_activation_probabilities(valid).show()
    # #model.plot_discretization(timestamp, valid_states.cpu(), valid_mode_prediction[0], data.cpu(), timestamp.cpu()).show()
    #

    # from ml4cps import examples, vis
    # conv = examples.simple_conveyor_8_states()
    #
    # conv.reinitialize(0)
    # data = conv.simulate(finish_time=100)
    # train_data = data[3][[data[3].columns[-2], data[3].columns[-1]]]
    #
    # conv.reinitialize(0)
    # valid_data = conv.simulate(finish_time=100)
    # valid_data = valid_data[3][[valid_data[3].columns[-2], valid_data[3].columns[-1]]]
    #
    # ###
    # mdl = DENTA(num_y=2, num_h=8, sigma=0.1, num_hidden_layers=1, log_mlflow=True)
    # mdl.learn_denta_network([train_data], [valid_data], max_epoch=20)
    #
    # # err = mdl.recon_error(mdl.prepare_data([train_data])[0], per_point=True)
    # fun = lambda x: mdl.recon_error(mdl.prepare_data(x), per_point=True)
    # fig = go.Figure()
    # fig.add_trace(vis.plot2d(tools.standardize(train_data, mean=mdl._mean, std=mdl._std), x=train_data.columns[0], y=train_data.columns[1]))
    # fig.add_trace(vis.plot_2d_contour_from_fun(fun, rangex=(-3,3), rangey=(-3,3)))
    #
    # fig.show()
    #
    # mdl.plot_learning_curve().show()
