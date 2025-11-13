#' Detect File Format from Extension
#'
#' @description
#' Automatically detect separator, compression format, comment character,
#' and whether file is VCF based on filename extension.
#'
#' @param filename Character. Path to file
#'
#' @return Named list with: sep, compression, comment, is_vcf
#'
#' @examples
#' \dontrun{
#' format <- detect_file_format("data.tsv.gz")
#' }
#'
#' @export
detect_file_format <- function(filename) {
  filename_lower <- tolower(filename)
  
  # Detect compression
  compression <- NULL
  if (grepl("\\.gz$", filename_lower)) {
    compression <- "gzip"
  } else if (grepl("\\.bz2$", filename_lower)) {
    compression <- "bz2"
  } else if (grepl("\\.zip$", filename_lower)) {
    compression <- "zip"
  } else if (grepl("\\.xz$", filename_lower)) {
    compression <- "xz"
  }
  
  # Detect separator, comment, and VCF
  comment <- NULL
  is_vcf <- FALSE
  
  if (grepl("\\.vcf", filename_lower)) {
    sep <- "\t"
    is_vcf <- TRUE
    comment <- NULL  # VCF handled specially
  } else if (grepl("\\.tsv|\\.tab", filename_lower)) {
    sep <- "\t"
  } else if (grepl("\\.csv", filename_lower)) {
    sep <- ","
  } else {
    sep <- NULL  # Will use whitespace
  }
  
  list(
    sep = sep,
    compression = compression,
    comment = comment,
    is_vcf = is_vcf
  )
}

#' Read VCF File
#'
#' @description
#' Read VCF file, handling ## comments and #CHROM header line.
#'
#' @param filename Character. Path to VCF file
#' @param compression Character. Compression type (NULL, "gzip", "bz2", etc.)
#'
#' @return Data frame with VCF data
#'
#' @keywords internal
read_vcf_file <- function(filename, compression = NULL) {
  # Read all lines
  if (!is.null(compression) && compression == "gzip" || grepl("\\.gz$", filename)) {
    con <- gzfile(filename, "rt")
  } else {
    con <- file(filename, "rt")
  }
  
  lines <- readLines(con)
  close(con)
  
  # Find header line (starts with #CHROM or CHROM)
  header_idx <- NULL
  for (i in seq_along(lines)) {
    if (grepl("^#CHROM", lines[i]) || (grepl("^CHROM", lines[i]) && !grepl("^##", lines[i]))) {
      header_idx <- i
      break
    }
  }
  
  if (is.null(header_idx)) {
    stop(sprintf("Could not find header line in VCF file: %s", filename))
  }
  
  # Extract column names
  header_line <- lines[header_idx]
  columns <- strsplit(header_line, "\t")[[1]]
  columns <- gsub("^#", "", columns)  # Remove leading #
  
  # Extract data lines (skip all comment lines)
  data_lines <- lines[(header_idx + 1):length(lines)]
  data_lines <- data_lines[!grepl("^#", data_lines)]
  
  if (length(data_lines) == 0) {
    # Create empty data frame with columns
    df <- as.data.frame(matrix(ncol = length(columns), nrow = 0))
    colnames(df) <- columns
    return(df)
  }
  
  # Parse data
  data_list <- lapply(data_lines, function(line) {
    strsplit(line, "\t")[[1]]
  })
  
  # Create data frame
  df <- as.data.frame(do.call(rbind, data_list), stringsAsFactors = FALSE)
  colnames(df) <- columns
  
  return(df)
}

#' Read Data File
#'
#' @description
#' Read bioinformatics data file with automatic format detection.
#' Uses readr if available, otherwise falls back to base R functions.
#'
#' @param filename Character. Path to file
#' @param sep Character. Column separator (NULL for whitespace)
#' @param compression Character. Compression format
#' @param comment Character. Comment character
#' @param is_vcf Logical. Whether file is VCF format
#'
#' @return Data frame
#'
#' @examples
#' \dontrun{
#' df <- read_data("data.tsv")
#' }
#'
#' @export
read_data <- function(filename, sep = NULL, compression = NULL, 
                     comment = NULL, is_vcf = FALSE) {
  if (is_vcf) {
    return(read_vcf_file(filename, compression))
  }
  
  # Determine separator
  if (is.null(sep)) {
    sep <- "\t"  # Default to tab
  }
  
  # Try to use readr if available, otherwise use base R
  if (requireNamespace("readr", quietly = TRUE)) {
    # Read with readr
    if (sep == ",") {
      df <- readr::read_csv(
        filename,
        comment = comment %||% "",
        show_col_types = FALSE,
        progress = FALSE
      )
    } else if (sep == "\t") {
      df <- readr::read_tsv(
        filename,
        comment = comment %||% "",
        show_col_types = FALSE,
        progress = FALSE
      )
    } else {
      df <- readr::read_delim(
        filename,
        delim = sep,
        comment = comment %||% "",
        show_col_types = FALSE,
        progress = FALSE
      )
    }
    return(as.data.frame(df))
  } else {
    # Fallback to base R
    # Handle compression
    if (!is.null(compression) && compression == "gzip" || grepl("\\.gz$", filename)) {
      con <- gzfile(filename, "rt")
    } else {
      con <- file(filename, "rt")
    }
    
    # Read file
    df <- read.table(
      con,
      header = TRUE,
      sep = sep,
      comment.char = comment %||% "",
      stringsAsFactors = FALSE,
      check.names = FALSE
    )
    close(con)
    
    return(df)
  }
}

#' Null-coalescing operator
#' @keywords internal
`%||%` <- function(x, y) {
  if (is.null(x)) y else x
}
