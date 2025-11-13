#' Create Column Name Patterns for Matching
#'
#' @description
#' Create regex patterns for matching various bioinformatics column names
#' to standardized field names across different omics types.
#'
#' @return A named list of patterns where names are standard column names
#'   and values are regular expressions for matching
#'
#' @examples
#' \dontrun{
#' patterns <- create_column_patterns()
#' }
#'
#' @export
create_column_patterns <- function() {
  list(
    # Genomics
    chr = "^(chr|chromosome|chrom|#?chr|#?chrom|#?CHROM|seqname)$",
    pos = "^(pos|position|bp|base_pair|base_position|ps|POS|start|end)$",
    a1 = "^(a1|allele1|allele_1|effect_allele|ea|alt|alt_allele|ALT)$",
    a2 = "^(a2|allele2|allele_2|other_allele|oa|ref|ref_allele|reference_allele|REF)$",
    n = "^(n|n_samples|sample_size|nsize|ns|n_total|ntotal|N)$",
    frq = "^(frq|freq|frequency|maf|af|eaf|allele_freq|allele_frequency|a1_freq|effect_allele_freq|AF)$",
    info = "^(info|imputation_quality|impquality|r2|rsq|INFO)$",
    beta = "^(beta|b|effect|coef|coefficient|effect_size|BETA|slope)$",
    or = "^(or|odds_ratio|oddsratio|OR)$",
    z = "^(z|zscore|z_score|zstat|z_statistic)$",
    rsid = "^(rsid|snp|snpid|snp_id|variant_id|varid|id|marker|markername|rs|ID)$",
    pval = "^(p|pval|p_value|pvalue|p-value|p\\.value|sig|pval_nominal|P)$",
    se = "^(se|stderr|standard_error|std_err|std_error|SE)$",
    
    # Transcriptomics
    gene_id = "^(gene_id|geneid|ensembl_id|ensembl|ensg)$",
    gene_name = "^(gene_name|genename|gene_symbol|symbol|gene)$",
    transcript_id = "^(transcript_id|transcriptid|enst)$",
    expression = "^(expression|expr|value)$",
    fpkm = "^(fpkm|rpkm)$",
    tpm = "^(tpm|transcripts_per_million)$",
    counts = "^(counts|read_count|reads)$",
    log2fc = "^(log2fc|log2_fold_change|log2foldchange|lfc)$",
    padj = "^(padj|adj_pval|adjusted_pvalue|fdr|qval|q_value)$",
    
    # Proteomics
    protein_id = "^(protein_id|proteinid|uniprot|uniprot_id)$",
    protein_name = "^(protein_name|proteinname|protein)$",
    peptide = "^(peptide|peptide_sequence|sequence)$",
    abundance = "^(abundance|protein_abundance)$",
    intensity = "^(intensity|signal|signal_intensity)$",
    ratio = "^(ratio|fold_change|fc)$",
    
    # Metabolomics
    metabolite_id = "^(metabolite_id|metaboliteid|compound_id|hmdb|hmdb_id)$",
    metabolite_name = "^(metabolite_name|metabolite|compound|compound_name)$",
    mz = "^(mz|m/z|mass|mass_to_charge)$",
    rt = "^(rt|retention_time|retentiontime)$",
    concentration = "^(concentration|conc|amount)$",
    peak_area = "^(peak_area|area|peak_intensity)$",
    
    # Sample information
    sample_id = "^(sample_id|sampleid|sample|sample_name)$",
    condition = "^(condition|group|treatment|class)$",
    timepoint = "^(timepoint|time|time_point)$",
    replicate = "^(replicate|rep|biological_replicate)$",
    batch = "^(batch|batch_id)$"
  )
}

#' Match a Single Column Name to Standard Field
#'
#' @param column_name Character. Column name to match
#' @param patterns Named list. Patterns from create_column_patterns()
#'
#' @return Character or NULL. Matched standard field name
#'
#' @keywords internal
match_column <- function(column_name, patterns) {
  column_name <- trimws(column_name)
  
  for (field_name in names(patterns)) {
    pattern <- patterns[[field_name]]
    if (grepl(pattern, column_name, ignore.case = TRUE, perl = TRUE)) {
      return(field_name)
    }
  }
  
  return(NULL)
}

#' Match Multiple Column Names
#'
#' @description
#' Match a vector of column names to standardized field names.
#'
#' @param column_list Character vector. Column names to match
#' @param custom_patterns Named list. Optional custom patterns to override defaults
#'
#' @return Named list. Original column names as names, matched standard names as values
#'
#' @examples
#' \dontrun{
#' cols <- c("CHR", "POS", "P_VALUE")
#' matched <- match_columns(cols)
#' }
#'
#' @export
match_columns <- function(column_list, custom_patterns = NULL) {
  patterns <- create_column_patterns()
  
  # Override with custom patterns if provided
  if (!is.null(custom_patterns)) {
    patterns <- modifyList(patterns, custom_patterns)
  }
  
  result <- list()
  for (col in column_list) {
    matched <- match_column(col, patterns)
    result[[col]] <- matched
  }
  
  return(result)
}
