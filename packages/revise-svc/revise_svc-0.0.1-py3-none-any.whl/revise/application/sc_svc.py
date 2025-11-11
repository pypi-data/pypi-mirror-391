import scanpy as sc

from revise.application.application_svc import ApplicationSvc


class ScSvc(ApplicationSvc):
    """
    sc-SVC class for application scenarios.
    
    This class handles single-cell resolution spatial transcriptomics data,
    filtering cells and genes based on transcript counts and preparing
    data for downstream annotation and reconstruction.
    """
    def __init__(self, st_adata, sc_ref_adata, config, logger):
        super().__init__(st_adata, sc_ref_adata, config, None, logger)
        self._adata_validate()
        self._adata_processing()

        self.sc_ref_adata_raw = self.sc_ref_adata.copy()
        overlap_genes = self.st_adata.var_names.intersection(self.sc_ref_adata.var_names)
        self.st_adata = self.st_adata[:, overlap_genes]
        self.sc_ref_adata = self.sc_ref_adata[:, overlap_genes]

    def _adata_processing(self):
        """
        Process spatial and single-cell data with transcript count filtering.
        
        Filters spatial cells by transcript counts (>= 60) and filters genes
        by minimum cell counts. Also normalizes cell type labels.
        """
        self.adata_st = self.st_adata[self.st_adata.obs['transcript_counts'] >= 60, :]
        sc.pp.filter_genes(self.adata_st, min_cells=100)
        sc.pp.filter_genes(self.sc_ref_adata, min_cells=100)
        self.sc_ref_adata.obs['Level1'].replace({"Mono/Macro": "Mono_Macro"}, inplace=True)
        overlap_genes = self.adata_st.var_names.intersection(self.sc_ref_adata.var_names)
        self.adata_st = self.adata_st[:, overlap_genes]
