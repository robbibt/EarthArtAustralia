suppressWarnings(library("readxl"))  # version 1.0.0

# Set up arguments
args = commandArgs(trailingOnly=TRUE)
map.title = args[1]
wd = args[2]
# map.title = "Every Road in Austin"
# wd = 'C:\\Users\\Robbi\\Google Drive\\EarthArtAustralia'
# wd = "D:\\Google Drive\\EarthArtAustralia"

# Set up paths
Sys.setenv(RSTUDIO_PANDOC="C:/Program Files/RStudio/bin/pandoc")
.libPaths(c("C:/Users/Robbi/Documents/R/win-library/3.3", "C:/Users/z3287630/Documents/R/win-library/3.3"))

# Set working directory and name
setwd(wd)

# Check if file exists
data_df = read_excel("./Download links/DownloadandPrintingGuide_data.xls")
file_name = data_df[data_df$name == map.title, "file_link"]

if (nrow(file_name) > 0 ) {
  
    dir_name = paste0(".", substr(file_name, 1, nchar(file_name) - 12)) 
    
    if (dir.exists(dir_name)) {

      # Render R markdown file as PDF inside 'scripts' directory
      rmarkdown::render("Scripts/DownloadandPrintingGuide.Rmd", "pdf_document",
             params = list(name = map.title, dropbox_dir = wd), quiet = TRUE)

      # Append map name to file name and copy to PDF download directory
      from_name = "Scripts/DownloadandPrintingGuide.pdf"
      to_name = paste0("Download links/DownloadandPrintingGuide-",
                       gsub(" ", "", map.title, fixed = TRUE), ".pdf")
      file.copy(from=from_name, to = to_name, overwrite = TRUE)

      # Remove original PDF and temporary TEX directories
      unlink("Scripts/tex2pdf*", recursive = TRUE)
      file.remove(from_name)

      # Open resulting file
      shell.exec(paste0(getwd(), "/", to_name))

    } else {

      message(paste0("'", basename(dir_name), "' does not exist; cannot create PDF"))

    }
  
} else {
  
  message(paste0("'", map.title, "' does not exist in excel file; cannot create PDF"))
  
}

  
