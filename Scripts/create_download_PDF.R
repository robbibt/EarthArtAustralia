library(rmarkdown)

# Set working directory and name
setwd("D:/Dropbox/EarthArtAustralia/")
name = "Streams of Arid Australia"

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

# Open resulting file
shell.exec(paste0(getwd(), "/", to_name))

# Create tags
tags = function(name) {
  
  suffix = c("map", "art", "poster")
  tag_list = paste(name, suffix, collapse = ', ')
  tag_list = paste0(tag_list, ", home decor, map art, unique gift, map print, wall art, art print, gift idea")
  
  print(tag_list)
  writeClipboard(tag_list)
  
}

tags(name = "North Carolina")
tags(name = strsplit(name, split = " ")[[1]][3])


