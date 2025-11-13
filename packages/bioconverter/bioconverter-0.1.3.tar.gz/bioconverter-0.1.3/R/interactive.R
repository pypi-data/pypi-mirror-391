#' Auto-detect Omics Type
#'
#' @description
#' Automatically detect the type of omics data based on column names.
#'
#' @param df Data frame. Input data
#'
#' @return Character. Detected omics type
#'
#' @examples
#' \dontrun{
#' omics_type <- auto_detect_omics_type(df)
#' }
#'
#' @export
auto_detect_omics_type <- function(df) {
  columns <- tolower(colnames(df))
  
  # Count matches for each omics type
  genomics_terms <- c("chr", "pos", "snp", "rsid", "pval", "beta", "gwas")
  transcriptomics_terms <- c("gene", "fpkm", "tpm", "counts", "expression", "log2fc", "padj")
  proteomics_terms <- c("protein", "peptide", "abundance", "intensity")
  metabolomics_terms <- c("metabolite", "mz", "rt", "peak", "concentration")
  
  genomics_score <- sum(sapply(genomics_terms, function(term) {
    any(grepl(term, columns))
  }))
  
  transcriptomics_score <- sum(sapply(transcriptomics_terms, function(term) {
    any(grepl(term, columns))
  }))
  
  proteomics_score <- sum(sapply(proteomics_terms, function(term) {
    any(grepl(term, columns))
  }))
  
  metabolomics_score <- sum(sapply(metabolomics_terms, function(term) {
    any(grepl(term, columns))
  }))
  
  scores <- c(
    genomics = genomics_score,
    transcriptomics = transcriptomics_score,
    proteomics = proteomics_score,
    metabolomics = metabolomics_score
  )
  
  if (max(scores) == 0) {
    return("unknown")
  }
  
  return(names(which.max(scores)))
}

#' Auto-suggest Column Mapping
#'
#' @description
#' Automatically suggest column mappings based on recognized patterns.
#'
#' @param input_file Character. Path to input file OR a data frame
#' @param n_rows Integer. Number of rows to read for analysis (default: 1000)
#'
#' @return Named list with suggested column mappings
#'
#' @examples
#' \dontrun{
#' # From file
#' suggestions <- auto_suggest_mapping("gwas_data.tsv")
#'
#' # From data frame
#' suggestions <- auto_suggest_mapping(df)
#' }
#'
#' @export
auto_suggest_mapping <- function(input_file, n_rows = 1000) {
  # Check if input is a data frame or file path
  if (is.data.frame(input_file)) {
    df <- input_file
    if (nrow(df) > n_rows) {
      df <- df[1:n_rows, , drop = FALSE]
    }
  } else {
    # Read sample data
    # Detect format
    format_info <- detect_file_format(input_file)
    
    # Read sample
    if (format_info$is_vcf) {
      df <- read_vcf_file(input_file, format_info$compression)
      if (nrow(df) > n_rows) {
        df <- df[1:n_rows, , drop = FALSE]
      }
    } else if (requireNamespace("readr", quietly = TRUE)) {
      # Use readr if available
      if (!is.null(format_info$sep) && format_info$sep == ",") {
        df <- readr::read_csv(
          input_file,
          n_max = n_rows,
          show_col_types = FALSE,
          progress = FALSE
        )
      } else {
        df <- readr::read_tsv(
          input_file,
          n_max = n_rows,
          show_col_types = FALSE,
          progress = FALSE
        )
      }
      df <- as.data.frame(df)
    } else {
      # Fallback to base R with read_data
      df <- read_data(
        input_file,
        sep = format_info$sep,
        compression = format_info$compression,
        comment = format_info$comment,
        is_vcf = format_info$is_vcf
      )
      if (nrow(df) > n_rows) {
        df <- df[1:n_rows, , drop = FALSE]
      }
    }
  }
  
  # Get column matches
  col_matches <- match_columns(colnames(df))
  
  # Filter out NULL matches and return as named list
  suggestions <- list()
  for (original_col in names(col_matches)) {
    std_col <- col_matches[[original_col]]
    if (!is.null(std_col)) {
      suggestions[[original_col]] <- std_col
    }
  }
  
  return(suggestions)
}

