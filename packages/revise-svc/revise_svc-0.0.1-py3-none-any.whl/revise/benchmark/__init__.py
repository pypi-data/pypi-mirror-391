import os

from revise.benchmark.sc_svc_dec import ScSvcDec
from revise.benchmark.sc_svc_impute import ScSvcImpute
from revise.benchmark.sp_svc import SpSvc
from revise.tools.metric import compute_metric


def main(svc):
    os.makedirs(svc.config.result_dir, exist_ok=True)
    if svc.st_adata.shape[0] == svc.real_st_adata.shape[0]:
        metric_df = compute_metric(
            svc.st_adata, svc.real_st_adata, svc.logger, adata_process=False, gene_list=None, normalize=True)
        metric_df.to_csv(os.path.join(svc.config.result_dir, "raw_metrics.csv"))
    svc.annotate()
    svc.reconstruct()
    for key, svc_adata in svc.svc.items():
        common_index = svc_adata.obs.index.intersection(svc.real_st_adata.obs.index)
        svc_adata = svc_adata[common_index, :].copy()
        real_st_adata = svc.real_st_adata[common_index, :].copy()
        metrics_df = compute_metric(
            svc_adata, real_st_adata, svc.logger, adata_process=False, gene_list=None, normalize=True)
        metrics_df.to_csv(os.path.join(svc.config.result_dir, f"{key}_metrics.csv"))


__all__ = ['SpSvc', 'ScSvcDec', 'ScSvcImpute']