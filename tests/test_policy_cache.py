def test_force_disables_policy_sensitivity_cache(tmp_path):
    from src.utils.cache_utils import should_use_cache

    cache = tmp_path / "sensitivity.csv"
    cache.write_text("cached", encoding="utf-8")

    assert should_use_cache(cache, force=False)
    assert not should_use_cache(cache, force=True)