#' Process Large File with Chunking
#'
#' @description
#' Process large files in chunks to manage memory usage.
#'
#' @param filename Character. Path to input file
#' @param output_file Character. Path to output file
#' @param column_mapping Named list. Column mapping to apply
#' @param chunk_size Integer. Number of rows per chunk (default: 100000)
#' @param verbose Logical. Print progress (default: TRUE)
#' @param ... Additional arguments passed to convert_single_file
#'
#' @return NULL (writes output file)
#'
#' @examples
#' \dontrun{
#' process_large_file(
#'   "large_data.tsv",
#'   "output.tsv",
#'   chunk_size = 50000
#' )
#' }
#'
#' @export
process_large_file <- function(filename,
                               output_file,
                               column_mapping = NULL,
                               chunk_size = 100000,
                               verbose = TRUE,
                               ...) {
  has_readr <- requireNamespace("readr", quietly = TRUE)
  
  if (verbose) {
    cat(sprintf("\nProcessing large file: %s\n", filename))
    cat(sprintf("  Chunk size: %d rows\n", chunk_size))
  }
  
  # Detect format
  format_info <- detect_file_format(filename)
  
  # For VCF files, process normally (they're typically not huge)
  if (format_info$is_vcf) {
    df <- convert_single_file(
      filename,
      column_mapping = column_mapping,
      verbose = verbose,
      ...
    )
    
    if (has_readr) {
      readr::write_tsv(df, output_file)
    } else {
      write.table(df, output_file, sep = "\t", row.names = FALSE, quote = FALSE)
    }
    
    if (verbose) {
      cat(sprintf("\n✓ Output written to: %s\n", output_file))
    }
    
    return(invisible(NULL))
  }
  
  # For regular files, use chunked reading
  if (verbose) {
    cat("  Reading and processing in chunks...\n")
  }
  
  # Read first chunk to get column info
  if (has_readr) {
    if (format_info$sep == ",") {
      first_chunk <- readr::read_csv(
        filename,
        n_max = chunk_size,
        show_col_types = FALSE,
        progress = FALSE
      )
    } else {
      first_chunk <- readr::read_tsv(
        filename,
        n_max = chunk_size,
        show_col_types = FALSE,
        progress = FALSE
      )
    }
    first_chunk <- as.data.frame(first_chunk)
  } else {
    # Use base R - read entire file then subset (not ideal for large files)
    if (verbose) {
      cat("  Warning: readr not available, reading entire file into memory\n")
    }
    first_chunk <- read_data(
      filename,
      sep = format_info$sep,
      compression = format_info$compression,
      comment = format_info$comment,
      is_vcf = format_info$is_vcf
    )
    if (nrow(first_chunk) > chunk_size) {
      first_chunk <- first_chunk[1:chunk_size, , drop = FALSE]
    }
  }
  
  # Auto-suggest mapping if not provided
  if (is.null(column_mapping)) {
    column_mapping <- auto_suggest_mapping(first_chunk)
    if (verbose && length(column_mapping) > 0) {
      cat("  Auto-detected column mappings:\n")
      for (orig in names(column_mapping)) {
        cat(sprintf("    %s -> %s\n", orig, column_mapping[[orig]]))
      }
    }
  }
  
  # Process first chunk
  std_chunk <- standardize_columns(
    first_chunk,
    column_mapping = column_mapping,
    ...
  )
  
  # Write first chunk
  if (has_readr) {
    readr::write_tsv(std_chunk, output_file)
  } else {
    write.table(std_chunk, output_file, sep = "\t", row.names = FALSE, quote = FALSE)
  }
  
  if (verbose) {
    cat(sprintf("  Processed chunk 1: %d rows\n", nrow(std_chunk)))
  }
  
  # Process remaining chunks (only if readr is available)
  if (has_readr) {
    chunk_num <- 1
    skip_rows <- chunk_size
    
    repeat {
      chunk_num <- chunk_num + 1
      
      # Read next chunk
      if (format_info$sep == ",") {
        chunk <- readr::read_csv(
          filename,
          skip = skip_rows,
          n_max = chunk_size,
          show_col_types = FALSE,
          progress = FALSE,
          col_names = colnames(first_chunk)
        )
      } else {
        chunk <- readr::read_tsv(
          filename,
          skip = skip_rows,
          n_max = chunk_size,
          show_col_types = FALSE,
          progress = FALSE,
          col_names = colnames(first_chunk)
        )
      }
      
      chunk <- as.data.frame(chunk)
      
      # Check if we're done
      if (nrow(chunk) == 0) {
        break
      }
      
      # Process chunk
      std_chunk <- standardize_columns(
        chunk,
        column_mapping = column_mapping,
        ...
      )
      
      # Append to file
      readr::write_tsv(std_chunk, output_file, append = TRUE)
      
      if (verbose) {
        cat(sprintf("  Processed chunk %d: %d rows\n", chunk_num, nrow(std_chunk)))
      }
      
      skip_rows <- skip_rows + chunk_size
    }
  } else {
    chunk_num <- 1
    if (verbose) {
      cat("  Note: Chunked processing requires readr package\n")
    }
  }
  
  if (verbose) {
    cat(sprintf("\n✓ Output written to: %s\n", output_file))
    cat(sprintf("  Total chunks processed: %d\n", chunk_num))
  }
  
  return(invisible(NULL))
}

#' Suggest Chunk Size for Large Files
#'
#' @description
#' Suggest an optimal chunk size based on file size and available memory.
#'
#' @param filename Character. Path to file
#' @param available_memory_gb Numeric. Available memory in GB (default: 4)
#'
#' @return Integer. Suggested chunk size in rows
#'
#' @examples
#' \dontrun{
#' chunk_size <- suggest_chunk_size("large_file.tsv")
#' }
#'
#' @export
suggest_chunk_size <- function(filename, available_memory_gb = 4) {
  file_size_mb <- file.info(filename)$size / (1024^2)
  
  if (file_size_mb < 100) {
    # Small files - process all at once
    return(Inf)
  } else if (file_size_mb < 1000) {
    # Medium files
    return(200000L)
  } else if (file_size_mb < 10000) {
    # Large files
    return(100000L)
  } else {
    # Very large files
    return(50000L)
  }
}
