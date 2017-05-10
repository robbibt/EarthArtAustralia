library(rmarkdown)

# Set working directory and name
setwd("D:/Google Drive/EarthArtAustralia/")
name = "Every Road in Dallas"

# Render R markdown file as PDF inside 'scripts' directory
render("Scripts/DownloadandPrintingGuide.Rmd", "pdf_document", 
       params = list(name = name, dropbox_dir = "D:/Google Drive/EarthArtAustralia"))

# Append map name to file name and copy to PDF download directory
from_name = "Scripts/DownloadandPrintingGuide.pdf"
to_name = paste0("Download links/DownloadandPrintingGuide-", 
                 gsub(" ", "", name, fixed = TRUE), ".pdf")
file.copy(from=from_name, to = to_name, overwrite = TRUE)

# Remove original PDF and temporary TEX directories
unlink("Scripts/tex2pdf*", recursive = TRUE)
file.remove(from_name)

# Open resulting file
shell.exec(to_name)

# Create tags
etsy_tags = function(name) {
  
  suffix = c("map", "art", "poster", "print", "gift idea")
  tag_list = paste(name, suffix, collapse = ', ')
  tag_list = paste0(tag_list, ", printable, map art, map print, wall art, art print")
  
  print(tag_list)
  writeClipboard(tag_list)
  
}

etsy_tags(name = "Germany")
etsy_tags(name = tail(strsplit(name, split = " ")[[1]], 1))
