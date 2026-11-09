# PubMed özetlerini NCBI E-utilities ile indirir ve data/pubmed_egfr.csv yazar.
#
# Kullanım:  Rscript data/fetch_pubmed.R
#
# Kurgu: Her yıl için (2015-2026) "EGFR + akciğer" sorgusu çalıştırılır ve her
# yıldan en fazla 60 özet alınır. Böylece yıllar arası karşılaştırma
# (dönemin tıbbi uygulamaları nasıl değişti?) dengeli bir veri kümesi üzerinden
# yapılabilir.
#
# Kaynak: https://www.ncbi.nlm.nih.gov/books/NBK25501/ (NCBI kaynak kullanımı)

library(tidyverse)
library(xml2)
library(jsonlite)

base_query <- 'EGFR[tiab] AND lung[tiab]'
years      <- 2015:2026
per_year   <- 60
out_file   <- "data/pubmed_egfr.csv"

esearch_one <- function(year) {
  query <- paste0(base_query, " AND ", year, "[dp]")
  url   <- paste0(
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
    "?db=pubmed&retmode=json&retmax=", per_year, "&sort=relevance&term=",
    URLencode(query, reserved = TRUE)
  )
  fromJSON(url)$esearchresult$idlist
}

parse_node <- function(node) {
  txt <- function(xpath) {
    v <- xml_text(xml_find_first(node, xpath))
    if (length(v) == 0 || is.na(v)) NA_character_ else trimws(v)
  }
  abs_nodes <- xml_find_all(node, ".//Abstract/AbstractText")
  abstract   <- if (length(abs_nodes) == 0) NA_character_ else
                   trimws(paste(xml_text(abs_nodes), collapse = " "))
  tibble(
    pmid     = txt(".//PMID"),
    year     = txt(".//PubDate/Year"),
    journal  = txt(".//Journal/Title"),
    title    = txt(".//ArticleTitle"),
    abstract = abstract
  )
}

pmids <- map(years, esearch_one)
cat("Bulunan kayit:", length(unlist(pmids)), "\n")

# NCBI efetch isteklerinde URL uzunlugu sinirli: 100'er PMID'lik paketler halinde indir
chunks <- split(unlist(pmids), ceiling(seq_along(unlist(pmids)) / 100))
nodes  <- do.call(c, map(chunks, function(ids) {
  u <- paste0(
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=",
    paste(ids, collapse = ",")
  )
  f <- tempfile(fileext = ".xml")
  download.file(u, f, quiet = TRUE, mode = "wb")
  Sys.sleep(0.4)
  xml_find_all(read_xml(f), "//PubmedArticle")
}))

articles <- map_dfr(nodes, parse_node) |>
  filter(!is.na(abstract), nchar(abstract) > 200) |>
  distinct(pmid, .keep_all = TRUE) |>
  mutate(across(c(title, abstract), ~ str_squish(.))) |>
  mutate(year = as.integer(year))

write_csv(articles, out_file)
cat("Kaydedilen:", nrow(articles), "ozet ->", out_file, "\n")
print(articles |> count(year, name = "n"))