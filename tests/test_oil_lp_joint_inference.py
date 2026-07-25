import numpy as np
import pytest


def test_joint_permutation_inference_uses_max_statistic_across_horizons():
    from src.analysis.oil_lp import joint_permutation_inference

    beta_hat = np.array([2.0, 0.5])
    beta_perm = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.5],
            [2.5, 0.1],
            [0.2, 1.5],
        ]
    )

    result = joint_permutation_inference(beta_hat, beta_perm, alpha=0.10)

    assert result["p_fwer"].shape == (2,)
    assert np.all((result["p_fwer"] > 0) & (result["p_fwer"] <= 1))
    assert result["global_p"] == pytest.approx(result["p_fwer"].min())
    assert result["uniform_critical"] >= 0
    assert result["uniform_lower"].shape == beta_hat.shape
    assert result["uniform_upper"].shape == beta_hat.shape


def test_joint_permutation_inference_rejects_invalid_shapes():
    from src.analysis.oil_lp import joint_permutation_inference

    with pytest.raises(ValueError, match="horizon dimension"):
        joint_permutation_inference(np.array([1.0, 2.0]), np.zeros((10, 3)))
