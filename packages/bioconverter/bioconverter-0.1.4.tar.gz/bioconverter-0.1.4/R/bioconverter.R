#' Universal Bioinformatics Data Converter
#'
#' @description
#' Native R package for converting various bioinformatics data formats
#' to unified standard formats. Supports genomics (GWAS, VCF),
#' transcriptomics (RNA-seq), proteomics, and metabolomics data.
#'
#' This is a pure R implementation that does not depend on Python.
#'
#' @docType package
#' @name bioconverter
NULL

#' Convert a bioinformatics data file
#'
#' @description
#' Convert a bioinformatics data file from its original format to a standardized format.
#' Automatically detects file format and omics type.
#'
#' @param input_file Character. Path to input file
#' @param output_file Character. Path to output file (optional)
#' @param auto_suggest Logical. Use automatic column mapping suggestions (default: TRUE)
#' @param column_mapping Named list. Manual column mapping (original_name = "standard_name")
#' @param keep_unmatched Logical. Keep columns that don't match standard patterns (default: TRUE)
#' @param verbose Logical. Print detailed information (default: TRUE)
#'
#' @return A data frame containing the converted data
#'
#' @examples
#' \dontrun{
#' # Convert with auto-suggestion
#' result <- convert_file(
#'   input_file = "gwas_data.tsv",
#'   output_file = "standardized_gwas.tsv"
#' )
#'
#' # Convert with manual mapping
#' result <- convert_file(
#'   input_file = "data.txt",
#'   output_file = "output.tsv",
#'   column_mapping = list(CHR = "chr", POS = "pos", P = "pval")
#' )
#'
#' # Convert without saving (return data only)
#' result <- convert_file(
#'   input_file = "data.tsv",
#'   output_file = NULL
#' )
#' }
#'
#' @export
convert_file <- function(input_file,
                        output_file = NULL,
                        auto_suggest = TRUE,
                        column_mapping = NULL,
                        keep_unmatched = TRUE,
                        verbose = TRUE) {
  
  # Auto-suggest mapping if requested and no manual mapping provided
  if (auto_suggest && is.null(column_mapping)) {
    column_mapping <- auto_suggest_mapping(input_file)
    if (verbose && length(column_mapping) > 0) {
      cat("\nAuto-detected column mappings:\n")
      for (orig in names(column_mapping)) {
        cat(sprintf("  %s -> %s\n", orig, column_mapping[[orig]]))
      }
    }
  }
  
  # Convert file
  result_df <- convert_single_file(
    filename = input_file,
    column_mapping = column_mapping,
    keep_unmatched = keep_unmatched,
    verbose = verbose
  )
  
  # Save output if file path provided
  if (!is.null(output_file)) {
    if (verbose) {
      cat(sprintf("\nSaving output to: %s\n", output_file))
    }
    
    if (requireNamespace("readr", quietly = TRUE)) {
      readr::write_tsv(result_df, output_file)
    } else {
      write.table(result_df, output_file, sep = "\t", row.names = FALSE, quote = FALSE)
    }
  }
  
  return(result_df)
}

#' Get supported column name patterns
#'
#' @description
#' Retrieve all supported column name patterns for automatic mapping.
#'
#' @return A list of pattern categories and their recognized variations
#'
#' @examples
#' \dontrun{
#' patterns <- get_column_patterns()
#' print(patterns$genomics)
#' }
#'
#' @export
get_column_patterns <- function() {
  pattern_list <- list(
    genomics = c("chr", "pos", "rsid", "ref", "alt", "pval", "beta", "se", "or", "frq", "n", "info", "a1", "a2", "z"),
    transcriptomics = c("gene_id", "gene_name", "transcript_id", "expression", "fpkm", "tpm", "counts", "log2fc", "padj"),
    proteomics = c("protein_id", "protein_name", "peptide", "abundance", "intensity", "ratio"),
    metabolomics = c("metabolite_id", "metabolite_name", "mz", "rt", "concentration", "peak_area"),
    sample_info = c("sample_id", "condition", "timepoint", "replicate", "batch")
  )
  
  return(pattern_list)
}
