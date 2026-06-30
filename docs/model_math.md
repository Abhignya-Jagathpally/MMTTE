# Model Mathematics

## Cox proportional hazards

For patient covariates `x_i`, risk score `r_i = f_theta(x_i)`. The loss is the negative Cox partial log-likelihood:

`L_Cox = - sum_{i:event_i=1} [ r_i - log sum_{j:t_j >= t_i} exp(r_j) ] / n_events`.

The proportional-hazards assumption must be checked outside the neural trainer before clinical interpretation.

## Log-normal accelerated failure time

The model predicts `mu_i, sigma_i` for `log(T_i) ~ Normal(mu_i, sigma_i)`. Observed events use the density; censored observations use the survival term:

`L_AFT = - event * log f(t_i | mu_i, sigma_i) - (1-event) * log S(t_i | mu_i, sigma_i)`.

## First hitting time

The model uses an inverse-Gaussian first-passage approximation:

`T_i ~ IG(mu_i, lambda_i)`.

Here `mu_i` is expected time to hit a progression/resistance boundary and `lambda_i` controls diffusion/noise. This is statistically meaningful for TTE even with one baseline snapshot, but mechanistic trajectory interpretation requires repeated pre-event states.

## On-policy self-distillation

A student survival network is trained with supervised TTE loss plus consistency against an exponential-moving-average teacher of itself:

`L = L_survival + alpha * || zscore(r_student / tau) - zscore(r_teacher / tau) ||_2^2`.

The teacher is updated after each epoch:

`phi <- decay * phi + (1-decay) * theta`.

This is on-policy because the teacher follows the current training policy and never introduces an offline frozen labeler. It should improve stability and calibration, not be advertised as a guarantee of SOTA performance.
