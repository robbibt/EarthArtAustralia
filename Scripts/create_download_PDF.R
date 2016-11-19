library(rmarkdown)

# Set working directory and name
setwd("D:/Dropbox/EarthArtAustralia/")
name = "Waterways of Norway"

# Render R markdown file as PDF inside 'scripts' directory
render("Scripts/DownloadandPrintingGuide.Rmd", "pdf_document", 
       params = list(name = name))

# Append map name to file name and copy to PDF download directory
from_name = "Scripts/DownloadandPrintingGuide.pdf"
to_name = paste0("Download links/DownloadandPrintingGuide-", gsub(" ", "", name, fixed = TRUE), ".pdf")
file.copy(from=from_name, to = to_name, overwrite = TRUE)

# Remove original PDF and temporary TEX directories
unlink("Scripts/tex2pdf*", recursive = TRUE)
file.remove(from_name)
