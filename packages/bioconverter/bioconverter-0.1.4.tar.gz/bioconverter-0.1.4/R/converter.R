#' Standardize DataFrame Columns
#'
#' @description
#' Standardize column names in a data frame according to patterns.
#'
#' @param df Data frame. Input data
#' @param column_mapping Named list. Manual column name mapping (original = standard)
#' @param custom_patterns Named list. Custom regex patterns
#' @param keep_unmatched Logical. Keep columns that don't match (default: TRUE)
#'
#' @return Data frame with standardized column names
#'
#' @keywords internal
standardize_columns <- function(df, column_mapping = NULL, 
                               custom_patterns = NULL, 
                               keep_unmatched = TRUE) {
  # Start with an empty list to collect columns
  result_cols <- list()
  
  # Apply manual mapping first
  if (!is.null(column_mapping) && length(column_mapping) > 0) {
    for (original_col in names(column_mapping)) {
      std_col <- column_mapping[[original_col]]
      if (original_col %in% colnames(df)) {
        result_cols[[std_col]] <- df[[original_col]]
      }
    }
  }
  
  # Auto-match remaining columns
  remaining_cols <- setdiff(colnames(df), names(column_mapping %||% list()))
  
  if (length(remaining_cols) > 0) {
    col_matches <- match_columns(remaining_cols, custom_patterns)
    
    for (original_col in names(col_matches)) {
      std_col <- col_matches[[original_col]]
      
      if (!is.null(std_col)) {
        # If standard name already exists, keep original name to avoid data loss
        if (!(std_col %in% names(result_cols))) {
          result_cols[[std_col]] <- df[[original_col]]
        } else {
          # Standard name exists, use original column name instead
          result_cols[[original_col]] <- df[[original_col]]
        }
      } else if (keep_unmatched) {
        # Unmatched columns keep original name
        result_cols[[original_col]] <- df[[original_col]]
      }
    }
  }
  
  # Convert list to data frame
  if (length(result_cols) > 0) {
    result_df <- as.data.frame(result_cols, stringsAsFactors = FALSE)
  } else {
    result_df <- data.frame()
  }
  
  return(result_df)
}

#' Convert Single Bioinformatics Data File
#'
#' @description
#' Convert a bioinformatics data file to standardized format with
#' automatic format detection and column mapping.
#'
#' @param filename Character. Path to input file
#' @param sep Character. Column separator (NULL for auto-detect)
#' @param compression Character. Compression format (NULL for auto-detect)
#' @param comment Character. Comment character (NULL for auto-detect)
#' @param column_mapping Named list. Manual column mapping
#' @param custom_patterns Named list. Custom regex patterns
#' @param keep_unmatched Logical. Keep unmapped columns (default: TRUE)
#' @param verbose Logical. Print detailed information (default: TRUE)
#'
#' @return Data frame with standardized columns
#'
#' @examples
#' \dontrun{
#' # Basic conversion with auto-detection
#' result <- convert_single_file("gwas_data.tsv")
#'
#' # With manual mapping
#' result <- convert_single_file(
#'   "data.txt",
#'   column_mapping = list(CHR = "chr", POS = "pos", P = "pval")
#' )
#' }
#'
#' @export
convert_single_file <- function(filename,
                                sep = NULL,
                                compression = NULL,
                                comment = NULL,
                                column_mapping = NULL,
                                custom_patterns = NULL,
                                keep_unmatched = TRUE,
                                verbose = TRUE) {
  if (verbose) {
    cat(sprintf("\nProcessing file: %s\n", filename))
  }
  
  # Auto-detect file format
  format_info <- detect_file_format(filename)
  sep <- sep %||% format_info$sep
  compression <- compression %||% format_info$compression
  comment <- if (is.null(comment)) format_info$comment else comment
  is_vcf <- format_info$is_vcf
  
  if (verbose) {
    cat(sprintf("  Detected format: sep=%s, compression=%s, is_vcf=%s\n",
                if (is.null(sep)) "NULL" else shQuote(sep),
                if (is.null(compression)) "NULL" else compression,
                is_vcf))
  }
  
  # Read data
  df <- read_data(
    filename,
    sep = sep,
    compression = compression,
    comment = comment,
    is_vcf = is_vcf
  )
  
  if (verbose) {
    cat(sprintf("  Original shape: %d rows, %d columns\n", nrow(df), ncol(df)))
    cat(sprintf("  Original columns: %s\n", paste(colnames(df), collapse = ", ")))
  }
  
  # Standardize columns
  standardized_df <- standardize_columns(
    df,
    column_mapping = column_mapping,
    custom_patterns = custom_patterns,
    keep_unmatched = keep_unmatched
  )
  
  if (verbose) {
    cat(sprintf("  Standardized shape: %d rows, %d columns\n", 
                nrow(standardized_df), ncol(standardized_df)))
    cat(sprintf("  Standardized columns: %s\n", 
                paste(colnames(standardized_df), collapse = ", ")))
  }
  
  return(standardized_df)
}

#' Convert Multiple Files
#'
#' @description
#' Batch convert multiple bioinformatics data files.
#'
#' @param file_list Character vector. Paths to input files
#' @param keep_unmatched Logical. Keep unmapped columns (default: TRUE)
#' @param verbose Logical. Print detailed information (default: TRUE)
#'
#' @return Named list of data frames
#'
#' @examples
#' \dontrun{
#' files <- c("file1.tsv", "file2.csv", "file3.txt")
#' results <- convert_multiple_files(files)
#' }
#'
#' @export
convert_multiple_files <- function(file_list, 
                                   keep_unmatched = TRUE, 
                                   verbose = TRUE) {
  results <- list()
  
  for (filename in file_list) {
    if (verbose) {
      cat(sprintf("\n%s\n", strrep("=", 60)))
    }
    
    tryCatch({
      df <- convert_single_file(
        filename,
        keep_unmatched = keep_unmatched,
        verbose = verbose
      )
      results[[filename]] <- df
    }, error = function(e) {
      if (verbose) {
        cat(sprintf("  Error processing %s: %s\n", filename, e$message))
      }
      results[[filename]] <- NULL
    })
  }
  
  return(results)
}
