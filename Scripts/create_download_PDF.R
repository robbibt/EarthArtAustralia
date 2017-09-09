# Set up arguments
args = commandArgs(trailingOnly=TRUE)
Sys.setenv(RSTUDIO_PANDOC="C:/Program Files/RStudio/bin/pandoc")
.libPaths("C:/Users/z3287630/Documents/R/win-library/3.3")

# Set working directory and name
setwd("D:/Google Drive/EarthArtAustralia/")

title = args[1]
# title = "Every Road in Vancouver Island"

# Render R markdown file as PDF inside 'scripts' directory
rmarkdown::render("Scripts/DownloadandPrintingGuide.Rmd", "pdf_document",
       params = list(name = title, dropbox_dir = "D:/Google Drive/EarthArtAustralia"), quiet = TRUE)

# Append map name to file name and copy to PDF download directory
from_name = "Scripts/DownloadandPrintingGuide.pdf"
to_name = paste0("Download links/DownloadandPrintingGuide-",
                 gsub(" ", "", title, fixed = TRUE), ".pdf")
file.copy(from=from_name, to = to_name, overwrite = TRUE)

# Remove original PDF and temporary TEX directories
unlink("Scripts/tex2pdf*", recursive = TRUE)
file.remove(from_name)

# Open resulting file
shell.exec(paste0(getwd(), "/", to_name))
