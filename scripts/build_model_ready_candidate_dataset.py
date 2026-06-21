from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.datasets.feature_label_merge import build_model_ready_candidate_dataset


if __name__ == "__main__":
    build_model_ready_candidate_dataset(ROOT)
